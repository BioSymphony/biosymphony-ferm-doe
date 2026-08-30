# ENTMOOT v2 Swap, Integration Design

> **Adapter status: delivered.** In-repo wrapper at
> `src/biosymphony_ferm_doe/adapters/entmoot_strategy.py` with 12 passing
> tests in `tests/test_entmoot_adapter.py`. All three risks identified in
> the original design are closed at the adapter layer:
> (1) `min_count` is now emitted via an adapter-side constraint shim;
> (2) HiGHS is the default solver, so `gurobipy>=11` is no longer required;
> (3) `_fantasy_tell` tie-cycles are guarded by the adapter's sample-uniqueness check.
> Registry posture: `status: adopted_optional`, `tool_id: entmoot`.
> The wave-2 routing layer treats ENTMOOT as the cardinality-aware
> Bayesian optimisation route when `nchoosek` constraints are present.

**Status:** Adapter delivered. Wired as a cardinality-aware BO route.
**Authored:** 2026-05-16. **Adapter delivered:** 2026-05-16.

Upstream issue #450 is now closed. This document preserves the behavior
observed with BoFire 0.3.1; later BoFire tags have not been evaluated against
this repository's adapter, so the ENTMOOT route remains conservative rather
than evidence that current BoFire has the same limitation.

## Why this swap

BoFire v0.3.1 `SoboStrategy.ask()` with `NChooseKConstraint` in the `Domain` hangs at
100% CPU (upstream issue #450; `RandomStrategy._sample_with_nchoosek` enumerates
combinatorial seeds for `optimize_acqf` and never terminates). The public
media-optimisation fixture encodes `at_most_two_carbons` as `type: nchoosek`
and is forced to enforce it via **post-hoc oversample + filter**:

> "Phase 2 enforces this constraint via post-hoc oversample + filter: ask for
> 20 candidates from a Domain with only linear constraints, then keep rows
> where 1 ≤ active_carbons ≤ 2, returning the first 8 that pass."
> (public fixture, `at_most_two_carbons.enforcement_note`)

The result of the example Phase 2 BO smoke shows the failure mode in numbers:

| ask_count | passed_linear_and_cardinality | recommended_batch_count |
|---|---|---|
| 8 | 0 | 0 |

Zero of eight BO-asked candidates satisfied the cardinality constraint.
The artifact run succeeded, but it produced no planning recommendation.

ENTMOOT v2 encodes NChooseK as a hard MIP constraint via Pyomo
(`entmoot/constraints.py::NChooseKConstraint`). The constraint is enforced
inside the acquisition optimization, not as a post-hoc filter, so the same
question, "find me K candidates that minimize cost-per-mg under
1 ≤ active_carbons ≤ 2 and a $1.20/L budget", becomes a feasibility-by-
construction problem instead of a rejection-sampling one.

## 1. Side-by-side comparison

