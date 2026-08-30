# BoFire Constraint × Strategy Compatibility Patterns

Status: historical compatibility snapshot from 2026-05-16, with a current
upstream note added 2026-08-30. The matrix records `bofire 0.3.1` and the
May 2026 `main` branch after PRs #705, #749, #752, and #757. It does not
describe current-release behavior.

BoFire 0.4 added generalized NChooseK DoE support and 0.5.0 is the current
upstream release. Issues #450 and #761 are closed. Neither closure proves
that the exact adapter cases below are fixed, because later tags have not
been evaluated in this repository. The primary adapter therefore remains on
`bofire>=0.3.1,<0.4` with its documented fallbacks.

This document is the authoritative cheat sheet for which BoFire constraints can be
combined with which BoFire strategies in a biosymphony-ferm-doe manifest
without stalling, raising `ConstraintNotFulfilledError`, or silently emitting
infeasible candidates. It supplements `BOFIRE_POSITIONING.md` with the
per-constraint detail needed to author manifests that survive contact with
the adapter.

## 0. NChooseK DoE version rule

For a separate evaluation of tagged NChooseK DoE support, use the
`adaptive-nchoosek-doe` extra. It pins BoFire 0.4.1 and requires Python 3.11
or newer:

```bash
pip install "biosymphony-ferm-doe[adaptive-nchoosek-doe]"
```

This is an unverified evaluation lane, not an expansion of the primary
adapter's compatibility claim. The pinned `bofire>=0.3.1,<0.4` extra predates
the native NChooseK DoE path.
Depending on the exact install, a DoE screen with a `min_count` floor may drop
or reject that floor before candidate generation. Treat pinned-0.3.1
NChooseK DoE output as fail-closed unless every emitted row is rechecked
against the manifest cardinality contract.

Two adapter details matter for this manifest shape:

- BoFire expects `allow_zero=True` continuous inputs to have a positive lower
  numeric bound, with zero modeled as the special allowed value. The adapter
  shifts zero-starting intervals by a tiny epsilon before building BoFire
  `ContinuousInput` objects.
- Multi-response manifests route to multi-objective BO by default. If the
  immediate goal is a first-batch D-optimal screen, call the DoE route
  explicitly rather than relying on a BO routing decision.

The matrix is grounded in:

- BoFire `main` constraint catalog,
  `bofire/data_models/constraints/api.py`
- BoFire `main` strategy catalog,
  `bofire/strategies/api.py`
- Verified bug reports, GitHub issues
  [#450](https://github.com/experimental-design/bofire/issues/450) (NChooseK
  + acquisition stall) and
  [#761](https://github.com/experimental-design/bofire/issues/761) (multi-fidelity
  + non-box constraints)
- Smoke-check notes from biosymphony-ferm-doe Phase 1, Phase 2, Phase 3
  example campaign runs (2026-05-15)

## 1. Constraint type catalog

Every constraint class BoFire's `main` branch re-exports as of 2026-05-16,
with one-line semantic and minimal example. Constructors are the ones that
worked in the inspected `bofire>=0.3.1,<0.4` and `main` releases.

