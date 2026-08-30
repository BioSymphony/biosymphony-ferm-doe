# Backend Evaluation Findings

**Evaluation date:** 2026-05. **Upstream status checked:** 2026-08-30.
**Status:** dated findings from a six-fixture validator harness across seven Bayesian optimization and DoE backends. This is neither a parity claim nor an academic benchmark. The fixtures are synthetic public examples under [`../examples/adaptive-backend-eval/`](../examples/adaptive-backend-eval/), and the verdicts apply only to the evaluated versions and conditions.

Since the evaluation, BoFire 0.4 added generalized NChooseK DoE support and
0.5.0 became the current upstream release. Issues #450 and #761 are closed.
The later releases have not been evaluated against this repository's adapters,
so the historical results below remain compatibility evidence only for the
recorded versions. The primary BoFire adapter remains on `>=0.3.1,<0.4`.

These findings give the public adapter list (`docs/TOOL_REGISTRY.md`, the `[bofire]`, `[entmoot]`, `[omlt]`, `[tabpfn]`, `[botorch]` extras) explicit depth rather than implicit parity. The depth ladder in [`BIOMANUFACTURING_ADAPTIVE_BACKENDS.md`](BIOMANUFACTURING_ADAPTIVE_BACKENDS.md) is the one-line summary; this doc is the long form.

## Provenance and reproducibility

The repository includes the transferable inputs needed to inspect the evaluation:

- the synthetic fixtures in `examples/adaptive-backend-eval/`
- the public adapter source under `src/biosymphony_ferm_doe/adapters/`
- the artifact validators and smoke-artifact schema
- the methodology notes in this document and [`ADAPTER_DESIGN_NOTES.md`](ADAPTER_DESIGN_NOTES.md)

The raw per-fixture outputs from the original evaluation are not distributed here, so the exact numerical results are not independently reproducible from this repository alone. Read the findings as a dated, single-seed record, not as current-release performance evidence. See "What was not tested" for the remaining caveats.

## Headline

In the May 2026 evaluation, OMLT produced the cleanest NChooseK result under the delivered-amount definition. The encoding difference from ENTMOOT is documented under "ENTMOOT definition-correction" and "OMLT lower-coupling fix" in [`ADAPTER_DESIGN_NOTES.md`](ADAPTER_DESIGN_NOTES.md). The evaluated BoFire 0.3.1 and May main-branch routes did not replace the MIP-backed BO slot. For NChooseK BO, OMLT and ENTMOOT therefore remain the conservative routes until a later BoFire release is evaluated here.

## Constraint-honoring spectrum

Ranking is on `NChooseK leak rate` on a 4-factor `1-of-2 active among 4 carbons` fixture (`cardinality_heavy_media`) plus structural constraint honoring on the other five fixtures. Single seed (42), single batch (16 candidates). Leak counts are recorded under a `x_i > 0` "actual amount delivered" definition rather than the binary-indicator-only definition that some adapters self-report (see ENTMOOT note below).

| Rank | Backend | NChooseK leaks (`cardinality_heavy_media`) | Linear leaks | Verdict |
|---|---|---|---|---|
| 1 | **OMLT 1.2.2** | **0 / 10** (combinatorial ceiling for `C(4,1)+C(4,2)=10` configs) | 0 | New cardinality workhorse. MIP encoding with explicit lower-coupling. |
| 2 | **TabPFN v3 (8.0.3)** | **0 / 16** | 0 | Foundation-model surrogate; sample-then-rank acquisition; low-data slot (n < 20, factors ≤ 8). |
| 3 | **BoFire 0.3.1** | FAIL_CLOSED (route declines) | FAIL_CLOSED | Honest-and-strict; routes to ENTMOOT/OMLT for NChooseK. Unchanged. |
| 4 | **BoTorch 0.17.2 direct** (separate cost-weighted wrapper, not the public `botorch_wave2.py`) | Budget-sensitive: 0/16 kept at q=16, 0/64 at q=64, **37/256** at q=256 | n/a (no native cost constraint here) | Honest-and-rejection. Footnote: see "BoTorch direct budget transition" below. The public `botorch_wave2.py` follow-up adapter is a different surface and does not apply cost weighting; the trap below documents the broader pattern. |
| 5 | **ENTMOOT 2.1.1** | 5 / 16 under the `x_i > 0` definition; 0 / 16 under the binary-indicator definition | 0 | Definition-scoped: indicator-only PASS; lab-semantic FAIL. The May 2026 evaluation ranked OMLT ahead for new campaigns; ENTMOOT remains supported for existing rigs. |
| 6 | **BayBE 0.14.3** | LEAKY — ~75% of candidates on the 4-factor cardinality fixture violate NChooseK | 0 | Honest but leaky on NChooseK; clean elsewhere. |
| 7 | **ProcessOptimizer 1.1.2** | LEAKY — ~95% on the cardinality fixture | 1 on the linear fixture | Honest but leaky on both NChooseK and linear. |
| FAIL | **BoFire main BO probes** (mid-2026-05) | NChooseK DoE was routed separately through PR #752; `SoboStrategy` emitted 0 candidates in 300s (issue [#450](https://github.com/experimental-design/bofire/issues/450) was open at evaluation time) | n/a | Did not replace the MIP-based BO slot in this dated evaluation. |