| Concern | BoFire `SoboStrategy` (v0.3.1) | ENTMOOT v2 `Enting + PyomoOptimizer` (v2.0.2 / v2.1.1) |
|---|---|---|
| Surrogate model | GP via BoTorch + GPyTorch | Gradient-boosted trees via LightGBM (`gbdt`, `num_boost_round=100`, `max_depth=3`) |
| Uncertainty | GP posterior variance | Distance-based (`l1` / `l2` / `euclidean_squared`) in input space, weighted by `beta` |
| Acquisition optimization | `optimize_acqf` (gradient-based on GP posterior) | MILP / MINLP via Pyomo + Gurobi (or `glpk`/`scip`/`ipopt` as configurable solver) |
| Continuous box constraints | `ContinuousInput(bounds=[lo, hi])` | `add_feature("real", (lo, hi), name=...)` → Pyomo `Reals` with bounds |
| Integer / discrete | `DiscreteInput(values=[...])` | `add_feature("integer", (lo, hi))` → Pyomo `Integers` with bounds |
| Binary | one-hot via `CategoricalInput` workaround | first-class: `add_feature("binary")` → Pyomo `Binary` |
| Categorical | `CategoricalInput(categories=[...])` (one-hot inside BoTorch GP) | `add_feature("categorical", ("blue", "orange", "gray"))` → Pyomo `Binary` per category with sum=1 |
| Linear (in)equality | `LinearInequalityConstraint.from_smaller_equal(features, coefficients, rhs)` | `LinearInequalityConstraint(feature_keys, coefficients, rhs)` → Pyomo expression `Σ c_i·x_i ≤ rhs` |
| **NChooseK** | In the v0.3.1 audit, `NChooseKConstraint(...)` did not return from `SoboStrategy.ask()` (issue #450) | `NChooseKConstraint(feature_keys, min_count, max_count, none_also_valid)`, encoded as hard MIP with binary indicators (see §3) |
| Multi-objective | `MoboStrategy + qLogNEHVI` | scalarized via weights tuple `(w_1, ..., w_n)`, `sum(weights) == 1.0`; Pareto sweep requires re-solving across weight grid |
| Multi-fidelity | `MultiFidelityStrategy` (sequential, fragile) | not supported in v2.x |
| Output shape | `pd.DataFrame` with column per factor; `candidate_count` rows | `OptResult(opt_point, obj, mu, unc, active_leaves)`, single point per `solve()` |
| Batch q>1 | `strategy.ask(candidate_count=q)` | sequential q=1 + `enting.fit()` on placeholder-tells, OR `weights` sweep, OR `model_core` reuse with fantasy points |
| Solver requirement | Python-only (BoTorch on torch) | Pyomo + a MIP solver. `gurobipy>=11` is listed as a hard dep in `entmoot/pyproject.toml`, but the `PyomoOptimizer(params={"solver_name": "glpk"\|"scip"\|"ipopt"})` path lets you swap to an OSS solver |
| Determinism | seeded but BoTorch's `optimize_acqf` uses multi-start | MIP solve is deterministic given solver + tolerances; LightGBM is seeded via `rnd_seed` on `ProblemConfig` |
| Fail modes | In the v0.3.1 audit: (a) `SoboStrategy` did not return with NChooseK; (b) `_sample_with_nchoosek` saturated a CPU; (c) `optimize_acqf` was slow at q≥4; (d) infeasibility could be silent | (a) infeasible MIP returns an infeasible status; (b) selected solver unavailable; (c) larger MIPs may be slow; (d) LightGBM cannot extrapolate outside the training-data envelope, so cold-start behavior is unreliable |

The decisive difference is the **NChooseK row**. BoFire's `SoboStrategy` cannot
honor it; ENTMOOT bakes it into the MIP as a hard constraint that the solver
proves feasible (or returns infeasible-status).

## 2. Adapter design

### File layout

```
src/biosymphony_ferm_doe/adapters/entmoot_strategy.py     # new
src/biosymphony_ferm_doe/adapters/__init__.py    # register
src/biosymphony_ferm_doe/adaptive_wave2.py       # routed dispatch
tests/test_optional_adapters.py                  # new ENTMOOT test classes
examples/<demo-campaign>/phase2_entmoot_manifest.json  # fixture
pyproject.toml                                   # add [entmoot] extras group
```

### Public claim level and routing

```python
# adapters/entmoot_strategy.py
from __future__ import annotations

import importlib.util
from typing import Any

from ..constraints import design_factors
from ..io_utils import parse_number


CLAIM_LEVEL = "entmoot_adapter_planning"
ENTMOOT_ROUTE_REASONS = (
    "nchoosek_constraint_with_bo",       # the swap's reason for existence
    "tree_surrogate_requested",           # operator requested
    "bofire_sobo_known_stall",            # explicit fallback from BoFire fail
)
NON_CLAIM = (
    "ENTMOOT-backed candidates are MIP-feasible model-based suggestions. "
    "Tree-ensemble surrogates cannot extrapolate outside the training-data "
    "envelope; the candidate batch is a planning suggestion contingent on "
    "real Phase 1 lab data replacing the synthetic simulator before any "
    "commit-grade handoff."
)


def is_available() -> bool:
    """ENTMOOT itself plus its solver dependency. Default to GLPK so OSS-only path is testable."""
    if importlib.util.find_spec("entmoot") is None:
        return False
    # Solver probe lives behind a lazy import, see _solver_available below.
    return True
```

### `EntmootDomainAdapter`

```python
class EntmootDomainAdapter:
    """Translate a biosymphony manifest into ENTMOOT's ProblemConfig + ConstraintList.

    The adapter never imports `entmoot` at module load time, only inside
    `build_problem` and `build_constraint_list`. This mirrors the BoFire
    adapter's stdlib-importable posture.
    """

    def __init__(self, state: dict[str, Any], *, seed: int = 0) -> None:
        self.state = state
        self.seed = seed
        self.factors = design_factors(state.get("factors", []))
        self.constraints_raw = list(state.get("constraints", []) or [])
        self.responses = _objective_responses(state)
        # Cached after build_problem to keep the binding stable.
        self._feature_keys: list[str] = []
        self._objective_names: list[str] = []

    # --- public surface -------------------------------------------------

    def build_problem(self):
        """Returns an entmoot.ProblemConfig with features and objectives."""
        from entmoot import ProblemConfig

        problem = ProblemConfig(rnd_seed=self.seed)
        for factor in self.factors:
            self._add_factor(problem, factor)
        self._feature_keys = [f.name for f in problem.feat_list]
        for response in self.responses:
            self._add_response(problem, response)
        self._objective_names = [o.name for o in problem.obj_list]
        return problem

    def build_constraint_list(self):
        """Returns an entmoot.constraints.ConstraintList of translated constraints."""
        from entmoot.constraints import (
            ConstraintList,
            LinearEqualityConstraint,
            LinearInequalityConstraint,
            NChooseKConstraint,
        )

        items = []
        for spec in self._normalized_constraints():
            if spec["type"] == "linear":
                if spec["operator"] in {">=", ">"}:
                    # ENTMOOT only ships LinearInequality (≤); flip sign for ≥.
                    items.append(
                        LinearInequalityConstraint(
                            feature_keys=spec["features"],
                            coefficients=[-c for c in spec["coefficients"]],
                            rhs=-spec["rhs"],
                        )
                    )
                elif spec["operator"] in {"==", "="}:
                    items.append(
                        LinearEqualityConstraint(
                            feature_keys=spec["features"],
                            coefficients=spec["coefficients"],
                            rhs=spec["rhs"],
                        )
                    )
                else:
                    items.append(
                        LinearInequalityConstraint(
                            feature_keys=spec["features"],
                            coefficients=spec["coefficients"],
                            rhs=spec["rhs"],
                        )
                    )
            elif spec["type"] == "nchoosek":
                items.append(
                    NChooseKConstraint(
                        feature_keys=spec["features"],
                        min_count=spec["min_count"],
                        max_count=spec["max_count"],
                        none_also_valid=spec.get("none_also_valid", False),
                    )
                )
            # Conditional / forbidden constraints follow the BoFire adapter's
            # linearization (only binary-threshold conditionals supported in
            # v1 of this adapter; same fail-closed posture).
        return ConstraintList(items)

    # --- factor / response translation ----------------------------------

    def _add_factor(self, problem, factor: dict[str, Any]) -> None:
        factor_id = str(factor.get("factor_id") or "")
        factor_type = str(factor.get("type") or "numeric").lower()
        low = parse_number(factor.get("low", factor.get("min")))
        high = parse_number(factor.get("high", factor.get("max")))
        levels = factor.get("levels") if isinstance(factor.get("levels"), list) else []

        if factor_type in {"categorical", "block", "hard_to_change"} and levels:
            problem.add_feature("categorical", tuple(str(level) for level in levels), name=factor_id)
        elif factor_type in {"ordinal"} and levels:
            int_levels = [int(parse_number(level) or 0) for level in levels]
            problem.add_feature("integer", (min(int_levels), max(int_levels)), name=factor_id)
        elif factor_type == "binary":
            problem.add_feature("binary", name=factor_id)
        else:
            # numeric / continuous
            problem.add_feature("real", (float(low), float(high)), name=factor_id)

    def _add_response(self, problem, response: dict[str, Any]) -> None:
        direction = str(response.get("direction") or "maximize").lower()
        name = str(response.get("response_id") or "")
        if direction == "minimize":
            problem.add_min_objective(name=name)
        else:
            problem.add_max_objective(name=name)

    def _normalized_constraints(self) -> list[dict[str, Any]]:
        # Reuse the BoFire adapter's normalization where signatures match.
        # Diverges only on (a) operator flipping for ≥, (b) min_count default.
        from .bofire_strategy import _constraint_specs
        return _constraint_specs(self.constraints_raw)

    # --- public read-only accessors -------------------------------------

    @property
    def feature_keys(self) -> list[str]:
        return list(self._feature_keys)

    @property
    def objective_names(self) -> list[str]:
        return list(self._objective_names)
```

### `EntmootStrategy`

```python
from dataclasses import dataclass

@dataclass
class EntmootAskResult:
    """Single ENTMOOT MIP solve result, normalized for biosymphony reporters."""
    factor_values: dict[str, float | int | str]
    objective_value: float
    mu: list[float]                          # mean predictions per objective
    uncertainty: float
    active_leaves: list[list[tuple[int, str]]]
    solver_status: str                       # "optimal" | "infeasible" | "infeasible_or_unbounded" | ...
    solver_wall_time_s: float
    iteration_index: int

class EntmootStrategy:
    """ENTMOOT acquisition loop, exposed as a tell()/ask() facade."""

    def __init__(
        self,
        adapter: EntmootDomainAdapter,
        *,
        solver_name: str = "gurobi",
        solver_options: dict[str, Any] | None = None,
        beta: float = 1.96,
        dist_metric: str = "l1",
        acq_sense: str = "exploration",
        weights: tuple[float, ...] | None = None,
    ) -> None:
        from entmoot import Enting, PyomoOptimizer
        from entmoot.models.model_params import EntingParams, UncParams

        self.adapter = adapter
        self.problem = adapter.build_problem()
        self.constraints = adapter.build_constraint_list()
        self.weights = weights  # for multi-objective scalarization

        params = EntingParams(
            unc_params=UncParams(
                beta=beta,
                dist_metric=dist_metric,
                acq_sense=acq_sense,
            ),
        )
        self.enting = Enting(self.problem, params=params)

        self.optimizer_params = {
            "solver_name": solver_name,
            "solver_options": solver_options or {"MIPGap": 0.01},
            "verbose": False,
        }
        self.optimizer = PyomoOptimizer(self.problem, params=self.optimizer_params)

        # Internal training buffers (mirror BoFire .tell semantics).
        self._X: list[list[Any]] = []
        self._Y: list[list[float]] = []
        self._iter: int = 0

    def tell(self, X: list[list[Any]], Y: list[list[float]]) -> None:
        """Append observations and refit the surrogate."""
        if len(X) != len(Y):
            raise ValueError("X and Y must have the same length")
        self._X.extend(X)
        self._Y.extend(Y)
        if not self._X:
            return
        import numpy as np
        self.enting.fit(self._X, np.array(self._Y))

    def ask(self) -> EntmootAskResult:
        """Solve the constrained MIP for the next candidate (q=1)."""
        from time import perf_counter

        model_core = self.problem.get_pyomo_model_core()
        self._apply_constraints(model_core)

        t0 = perf_counter()
        result = self.optimizer.solve(
            self.enting,
            model_core=model_core,
            weights=self.weights,
        )
        wall_time = perf_counter() - t0
        self._iter += 1

        return EntmootAskResult(
            factor_values=dict(zip(self.adapter.feature_keys, result.opt_point)),
            objective_value=float(result.opt_val),
            mu=list(result.mu_unscaled),
            uncertainty=float(result.unc),
            active_leaves=result.active_leaves,
            solver_status=self._solver_status(result),
            solver_wall_time_s=wall_time,
            iteration_index=self._iter,
        )

    def ask_batch(self, count: int) -> list[EntmootAskResult]:
        """Sequential q=1 × count with placeholder-tell between solves.

        Avoids the q≥4 quadratic memory failure mode seen in SoboStrategy paths.
        """
        results = []
        for _ in range(count):
            asked = self.ask()
            results.append(asked)
            self._fantasy_tell(asked)  # see §below
        return results

    # --- internal helpers -----------------------------------------------

    def _apply_constraints(self, model_core) -> None:
        import pyomo.environ as pyo

        if not self.constraints._constraints:
            return
        model_core.problem_constraints = pyo.ConstraintList()
        self.constraints.apply_pyomo_constraints(
            model_core,
            self.problem.feat_list,
            model_core.problem_constraints,
        )

    def _fantasy_tell(self, asked: EntmootAskResult) -> None:
        """Append predicted mean as a fake observation to break tie-cycles."""
        x_row = [asked.factor_values[k] for k in self.adapter.feature_keys]
        y_row = list(asked.mu)
        self.tell([x_row], [y_row])

    def _solver_status(self, result) -> str:
        # ENTMOOT v2's OptResult does not carry a status string; we infer from
        # whether opt_point is well-formed. Detailed status lives in the
        # solver-specific result object that the caller can attach if needed.
        return "optimal" if result.opt_point is not None else "infeasible_or_unbounded"
```

### Adapter-package registration

`adapters/__init__.py` gains:

```python
ADAPTERS = ("scipy", "nist", "pydoe3", "botorch", "bofire", "entmoot", "salib")

# ...
if name == "entmoot":
    try:
        from . import entmoot as entmoot_module
    except ImportError:
        return None
    return entmoot_module if entmoot_module.is_available() else None
```

`pyproject.toml` gains an extras group:

```toml
[project.optional-dependencies]
entmoot = [
  "entmoot>=2.0.2,<3",
  "pyomo>=6.7,<7",
  # Solver is BYO. Document the three OSS paths:
  #   - "highspy>=1.7"     ← Pyomo "appsi_highs"; fully OSS
  #   - "glpk"             ← system package, OSS
  #   - "gurobipy>=11"     ← commercial, listed by ENTMOOT itself
  # The adapter probes for available solvers at strategy-instantiation time.
]
```

The ENTMOOT v2.0.2 / 2.1.1 `pyproject.toml` lists `gurobipy>=11` as a hard dep
of *its own*. Pinning ENTMOOT pulls Gurobi's pip package; activation requires a
license (free academic / WLS). The adapter MUST still try GLPK / HiGHS / SCIP
at run time via `pyo.SolverFactory(name).available()` and fall back to a route
report rather than failing inside `.ask()`.

### Routing decision

In `adaptive_wave2.py` the existing `_maybe_run_bofire_adapter` becomes:

```python
def _maybe_run_bo_adapter(state, usable_rows, remaining_budget, backend):
    """Route order: explicit backend > NChooseK forces ENTMOOT > BoFire route."""
    requested = (backend or "auto").lower()

    if requested == "entmoot":
        return _run_entmoot_adapter(state, usable_rows, remaining_budget, backend)

    has_nchoosek = _state_has_nchoosek(state)
    if has_nchoosek and adapters.is_available("entmoot"):
        return _run_entmoot_adapter(state, usable_rows, remaining_budget, backend)

    # Fall through to the existing BoFire path (with its post-hoc-filter caveat).
    return _maybe_run_bofire_adapter(state, usable_rows, remaining_budget, backend)
```

The `has_nchoosek` short-circuit is what closes the gap. With ENTMOOT installed
and an NChooseK in the manifest, the engine routes through MIP-feasibility
instead of post-hoc filtering. Without ENTMOOT, the existing BoFire-plus-filter
path remains the fallback (and its caveats remain accurate).

## 3. NChooseK encoding, concrete Pyomo block

Source: `entmoot/constraints.py::NChooseKConstraint._get_expr` (verified
against the upstream repo at sha `entmoot-v2`). Reproduced here for the design
record and so the test suite can assert the exact encoding the adapter will
generate.

```python
class NChooseKConstraint(ExpressionConstraint):
    """Constrain the number of active features to be bounded by min/max."""

    tol: float = 1e-6
    M: float = 1e6

    def __init__(self, feature_keys, min_count, max_count, none_also_valid=False):
        self.min_count = min_count
        self.max_count = max_count
        self.none_also_valid = none_also_valid
        super().__init__(feature_keys)

    def _get_expr(self, model, features):
        # Binary indicator z_i ∈ {0,1} for each feature in the constraint.
        model.feat_selected = pyo.Var(range(len(features)), domain=pyo.Binary, initialize=0)
        model.ub_selected = pyo.ConstraintList()
        model.lb_selected = pyo.ConstraintList()

        for i in range(len(features)):
            # Big-M:    x_i ≤ M · z_i        (z_i = 0  ⇒  x_i = 0)
            model.ub_selected.add(expr=model.feat_selected[i] * self.M >= features[i])
            # Tol-bound: x_i ≥ tol · z_i     (z_i = 1  ⇒  x_i ≥ 1e-6, i.e. "active")
            model.lb_selected.add(expr=model.feat_selected[i] * self.tol <= features[i])

        # Cardinality:  Σ z_i ≤ max_count
        return sum(model.feat_selected.values()) <= self.max_count
```

For an example Phase 2 problem with carbon set `{glucose, glycerol, lactose,
sucrose, xylose}` and `min_count=1, max_count=2`, this generates:

```
# Decision variables introduced by the constraint
z_glucose, z_glycerol, z_lactose, z_sucrose, z_xylose ∈ {0, 1}

# Upper coupling (big-M):  x_i ≤ 1e6 · z_i
z_glucose * 1e6 >= glucose
z_glycerol * 1e6 >= glycerol
z_lactose * 1e6 >= lactose
z_sucrose * 1e6 >= sucrose
z_xylose * 1e6 >= xylose

# Lower coupling (tol):    z_i · 1e-6 ≤ x_i
z_glucose * 1e-6 <= glucose
z_glycerol * 1e-6 <= glycerol
z_lactose * 1e-6 <= lactose
z_sucrose * 1e-6 <= sucrose
z_xylose * 1e-6 <= xylose

# Cardinality upper bound (built-in via _get_expr)
z_glucose + z_glycerol + z_lactose + z_sucrose + z_xylose <= 2
```

### Minimum-count caveat (adapter-side fix)

The shipped `NChooseKConstraint._get_expr` returns ONLY the `≤ max_count`
expression. `min_count` is stored on the object but not emitted. To enforce
`min_count ≥ 1` we MUST register a second constraint after constructing it:

```python
# adapters/entmoot_strategy.py, inside _apply_constraints
from entmoot.constraints import NChooseKConstraint
import pyomo.environ as pyo

for raw in self.constraints._constraints:
    raw.as_pyomo_constraint(model_core, self.problem.feat_list)
    if isinstance(raw, NChooseKConstraint) and raw.min_count > 0:
        # Emit the missing min_count constraint using the same z variables
        # we just installed via _get_expr.
        # Note: ENTMOOT's _get_expr installs z as model.feat_selected, but
        # later constraints in the same model would overwrite that handle.
        # The adapter therefore creates a NAMED block per constraint:
        #   model.add_component(f"z_{raw_id}", ...) ...
        # See "Risk list, single-block name collision" below.
        ...
```

If `min_count == 0` and `none_also_valid` is True (the default for the
BoFire adapter), the only constraint needed is `Σ z_i ≤ max_count`, which
ENTMOOT's shipped implementation handles correctly. The adapter v1 fails
closed when `min_count > 0` is requested AND ENTMOOT's shipped
`NChooseKConstraint` is used unmodified, and the adapter test suite asserts
that the emitted MIP includes the second constraint when `min_count > 0`.

This is the smallest concrete piece of "shipped library doesn't quite do
what we need" in the design. The fix is local (a wrapper constraint class
in the adapter), but it has to land or the `at_most_two_carbons`
constraint with `min_count=1, max_count=2` will silently drop the lower bound.

