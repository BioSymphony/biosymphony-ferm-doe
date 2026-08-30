# Product Brief

## Name

BioSymphony Ferm DoE

## Thesis

The highest ROI in fermentation planning is upstream of the physical experiment: deciding whether the campaign is ready, what the lab can actually run, which data can be trusted, which hypotheses are plausible, and which design will teach the most per run.

## Product Unit

The product unit is a campaign dossier:

```text
ferm-doe-dossier/
  campaign_contract.md
  historical_run_ledger.csv
  data_trust_report.md
  factor_space.yaml
  bottleneck_hypotheses.md
  assay_readiness_report.md
  feasibility_report.md
  design_candidates/
  selected_wave_1_design.csv
  factors.tsv
  constraints.tsv
  design-matrix.tsv
  randomization-seed.txt
  run_sheet.md
  run-sheet.tsv
  plate_or_reactor_map.csv
  reagent_plan.md
  sampling_schedule.md
  result_capture_template.csv
  results-ledger.tsv
  model-report.json
  campaign_maturity.json
  claim_audit.json
  contract_self_check.json
  wave_2_decision_rules.md
  provenance.md
```

## Readiness Verdict

Every campaign should produce an explicit status before physical setup:

- `GREEN`: meets the declared readiness checks; separate execution review still applies
- `YELLOW`: planning may continue with explicit caveats
- `RED`: do not run yet; fix assay, data, constraints, objective, or safety blockers

## High-ROI Modules

1. Campaign contract compiler
2. Historical data rescue and trust scoring
3. Factor universe builder
4. Assay and measurement readiness gate
5. Constraint and feasibility solver
6. Bottleneck hypothesis engine
7. Design tournament
8. Pre-registered follow-up decision rules
9. Experiment packet compiler
10. Negative-result memory
11. Joined contract self-check and claim audit

## V1 Wedge

Given a fermentation goal, optional historical CSVs, approximate reagent inventory, and equipment capacity, generate:

- readiness verdict
- cleaned run ledger
- factor-space draft
- assay readiness checklist
- feasibility report
- selected first-batch design stub
- planning packet outline for lab review
- optional tracker issues for follow-up work