The unconstrained-fixture cells, the bounds-only fixture cell, and the linear-only cell for backends not listed here as leaky are all clean. The leaky cells in the table are exactly the cells where each backend's documented limitations live; this is consistent with each backend's upstream documentation.

## Per-backend depth

### OMLT — new cardinality workhorse

OMLT is the public Imperial-College/COIN-OR MIP-encoded BO route over a LightGBM gradient-boosted-tree surrogate. The adapter is in [`src/biosymphony_ferm_doe/adapters/omlt_strategy.py`](../src/biosymphony_ferm_doe/adapters/omlt_strategy.py) with 20 unit tests in [`tests/test_omlt_strategy.py`](../tests/test_omlt_strategy.py) (13 translation tests + 7 live MIP-solve tests).

**Stack:** `omlt 1.2.2` + `pyomo 6.10.0` + `highspy 1.14.0` + `lightgbm 4.6.0` + `onnx 1.21.0` + `onnxmltools 1.16.0` + `scikit-learn 1.8.0`. All MIT/BSD/Apache; no copyleft, no paid-license footguns.

**Result on the 6-fixture sweep:**

| Fixture | Status | Cands | NChooseK leaks | Linear leaks | Notes |
|---|---|---|---|---|---|
| `static_constrained_media` | PASS | 6 | 0 | 0 | Stops at combinatorial ceiling for the binary-config space |
| `cardinality_heavy_media` | PASS | 10 | **0** | n/a | Stops at combinatorial ceiling `C(4,1)+C(4,2)=10` |
| `cost_aware_multiobjective` | DEFERRED | — | — | — | No native MO; route declines |
| `low_data_hybrid_transfer` | PASS | 16 | 0 | n/a | |
| `scale_bridge_planning` | PASS | 16 | n/a | n/a | |
| `adaptive_orchestration` | PASS | 16 | 0 | 0 | |

The candidate counts below 16 on the cardinality fixtures are the combinatorial ceiling on distinct binary indicator configurations, not failures; duplicate-with-perturbation would not add information. The diversity-via-no-good-cuts strategy that produces this behavior is documented in [`ADAPTER_DESIGN_NOTES.md`](ADAPTER_DESIGN_NOTES.md).

**Caveats:** no native multi-objective support; HiGHS solver may not scale to large MIPs (>~1000 binary variables); OMLT's MIP encoding can blow up for deep trees. Practical operating regime: ≤ 50 numeric factors, ≤ 5 cardinality, single-objective.

### TabPFN v3 — low-data low-dim foundation-model surrogate

TabPFN v3 is the Prior Labs foundation-model regressor wrapped as a BoTorch surrogate. The adapter is in [`src/biosymphony_ferm_doe/adapters/tabpfn_strategy.py`](../src/biosymphony_ferm_doe/adapters/tabpfn_strategy.py) with 15 unit tests in `tests/test_tabpfn_strategy.py`.

**Stack:** `tabpfn 8.0.3` + `botorch 0.17.2` + `torch 2.12.0`. Token-gated by Prior Labs; the adapter checks for `TABPFN_TOKEN` in the environment and routes-decline cleanly when absent. No token is ever stored in the manifest, fixture, registry, or any tracked file.

