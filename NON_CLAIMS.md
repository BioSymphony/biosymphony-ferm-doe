# Non-Claims

Canonical boundary statements for BioSymphony Ferm DoE. Other files keep short reminders that link here.

## What this is

Pre-experiment planning. It assesses whether a fermentation campaign is measurable, feasible under its declared constraints, and worth considering before the lab spends time and materials.

## What this is not

- Not a physical execution system. Not LIMS, not ELN, not robotics, not real-time bioreactor control, not scheduling.
- Not a validated GxP batch-record system. Validators do not produce regulatory-grade evidence.
- Not a replacement for JMP, Design-Expert, Modde, or a statistician. First-batch designs carry a labeled statistical claim level (`exact` | `adapter_backed` | `approximate` | `heuristic`). First-batch analysis (`ferm-doe analyze`) provides stdlib OLS estimates with permutation p-values, bootstrap CIs, and lack-of-fit decomposition, labeled `wave1_analysis_planned`. These labels support statistician review before expensive follow-up runs; they are not final regulatory-grade analysis.
- Not a physical-execution validation system for scale-up or scale-down. Scale-bridge artifacts in this repo describe planning, criteria, and qualification evidence the campaign would need; they do not validate that a small-scale model recapitulates a large-scale process unless executed runs with provenance and QC have been ingested.
- Not a lab-execution cost, yield, or throughput model. `ferm-doe cost-rollup` multiplies operator-declared unit costs against artifact-derived counts (first-batch run count, sample count, sample volume, run duration) and emits a planning rollup labeled `cost_rollup_planning`; it does not estimate biological yields, robotics queueing, or staff time. Use it as a budgeting input, not as a quote. The five-tier cost stack documented in `docs/COST_MODEL_REALISM_CHECK.md` (simulator, bulk reagent, fully-loaded COGS, CMO benchmark, range) is the recommended honesty framing; a single $/mg number is never load-bearing.
- Not an autonomous optimization system. Adaptive follow-up artifacts are planned next-step recommendations and learning records; they do not prove optimality, transferability, or execution readiness. BoFire and BoTorch adapter outputs are labeled `bayesian_optimization_planned`, not validated optimization.
- Not a validated process simulator. Any simulator outputs (when present) carry a `simulator.fidelity_level` annotation on the manifest. A simulator number is one tier in the cost stack, not a substitute for the literature pressure-test at `templates/PARETO_LIT_CHECK.template.md` or for lab data.
- Not a literature-discovery system. The cumulative-dossier pattern (per-corpus swarm, integrator, harvester) records what evidence rows the operator or a research worker provided, with provenance, confidence, and contradiction tracking. It does not perform unbounded web search inside the engine, and it does not promise topic coverage beyond what the operator supplies.

## What this validates

- Manifest structure (campaign_id, claim_level, factor types, response measurement contracts).
- Public-safety properties when `claim_level == public_synthetic_demo`.
- Profile-required blocks (e.g., scale_context for scale-bridge profiles).
- DoE family minimum-runs guidance for declared families.
- Per-axis readiness state (responses, factors, arms, scale_context, doe, decision_rules, evidence, feasibility).
- Public follow-up planning checks after results are supplied: result-row QC/trust filtering, response-level assay-power policy, conservative next-action labels, arm-scoped negative memory, and learning-ledger handoff.
- Stdlib OLS analysis of first-batch results: effect estimates, permutation p-values, residual-bootstrap CIs, lack-of-fit decomposition (when replicates exist), and an active-factor list to drive follow-up narrowing.
- Frictionless-compatible table contracts on CSV inputs (run ledger, evidence, equipment, reagent, design, results); stdlib by default, full Frictionless validation lights up with the `[contracts]` extra.
- Curated BO/DoE registry consistency at `docs/tool-registry.json` (adapter availability, route reasons, claim level).

## What this never claims

- Optimized.
- Validated.
- Production-ready.
- Lab-proven.
- GxP-ready.
- Equivalent to a commercial DoE platform.

These statements stand unless executed result rows have been ingested with provenance and validation evidence, and even then only at the claim level the ingest provides.

## Biosafety scope

Campaigns involving high-containment work, recombinant DNA at scale, or research the operator considers dual-use should also consult the operator's institutional biosafety committee and the relevant frameworks listed in [`BIOSAFETY.md`](BIOSAFETY.md). The skill does not perform biosafety review.
