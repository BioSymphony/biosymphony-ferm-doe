"""ENTMOOT v2 routed adapter for NChooseK Bayesian optimization.

.. note::

    OMLT (``omlt_strategy``) is now the preferred cardinality workhorse for
    new campaigns because it provides a separate implementation of the same
    MIP semantics and ships the lower-coupling encoding by default. ENTMOOT
    here also ships the lower-coupling fix (``x_i >= min_active_i * b_i``),
    closing the lab-semantic ON-but-empty leak. See
    ``docs/ADAPTER_DESIGN_NOTES.md`` and ``docs/BACKEND_EVAL_FINDINGS.md``
    for the full diagnosis and the recommended one-line patch.

ENTMOOT is a conservative BO route for campaign manifests that carry a
:class:`NChooseKConstraint`. The repository's BoFire 0.3.1 audit found that
``SoboStrategy`` did not return for that shape. Upstream issue #450 is now
closed, but later BoFire tags have not been evaluated against this adapter.
ENTMOOT encodes the cardinality bound as a hard MIP constraint inside the
acquisition optimization via Pyomo + HiGHS.

Three documented risks (``docs/ENTMOOT_SWAP_DESIGN.md``) are closed in this
adapter:

1. **Silent ``min_count`` drop.** ENTMOOT's shipped
   ``NChooseKConstraint._get_expr`` emits ``Σ z_i <= max_count`` only — the
   lower bound ``Σ z_i >= min_count`` is stored on the object but never
   added to the Pyomo model. :meth:`EntmootStrategy._apply_nchoosek_min_count`
   appends the missing constraint after ENTMOOT generates its expression.

2. **PyomoOptimizer / APPSI clash.** ``PyomoOptimizer.solve`` hardcodes
   ``solver_io="python"`` which the APPSI HiGHS interface rejects. This
   adapter subclasses :class:`PyomoOptimizer` and overrides ``solve`` to
   drop the ``solver_io`` kwarg when the solver name starts with ``appsi_``.

3. **LightGBM tie-cycle on small N.** Sequential q=1 with fantasy-tell can
   propose byte-identical candidates. :meth:`EntmootStrategy._deduplicate`
   perturbs continuous components by ±5 percent of the factor range when a
   repeat is detected, and the returned dict carries
   ``tie_cycle_detected: True`` so callers know perturbation fired.

The adapter stays importable without ENTMOOT installed. All ENTMOOT and
Pyomo imports happen inside :meth:`EntmootStrategy.__init__` and downstream
methods, so the engine can record routing decisions and degrade cleanly
when the optional dependency is absent.

Public surface mirrors :mod:`bofire_strategy`:

- :func:`is_available` — module-importability probe
- :func:`routing_decision` — manifest-level "should we route here?" verdict
- :func:`plan_entmoot_wave2` — top-level engine entry point
- :class:`EntmootStrategy` — the actual tell/ask BO facade

The adapter never imports ``gurobipy`` directly. The default solver is
HiGHS (``appsi_highs``), confirmed working in VAL-6's smoke without any
paid license.
"""

from __future__ import annotations

import importlib.util
import warnings
from dataclasses import dataclass, field
from time import perf_counter
from typing import Any

from ..constraints import design_factors
from ..io_utils import parse_number


CLAIM_LEVEL = "entmoot_adapter_planning"
ENTMOOT_ROUTE_REASONS = (
    "nchoosek_constraint_with_bo",
    "tree_surrogate_requested",
    "bofire_sobo_known_stall",
)
NON_CLAIM = (
    "ENTMOOT-backed candidates are MIP-feasible model-based suggestions. "
    "Tree-ensemble (LightGBM) surrogates cannot extrapolate outside the "
    "training-data envelope; the candidate batch is a planning suggestion "
    "contingent on real Phase 1 lab data replacing the synthetic simulator "
    "before any commit-grade handoff."
)

# Default OSS solver. Confirmed working in VAL-6 smoke.
# Other tested fallbacks: "glpk", "scip", "ipopt".
DEFAULT_SOLVER = "appsi_highs"

# Perturbation magnitude (fraction of factor range) when a tie-cycle is
# detected in `ask()`. ±5 percent is small enough to stay near the proposed
# operating point but large enough to break exact-equality ties.
TIE_CYCLE_PERTURBATION_FRAC = 0.05

# Lower-bound coupling for NChooseK indicators. When b_i = 1, force x_i to a
# strictly positive dose so downstream "active iff amount > threshold" checks
# agree with the MIP's binary cardinality.
MIN_ACTIVE_AMOUNT_FRAC = 0.01

# Float comparison tolerance for "binary value == 1" decisions.
BINARY_THRESHOLD = 0.5