**Result on the 6-fixture sweep:** 5 / 6 PASS locally (0 NChooseK leaks, 0 linear leaks where the fixture exercises those classes); 1 / 6 deferred (`cost_aware_multiobjective` — see "Multi-objective notes" below).

**Caveats:** the default TabPFN-3 weights are non-commercial. The code and v2 weights use the Prior Labs License, an Apache-2.0 derivative with an attribution provision. Review the applicable terms before use. The Gaussian-approximation posterior wrap may underestimate uncertainty in highly non-Gaussian regions; TabPFN fit scales O(n²), and there is no batch-fantasies path. Routing rules and the Gaussian-approximation design decision are in [`ADAPTER_DESIGN_NOTES.md`](ADAPTER_DESIGN_NOTES.md).

### BoFire 0.3.1: strict constrained-DoE default

Unchanged this cycle. Routes constrained DoE through `DoEStrategy + DOptimalityCriterion + IPOPT`, single-objective constrained BO through `SoboStrategy`, multi-fidelity through `MultiFidelityVarianceBasedStrategy` (with the parallel-arms fallback documented in [`BOFIRE_CONSTRAINT_PATTERNS.md`](BOFIRE_CONSTRAINT_PATTERNS.md)). For NChooseK BO, routes decline and the agent falls back to ENTMOOT/OMLT. The spectrum table labels this as FAIL_CLOSED. Stays the default constrained-DoE/BO route per [`BOFIRE_POSITIONING.md`](BOFIRE_POSITIONING.md).

### BoFire May 2026 main snapshot: DoE screen route with BO limits

Tested against BoFire `main` as of mid-2026-05 while probing whether main removed the need for MIP-backed NChooseK BO. Two findings remain load-bearing:

1. **`DoEStrategy` + `NChooseK`:** use the PR #752 route for model-free NChooseK DoE screens. The pinned `bofire>=0.3.1,<0.4` extra predates that path, so this repo exposes `adaptive-nchoosek-doe` for the main-branch route and requires row-level cardinality rechecks. This DoE screen route does not change the BO workhorse decision below.

2. **`SoboStrategy` + `NChooseK` + linear:** PR #753's shared-variable NChooseK did not unblock the evaluated SLSQP path. The run timed out after 300 seconds with no candidates. Upstream issue [#450](https://github.com/experimental-design/bofire/issues/450) was open at evaluation time and is now closed; the later tagged behavior has not been evaluated here.

**Disposition:** the `adaptive-nchoosek-doe` extra now pins BoFire 0.4.1 as a separate Python 3.11 or newer evaluation lane. It is not part of the verified primary adapter range. Keep ENTMOOT or OMLT as the conservative NChooseK BO route until a later BoFire release passes the public fixtures.

**Limits:** single seed and single evaluation day. A later-release evaluation is required before changing the compatibility claim. A separate May observation found that `MultiFidelityVarianceBasedStrategy` returned on one 12-input domain while bare `SoboStrategy` did not return on the same shape; the evaluation did not establish whether that difference was strategy-specific or domain-shape-dependent.

### BoTorch direct — budget-sensitive, wrapper-side trap

**Important scoping note:** the public repo ships [`botorch_wave2.py`](../src/biosymphony_ferm_doe/adapters/botorch_wave2.py), a simpler follow-up BoTorch route around `qEI` / `qUCB` / `qTS`, without cost weighting and without post-hoc NChooseK filtering. The findings below come from a separate cost-weighted BoTorch wrapper that wraps `qLogExpectedImprovement` (single-objective) and `qLogExpectedHypervolumeImprovement` (multi-objective) in `InverseCostWeightedUtility` and applies post-hoc NChooseK filtering. That wrapper is not in the public repo today; the findings are documented here as a design pattern to know if you build or evaluate a similar wrapper.

**Budget transition on `cardinality_heavy_media` with that wrapper:**

| Budget | Raw emitted | Kept (PASS NChooseK) | Active-factor distribution of raw |
|---|---|---|---|
| 16 | 16 | **0** | All 16 collapsed to active=0 |
| 64 | 64 | **0** | All 64 collapsed to active=0 |
| 256 | 256 | **37** | active∈{1..4} spread, no collapse |

