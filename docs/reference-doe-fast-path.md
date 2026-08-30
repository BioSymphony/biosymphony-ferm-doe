# Reference DOE Fast Path

## Product Intent

Many fermentation users already know commercial DOE software. BioSymphony Ferm DoE should give those users a familiar DOE path while adding campaign context that may not be represented in a basic DOE workflow: assay readiness, scale-transfer logic, process-phase constraints, cost/time scoring, planning packets, and follow-up memory.

This is not a promise that every commercial DOE method is fully reimplemented today. BioSymphony now emits reference DOE planning artifacts locally, and every metric is labeled as exact, adapter-backed, approximate, or heuristic.

## User-Facing Positioning

Suggested user-facing wording:

```text
If you would normally open Custom Design, Screening, RSM, Mixture,
Space-Filling, Augment Design, or Bayesian Optimization, use this as a planning
companion. It builds a DOE table and checks whether the experiment is
biologically measurable, feasible under its declared constraints, and worth
considering.
```

## Parity Matrix

| Reference DOE Surface | BioSymphony Fast-Path Target | BioSymphony Add-On |
| --- | --- | --- |
| Custom Design | Factor model, terms, constraints, run budget, randomization, blocking, hard-to-change factors | Translate fermentation reality into constraints before design generation |
| Screening / DSD | Fractional, Plackett-Burman, DSD-like, main-effect and mixed-factor screening | Factor-prior audit from literature, prior runs, phase structure, and product class |
| RSM | CCD, Box-Behnken, custom quadratic candidates, center/lack-of-fit runs | Block RSM when assay noise or response semantics are not ready |
| Mixture | Mixture bounds, sum constraints, mixture-process interactions | Convert media/feed components into recipe tables, feasibility, and cost burden |
| Space-Filling | LHS/Sobol/Halton/scouting candidates with coverage diagnostics | Use only when campaign priors justify scouting; pre-register follow-up narrowing rules |
| Diagnostics | Rank, estimability, alias/correlation, D/I/A/G proxies, FDS, prediction variance, power assumptions | Add assay power, sampling burden, oxygen/feed/pH risk, and cost/run diagnostics |
| Compare Designs | Side-by-side scorecards and selected design rationale | Multi-agent tournament with skeptical assay/process/cost lanes |
| Augment Design | Append runs to locked historical/current design under updated model | Recommend confirm, narrow, expand, pause, stop, or scale/downscale |
| Bayesian Optimization | Historical data to candidate set, batch selection, stopping recommendation | BO is gated by assay/readiness, phase logic, and negative-result memory |
| Profiler / Prediction | Prediction model and operating-window report | Operating window includes fermentation caveats and lab review packet |

## Implementation Shape

Add a workflow mode named `reference-doe-engine`. It should be selected when users mention commercial/reference DOE, Custom Design, DSD, RSM, mixture, space-filling, augment design, Bayesian optimization, or "DOE comparable."

The mode must produce:

- `doe_parity_report.md`
- `doe_parity_matrix.json`
- `design_candidates/*.csv`
- `design_candidates/*.scorecard.json`
- `design_candidates/*.model_matrix.csv`
- `design_candidates/*.diagnostics.json`
- `design_diagnostics.json`
- `design_comparison.json`
- `design_comparison.md`
- `selected_wave_1_design.csv`
- `doe_reference_export.csv`
- `assumptions_and_nonparity.md`

The starter fast-path example is:

```bash
ferm-doe engine compile-dossier \
  --manifest examples/reference-doe-custom-design/campaign_manifest.json \
  --out .runtime/doe-fast-path-dossier \
  --run-budget 14
```

Optional reference DOE utilities are available when a user wants a more reference DOE-like inspection path without making those utilities mandatory:

- `ferm-doe engine utility custom-optimal` - constrained D/I/A/G-style row selection with fixed controls and trace output.
- `ferm-doe engine utility augment-design` - actual next-run rows from locked results and remaining budget.
- `ferm-doe engine utility profiler` - local prediction/operating-window report after results exist.
- `ferm-doe engine utility simulate-design` - deterministic effect/noise simulation and power proxy.
- `ferm-doe engine utility doe-export` - simple CSV import/export bridge for DOE-oriented users.
- `ferm-doe engine utility benchmark-doe` - synthetic property harness for parity claims.
- `ferm-doe engine utility check-deps` - optional adapter availability report.

Every utility emits `utility_manifest.json` with backend, dependency status, metric labels, artifacts, and caveats.

## Evaluation Campaign

Use `packs/issue-packs/doe-parity-v0/` when the goal is specifically to assess DOE statistical parity. Keep it separate from the default fermentation-readiness workflow so the product can state its scope clearly.

The campaign should prioritize:

1. true custom design model matrices and optimality metrics
2. DSD/screening/RSM/mixture/space-filling generators
3. design diagnostics and compare-design reports
4. augmentation and result-ingestion-backed next-run selection
5. optional Bayesian optimization adapters
6. user-facing parity report and examples

## Success Criteria

This path is successful when a DOE software user can inspect a BioSymphony dossier and find:

- the design class they expected
- familiar diagnostics and assumptions
- a clear reason for selected design
- exportable design tables
- passing dossier and contract self-check artifacts
- an explicit non-parity list when we are weaker than commercial DOE software
- fermentation-specific warnings generic DOE software would not have forced