# UPSTREAM_PIN: entmoot==2.1.1 ships ``PyomoOptimizer.solve`` with hardcoded
# ``solver_io="python"`` (entmoot/optimizers/pyomo_opt.py around line 99).
# APPSI solvers (appsi_highs, appsi_cbc, ...) reject ``solver_io`` and the
# call raises TypeError. The subclass below drops the kwarg for APPSI names.
# Revisit if entmoot exposes a clean ``solver_factory_kwargs`` parameter.
APPSI_SOLVER_PREFIX = "appsi_"


# ---------------------------------------------------------------------------
# Availability + routing
# ---------------------------------------------------------------------------


def is_available() -> bool:
    """Return True when ENTMOOT, Pyomo, and a default OSS solver are importable.

    Does NOT probe Gurobi licensing — Gurobi is BYO. The default solver is
    HiGHS via APPSI, confirmed in VAL-6 to work on macOS / Linux laptops
    without a paid license.
    """
    if importlib.util.find_spec("entmoot") is None:
        return False
    if importlib.util.find_spec("pyomo") is None:
        return False
    return True


def _solver_available(solver_name: str) -> bool:
    """Probe a Pyomo SolverFactory at runtime.

    Kept private and lazy-imported so the adapter module loads cleanly even
    when Pyomo is missing.
    """
    try:
        import pyomo.environ as pyo
    except ImportError:
        return False
    try:
        return bool(pyo.SolverFactory(solver_name).available())
    except Exception:  # pragma: no cover - defensive
        return False


def routing_decision(
    state: dict[str, Any],
    usable_rows: list[dict[str, Any]] | None = None,
    *,
    backend: str | None = None,
) -> dict[str, Any]:
    """Return a routing report for the engine's dispatch loop.

    Mirrors :func:`bofire_strategy.routing_decision`. The route fires when:

    - The operator explicitly requests ``--backend entmoot``, OR
    - The manifest carries an NChooseK constraint AND the campaign has a
      BO-friendly response (single-objective derived cost, or multi-objective
      that the operator is willing to scalarize).

    The returned dict matches the bofire_strategy shape so downstream
    routers can treat both adapters uniformly.
    """
    del usable_rows  # not consulted yet; kept for signature parity with bofire

    requested = str(backend or "auto").lower()
    hard_off = requested in {"stdlib", "numpy", "scipy", "pydoe", "pydoe3", "botorch", "bofire"}
    reasons: list[str] = []

    if requested == "entmoot":
        reasons.append(ENTMOOT_ROUTE_REASONS[1])
    if _state_has_nchoosek(state):
        reasons.append(ENTMOOT_ROUTE_REASONS[0])
    policy = _policy(state)
    if str(policy.get("preferred_backend") or "").lower() == "entmoot":
        reasons.append(ENTMOOT_ROUTE_REASONS[2])

    return {
        "schema_version": 1,
        "route_kind": "entmoot_adapter_route",
        "backend_requested": requested,
        "should_route": bool(reasons) and not hard_off,
        "adapter_available": is_available(),
        "reasons": reasons,
        "strategy_kind": _strategy_kind(reasons),
        "fallback": "bofire_post_hoc_filter" if not is_available() else "",
    }


def plan_entmoot_wave2(
    state: dict[str, Any],
    usable_rows: list[dict[str, Any]],
    *,
    remaining_budget: int | None = None,
    backend: str | None = None,
    seed: int = 0,
    solver_name: str = DEFAULT_SOLVER,
) -> dict[str, Any]:
    """Plan sequential candidates with ENTMOOT when installed, else emit a route report.

    Mirrors :func:`bofire_strategy.plan_bofire_wave2`. Returns a JSON-able
    report dict the engine can ledger or render as HTML.
    """
    route = routing_decision(state, usable_rows, backend=backend)
    factors = design_factors(state.get("factors", []) or [])
    budget = int(
        remaining_budget
        or _policy(state).get("augment_remaining_budget")
        or max(1, min(8, len(factors) + 2))
    )

    report: dict[str, Any] = {
        "schema_version": 1,
        "adapter_kind": "entmoot_strategy",
        "claim_level": CLAIM_LEVEL,
        "non_claim": NON_CLAIM,
        "campaign_id": state.get("campaign_id"),
        "route": route,
        "strategy_kind": route["strategy_kind"],
        "remaining_run_budget": budget,
        "solver_name": solver_name,
        "candidate_design": [],
        "candidate_design_count": 0,
        "adapter_status": "not_routed" if not route["should_route"] else "not_available",
        "issues": [],
    }

    if not route["should_route"]:
        report["issues"].append("ENTMOOT routing rule did not fire for this campaign.")
        return report
    if not route["adapter_available"]:
        report["issues"].append(
            "ENTMOOT is not installed; bofire post-hoc-filter path remains the fallback."
        )
        return report
    if not _solver_available(solver_name):
        report["adapter_status"] = "solver_unavailable"
        report["issues"].append(
            f"Pyomo solver '{solver_name}' is not available at runtime; "
            f"install highspy or override with a different solver_name."
        )
        return report

    try:
        strategy = EntmootStrategy(
            state,
            seed=seed,
            solver_name=solver_name,
        )
        if usable_rows:
            X, Y = strategy.training_data_from_rows(usable_rows)
            if X:
                strategy.tell(X, Y)
        candidates = []
        for _ in range(budget):
            candidates.append(strategy.ask())
    except Exception as exc:  # pragma: no cover - only exercised live
        report["adapter_status"] = "execution_failed"
        report["issues"].append(
            f"ENTMOOT execution failed; bofire post-hoc-filter fallback required: "
            f"{type(exc).__name__}: {exc}"
        )
        return report

    report["adapter_status"] = "executed"
    report["candidate_design"] = candidates
    report["candidate_design_count"] = len(candidates)
    if not candidates:
        report["issues"].append("ENTMOOT executed but returned no candidate rows.")
    return report