The cause is wrapper-side, not BoTorch upstream. With 4 prior observations the GP posterior is essentially flat over the bulk of the cube, the wrapper's `InverseCostWeightedUtility` cost-weighting then dominates the acquisition value, and the joint optimizer collapses every candidate to the cost minimum (the origin). At q=256, joint-batch acquisition cannot collapse all candidates to one point, so the optimizer spreads. The wrapper-side fix is to make the cost-model build conditional on the fixture actually having a `type=linear` cost constraint declared; absent that, use plain `qLogExpectedImprovement` without cost weighting. The fix is recorded in [`ADAPTER_DESIGN_NOTES.md`](ADAPTER_DESIGN_NOTES.md).

**Operating-regime note:** a cost-weighted BoTorch direct wrapper is structurally clean for budget ≥ 256 on cardinality fixtures with no explicit cost constraint. For typical 16-candidate budgets on cardinality problems, prefer OMLT (rank 1) or ENTMOOT-with-fix. The public `botorch_wave2.py` follow-up adapter, which does not apply cost weighting, is not subject to this specific trap.

### ENTMOOT — definition-correction

ENTMOOT v2 is the BoFire-side documented swap when `SoboStrategy + NChooseK` stalls (per [`ENTMOOT_SWAP_DESIGN.md`](ENTMOOT_SWAP_DESIGN.md)). A reconciliation pass surfaced an important nuance: the adapter's internal `cardinality_ok` flag uses the binary indicator definition (`b_i ≥ 0.5`), and under that definition the adapter passes at all tested batch sizes. The contract-emitter and lab-side check use a different definition (`x_i > 0`, i.e. the actual amount delivered), and under that definition the same runs surface 5 / 16 leaks on the `cardinality_heavy_media` fixture.

The root cause is the one-directional big-M coupling in the MIP encoding:

```
x_i ≤ M · b_i        (the standard big-M; "if not active, amount must be zero")
```

The MIP is then free to satisfy a `min_count` constraint by setting `b_i = 1, x_i = 0` (degenerate ON-but-empty). Auto-fantasy resampling at batch=16 plus the larger candidate space makes the degenerate corner attractive.

The one-line fix is a complementary lower-coupling that closes the corner: `x_i >= epsilon * b_i`. OMLT ships this lower-coupling and passed the fixture checks. See [`ADAPTER_DESIGN_NOTES.md`](ADAPTER_DESIGN_NOTES.md) for the encoding details. For new campaigns, prefer OMLT; for existing rigs with ENTMOOT in place, the one-line patch is straightforward and is the right next step on the ENTMOOT side.

### BayBE — leaky on NChooseK, clean elsewhere

BayBE 0.14.3 (Apache-2.0, Merck KGaA). Around 75% of candidates on the 4-factor `1-of-2 active` cardinality fixture violate NChooseK. Linear constraints honored cleanly; unconstrained and bounds-only fixtures clean. Slot for BayBE remains "low-data and hybrid-space comparison target" per [`BIOMANUFACTURING_ADAPTIVE_BACKENDS.md`](BIOMANUFACTURING_ADAPTIVE_BACKENDS.md). Not recommended where NChooseK is load-bearing.

### ProcessOptimizer — leaky on both

ProcessOptimizer 1.1.2 (BSD-3, scikit-optimize lineage). Around 95% of candidates leak NChooseK on the cardinality fixture; one linear-constraint violation on the static-linear fixture. Listed in the registry for landscape coverage; not routed as a default for constrained problems.

## Multi-objective notes

Multi-objective Bayesian optimization (`qLogEHVI` / `qLogNEHVI` on a Pareto-front problem) is structurally heavier than single-objective. The public repo does not currently ship an MO wrapper for the `cost_aware_multiobjective` fixture; the findings below come from an external cost-weighted MO BoTorch wrapper and are documented as design guidance for anyone building or evaluating one.

