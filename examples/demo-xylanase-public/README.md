# Demo: Public Xylanase Fermentation Planning

This directory holds the first public-safe BioSymphony Ferm DoE demo campaign.

Goal: show the planning workflow on an enzyme-production fermentation example without private process data.

Scope:

- synthetic historical run ledger
- public-source and synthetic evidence table
- measurement-readiness checks
- factor and constraint table
- readiness verdict
- first-batch design stub
- run-packet handoff

Non-goals:

- no private strain details
- no unpublished sequences
- no confidential media formulations
- no physical execution claims
- no production-scale validation claims

The demo may intentionally finish `YELLOW` or `RED` if assay, data, or feasibility caveats remain. That is part of the point: BioSymphony should prevent bad experiments, not only format polished plans.

Current verdict: `YELLOW`.

Run:

```bash
PYTHONPATH=src python3 -m biosymphony_ferm_doe.cli validate examples/demo-xylanase-public
```

## A note on `doe.family`

This demo declares `doe.family: custom_constrained` so the four-row first-batch design passes the validator without firing a min-runs warning. That is a deliberate hygiene choice for the canonical demo.

If you want to see the validator's DoE guidance fire, change `family` to `definitive_screening` in `campaign_manifest.json`. The validator will then warn that `n_runs (4)` is below the family minimum (`2k+1 = 7` for `k = 3`). That warning is exactly what a long-running agent should see when its design is undersized, and is by design *not* an error, so the manifest still validates to YELLOW.

For a worked example of the validator's warning path, see [`examples/demo-warnings-walkthrough-public/`](../demo-warnings-walkthrough-public/).