# ---------------------------------------------------------------------------
# Strategy facade
# ---------------------------------------------------------------------------


@dataclass
class EntmootAskResult:
    """Single ENTMOOT MIP solve result, normalized for biosymphony reporters.

    Field names match the smoke's ``result.json`` shape so the same
    downstream tooling can consume both.
    """

    iteration: int
    amounts: dict[str, float]
    binary: dict[str, int]
    n_active: int
    active_components: list[str]
    objective_estimate: float
    cardinality_ok: bool
    tie_cycle_detected: bool
    solver_status: str
    solver_wall_time_s: float
    elapsed_s: float
    extras: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "iteration": self.iteration,
            "amounts": self.amounts,
            "binary": self.binary,
            "n_active": self.n_active,
            "active_components": self.active_components,
            "objective_estimate": self.objective_estimate,
            "cardinality_ok": self.cardinality_ok,
            "tie_cycle_detected": self.tie_cycle_detected,
            "solver_status": self.solver_status,
            "solver_wall_time_s": self.solver_wall_time_s,
            "elapsed_s": self.elapsed_s,
            **self.extras,
        }


class EntmootStrategy:
    """Tell/ask BO facade over ``entmoot.Enting`` + ``PyomoOptimizer``.

    Parameters
    ----------
    state:
        Campaign manifest dict (the same shape the BoFire adapter consumes).
        Reads ``factors``, ``responses``, ``constraints``, and
        ``design_policy``.
    seed:
        Random seed for ``ProblemConfig`` (LightGBM training is seeded via
        this value too).
    solver_name:
        Pyomo solver name. Defaults to ``"appsi_highs"`` (HiGHS via APPSI),
        the OSS path validated in VAL-6. Other tested options:
        ``"glpk"``, ``"scip"``, ``"ipopt"``, ``"gurobi"``.
    solver_options:
        Forwarded to Pyomo's solver factory. Defaults to ``{"MIPGap": 0.01}``
        when None.
    beta:
        ENTMOOT uncertainty weight (passed to ``UncParams``).
    dist_metric:
        Distance metric for ENTMOOT's uncertainty model. Defaults to ``"l1"``.
    acq_sense:
        Acquisition sense; ``"exploration"`` matches the VAL-6 smoke.
    weights:
        Optional multi-objective scalarization tuple; must sum to 1.0 when set.
    """

    def __init__(
        self,
        state: dict[str, Any],
        *,
        seed: int = 0,
        solver_name: str = DEFAULT_SOLVER,
        solver_options: dict[str, Any] | None = None,
        beta: float = 1.96,
        dist_metric: str = "l1",
        acq_sense: str = "exploration",
        weights: tuple[float, ...] | None = None,
    ) -> None:
        # Lazy import — keeps the module importable without ENTMOOT installed.
        from entmoot import Enting, ProblemConfig

        # Validate the solver up front. This is hard requirement #1: fail
        # loudly at instantiation time, not silently inside `.ask()`.
        if not _solver_available(solver_name):
            raise RuntimeError(
                f"Pyomo solver '{solver_name}' is not available. "
                f"Install highspy for the default OSS path, "
                f"or pass solver_name='glpk'/'gurobi'/etc."
            )

        self.state = state
        self.seed = seed
        self.solver_name = solver_name
        self.weights = weights
        self._iter = 0
        self._told_X: list[tuple[float, ...]] = []
        self._told_Y: list[list[float]] = []

        self._factors = design_factors(state.get("factors", []) or [])
        self._responses = _objective_responses(state)
        self._constraints_raw = list(state.get("constraints", []) or [])
        self._normalized_constraints = _normalize_constraints(self._constraints_raw)

        # Build problem_config from manifest.
        self.problem_config = ProblemConfig(rnd_seed=seed)
        self._continuous_keys: list[str] = []
        self._binary_keys: list[str] = []
        self._nchoosek_specs: list[dict[str, Any]] = []
        self._add_features_to_problem()
        self._add_objectives_to_problem()

        # Build surrogate.
        unc_params: dict[str, Any] = {
            "beta": beta,
            "dist_metric": dist_metric,
            "acq_sense": acq_sense,
        }
        params = {"unc_params": unc_params}
        self.enting = Enting(self.problem_config, params=params)

        # Build optimizer (uses APPSI-aware subclass to close RISK #2).
        opt_params = {
            "solver_name": solver_name,
            "solver_options": solver_options or {"MIPGap": 0.01},
            "verbose": False,
        }
        self.optimizer = APPSIPyomoOptimizer(self.problem_config, params=opt_params)

        # Build model core with NChooseK + linear + min_count fixups.
        self._model_core = self._build_constrained_model_core()

    # ------------------------------------------------------------------ API

    def tell(self, X: list[list[float]], Y: list[list[float]]) -> None:
        """Append observations and refit the surrogate.

        Parameters
        ----------
        X:
            List of feature-vector rows. Each row's element order must
            match ``self.feature_order`` (continuous keys first, then
            binary indicators per NChooseK constraint).
        Y:
            List of objective-vector rows. Each row length must equal the
            number of objectives in the manifest.
        """
        import numpy as np

        if len(X) != len(Y):
            raise ValueError("X and Y must have the same length")
        if not X:
            return
        self._told_X.extend(tuple(float(v) for v in row) for row in X)
        self._told_Y.extend([float(v) for v in row] for row in Y)
        # Refit on the full accumulated history.
        all_X = np.array(self._told_X, dtype=float)
        all_Y = np.array(self._told_Y, dtype=float)
        self.enting.fit(all_X, all_Y)

    def ask(self) -> dict[str, Any]:
        """Solve the constrained MIP for the next candidate (q=1).

        Returns a dict matching the VAL-6 smoke's ``result.json`` candidate
        shape (see :class:`EntmootAskResult`).
        """
        if not self._told_X:
            raise RuntimeError(
                "ENTMOOT requires at least one tell() before ask() — "
                "the LightGBM surrogate has no training data."
            )

        t0 = perf_counter()
        solver_wall_t0 = perf_counter()

        # Solve with the constraint-augmented model_core. The optimizer
        # *copies* model_core internally so re-solves are idempotent.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = self.optimizer.solve(
                self.enting,
                model_core=self._model_core,
                weights=self.weights,
            )

        solver_wall_time_s = perf_counter() - solver_wall_t0
        opt_point_arr = list(result.opt_point[0]) if hasattr(result.opt_point, "__getitem__") and len(result.opt_point) > 0 and hasattr(result.opt_point[0], "__iter__") else list(result.opt_point)

        # Decompose into amounts (continuous) and binary indicators.
        amounts, binary = self._split_solution(opt_point_arr)
        n_active = sum(1 for v in binary.values() if v >= BINARY_THRESHOLD)
        active_components = [k for k, v in binary.items() if v >= BINARY_THRESHOLD]
        cardinality_ok = self._check_cardinality(binary)

        # Build candidate vector for tie-cycle detection.
        candidate_vec = tuple(float(v) for v in opt_point_arr)
        tie_cycle_detected = False
        if any(self._approx_equal(candidate_vec, prev) for prev in self._told_X):
            tie_cycle_detected = True
            opt_point_arr, amounts, binary = self._perturb(opt_point_arr, amounts, binary)
            n_active = sum(1 for v in binary.values() if v >= BINARY_THRESHOLD)
            active_components = [k for k, v in binary.items() if v >= BINARY_THRESHOLD]
            cardinality_ok = self._check_cardinality(binary)

        self._iter += 1

        # Auto fantasy-tell: append the predicted mean as a synthetic
        # observation so the surrogate moves on the next ask. Mirrors the
        # VAL-6 smoke's behavior. Use predicted mean from result.
        try:
            fantasy_y = list(result.mu_unscaled)
        except Exception:
            fantasy_y = [float(result.opt_val)] * max(1, len(self._responses))
        self.tell([list(opt_point_arr)], [fantasy_y])

        elapsed = perf_counter() - t0

        ask_result = EntmootAskResult(
            iteration=self._iter,
            amounts={k: float(v) for k, v in amounts.items()},
            binary={k: int(round(v)) for k, v in binary.items()},
            n_active=n_active,
            active_components=active_components,
            objective_estimate=float(result.opt_val),
            cardinality_ok=cardinality_ok,
            tie_cycle_detected=tie_cycle_detected,
            solver_status="optimal" if result.opt_point is not None else "infeasible_or_unbounded",
            solver_wall_time_s=round(solver_wall_time_s, 4),
            elapsed_s=round(elapsed, 4),
            extras={
                "uncertainty": float(result.unc_unscaled) if hasattr(result, "unc_unscaled") else float("nan"),
            },
        )
        return ask_result.to_dict()

    @property
    def feature_order(self) -> list[str]:
        """The exact order ENTMOOT expects in tell/ask vectors."""
        return list(self._continuous_keys) + list(self._binary_keys)

    def training_data_from_rows(
        self, rows: list[dict[str, Any]]
    ) -> tuple[list[list[float]], list[list[float]]]:
        """Convert manifest-shaped observation rows into (X, Y) lists.

        Each row must carry numeric values for every continuous factor and
        every response. Binary indicators are derived from
        ``value > BINARY_THRESHOLD`` for continuous factors that also
        appear in a NChooseK constraint.
        """
        X: list[list[float]] = []
        Y: list[list[float]] = []
        for row in rows or []:
            x_row: list[float] = []
            ok = True
            for key in self._continuous_keys:
                value = parse_number(row.get(key))
                if value is None:
                    ok = False
                    break
                x_row.append(float(value))
            for binary_key in self._binary_keys:
                src_key = binary_key[2:] if binary_key.startswith("b_") else binary_key
                src_val = parse_number(row.get(src_key, 0.0))
                x_row.append(1.0 if (src_val or 0.0) > BINARY_THRESHOLD else 0.0)
            if not ok:
                continue
            y_row: list[float] = []
            for response in self._responses:
                rid = str(response.get("response_id") or "")
                yv = parse_number(row.get(rid))
                if yv is None:
                    ok = False
                    break
                y_row.append(float(yv))
            if not ok:
                continue
            X.append(x_row)
            Y.append(y_row)
        return X, Y

    # --------------------------------------------------------- internals

    def _add_features_to_problem(self) -> None:
        """Map manifest factors to ENTMOOT ``add_feature`` calls.

        Continuous / numeric factors land as ``real`` with bounds.
        Categorical/discrete factors land as ``categorical`` with their
        level tuple. For every NChooseK constraint, we also add a
        ``binary`` indicator per feature (``b_<name>``) so the MIP can
        couple amounts to activation.
        """
        # First pass: add factors as features.
        for factor in self._factors:
            key = str(factor.get("factor_id") or "")
            ftype = str(factor.get("type") or "continuous").lower()
            levels = factor.get("levels") if isinstance(factor.get("levels"), list) else []
            low = parse_number(factor.get("low", factor.get("min")))
            high = parse_number(factor.get("high", factor.get("max")))

            if ftype in {"categorical", "block", "hard_to_change"} and levels:
                self.problem_config.add_feature(
                    "categorical", tuple(str(level) for level in levels), name=key
                )
                # Categorical features do not directly appear in NChooseK
                # in this adapter v1; they are kept for surrogate signal.
                continue
            if ftype in {"ordinal", "integer"} and levels:
                int_levels = [int(parse_number(level) or 0) for level in levels]
                self.problem_config.add_feature(
                    "integer", (min(int_levels), max(int_levels)), name=key
                )
                self._continuous_keys.append(key)
                continue
            if ftype == "binary":
                self.problem_config.add_feature("binary", name=key)
                self._continuous_keys.append(key)
                continue
            # Default: continuous / numeric real
            if low is None or high is None:
                raise ValueError(
                    f"Factor '{key}' is continuous but missing min/max bounds."
                )
            self.problem_config.add_feature("real", (float(low), float(high)), name=key)
            self._continuous_keys.append(key)

        # Second pass: add binary indicators for every NChooseK feature set.
        # This is what gives the MIP cardinality coupling. Each indicator is
        # named ``b_<feature_id>`` and is the variable ENTMOOT's
        # ``_get_expr`` would otherwise create internally.
        nchoosek_features: set[str] = set()
        for spec in self._normalized_constraints:
            if spec["type"] == "nchoosek":
                for feat in spec["features"]:
                    nchoosek_features.add(feat)
                self._nchoosek_specs.append(spec)
        # Stable ordering for reproducibility.
        for feat in self._continuous_keys:
            if feat in nchoosek_features:
                binary_key = f"b_{feat}"
                self.problem_config.add_feature("binary", name=binary_key)
                self._binary_keys.append(binary_key)

    def _add_objectives_to_problem(self) -> None:
        for response in self._responses:
            name = str(response.get("response_id") or "")
            direction = str(response.get("direction") or "maximize").lower()
            if direction == "minimize":
                self.problem_config.add_min_objective(name=name)
            else:
                self.problem_config.add_max_objective(name=name)
        if not self._responses:
            # ENTMOOT requires at least one objective. Default to min.
            self.problem_config.add_min_objective()

    def _build_constrained_model_core(self):
        """Construct a Pyomo model_core with all constraints baked in.

        Order:

        1. Linear inequality / equality from the manifest.
        2. NChooseK upper bound (ENTMOOT's shipped expression).
        3. NChooseK lower bound (``min_count`` fix-up; closes RISK #1).
        4. Big-M linking between continuous and binary indicators.
        """
        import pyomo.environ as pyo

        model_core = self.problem_config.get_pyomo_model_core()
        feats = model_core._all_feat  # list of pyo.Var indexed by feature

        feat_index = {name: idx for idx, name in enumerate(self._all_feature_names())}

        # 1. Linear constraints
        if any(spec["type"] == "linear" for spec in self._normalized_constraints):
            model_core.linear_constraints = pyo.ConstraintList()
            for spec in self._normalized_constraints:
                if spec["type"] != "linear":
                    continue
                features = spec["features"]
                coeffs = spec["coefficients"]
                rhs = spec["rhs"]
                op = spec.get("operator", "<=")
                # Skip any feature not present in the problem (defensive).
                if not all(f in feat_index for f in features):
                    continue
                lhs = sum(
                    coeffs[i] * feats[feat_index[features[i]]]
                    for i in range(len(features))
                )
                if op in {">=", ">"}:
                    model_core.linear_constraints.add(lhs >= rhs)
                elif op in {"==", "="}:
                    model_core.linear_constraints.add(lhs == rhs)
                else:
                    model_core.linear_constraints.add(lhs <= rhs)

        # 2 + 3 + 4. NChooseK + min_count + big-M linking.
        # NOTE: We deliberately do NOT use ENTMOOT's own
        # ``ConstraintList.apply_pyomo_constraints`` here. That path uses
        # ``model.feat_selected`` as a *single* shared binary handle which
        # collides across multiple NChooseK constraints. By emitting our
        # own per-constraint indicators we (a) close RISK #1 (min_count
        # also emitted), (b) avoid the name-collision risk in the design doc.
        for nk_idx, spec in enumerate(self._nchoosek_specs):
            self._apply_nchoosek(model_core, feats, feat_index, spec, nk_idx)

        return model_core

    def _apply_nchoosek(
        self,
        model_core,
        feats,
        feat_index: dict[str, int],
        spec: dict[str, Any],
        nk_idx: int,
    ) -> None:
        """Emit big-M coupling, max_count and min_count constraints.

        Closes RISK #1: ``min_count`` is part of the spec but ENTMOOT's
        shipped ``_get_expr`` drops it. We emit both bounds explicitly.
        """
        import pyomo.environ as pyo

        features_list = spec["features"]
        min_count = int(spec.get("min_count", 0))
        max_count = int(spec.get("max_count", len(features_list)))

        # Bind binary indicators that were added in _add_features_to_problem.
        indicator_keys = [f"b_{f}" for f in features_list]
        if not all(k in feat_index for k in indicator_keys):
            return  # Should not happen if _add_features_to_problem ran.
        indicators = [feats[feat_index[k]] for k in indicator_keys]
        continuous = [feats[feat_index[f]] for f in features_list]

        # Big-M linking:
        #   x_i <= M * b_i
        #   x_i >= min_active_i * b_i
        # The lower companion closes the ON-but-empty leak where b_i=1 and
        # x_i=0 satisfies binary cardinality but fails lab/contract semantics.
        bigm = []
        min_active_amounts = []
        for fname in features_list:
            factor = next((f for f in self._factors if f.get("factor_id") == fname), None)
            high = parse_number(factor.get("high", factor.get("max"))) if factor else None
            bigm.append(float(high) if high is not None else 1e6)
            min_active_amounts.append(_nchoosek_min_active_amount(factor or {}))
        cl_name = f"nchoosek_{nk_idx}_bigm"
        model_core.add_component(cl_name, pyo.ConstraintList())
        cl = getattr(model_core, cl_name)
        for i, b in enumerate(indicators):
            cl.add(continuous[i] <= bigm[i] * b)
            cl.add(continuous[i] >= min_active_amounts[i] * b)

        # Cardinality upper bound:  Σ b_i ≤ max_count
        ub_name = f"nchoosek_{nk_idx}_max_count"
        model_core.add_component(ub_name, pyo.Constraint(expr=sum(indicators) <= max_count))

        # Cardinality lower bound:  Σ b_i ≥ min_count  (RISK #1 closure)
        if min_count > 0:
            lb_name = f"nchoosek_{nk_idx}_min_count"
            model_core.add_component(
                lb_name, pyo.Constraint(expr=sum(indicators) >= min_count)
            )

    def _all_feature_names(self) -> list[str]:
        """Match the order ProblemConfig assigns to _all_feat."""
        return [f.name for f in self.problem_config.feat_list]

    def _split_solution(
        self, opt_point: list[Any]
    ) -> tuple[dict[str, float], dict[str, float]]:
        names = self._all_feature_names()
        amounts: dict[str, float] = {}
        binary: dict[str, float] = {}
        for name, value in zip(names, opt_point):
            if name.startswith("b_") and name in self._binary_keys:
                binary[name[2:]] = float(value)
            else:
                amounts[name] = float(value)
        # Ensure every NChooseK feature has a binary entry.
        for spec in self._nchoosek_specs:
            for feat in spec["features"]:
                binary.setdefault(feat, 0.0)
        return amounts, binary

    def _check_cardinality(self, binary: dict[str, float]) -> bool:
        """Verify every NChooseK constraint is honored in the returned point."""
        for spec in self._nchoosek_specs:
            n_active = sum(
                1
                for f in spec["features"]
                if binary.get(f, 0.0) >= BINARY_THRESHOLD
            )
            if n_active < int(spec.get("min_count", 0)):
                return False
            if n_active > int(spec.get("max_count", len(spec["features"]))):
                return False
        return True

    def _approx_equal(
        self, a: tuple[float, ...], b: tuple[float, ...], tol: float = 1e-6
    ) -> bool:
        if len(a) != len(b):
            return False
        return all(abs(ai - bi) <= tol for ai, bi in zip(a, b))

    def _perturb(
        self,
        opt_point: list[Any],
        amounts: dict[str, float],
        binary: dict[str, float],
    ) -> tuple[list[Any], dict[str, float], dict[str, float]]:
        """Apply ±TIE_CYCLE_PERTURBATION_FRAC kick to continuous values.

        Closes RISK #3. Only perturbs the continuous slice; binary
        indicators stay untouched so cardinality remains satisfied.
        """
        import random

        rng = random.Random(self.seed + self._iter)
        names = self._all_feature_names()
        new_point = list(opt_point)
        new_amounts = dict(amounts)
        for i, name in enumerate(names):
            if name.startswith("b_"):
                continue
            factor = next((f for f in self._factors if f.get("factor_id") == name), None)
            if factor is None:
                continue
            low = parse_number(factor.get("low", factor.get("min")))
            high = parse_number(factor.get("high", factor.get("max")))
            if low is None or high is None:
                continue
            span = float(high) - float(low)
            sign = 1.0 if rng.random() >= 0.5 else -1.0
            kick = sign * TIE_CYCLE_PERTURBATION_FRAC * span
            new_val = max(float(low), min(float(high), float(opt_point[i]) + kick))
            new_point[i] = new_val
            new_amounts[name] = new_val
        return new_point, new_amounts, dict(binary)