| Class | Semantic | Minimal example |
|---|---|---|
| `LinearEqualityConstraint` | `sum(c_i * x_i) == rhs` over continuous features | `LinearEqualityConstraint(features=["a","b","c"], coefficients=[1,1,1], rhs=1.0)` (mixture) |
| `LinearInequalityConstraint` | `sum(c_i * x_i) <= rhs` (use `from_greater_equal` for `>=`) | `LinearInequalityConstraint.from_smaller_equal(["glucose","glycerol"], [1,1], 100.0)` |
| `NonlinearEqualityConstraint` | Symbolic / callable `f(x) == 0`; auto-jacobian/hessian if expression is a string | `NonlinearEqualityConstraint(features=["x","y"], expression="x**2 + y**2 - 1")` |
| `NonlinearInequalityConstraint` | Symbolic / callable `f(x) <= 0` | `NonlinearInequalityConstraint(features=["x","y"], expression="x*y - 4")` |
| `NChooseKConstraint` | At least `min_count` and at most `max_count` of `features` are non-zero | `NChooseKConstraint(features=["c1","c2","c3","c4","c5"], min_count=1, max_count=2, none_also_valid=False)` |
| `ProductEqualityConstraint` | `sign * prod(x_i^e_i) == rhs` (multiplicative balance) | `ProductEqualityConstraint(features=["x","y"], exponents=[1, -1], rhs=2.0)` (x/y == 2) |
| `ProductInequalityConstraint` | `sign * prod(x_i^e_i) <= rhs` | `ProductInequalityConstraint(features=["agitation","kla"], exponents=[1,1], rhs=500)` |
| `InterpointEqualityConstraint` | Across a batch, every candidate must share the same value for one feature (or in groups of `multiplicity`) | `InterpointEqualityConstraint(features=["block"], multiplicity=4)` (4 candidates share the same block id) |
| `CategoricalExcludeConstraint` | Logical AND/OR/XOR over `ThresholdCondition` + `SelectionCondition` evaluated on categorical or numeric features; excludes the combination when the logic is true | `CategoricalExcludeConstraint(features=["strain","inducer"], conditions=[SelectionCondition(feature="strain", selection=["S1"]), SelectionCondition(feature="inducer", selection=["I3"])], logical_op="AND")` |

Conditions used inside `CategoricalExcludeConstraint`:

- `ThresholdCondition(feature, threshold, operator)`, fires on `<=` or `>=`
  against a numeric feature
- `SelectionCondition(feature, selection)`, fires when the categorical
  value is in the selection list
- `NonZeroCondition(feature)`, fires when a continuous feature is > 0

Type hierarchy is `Constraint` → `IntrapointConstraint` |
`InterpointConstraint`. Almost everything in the catalog is intrapoint
(applies to a single candidate). `InterpointEqualityConstraint` is the only
production-grade interpoint constraint shipped today.

## 2. Strategy × constraint compatibility matrix

Strategy columns (BoFire `main`, exported from `bofire.strategies.api`):

- **DoE** = `DoEStrategy` (IPOPT/cyipopt augmented D-optimal)
- **Random** = `RandomStrategy` (polytope / rejection sampler)
- **Sobo** = `SoboStrategy` / `AdditiveSoboStrategy` / `CustomSoboStrategy` /
  `MultiplicativeSoboStrategy` / `MultiplicativeAdditiveSoboStrategy`
  (single-output BO with botorch acquisition optimization)