- The single biggest RAM lever for q ≥ 8 MO is `optimize_acqf(sequential=True)`, not the choice between `qLogEHVI` and `qLogNEHVI` (those are within noise on the public fixtures at small q; they're equivalent at the autograd-graph level under parallel q-batch mode).
- Setting `MC_SAMPLES=32` (down from BoTorch's default 512) plus `num_restarts=3`, `raw_samples=64` makes a 4-response cost-aware MO BO at q=8 reproducible on commodity hardware.
- Dropping `measurement_type ∈ {derived, calculated}` responses from the surrogate fit when ≥3 responses are present collapses a 4-response 16-orthant FastNondominatedPartitioning to a 2-GP + 4-orthant partitioning, which is well within budget.

The env-driven knob defaults and the `_CostWeightedAcquisition.X_pending` setter that makes `optimize_acqf(sequential=True)` work under cost weighting are written up in [`ADAPTER_DESIGN_NOTES.md`](ADAPTER_DESIGN_NOTES.md). Observed PASS routes with this kind of wrapper, in case they help calibrate expectations:

- A cost-weighted **BoTorch direct** wrapper on `cost_aware_multiobjective` with `qLogEHVI` + `sequential=True` + `MC_SAMPLES=32` + `drop_derived=True` at q=8.
- **BayBE** on `cost_aware_multiobjective` under the same wrapper-side defaults (BayBE under the hood routes through BoTorch).
- BoFire MO via `MoboStrategy` works at the wrapper level (no OOM, no crash) but is substantially slower in wall time than the BoTorch direct wrapper because of the additional Domain-translation step in front of `optimize_acqf(sequential=True)`.

## What this changes in the public adapter set

1. **OMLT becomes the cardinality workhorse** in the depth ladder (documented route + smoke + findings tier). The `[omlt]` extra was already in the public adapter list; this doc adds the depth.
2. **ENTMOOT v2 is positioned as "valid for existing rigs"** with the documented one-line patch path. The `[entmoot]` extra still ships; the depth ladder in [`BIOMANUFACTURING_ADAPTIVE_BACKENDS.md`](BIOMANUFACTURING_ADAPTIVE_BACKENDS.md) signals the swap.
3. **BoTorch direct is documented as budget-sensitive** on cardinality fixtures with no explicit cost constraint, with an operating-regime note (prefer OMLT or ENTMOOT-with-fix for typical 16-candidate budgets on cardinality problems).
4. **The MO BO route gets a single documented configuration** (`qLogEHVI + sequential=True + MC_SAMPLES=32 + drop_derived`) that reproduces.

## What was not tested

- Multiple seeds. All measurements above are single-seed (42); seed variance is not characterized.
- Real fermentation data. The fixtures are synthetic backend-contract probes; results don't speak to candidate quality on real campaigns, only to constraint honoring on the contract surface.
- Backends beyond the seven above. Ax, NIMO Controller, CellCultureBO, Anubis, Foumani GP+, LLAMBO are listed in `docs/TOOL_REGISTRY.md` but were not in this cycle's sweep.
- Production-scale n. Tested at n ≤ 500; large-n behavior is not characterized.
- Multi-fidelity NChooseK end-to-end. The parallel-arms fallback under `MultiFidelityVarianceBasedStrategy` (when it raises `ConstraintNotFulfilledError`) is documented in [`BOFIRE_CONSTRAINT_PATTERNS.md`](BOFIRE_CONSTRAINT_PATTERNS.md); structural multi-fidelity NChooseK without the fallback is not yet measured.

## Pointers

- The actual fixtures: [`examples/adaptive-backend-eval/`](../examples/adaptive-backend-eval/).
- Per-adapter design notes (encodings, posterior wraps, optimizer-knob defaults): [`ADAPTER_DESIGN_NOTES.md`](ADAPTER_DESIGN_NOTES.md).
- Default constrained-DoE/BO routing: [`BOFIRE_POSITIONING.md`](BOFIRE_POSITIONING.md), [`BOFIRE_CONSTRAINT_PATTERNS.md`](BOFIRE_CONSTRAINT_PATTERNS.md).
- ENTMOOT swap design: [`ENTMOOT_SWAP_DESIGN.md`](ENTMOOT_SWAP_DESIGN.md).
- Tool-registry-level positioning: [`TOOL_REGISTRY.md`](TOOL_REGISTRY.md), [`tool-registry.json`](tool-registry.json).
- Adaptive-backend comparison surface fixtures: [`adaptive-backend-evaluation.json`](adaptive-backend-evaluation.json).
- Capability-centric map of optional extras: [`ADAPTER_MAP.md`](ADAPTER_MAP.md).