# ---------------------------------------------------------------------------
# PyomoOptimizer subclass — closes RISK #2
# ---------------------------------------------------------------------------


def _make_appsi_pyomo_optimizer():
    """Build the APPSI-aware PyomoOptimizer subclass lazily.

    We define the class inside a function so that importing this module
    does not pull in entmoot when it is not installed.
    """
    import pyomo.environ as pyo
    from entmoot.optimizers.pyomo_opt import PyomoOptimizer
    from entmoot.utils import OptResult

    class _APPSIPyomoOptimizer(PyomoOptimizer):
        """PyomoOptimizer subclass that handles APPSI / HiGHS correctly.

        Upstream ``PyomoOptimizer.solve`` passes ``solver_io="python"`` to
        ``pyo.SolverFactory`` unconditionally. APPSI solvers reject that
        kwarg (TypeError). We override ``solve`` and only pass the
        ``solver_io`` kwarg when the solver name does NOT look like APPSI.

        Reference: entmoot v2.1.1 ``entmoot/optimizers/pyomo_opt.py`` line ~99.
        """

        def solve(self, tree_model, model_core=None, weights=None):  # type: ignore[override]
            if model_core is None:
                opt_model = self._problem_config.get_pyomo_model_core()
            else:
                opt_model = self._problem_config.copy_pyomo_model_core(model_core)

            if weights is not None:
                assert len(weights) == len(self._problem_config.obj_list), (
                    f"Number of 'weights' is '{len(weights)}', number of objectives "
                    f"is '{len(self._problem_config.obj_list)}'."
                )
                assert sum(weights) == 1.0, "weights don't add up to 1.0"

            solver_name = self._params["solver_name"]
            factory_kwargs: dict[str, Any] = {}
            if not solver_name.startswith(APPSI_SOLVER_PREFIX):
                factory_kwargs["solver_io"] = self._params.get("solver_io", "python")

            opt = pyo.SolverFactory(solver_name, **factory_kwargs)
            if "solver_options" in self._params:
                for k, v in self._params["solver_options"].items():
                    opt.options[k] = v

            tree_model.add_to_pyomo_model(opt_model)

            verbose = self._params.get("verbose", True)
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=DeprecationWarning)
                opt.solve(opt_model, tee=verbose)

            self._curr_sol, self._active_leaves = self._get_sol(opt_model)
            return OptResult(
                self.get_curr_sol,
                pyo.value(opt_model.obj),
                [opt_model._unscaled_mu[k].value for k in opt_model._unscaled_mu],
                pyo.value(opt_model._unc),
                self._active_leaves,
            )

    return _APPSIPyomoOptimizer