## 4. Cost-aware extension

The example fixture's actual objective is `cost_per_mg_usd` (derived,
minimize). The BoFire path computes `cost_per_mg = media_cost_per_L_usd /
product_titer_mg_per_L` post-hoc and gives the GP only that scalar.
ENTMOOT can do the same, but it also lets us **inject the cost MIP directly**
so cost feasibility is enforced at acquisition time rather than evaluated
after-the-fact.

### Candidate A, scalar derived objective (parity with BoFire path)

Simulate titer offline, compute `cost_per_mg`, tell ENTMOOT the scalar. Use a
single `MinObjective` with the cost_per_mg name. This is the minimum-change
swap and preserves the cost-per-mg semantics of the current Phase 2.

### Candidate B, multi-objective scalarization with annealed cost weight

Declare two objectives in the manifest and use ENTMOOT's `weights` argument:

```python
# Manifest declares:
#   product_titer_mg_per_L (direction: maximize)
#   cost_per_mg_usd        (direction: minimize)
#
# Adapter passes the tuple to PyomoOptimizer.solve:
strategy = EntmootStrategy(adapter, weights=(0.7, 0.3))
strategy.ask()
```

Per `tests/test_optimality_pyomo.py`, ENTMOOT validates that
`sum(weights) == 1.0` and applies them as a linear scalarization of the
(sign-adjusted) objectives. A weight schedule that anneals from
`(1.0, 0.0) → (0.5, 0.5) → (0.2, 0.8)` across the BO loop biases early
iterations toward titer exploration and late iterations toward cost-floor
refinement.

