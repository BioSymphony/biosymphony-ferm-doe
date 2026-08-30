# BioSymphony Ferm DoE Capabilities

## Capability Index

| Capability | Public command or artifact | Demo path | Claim boundary |
|---|---|---|---|
| Readiness verdict | `ferm-doe validate <campaign> --summary` | `examples/demo-pb-screening-public/` | Planning readiness only; no physical execution approval |
| Historical data rescue | `inputs/historical_run_ledger.csv` plus validator trust-score checks | `examples/xylanase-wxz1-2012/` | Public-source or synthetic rows with provenance |
| Assay readiness gate | `ferm-doe assay-power <campaign>` | `examples/demo-pb-screening-public/` | Assay-policy adequacy for planning, not analytical-method validation |
| Factor universe and evidence | `ferm-doe engine compile-swarm-plan ...` | `examples/yeast-isoprenoid-2l-fedbatch/` | Evidence rows influence planning; they are not target-specific proof |
| Feasibility and scale bridge | `ferm-doe scale-recipe ...` and `ferm-doe bridge-qualification ...` | `examples/demo-scale-bridge-public/` | Engineering planning; bridge success requires later joined result evidence |
| Design tournament | `ferm-doe engine compare-designs ...` | `examples/reference-doe-custom-design/` | Candidate selection with explicit claim labels |
| Follow-up memory | `ferm-doe plan-wave2 ... --results ...` | `examples/demo-pb-screening-public/` | Planned next-experiment-round candidates only |
| Run packet compiler | `ferm-doe finalize ... --out run_packet.md` | `examples/demo-pb-screening-public/` | Review-ready planning packet, not a batch record |
| Agent work graph | `ferm-doe engine generate-issue-pack ...` | `examples/reference-doe-custom-design/` | Bounded work packets for humans, agents, or trackers |
| Linear handoff | `agents/linear.md` conventions | `docs/WORKFLOWS.md` | Tracker status and comments mirror local artifacts |
| Cloud wrappers | `deploy/aws-lambda/`, `deploy/modal/` | `deploy/README.md` | Stateless API endpoints around local commands |
| Reference DOE utilities | `ferm-doe engine utility check-deps` and utility subcommands | `examples/reference-doe-custom-design/` | Utility manifests label backend, caveats, and adapter status |
| Release quality gate | `make public-ready` | repo root | Reproducibility and public-switch gate before sharing |

## 1. Readiness Verdict

The system should help decide whether a campaign is ready for review and, later, physical work. It is valuable because the most expensive mistake is a well-formatted experiment that cannot answer the scientific question.

## 2. Historical Data Rescue

Old fermentation data is often scattered across spreadsheets, assay exports, plate maps, operator notes, and failed campaigns. BioSymphony Ferm DoE should normalize this into a trusted run ledger and mark every record as `trusted`, `usable_with_caveat`, `excluded`, or `unknown`.

## 3. Assay Readiness Gate

Before optimizing fermentation, verify that the readout can detect expected effects. Check dynamic range, calibration, controls, replicate noise, saturation, sample stability, dilution linearity, normalization, and turnaround time.

## 4. Factor Universe Builder

The system should propose candidate factors instead of requiring the scientist to name all of them. Categories include strain, clone, construct, media, feed, induction, pH, DO, agitation, temperature, harvest time, and assay conditions.

## 5. Bottleneck Hypothesis Engine

Generate plausible process hypotheses before designing the experiment: oxygen transfer limitation, carbon overflow, feed inhibition, pH stress, induction burden, plasmid instability, proteolysis, secretion bottleneck, folding burden, nutrient limitation, and assay artifact.

## 6. Feasibility Solver

Convert ideal experimental designs into physically feasible planning candidates. Include equipment count, working volume, run duration, sampling windows, analytics throughput, reagent quantities, blocking, randomization, staffing windows, and forbidden combinations.

## 7. Design Tournament

Dispatch multiple design lanes:

- classical DoE
- Bayesian or adaptive design
- robustness-focused design
- scale-up-aware design
- low-cost scouting design
- skeptical auditor

The adjudicator selects the most informative candidate that fits the declared constraints.

## 8. Pre-Registered Follow-Up Rules

The first batch should include a decision tree before results exist. Examples:

- if response noise dominates, pause optimization and run assay/process reproducibility checks
- if feed improves titer but harms viability, explore feed timing and oxygen transfer
- if temperature dominates, narrow temperature and induction timing
- if one condition wins but nearby space is untested, run confirmation and robustness checks
- if improvement plateaus, stop and prepare decision dossier

## 9. Experiment Packet Compiler

Generate the materials the lab needs: run sheet, plate or reactor map, reagent plan, sampling schedule, result capture template, QC flags, and ingestion contract.

## 10. Negative-Result Memory

Record failures as reusable constraints. Failed regions, assay artifacts, contamination events, toxic feeds, and impossible schedules should shape future campaigns instead of disappearing.

## 11. Agent Work Graph

Convert one manifest into issue-pack work items with inputs, artifacts, acceptance criteria, validation commands, dependencies, and risk notes. This makes the repo useful for multi-turn agents and for human review queues, not just single-shot CLI use.

## 12. Cloud-Ready Command Surface

Keep the manifest contract stable while exposing selected commands through AWS Lambda or Modal. Lightweight stdlib checks stay cheap; heavy BoTorch planning moves into a larger image with scale-to-zero behavior.

## Burden Traps

Avoid these until the campaign loop works:

- robotics first
- full LIMS/ELN integration
- monolithic app UI
- giant ontology
- autonomous purchasing
- full digital twin
- real-time PAT control
- full GxP/regulatory package
- agent swarm for trivial tasks