- **Mobo** = `MoboStrategy` / `QparegoStrategy` (multi-output Pareto BO)
- **MF-Var** = `MultiFidelityVarianceBasedStrategy` (variance-based
  multi-fidelity; main-branch since PR #705)
- **MF-HVKG** = `MultiFidelityHVKGStrategy` (hypervolume KG multi-fidelity;
  main-branch since PR #705)
- **AL** = `ActiveLearningStrategy`
- **Stepwise** = `StepwiseStrategy` (orchestrates substrategies per stage)
- **Enting** = `EntingStrategy` (ENTMOOT tree-based opt)
- **LLM** = `LLMStrategy` (PR #749; literature-warmstart; research-grade)
- **FF** = `FractionalFactorialStrategy`
- **SP** = `ShortestPathStrategy`

Cell legend:

- OK: works
- box-only: works only without non-box constraints
- caveat: works but with a tested workaround
- stall: hangs >5 min on CPU; treat as broken
- error: raises `ConstraintNotFulfilledError` /
  `NotImplementedError` / validator rejection
- N/A: strategy ignores constraints by design (e.g., `ShortestPathStrategy`
  pathing between fixed candidates)

| Constraint \ Strategy | DoE | Random | Sobo | Mobo | MF-Var | MF-HVKG | AL | Stepwise | Enting | LLM | FF | SP |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LinearEquality | OK | OK | OK | OK | error #761 | error #761 | OK | OK (per substrategy) | OK | caveat | error | N/A |
| LinearInequality | OK | OK | OK | OK | error #761 | error #761 | OK | OK | OK | caveat | error | N/A |
| NonlinearEquality | caveat (warn) | rejection-sample | caveat | caveat | error | error | caveat | caveat | error | caveat | error | N/A |
| NonlinearInequality | caveat (warn) | rejection-sample | caveat | caveat | error | error | caveat | caveat | error | caveat | error | N/A |
| NChooseK | OK (PR #752 native) | OK (PR #757 scaled) | stall #450 | stall #450 | error #761 | error #761 | stall #450 | depends on substrategy | OK (PR #644 GA) | stall #450 | box-only | N/A |
| ProductEquality | caveat (nonlinear path) | rejection-sample | caveat | caveat | error | error | caveat | caveat | error | caveat | error | N/A |
| ProductInequality | caveat (nonlinear path) | rejection-sample | caveat | caveat | error | error | caveat | caveat | error | caveat | error | N/A |
| InterpointEquality | error (intrapoint solver) | OK | error | error | error | error | error | depends | error | caveat | error | N/A |
| CategoricalExclude | error (continuous solver) | OK | caveat (categorical input handling) | caveat | error | error | caveat | depends | OK (PR #644) | caveat | error | N/A |

How to read the caveats:

- **DoE + nonlinear / product**: DoEStrategy emits a runtime warning
  `"Nonlinear constraints were detected. Not all features and checks are
  supported for this type of constraints"`. The IPOPT path accepts the
  constraint via the symbolic jacobian/hessian (auto-derived from the
  expression string), but D-efficiency reporting may be incomplete. Treat
  the design as feasible-but-not-fully-audited; verify each row against
  the constraint post-hoc.
- **Sobo / Mobo + nonlinear / product**: botorch's `optimize_acqf` accepts
  nonlinear constraints only when provided as `nonlinear_inequality_constraints`
  callables; BoFire wraps the expression but is sensitive to the differentiability
  of the callable. Test on a smoke before scaling.
- **Random + nonlinear / product**: BoFire falls back to rejection sampling.
  Feasible-region volume below ~5% of the box makes the smoke time out;
  document the rejection rate in your report.
- **Stepwise**: each substrategy applies its own compatibility; pick the
  substrategies according to the rows above.
- **LLM**: the strategy proposes candidates as natural language, then
  `validate_candidates` rejects infeasibility. Caveat across the board
  because the cost of rejection is one LLM call per cycle and the API key
  has to be configured; not load-bearing for anything biosymphony-ferm-doe
  ships in this milestone.

## 3. Compatibility findings from the May 2026 audit

### Finding A: NChooseK with acquisition-optimizing strategies (issue #450)

- **Audit status:** open upstream on 2026-05-16; closed by 2026-08-30; later
  tagged behavior not evaluated here
- Affects: SoboStrategy, MoboStrategy, QparegoStrategy, ActiveLearningStrategy,
  LLMStrategy (any strategy that calls `RandomStrategy._sample_with_nchoosek`
  to seed `optimize_acqf` starting points)
- Symptom: during the audit, `.ask()` used 100% CPU and did not terminate. The
  Phase 2 BO smoke was stopped after 25 minutes.
- Root cause: `RandomStrategy._sample_with_nchoosek` enumerates
  combinations via `domain.get_nchoosek_combinations()` in legacy code
  that does not scale beyond ~20 input dims. PR #757 (merged
  2026-04-29) scales the *RandomStrategy* path but does not patch the
  acquisition seeding flow.
- Workaround: drop `NChooseKConstraint` from the BO-phase domain and
  enforce cardinality post-hoc. The Phase 2 manifest's
  `enforcement_note` records the canonical pattern (oversample by 2.5×,
  filter, return first 8).

### Finding B: Multi-fidelity strategies and non-box constraints (issue #761)

- **Audit status:** open upstream on 2026-05-16; closed by 2026-08-30; later
  tagged behavior not evaluated here
- Affects: `MultiFidelityVarianceBasedStrategy`,
  `MultiFidelityHVKGStrategy`
- Symptom: during the audit, `.ask()` raised `ConstraintNotFulfilledError` from
  `Domain.validate_candidates` because the acquisition optimizer
  proposes candidates outside the linear / NChooseK feasible region.
- Verified in a Phase 3 scale-bridge smoke (2026-05-15) with 12
  continuous factors + 1 linear inequality + 1 NChooseK + 1 linear cost.
- Root cause: BoFire's MF strategies inherited Sobo's acquisition path
  but did not propagate the Domain's `LinearInequalityConstraint` list
  to scipy/`optimize_acqf`'s `inequality_constraints` kwarg after the
  task-feature substitution. The validator then rejects the candidate.
- Workaround: fall back to "parallel-arms", instantiating one
  `DoEStrategy` per fidelity tier with a shared seed for reproducibility.
  No cross-fidelity variance learning, but every emitted candidate is
  feasible. The Phase 3 manifest's `fallback_pattern` is the canonical
  recipe.

### Bug C, Nonlinear constraint partial support in DoE solver (latent)

- DoEStrategy emits a non-blocking warning and proceeds. Some assertions
  in `nonlinear_constraints_check` are skipped. There is no GitHub issue
  for this yet; if a future manifest uses nonlinear constraints, file
  one before scaling.

## 4. Recommended manifest patterns

These are vetted templates for bioprocess scenarios that recur in
biosymphony-ferm-doe campaigns. Each pattern names the constraints, the
strategy that processes them, and the fallback if BoFire is unavailable.

### Pattern P1, media composition with cardinality (pick K of N carbons)

Two-phase pattern (Phase 1 D-optimal screen, Phase 2 BO refinement):

```jsonc
// Phase 1: constrained DoE screen
"constraints": [
  { "type": "linear",
    "constraint_id": "total_carbon_lte_100",
    "coefficients": {"glucose":1,"glycerol":1,"lactose":1,"sucrose":1,"xylose":1},
    "operator": "<=", "rhs": 100.0 },
  { "type": "linear",
    "constraint_id": "media_cost_lte_120_per_L",
    "coefficients": {"glucose":0.0007,"glycerol":0.0017,"lactose":0.0009,
                     "sucrose":0.0011,"xylose":0.0020,"yeast_extract":0.0035},
    "operator": "<=", "rhs": 1.20 },
  { "type": "nchoosek",
    "constraint_id": "at_most_two_carbons",
    "features": ["glucose","glycerol","lactose","sucrose","xylose"],
    "min_count": 1, "max_count": 2, "none_also_valid": false }
]
// Strategy: DoEStrategy + DOptimalityCriterion(formula="linear")  -> OK
```

```jsonc
// Phase 2: BO refinement of Phase 1 winners
// CRITICAL: drop NChooseK; enforce cardinality post-hoc.
"constraints": [
  { "type": "linear", "constraint_id": "total_carbon_lte_100", "...": "..." },
  { "type": "linear", "constraint_id": "media_cost_lte_120_per_L", "...": "..." },
  { "type": "nchoosek", "constraint_id": "at_most_two_carbons",
    "enforcement": "post_hoc_filter",
    "enforcement_note": "BoFire #450, SoboStrategy stalls with NChooseK in Domain. Oversample 2.5x, filter, return first K." }
]
// Strategy: SoboStrategy.make(domain).tell(experiments).ask(N * oversample_factor)
//   then filter on (1 <= active_carbons <= 2)
```

### Pattern P2, fed-batch with linear ratio constraints

A C:N ratio constraint is just a linear inequality after a small rearrange:

```
C/N >= 5   <=>   1*total_C - 5*total_N >= 0   <=>   LinearInequality(>= 0)
```

```jsonc
"constraints": [
  { "type": "linear",
    "constraint_id": "cn_ratio_gte_5",
    "coefficients": {"glucose":1, "glycerol":1, "ammonium_sulfate":-5, "yeast_extract":-5},
    "operator": ">=", "rhs": 0.0 },
  { "type": "linear",
    "constraint_id": "feed_pulse_total_lte_60_g",
    "coefficients": {"pulse_1_g":1,"pulse_2_g":1,"pulse_3_g":1},
    "operator": "<=", "rhs": 60.0 }
]
// Strategy: DoEStrategy for screen, SoboStrategy (or Mobo) for BO. Both OK with LinearInequality.
```

### Pattern P3, scale-bridge with multi-fidelity (current API caveat)

```jsonc
"factors": [
  { "factor_id":"fidelity", "type":"discrete",
    "values":["shake_flask_50ml","bioreactor_2L"] }
],
"constraints": [
  { "type":"linear", "constraint_id":"total_carbon_lte_100", "...":"..." }
]
// Primary strategy attempt: MultiFidelityVarianceBasedStrategy
//   -> Bug B (#761) is hit when constraints are non-box. Use try/except.
// Fallback: parallel DoEStrategy per fidelity tier, shared seed.
"doe": {
  "primary_strategy_class": "MultiFidelityVarianceBasedStrategy",
  "fallback_strategy_class": "DoEStrategy",
  "fallback_pattern": "parallel_arms"
}
```

Once issue #761 is patched (and BoFire 0.4+ tags), the fallback can be
retired. Until then, the adapter must record which path was taken
(`fidelity_path: "main_multifidelity" | "fallback_parallel_arms"`) and
the primary traceback tail when the fallback fires.

### Pattern P4, cost-aware optimization (linear cost as a budget)

The canonical biosymphony pattern: encode every priced ingredient with a
`cost_per_kg_usd_bulk`, then declare a linear cost constraint with
`coefficient_i = cost_per_kg_usd_bulk_i / 1000.0` (so `g/L * $/g == $/L`):

```jsonc
"constraints": [
  { "type": "linear",
    "constraint_id": "media_cost_lte_120_per_L",
    "coefficients": {
      "glucose": 0.00070, "glycerol": 0.00170, "lactose": 0.00090,
      "sucrose": 0.00110, "xylose": 0.00200,
      "ammonium_sulfate": 0.00025, "corn_steep_liquor": 0.00080,
      "yeast_extract": 0.00350, "tryptone": 0.01200
    },
    "operator": "<=", "rhs": 1.20 }
]
// Strategy: DoEStrategy (screen) or SoboStrategy (refine). Both OK.
// Bonus: derived "cost_per_mg" response = cost_per_L / titer ->
// MoboStrategy can Pareto-search titer vs cost-per-mg directly.
```

This is the only manifest pattern where a linear constraint pulls double
duty as both a feasibility wall and an optimization signal.

### Pattern P5, conditional infeasibility (strain × inducer incompatibility)

Most current manifests linearize a binary conditional (`if x=1 then y >=
T`). The adapter's `_conditional_linear_spec` handles that subset. For
the full categorical-categorical case, use
`CategoricalExcludeConstraint`:

```jsonc
"constraints": [
  { "type": "categorical_exclude",
    "constraint_id": "strain_S1_incompatible_with_inducer_I3",
    "features": ["strain", "inducer"],
    "logical_op": "AND",
    "conditions": [
      { "kind": "selection", "feature": "strain", "selection": ["S1"] },
      { "kind": "selection", "feature": "inducer", "selection": ["I3"] }
    ]
  }
]
// Strategy: RandomStrategy or EntingStrategy.
// DO NOT use with DoEStrategy (continuous IPOPT solver) or SoboStrategy
// (no categorical exclusion handling without a categorical kernel).
```

This requires extending the adapter; the current adapter recognizes
`forbidden`/`conditional` constraints but fails closed. The translation
target on the adapter side is `CategoricalExcludeConstraint`. Not yet
wired; file before authoring a manifest that needs it.

### Pattern P6, batch blocking with InterpointEqualityConstraint

For a campaign where each plate / day / operator forms a block of `k`
runs that must share a hard-to-change factor:

```jsonc
"constraints": [
  { "type": "interpoint_equality",
    "constraint_id": "plate_block_share_buffer_lot",
    "features": ["buffer_lot"],
    "multiplicity": 8 }
]
// Strategy: RandomStrategy emits batches where 8 candidates share buffer_lot.
// DoEStrategy and Sobo/Mobo currently error, they assume intrapoint constraints.
```

This is the most under-utilized constraint in the catalog. Use it when
blocking matters and the BO step is happy to alternate between
`RandomStrategy.ask(8)` (block-respecting) and `SoboStrategy.ask(1)`
(within-block exploitation). Not yet wired in the adapter.

## 5. Red flags, never put these in a manifest

The following patterns broke the supported 0.3.x adapter or the May 2026
audit surface. Keep the conservative routes until a later release is evaluated.

1. **`NChooseKConstraint` with an acquisition-optimizing BO strategy**, did
   not return from `.ask()` during the May 2026 audit (finding A, #450). If the manifest declares both
   `nchoosek` and `preferred_backend = "bofire"` with `family !=
   d_optimal_constrained`, the adapter must either drop the constraint
   for the BO phase or refuse to route. The Phase 2 manifest's
   `enforcement: "post_hoc_filter"` field is the canonical signal that
   the constraint is documentation-only at the BoFire boundary.
2. **`MultiFidelityVarianceBasedStrategy` / `MultiFidelityHVKGStrategy`
   with any non-box constraint**, raised
   `ConstraintNotFulfilledError` during the May 2026 audit (finding B, #761).
   The Phase 3 manifest's
   `fallback_strategy_class: "DoEStrategy"` + `fallback_pattern:
   "parallel_arms"` is the canonical signal.
3. **`InterpointEqualityConstraint` + `DoEStrategy`**, the IPOPT solver
   is intrapoint and the interpoint constraint is silently dropped.
   Use `RandomStrategy` for the blocking step or implement post-hoc
   block assignment.
4. **`CategoricalExcludeConstraint` + `DoEStrategy`**, DoEStrategy
   expects continuous inputs only. Use `RandomStrategy` (PR #644 GA
   path) or `EntingStrategy` for categorical exclusions until BoFire
   plumbs categorical kernels into Sobo.
5. **Symbolic nonlinear constraints inside a Sobo `.ask()` without a
   smoke test**, botorch's `optimize_acqf` accepts
   `nonlinear_inequality_constraints` as callables, but the wrapping in
   BoFire is sensitive to non-differentiable expressions (e.g.,
   `abs(x)`). Always run a 1-candidate smoke before scaling.
6. **Mixing `LinearEqualityConstraint` (sum-to-one mixture) with
   `NChooseKConstraint` in a Sobo phase**, even before bug A kicks in,
   the polytope sampler is asked to sample on a `(d-1)`-simplex with
   discrete cardinality bumps, which makes the rejection rate
   pathological. Use a mixture parameterization (`MixtureInput`) or
   the post-hoc-filter pattern.
7. **Declaring a constraint that the adapter's
   `_unsupported_constraint_ids` rejects, then setting `preferred_backend:
   "bofire"`**, the adapter writes
   `adapter_status: "translation_blocked"` and the stdlib fallback
   takes over. The manifest still claims `bofire_adapter_planning`.
   This is the worst-of-both state; either get the constraint into the
   supported set or change the claim.

## 6. Features that entered later BoFire releases

The pinned `bofire>=0.3.1,<0.4` includes the December 2025 surface. The
following changes were on `main` during the May audit and later entered the
0.4 release line. The impact column preserves the audit-time assessment.

| PR | Title | Merged | Impact |
|---|---|---|---|
| [#705](https://github.com/experimental-design/bofire/pull/705) | Multi-output, multi-fidelity optimization | 2026-05-11 | Added `MultiFidelityVarianceBasedStrategy` and `MultiFidelityHVKGStrategy`; the exact non-box adapter case still needs a later-release evaluation. |
| [#749](https://github.com/experimental-design/bofire/pull/749) | LLM Strategy | 2026-04-30 | Added `LLMStrategy` for literature-warmstart BO. It is not wired into this repository. |
| [#752](https://github.com/experimental-design/bofire/pull/752) | True NChooseK support for DoE | 2026-04-16 | Added native NChooseK handling to `DoEStrategy`; released in BoFire 0.4. The separate evaluation extra pins 0.4.1. |
| [#757](https://github.com/experimental-design/bofire/pull/757) | Scale RandomStrategy NChooseK sampling | 2026-04-29 | Made `RandomStrategy` usable for 50+ dim NChooseK problems. It did not fix finding A in the audited Sobo seeding path. |
| [#754](https://github.com/experimental-design/bofire/pull/754) | Fix MultiTaskGP serialization | 2026-04-21 | Unblocks save/load of multi-fidelity surrogates. Required before any multi-fidelity dossier-handoff workflow. |
| [#646 / #644](https://github.com/experimental-design/bofire/pull/644) | Exclude constraints usable in GA / Conditional input features | 2025-10–11 | Already in 0.3.1; lets `EntingStrategy` (GA) honor `CategoricalExcludeConstraint`. |

Before widening the verified primary adapter range:

1. Evaluate the current supported release line on the public compatibility fixtures.
2. Rename the import sites: `MultiFidelityStrategy` →
   `MultiFidelityVarianceBasedStrategy` (already accommodated in
   `phase3_manifest.json:doe.primary_strategy_class`).
3. Re-run the multi-fidelity compatibility fixture; retire the
   parallel-arms fallback and let `MultiFidelityVarianceBasedStrategy`
   be the primary path only if it honors the declared constraints.
4. Re-evaluate the bug A workaround. PR #757 scaled RandomStrategy's
   NChooseK sampler but did not touch the audit-time Sobo seeding path. Until
   a later release passes the repository fixture, keep
   `enforcement: "post_hoc_filter"` on any NChooseK in a BO-phase
   manifest.
5. Add `LLMStrategy` only after a public fixture establishes a bounded use
   and records its claim limits.

## 7. Adapter implications (what changes here)

The adapter today supports `linear`, `nchoosek`, and a narrow
`conditional → linear` linearization (binary threshold case). Adding the
patterns above requires:

1. **CategoricalExcludeConstraint translation.** The current adapter writes
   `unsupported_constraints` for general conditionals. Wire the
   conditions union (`SelectionCondition`, `ThresholdCondition`,
   `NonZeroCondition`) into a translator and gate the strategy choice
   to `RandomStrategy` or `EntingStrategy` for any manifest that
   declares one.
2. **InterpointEqualityConstraint translation.** Straightforward
   constructor mapping; the adapter should refuse to use
   `DoEStrategy`/`SoboStrategy`/`MoboStrategy` whenever an interpoint
   constraint is declared.
3. **Nonlinear / Product constraint translation.** Accept the
   expression string verbatim and gate on whether the chosen strategy is
   in the "OK" or "caveat" cell. Block routing to MF strategies until a
   later tagged release passes the repository's non-box fixture.
4. **Issue gate on every smoke.** The adapter should emit
   `bofire_compat_report.json` alongside `bofire_strategy_report.json`
   summarizing which row/column of this matrix the smoke landed in,
   and which workaround (if any) was applied. That makes the matrix
   load-bearing rather than aspirational.

## 8. References

- Decision: `docs/BOFIRE_POSITIONING.md`
- Adapter: `src/biosymphony_ferm_doe/adapters/bofire_strategy.py`
- Constraint validator: `src/biosymphony_ferm_doe/constraints.py`
- BoFire constraints: `experimental-design/bofire/blob/main/bofire/data_models/constraints/api.py`
- BoFire strategies: `experimental-design/bofire/blob/main/bofire/strategies/api.py`
- Issue #450: NChooseK + acquisition stall
- Issue #761: Multi-fidelity + non-box constraint validator rejection

---

This doc is the read-once gate for any new manifest that sets
`preferred_backend: "bofire"`. If a proposed manifest does not map onto
one of the patterns above, file a ticket before authoring it.