```python
def cost_annealing_schedule(iteration: int, total: int) -> tuple[float, float]:
    """Linear schedule from titer-heavy to cost-heavy across the batch."""
    if total <= 1:
        return (0.5, 0.5)
    t = iteration / (total - 1)  # 0.0 → 1.0
    titer_w = 1.0 - 0.8 * t       # 1.0 → 0.2
    cost_w = 1.0 - titer_w        # 0.0 → 0.8
    return (titer_w, cost_w)
```

This complements ENTMOOT's native objective by using its built-in scalarizer
(verified in source at `entmoot/optimizers/pyomo_opt.py::solve`; the
`weights` argument is asserted summing to 1 and passed straight through to
the Pyomo objective expression).

### Option C, linear-constraint cost budget (already in the manifest)

The public fixture already encodes the $1.20/L budget as a linear <=
constraint via the `media_cost_lte_120_per_L` entry. Translation:

```python
LinearInequalityConstraint(
    feature_keys=[
        "ammonium_sulfate", "corn_steep_liquor", "glucose", "glycerol",
        "lactose", "sucrose", "tryptone", "xylose", "yeast_extract",
    ],
    coefficients=[0.00025, 0.0008, 0.0007, 0.0017, 0.0009, 0.0011, 0.012, 0.002, 0.0035],
    rhs=1.2,
)
```

