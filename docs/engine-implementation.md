# Engine Implementation

BioSymphony Ferm DoE now has a local engine baseline under `src/biosymphony_ferm_doe/`.

## What Exists

- Campaign state compiler: manifest plus inputs and constraints become `campaign_state.json`, `missing_info.json`, selected workflow modes, assumptions, and precheck status.
- Versioned public contracts for campaign state, candidate designs, readiness scorecards, design adjudication, dossier manifests, and follow-up result ingestion.
- Readiness scoring: contract, data trust, factors, response semantics, assay readiness, feasibility, cost/time, workflow-mode checks, and mode-transfer gates.
- DOE candidate generation: deterministic full/fractional factorial, Plackett-Burman-like, definitive-screening-like, RSM, CCD-like, Box-Behnken-like, mixture, mixture-process, LHS, Halton, Sobol-like, greedy custom-optimal, low-cost scouting, and robustness candidates.
- Constraint validation: numeric bounds, categorical levels, mixture sums, fixed controls, linear constraints, forbidden combinations, and run exclusions.
- Model matrix diagnostics: rank, estimability, alias/correlation summary, D/I/A/G efficiency labels, FDS approximation, prediction-variance summary, replicate/control counts, center points, and constraint violations.
- Design tournament: scores candidate designs on statistical quality, feasibility, assay readiness, response semantics, mode transfer, cost/time, robustness, and follow-up value.
- Full dossier compiler: writes a review-ready planning `ferm-doe-dossier/` with design candidates, design comparison, reference DOE parity report, selected first-batch design, reference DOE-style export, planning packet for lab review, result template, follow-up rules, provenance, and verdict.
- Contract self-check: writes standard proof artifacts (`factors.tsv`, `constraints.tsv`, `design-matrix.tsv`, `run-sheet.tsv`, `results-ledger.tsv`, `model-report.json`), campaign maturity, and a claim audit that blocks unsupported optimized/validated/production-ready claims.
- Dry-run issue generation: creates local Markdown issue bodies for fermentation readiness, reference DOE parity, or both without calling an external tracker.
- Result ingestion: reads completed run data, preserves negative-result memory, emits a local augment-design recommendation, and recommends confirm, narrow, expand, pause, stop, or scale/downscale.
- Optional reference DOE utilities: custom-optimal row selection, augment-design row generation, profiler, simulation/power proxy, reference DOE CSV import/export, synthetic benchmark harness, and dependency checks.
- Optional Scientific Swarm: local dry-run evidence lanes, local evidence-table ingestion, provenance/quality scoring, evidence-enriched factor universe, assumption attack, observability plan, budget-aware control-row augmentation, swarm-to-tournament scoring, and a tracker-ready issue graph.
- Optional Evidence Executor: bounded research-worker issue pack for PubMed, bioRxiv, Scholar/manual-citation, vendor, protocol, and sanitized prior-run evidence extraction into `evidence_table.csv`.

## Local Commands

```bash
python3 skills/biosymphony-ferm-doe/scripts/compile_campaign_state.py \
  --manifest examples/xylanase-wxz1-2012/campaign_manifest.json \
  --out .runtime/xylanase-state

python3 skills/biosymphony-ferm-doe/scripts/score_campaign_readiness.py \
  --manifest examples/xylanase-wxz1-2012/campaign_manifest.json \
  --out .runtime/xylanase-readiness.json

python3 skills/biosymphony-ferm-doe/scripts/propose_wave1_design.py \
  --manifest examples/xylanase-wxz1-2012/campaign_manifest.json \
  --out .runtime/xylanase-designs

python3 skills/biosymphony-ferm-doe/scripts/compile_ferm_doe_dossier.py \
  --manifest examples/xylanase-wxz1-2012/campaign_manifest.json \
  --out ferm-doe-dossier

python3 skills/biosymphony-ferm-doe/scripts/dossier_check.py ferm-doe-dossier

python3 skills/biosymphony-ferm-doe/scripts/ferm_doe_contract_self_check.py ferm-doe-dossier

ferm-doe engine compile-state \
  --manifest examples/reference-doe-custom-design/campaign_manifest.json \
  --out .runtime/doe-state

ferm-doe engine propose-design \
  --manifest examples/reference-doe-custom-design/campaign_manifest.json \
  --out .runtime/doe-designs \
  --run-budget 14

ferm-doe engine compare-designs \
  --manifest examples/reference-doe-custom-design/campaign_manifest.json \
  --out .runtime/doe-compare \
  --run-budget 14

ferm-doe engine compile-dossier \
  --manifest examples/yeast-isoprenoid-2l-fedbatch/campaign_manifest.json \
  --out .runtime/yeast-isoprenoid-dossier \
  --run-budget 16

ferm-doe engine contract-self-check .runtime/yeast-isoprenoid-dossier

ferm-doe engine utility custom-optimal \
  --manifest examples/reference-doe-custom-design/campaign_manifest.json \
  --out .runtime/custom-optimal \
  --run-budget 12 \
  --criterion d

ferm-doe engine utility benchmark-doe \
  --manifest examples/reference-doe-custom-design/campaign_manifest.json \
  --out .runtime/doe-benchmark

ferm-doe engine compile-swarm-plan \
  --manifest examples/yeast-isoprenoid-2l-fedbatch/campaign_manifest.json \
  --out .runtime/yeast-scientific-swarm

ferm-doe engine compile-swarm-plan \
  --manifest examples/yeast-isoprenoid-2l-fedbatch/campaign_manifest.json \
  --out .runtime/yeast-scientific-swarm-with-evidence \
  --evidence-table path/to/evidence.csv
```

Swarm-enabled manifests can also set:

```json
{
  "swarm_policy": {
    "enabled": true,
    "evidence_tables": ["inputs/evidence.csv"],
    "apply_factor_universe_to_design": true,
    "use_swarm_for_tournament": true,
    "control_row_augmentation": true,
    "control_row_max_fraction": 0.35,
    "evidence_quality_minimum": 0.7
  }
}
```

## Current Limits

The engine is still intentionally stdlib-first. Several DOE families are exact local constructions, while Plackett-Burman, DSD, CCD, Box-Behnken, Sobol-like, profiler models, simulation power, and optimality metrics are labeled approximate or heuristic when not backed by an optional adapter. Optional utilities report missing extras and fall back to stdlib instead of failing. Scientific Swarm evidence collection is optional: an evidence-executor pack can collect source material, while the core engine deterministically ingests local evidence rows with provenance, confidence, contradictions, and decision impact.