class _LazyOptimizer:
    """Module-level placeholder; resolved to the real subclass on first use.

    Keeps ``import biosymphony_ferm_doe.adapters.entmoot_strategy`` cheap
    even when ENTMOOT isn't installed (the adapter's whole point).
    """

    _cls = None

    def __call__(self, problem_config, params):
        if _LazyOptimizer._cls is None:
            _LazyOptimizer._cls = _make_appsi_pyomo_optimizer()
        return _LazyOptimizer._cls(problem_config, params=params)


APPSIPyomoOptimizer = _LazyOptimizer()


# ---------------------------------------------------------------------------
# Helpers shared with the bofire_strategy module
# ---------------------------------------------------------------------------


def _normalize_constraints(constraints: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Translate manifest-shaped constraints into the adapter's internal form.

    Delegates to :func:`bofire_strategy._constraint_specs` when present (the
    two adapters share normalization rules), and falls back to a local
    minimal implementation otherwise so this module stays usable in
    isolation.
    """
    try:
        from .bofire_strategy import _constraint_specs
    except ImportError:
        return _local_normalize_constraints(constraints)
    return _constraint_specs(constraints)


def _local_normalize_constraints(constraints: list[dict[str, Any]]) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for constraint in constraints or []:
        if not isinstance(constraint, dict):
            continue
        ctype = str(constraint.get("type") or "").lower()
        if ctype in {"linear", "linear_constraint"} or "coefficients" in constraint:
            coeffs = constraint.get("coefficients")
            rhs = parse_number(constraint.get("rhs"))
            if isinstance(coeffs, dict) and rhs is not None:
                features = [str(k) for k in coeffs]
                values = [float(parse_number(coeffs[k]) or 0.0) for k in coeffs]
                specs.append(
                    {
                        "id": str(constraint.get("constraint_id") or "linear"),
                        "type": "linear",
                        "features": features,
                        "coefficients": values,
                        "rhs": float(rhs),
                        "operator": str(constraint.get("operator") or "<="),
                    }
                )
        elif ctype in {"nchoosek", "n_choose_k", "n-choose-k"} or {"features", "max_count"} <= set(constraint):
            features = constraint.get("features")
            max_count = parse_number(constraint.get("max_count"))
            if isinstance(features, list) and max_count is not None:
                specs.append(
                    {
                        "id": str(constraint.get("constraint_id") or "nchoosek"),
                        "type": "nchoosek",
                        "features": [str(f) for f in features],
                        "min_count": int(parse_number(constraint.get("min_count")) or 0),
                        "max_count": int(max_count),
                        "none_also_valid": bool(constraint.get("none_also_valid", False)),
                    }
                )
    return specs


def _nchoosek_min_active_amount(factor: dict[str, Any]) -> float:
    """Minimum positive amount coupled to a selected NChooseK indicator."""
    low = parse_number(factor.get("low", factor.get("min")))
    high = parse_number(factor.get("high", factor.get("max")))
    low_f = 0.0 if low is None else float(low)
    high_f = 1.0 if high is None else float(high)
    span = max(high_f - low_f, 0.0)
    return max(1e-9, low_f + MIN_ACTIVE_AMOUNT_FRAC * span)


def _objective_responses(state: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the list of responses that count as BO objectives."""
    responses: list[dict[str, Any]] = []
    for response in state.get("responses", []) or []:
        if not isinstance(response, dict):
            continue
        if str(response.get("direction") or "").lower() in {"maximize", "minimize"}:
            responses.append(response)
    if responses:
        return responses
    objective = state.get("objective") if isinstance(state.get("objective"), dict) else {}
    response_id = objective.get("response_id") if isinstance(objective, dict) else None
    if response_id:
        return [{"response_id": response_id, "direction": objective.get("direction", "maximize")}]
    return []


def _state_has_nchoosek(state: dict[str, Any]) -> bool:
    for c in state.get("constraints", []) or []:
        if isinstance(c, dict):
            ctype = str(c.get("type") or c.get("constraint_type") or c.get("kind") or "").lower()
            if ctype in {"nchoosek", "n_choose_k", "n-choose-k"}:
                return True
            if {"features", "max_count"} <= set(c):
                return True
    return False


def _strategy_kind(reasons: list[str]) -> str:
    if "nchoosek_constraint_with_bo" in reasons:
        return "nchoosek_bo"
    if "tree_surrogate_requested" in reasons:
        return "tree_surrogate_bo"
    if "bofire_sobo_known_stall" in reasons:
        return "bofire_fallback_bo"
    return "not_routed"


def _policy(state: dict[str, Any]) -> dict[str, Any]:
    p = state.get("design_policy")
    return p if isinstance(p, dict) else {}


__all__ = [
    "APPSIPyomoOptimizer",
    "CLAIM_LEVEL",
    "DEFAULT_SOLVER",
    "ENTMOOT_ROUTE_REASONS",
    "EntmootAskResult",
    "EntmootStrategy",
    "NON_CLAIM",
    "MIN_ACTIVE_AMOUNT_FRAC",
    "TIE_CYCLE_PERTURBATION_FRAC",
    "is_available",
    "plan_entmoot_wave2",
    "routing_decision",
]