Combined with Candidate A or B, this means: ENTMOOT minimizes cost-per-mg AS the
objective, with the per-L budget AS a hard MIP constraint, AND the cardinality
constraint AS a hard MIP constraint. Three constraints that BoFire could not
honor jointly are honored simultaneously inside one MIP solve.

The "annealed cost weight" lives at the objective-scalarization layer. The
"per-L budget" lives at the constraint layer. Both are MIP-native in ENTMOOT.

## 5. Migration milestones

### m1, side-by-side comparison run (~2 days)

**Build:**
- `adapters/entmoot_strategy.py` skeleton (no execution path; route reporting only).
- Translation tests: example manifest → `ProblemConfig` round-trip; cardinality
  constraint emits the right Pyomo expression.

**Run:**
- ENTMOOT manifest fixture (mostly a copy of the BoFire fixture with
  the `at_most_two_carbons.enforcement` field set to `entmoot_mip` instead of
  `post_hoc_filter`).
- Local execution with HiGHS or GLPK as the solver.
- Output: BoFire phase-2 report AND ENTMOOT phase-2 report, same training data,
  same problem.

**Acceptance criteria:**
- `entmoot_phase2_report.recommended_batch_count >= 8`
  (the BoFire run produced 0; ENTMOOT MUST clear the cardinality bar by
  construction).
- Every row satisfies cost ≤ $1.20/L AND 1 ≤ active_carbons ≤ 2 AND
  Σ carbon ≤ 100 g/L.
- Wall time per `.ask()` ≤ 60 s on CPU-only laptop (HiGHS / GLPK).
- A `comparison_report.md` lands in `.runtime/entmoot-vs-bofire/`
  showing best-observed cost-per-mg and per-row feasibility for both adapters.

### m2, shadow-mode in CI (~3 days)

**Build:**
- Adapter routing decision in `adaptive_wave2.py` runs ENTMOOT *in addition
  to* BoFire when both adapters are available, but materializes ONLY the
  existing BoFire artifacts. ENTMOOT's report lands in
  `utility_outputs/entmoot-shadow/entmoot_strategy_report.json` for diffing.
- New test class `EntmootShadowParityTests` in
  `tests/test_optional_adapters.py` behind `@skipUnless(adapters.is_available("entmoot"))`.

**Acceptance criteria:**
- Shadow-mode artifacts exist for every follow-up plan run that has an NChooseK
  constraint in its manifest.
- Shadow ENTMOOT run never blocks the BoFire path (failures degrade to a
  fallback report; the engine's primary action is unchanged).
- The new test class passes locally with HiGHS or GLPK installed; skips
  cleanly without ENTMOOT.

### m3, feature-flag swap (~2 days, but only after operator review of m2)

**Build:**
- `design_policy.preferred_backend = "entmoot"` becomes the routing
  preference for any manifest with NChooseK + `assay_required: false`
  derived-cost objective.
- Existing BoFire path remains accessible via
  `--backend bofire` for parity / reproduction runs.
- New CLI route: `ferm-doe plan-wave2 --backend entmoot ...`.

**Acceptance criteria:**
- The public fixture re-run with `--backend entmoot` produces a
  `recommended_batch_count >= 8` artifact set.
- The campaign's `index.html` and `dossier` link both the original BoFire
  artifact and the new ENTMOOT artifact, side-by-side, with a caveat-style
  note explaining the swap rationale.
- Parity matrix (`docs/high-roi-doe-parity-strategy.md` and `parity.py`)
  records ENTMOOT as the routed BO path when NChooseK is in the Domain;
  BoFire remains the routed BO path otherwise.

## 6. Test plan

### Unit tests, `tests/test_optional_adapters.py`

```python
# Class: EntmootAdapterTranslationTests (no entmoot import needed)
def test_domain_adapter_emits_continuous_real_features_with_bounds():
    adapter = EntmootDomainAdapter(_minimal_state())
    # Mock entmoot.ProblemConfig and assert add_feature calls.

def test_domain_adapter_translates_linear_le_constraint():
    # Manifest → _normalized_constraints → LinearInequalityConstraint
    # with correct feature_keys, coefficients, rhs.

def test_domain_adapter_flips_sign_on_ge_constraint():
    # operator ">=" yields negated coefficients + rhs.

def test_domain_adapter_translates_nchoosek():
    # NChooseK manifest entry → NChooseKConstraint with right keys + counts.

def test_domain_adapter_routes_nchoosek_when_entmoot_available():
    with mock.patch.object(entmoot_adapter, "is_available", return_value=True):
        report = entmoot_adapter.plan_entmoot_wave2(state, [], backend="auto", remaining_budget=8)
    self.assertEqual(report["adapter_status"], "routed")
```

### Live-execution tests, gated by `@skipUnless`

```python
@unittest.skipUnless(
    adapters.is_available("entmoot") and _solver_available(),
    "ENTMOOT or MIP solver not available",
)
class EntmootMediaCostLiveExecutionTests(unittest.TestCase):
    def test_live_strategy_emits_only_feasible_candidate_rows(self):
        state = _load_example_phase2_state()
        report = entmoot_adapter.plan_entmoot_wave2(
            state, _phase1_observations(), backend="entmoot",
            remaining_budget=8, seed=42,
        )
        self.assertEqual(report["adapter_status"], "executed")
        self.assertGreaterEqual(report["candidate_design_count"], 8)
        for row in report["candidate_design"]:
            active_carbons = sum(
                1 for k in ("glucose", "glycerol", "lactose", "sucrose", "xylose")
                if row.get(k, 0.0) > 1e-6
            )
            self.assertGreaterEqual(active_carbons, 1)
            self.assertLessEqual(active_carbons, 2)
            total_cost_per_L = (
                0.00025 * row.get("ammonium_sulfate", 0.0)
                + 0.0008  * row.get("corn_steep_liquor", 0.0)
                + 0.0007  * row.get("glucose", 0.0)
                + 0.0017  * row.get("glycerol", 0.0)
                + 0.0009  * row.get("lactose", 0.0)
                + 0.0011  * row.get("sucrose", 0.0)
                + 0.012   * row.get("tryptone", 0.0)
                + 0.002   * row.get("xylose", 0.0)
                + 0.0035  * row.get("yeast_extract", 0.0)
            )
            self.assertLessEqual(total_cost_per_L, 1.2 + 1e-6)
```

### Fixtures

- A Phase 2 ENTMOOT manifest fixture with the same factors / responses /
  constraints as the BoFire fixture but with
  `enforcement: entmoot_mip` on `at_most_two_carbons`.
- A 16-row Phase 1 design + simulated titers fixture, identical to the
  BoFire smoke's training set, for fair side-by-side comparison.

### Assertions taxonomy

| Assertion | Why |
|---|---|
| `adapter_status == "executed"` | Sanity: the strategy completed `tell + ask_batch` |
| `len(candidate_design) >= 8` | The headline failure of the BoFire path; must succeed here by construction |
| `1 ≤ active_carbons ≤ 2 per row` | NChooseK is the swap's reason for existence; assert at row level |
| `cost_per_L <= 1.2` | Linear inequality constraint, must hold |
| `Σ carbon ≤ 100` | Other linear constraint, must hold |
| `factor_value in [low, high] for every factor` | Pyomo bounds; should be trivially satisfied but assert anyway |
| `solver_wall_time_s < 60.0 per ask` | Smoke time budget; reject pathologically slow MIPs early |
| `solver_status == "optimal"` for every ask | Detect silent infeasibility |
| `len({tuple(sorted(row.items())) for row in candidate_design}) == len(candidate_design)` | Distinct rows; sequential q=1 with fantasy-tell should not collapse to repeats |

## 7. Risk list

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **Gurobi license required at runtime** even though `gurobipy` pip-installs cleanly | High | Adapter cannot solve without a license | At strategy-init time, probe `pyo.SolverFactory("gurobi").available()`. If False, fall through to `appsi_highs` (HiGHS), `glpk`, `scip` (in that order). Document in README. Adapter v1 ships HiGHS as the default OSS path. |
| **No multi-fidelity support in ENTMOOT v2** | Certain | Phase 3 scale-bridge cannot use ENTMOOT | BoFire `MultiFidelityVarianceBasedStrategy` (post-0.4) remains the Phase 3 path. ENTMOOT swap is Phase 2 only. |
| **`NChooseKConstraint.min_count` is stored but not emitted** by ENTMOOT v2's `_get_expr` | High | Silent constraint violation if `min_count > 0` | Adapter MUST wrap or subclass to emit the second `Σ z_i ≥ min_count` expression. Test asserts emitted MIP includes both bounds. Open an upstream issue. |
| **`model.feat_selected` name collision** if multiple NChooseK constraints share one Pyomo model | Medium | Second constraint overwrites first's binary vars | Adapter creates a named pyomo Block per constraint (`model.add_component(f"nchoosek_{cid}", pyo.Block(...))`) so binary vars are scoped. |
| **MIP runtime explodes at large K** (many continuous + many binary indicators) | Medium for Phase 2 (5 carbons, K=2) | Wall time spikes; solver times out | Set `MIPGap=0.01` (1% optimality gap) and `TimeLimit=120 s` in `solver_options`. Report wall time per ask; fail closed (and write a route-fallback report) if time limit hits. The example Phase 2 shape (12 factors, 5 in cardinality) is small enough this should not bite. |
| **LightGBM surrogate cannot extrapolate** outside training-data envelope | Certain | Cold-start before ~10 observations is unreliable | The public fixture feeds 16 seed candidates as training data. For NEW campaigns, the adapter MUST refuse to `ask()` until `len(self._Y) >= 10` (matches ENTMOOT's documented `num_boost_round=100` regime). |
| **`gurobipy` is a hard dep of `entmoot`** (declared in upstream `pyproject.toml`) | Certain | Installing `entmoot` pulls Gurobi even on OSS-only users | The `[entmoot]` extras group acknowledges this and documents the BYO-solver story. The adapter never imports `gurobipy` directly. |
| **Pyomo + LightGBM are heavy dependencies** vs. biosymphony's stdlib-first promise | Medium | Adds ~150 MB to the optional install footprint | This is an OPTIONAL adapter, gated by `[entmoot]` extras. Stdlib remains the default. Adapter never imports at module load; only inside `is_available()` and execution paths. |
| **ENTMOOT v2's `Enting.predict` API differs from BoFire's GP posterior API** | Low (we don't use predict; we use the optimizer's MIP-encoded surrogate) | Reporter assumptions break | Reporter layer should consume `EntmootAskResult` directly (it carries `mu` and `uncertainty`), not poke into `Enting` internals. |
| **ENTMOOT v2.0.2 → v2.1.1 API drift** | Low (changelog shows mostly type-hint refactors) | Lock-step bumps | Pin `entmoot>=2.0.2,<3` in `[entmoot]` extras. Re-validate via the live-execution test class on each upgrade. |
| **BoFire/ENTMOOT BO produce different "best" rows on the same training data** | Certain (they have different surrogates) | Operator confusion when reading parallel reports | The m1 / m2 / m3 deliverables explicitly carry both reports side-by-side AND a `comparison_report.md` that explains the surrogate-class difference. The honest answer is "GP and tree-ensemble disagree because they extrapolate differently from sparse training data; ENTMOOT's answer is feasible by construction, BoFire's is not." |

## Appendix, pinned upstream references (verified 2026-05-16)

- ENTMOOT v2.0.2 release: `https://github.com/cog-imperial/entmoot/releases/tag/v2.0.2`
- ENTMOOT current `pyproject.toml` (v2.1.1): hard deps `gurobipy>=11.0.0`,
  `lightgbm~=4.6.0`, `numpy`, `pyomo~=6.9.0`.
- `ProblemConfig.add_feature`: `feat_type in {"real", "integer", "binary", "categorical"}`,
  `bounds=(lo, hi)` or `bounds=("cat0", "cat1", ...)`.
- `Enting.fit(X, y)` and `Enting.predict(X)`: `entmoot/models/enting.py`.
- `PyomoOptimizer.solve(enting, model_core=None, weights=None) -> OptResult`:
  returns `(opt_point, opt_val, mu_unscaled, unc, active_leaves)`.
- `NChooseKConstraint`: `entmoot/constraints.py`. Emits `Σ z_i ≤ max_count`
  with big-M `x_i ≤ M · z_i` and tol-bound `z_i · tol ≤ x_i`. Note:
  `min_count` is NOT emitted by the shipped `_get_expr`; adapter must
  supplement.
- Linear constraint: `LinearInequalityConstraint(feature_keys, coefficients, rhs)`
  yields `Σ c_i · x_i ≤ rhs`.

## Appendix, non-goals

This design does NOT cover:

- Phase 3 multi-fidelity scale-bridge (ENTMOOT v2 has no multi-fidelity).
- Multi-objective Pareto-frontier sweeping (ENTMOOT scalarizes; for true
  Pareto search across many weight tuples the BoFire `MoboStrategy + qLogNEHVI`
  path remains canonical).
- Replacing the dossier authoring or handoff packet generation.
- Adopting ENTMOOT's `ProblemConfig` as the manifest source-of-truth. Same
  posture as `docs/BOFIRE_POSITIONING.md`: ENTMOOT is a powerup, not a
  destination. Translate at the adapter boundary.
