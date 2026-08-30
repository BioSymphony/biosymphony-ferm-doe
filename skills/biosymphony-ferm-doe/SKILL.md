---
name: biosymphony-ferm-doe
description: Use only for an active BioSymphony Ferm DoE campaign involving fermentation, cell-culture, upstream bioprocess, adaptive DoE, assay-readiness, or pre-experiment planning.
---

# BioSymphony Ferm DoE

BioSymphony Ferm DoE turns upstream bioprocess goals into readiness-gated, evidence-backed experiment-planning packets before the lab spends time and materials.

## Activation Boundary

Use this skill only when there is an active or requested BioSymphony Ferm DoE campaign. Do not treat it as a default behavior for unrelated coding, research, writing, or repository tasks, even when the current checkout contains this repo. A campaign means the user is asking to intake, plan, compile, validate, dispatch, review, or adapt a fermentation or upstream DoE package.

If the user is only asking about the repository, skill installation, code style, tests, docs, or generic project maintenance, answer from the repo context without invoking the campaign workflow.

## Operating Model

Resolve these environment variables at the start of an orchestrated run when they are needed:

- `FERM_DOE_REPO`: repository checkout for the campaign
- `EXTERNAL_ARTIFACT_ROOT`: external durable checkpoint and log root, when present
- `PROVIDER_BRIDGE_BIN`: remote provider bridge executable, when present

Keep the workflow portable. Deployment-specific paths belong in an adapter document or environment variables, not in the core workflow.

Compute should stay laptop-orchestrated and profile-driven. The local operator or a lightweight orchestrator should remain the dispatcher, ledger updater, and reviewer. Remote providers are execution substrates, not the campaign brain.

- Default to local stdlib execution unless the user or manifest selects another profile.
- Treat remote compute as an optional lane for container smoke tests, heavier DOE or statistics adapters, benchmark sweeps, and artifact builds that benefit from larger models or more compute.
- Keep evidence swarms, issue orchestration, status reconciliation, and campaign closeout local by default.
- Allow cloud or neocloud alternatives only as explicit worker adapters that preserve the same validation commands, artifact contract, closeout, and tracker outcome block.
- Never launch paid remote resources unless the operator explicitly asks for launch and the compute policy, budget, cleanup plan, dossier check, and contract self-check are all explicit.
- For any long local or cloud run, require a stage contract with expected outputs, timeout, done marker, progress ledger, resume command, and fail-closed behavior.
- Treat provider desired state as intent only. A `desiredStatus: RUNNING` is not evidence that the container pulled, started, or executed the workload.
- Treat worker-side provider API reachability as a preflight, not an assumption. If the worker cannot reach the provider API, it must emit `provider_handoff.json` and stop before paid mutation.
- Keep paid provider mutation centralized: workers validate and prepare; an orchestrator, bridge service, or trusted hook creates resources, verifies artifacts, deletes resources, and posts closeout.
- Private registry images require registry-auth references from a secure store or runtime injection before launch. If image pull cannot be verified, stop before creating paid resources.
- Do not silently fall back from remote to local, real execution to dry-run, full route to rescue route, or a configured worker to another agent. Record the fallback and close as degraded or partial.

Use this compute-lane filter before adding remote work:

- High ROI now: optional DOE and statistics adapters, reproducible container validation, benchmark or regression campaigns, simulation or power sweeps with declared scenarios, large-model report or workbook drafting, and artifact rendering.
- Usually local: campaign intake, manifest edits, readiness scoring, issue dispatch, evidence-swarm orchestration, status reconciliation, handoff writing, and closeout.
- Defer unless forced by a real campaign: autonomous provider-side orchestration, long idle remote agents, GUI-first DOE tooling, real-time control, LIMS or ELN integration, and private-data processing without secure references.

Choose worker model and turn budget by task class, and record both in the worker closeout:

- Low-cost or fast workers: corpus extraction, citation harvest, simple evidence rows, smoke validation, narrow file edits.
- Standard synthesis workers: audits, protocol or run-packet writing, workbook and report sections, status reconciliation, moderate code fixes.
- Frontier or deep-reasoning workers: Phase 0 scope architecture, ambiguous scientific arbitration, chimeric-design prevention, categorical aliasing math, final design adjudication, format-convention research when industry expectations matter.

Do not silently inherit a parent model for dispatched workers. If a ticket needs a higher tier than its class suggests, record the reason in the ticket or closeout.

## Pre-experiment Readiness Program

Treat every campaign as a pre-experiment readiness program. Each step must leave an artifact, not just prose.

1. Clarify objective and stop policy: `campaign_manifest.json`, `campaign_manifest.draft.json`, or `references/templates/campaign-contract.md`.
2. Rescue and score historical data: `historical_run_ledger.csv`, `data_trust_report.md`, or `missing_info.json`.
3. Build factor universe: `factor_universe.json`, `factor_universe.md`, or `factor_space.yaml`.
4. Check assay readiness: `assay_readiness_report.md` plus response semantics in `campaign_state.json`.
5. Check reagent and equipment feasibility: `readiness_scorecard.json`, `constraints.tsv`, and feasibility gates.
6. Run design tournament: `candidate_designs.json`, `design_comparison.json`, and `design_adjudication.json`.
7. Compile a review-ready planning packet: `ferm-doe-dossier/`, `experimental_setup.json`, `experimental_setup.md`, `horizontal_doe.csv`, `horizontal_doe.json`, `run-sheet.tsv`, `sampling_schedule.csv`, and `result_capture_template.csv`.
8. Pre-register follow-up decision rules: `wave_2_decision_rules.json`, `wave_2_decision_rules.md`, and result-ingestion outputs.
9. After first-batch results arrive, run adaptive follow-up planning: `adaptive_wave2_plan.json`, `result_ingestion_report.json`, `assay_power_results.json`, `negative_result_memory.json`, `locked_prior_runs.csv`, and `augment_design.csv`.
10. Capture self-learning and hiccups: `learning_ledger.csv`, `hiccup_review.md`, `artifacts/<campaign>/AGENTS.md`, and dated notes when lessons should affect future campaigns.

For DOE work, set `design_policy.design_intent` when the user's goal is clear. Supported intent labels are `screening`, `space_filling_scout`, `rsm_fit`, `mixture`, `custom_constrained`, `augmentation`, `confirmatory`, and `user_supplied_design`. The engine validates and labels the chosen path instead of forcing all campaigns into one DOE family.

For follow-up planning work, use `ferm-doe plan-wave2` rather than manually narrowing from a result table. The `wave2` name is a checkpoint label, not a predetermined experiment. The loop must validate result joins, ignore excluded, QC-failed, and low-trust rows, check response-level `assay_power_policy`, preserve arm-scoped negative memory, and block `scale_or_downscale` unless bridge eligibility passes. The output is a `planned_wave2_design`. Do not call it optimized, validated, or transferred.

For self-learning DOE work, treat hiccups as first-class campaign memory. Use `learning_ledger.csv` and `hiccup_review.md` to record join failures, QC exclusions, low-trust rows, assay-power gaps, bridge blocks, chimeric arm rows, operator overrides, and pause or stop decisions. Promote broadly reusable lessons to dated notes that can affect future campaigns. Learning entries can drive manifest patches and future designs. They are not validation evidence by themselves.

## Evidence Execution Boundary

Keep live literature and web search out of the core Python engine. The engine stays deterministic, testable, offline-capable, and provenance-driven.

When outside evidence is needed, use Scientific Swarm or the optional evidence executor issue pack at `references/packs/issue-packs/evidence-executor-v0/`. Research workers can search PubMed, bioRxiv, Scholar or manual citation sources, vendor protocols, equipment manuals, assay methods, and sanitized prior-run summaries. Their deliverable is `evidence_table.csv` rows plus a source ledger and search log.

Evidence rows must follow `references/templates/evidence-table.template.csv` and should use `references/templates/evidence-executor-agent-brief.md` as the worker brief. Rows must carry source refs, confidence, source trust, review status, contradiction groups, caveats, and decision impact. Public or reference evidence must not be claimed as target-specific experimental proof. The DOE engine ingests those rows locally and lets factor-universe, assumption-attack, observability, control-row, and tournament scoring decide how much influence they deserve.

For synthesis-heavy campaigns, build one cumulative evidence dossier instead of isolated worker reports. Prefer per-corpus fan-out, a per-ticket integrator, and a final single-writer harvester that owns:

- `artifacts/<campaign>/_swarm/CITATIONS.json` for deduplicated citations with ticket and topic attribution
- `artifacts/<campaign>/_swarm/NOTES.md` for cross-ticket findings and caveats
- `artifacts/<campaign>/_swarm/SOURCES.bib` for bibliography export

Do not let corpus workers or ticket integrators concurrently edit `_swarm/` shared files. They write disjoint corpus or ticket outputs, and the harvester merges them. For format-heavy deliverables such as HTML dossiers, run packets, scale-up packages, or batch-record templates, dispatch a small research swarm first when industry convention matters.

## Validated Patterns and Traps

These patterns came out of real campaigns and apply to most fermentation DoE work. Each pattern has a mechanical rule that operationalizes it as an artifact or check.

### Simulator dose-response gaps: run a literature check before sealing

A simulator that lacks a published dose-response term for a load-bearing factor can produce Pareto winners that are simulator artifacts rather than physically meaningful designs. A common example: when a synergy term is gated on a co-substrate being present, a winner found at the co-substrate level of zero may carry excess of the inducer at pure cost with no titer benefit, contradicting decades of literature on that system.

Mechanical rule. Declare `simulator.fidelity_level` in the campaign manifest with one of `linear_placeholder`, `dose_response_v2`, or `surrogate_on_observed`. If `linear_placeholder`, the simulator may not rank Pareto winners across factor levels, only across recipe families, and a completed `references/templates/PARETO_LIT_CHECK.template.md` is a mandatory sealing-gate artifact. Section 2 of that template halts sealing when a load-bearing factor has no published dose-response term in the simulator. Check K equals 3 or more winners so cross-winner concordance is computable.

Pointers: `references/docs/SIMULATOR_V2_SPEC.md` (spec only status), `references/templates/PARETO_LIT_CHECK.template.md`.

### Cost-model honesty: never report a bare cost-per-mg number

A cost-per-mg figure carries different meaning at different stack layers. Material at bulk prices excluding the inducer can be three to six orders of magnitude away from a fully-loaded shake-flask COGS estimate, which is itself far from a CMO process-scale benchmark. Reporting any one of those numbers in isolation creates a target the design cannot defend.

Mechanical rule. Every cost-per-mg claim that ships in a handoff packet, dossier, or lab brief must stack five layers explicitly: simulator media-only at bulk, then plus inducer at bulk, then fully-loaded shake-flask COGS including materials, labor, QC, and depreciation, then an industry CMO process-scale benchmark, and finally an honest range that spans the four. Call out inducer dominance when the recipe specifies inducer at induction-relevant concentrations. Use `references/templates/cost_stack.template.md` as the authoring template.

Pointers: `references/docs/COST_MODEL_REALISM_CHECK.md`, `references/templates/cost_stack.template.md`.

### Flask scale-down oxygen trap: entry conditions for flask-based screens

A 250 mL unbaffled Erlenmeyer at typical shaker conditions reaches a kLa of 15 to 30 per hour, giving an OTR ceiling around 5 to 10 mmol O2 per liter per hour. *E. coli* BL21 at a growth rate of 0.3 per hour oxygen-limits at DCW 1.5 to 3 g/L, well before titer signals would meaningfully separate media recipes. The ranking that comes out of such a flask campaign reflects which recipes happen to slow growth enough to stay under the OTR ceiling, not which support best product expression. A larger bioreactor at kLa 400 per hour will disagree with the flask ranking, and the apparent translation failure will be misdiagnosed as a media-formulation problem.

Mechanical rule. Any flask-based screening campaign must produce a filled `references/templates/scale_bridge_entry_conditions.template.md` before claiming the flask rankings are transferable to a bioreactor. The entry conditions for transferability are a baffled 500 mL flask, a sulfite-method or gassing-out kLa calibration of the actual shaker measured at 100 per hour or above, and a PreSens DO patch confirming DO at 30 percent or above on at least one flask of every batch. None of these is the simulator's job. They are entry conditions for the simulator's predictions to mean anything.

Pointers: `references/docs/SCALE_BRIDGE_METHODOLOGY.md`, `references/templates/scale_bridge_entry_conditions.template.md`.

### BoFire constraint-strategy compatibility: known traps

The repository's BoFire 0.3.1 and May 2026 main-branch checks found two compatibility traps. NChooseK plus `SoboStrategy` did not return from `ask()`, and `MultiFidelityVarianceBasedStrategy` rejected non-box constraints. Upstream issues #450 and #761 are now closed, but later tagged releases have not been evaluated against this adapter. Treat the findings as compatibility boundaries for the supported `bofire>=0.3.1,<0.4` route, not as claims about current upstream behavior.

Mechanical rule. Consult `references/docs/BOFIRE_CONSTRAINT_PATTERNS.md` before choosing a BoFire strategy. The primary BoFire adapter remains on the verified 0.3.x range. For a separate Python 3.11 or newer NChooseK DoE evaluation, `adaptive-nchoosek-doe` pins BoFire 0.4.1; that lane is unverified and does not widen the primary adapter claim. Keep row-level cardinality checks. For NChooseK BO, use the in-repo ENTMOOT or OMLT adapter. The ENTMOOT adapter closes the three integration risks documented in its design note by emitting `min_count`, using HiGHS, and handling repeated proposals. For multi-fidelity constraints, keep the parallel D-optimal arm fallback until a later BoFire release is evaluated and record `fidelity_path: fallback_parallel_arms`.

Pointers: `references/docs/BOFIRE_CONSTRAINT_PATTERNS.md`, `references/docs/ENTMOOT_SWAP_DESIGN.md`.

### How to evolve this section

As future campaigns surface new patterns, add them here. Each new entry should follow the same shape: a one-paragraph context, a mechanical rule that names the artifact or check that enforces it, and pointers to the canonical detail documents and templates that operationalize the rule.

## Default Intake And Interview

Use a short intake pass when the user starts from a messy ask, partial shake-flask data, scattered files, or an undefined goal. Do not turn this into a long questionnaire.

Intake rule:

1. Read existing manifests, ledgers, recipes, inventories, equipment notes, and user-provided text before asking questions.
2. Summarize what is already known in five bullets or fewer.
3. Ask at most three high-leverage operator questions only for items that change the campaign shape.
4. Offer a clear skip path: "I can proceed with assumptions and mark missing fields as blockers, warnings, or assumed-for-readiness."
5. If the user skips, proceed and record assumptions in `missing_info.json`, `campaign_state.json`, and the dossier.

Prefer these question categories, in this order:

- Objective and response: what is being optimized, measured, and considered success.
- System and format: organism or cell type, current scale, target scale, and run duration.
- Assay and product semantics: extracellular, intracellular, pellet-associated, volatile, activity, quality, titer, productivity, or yield.
- Available measurements: online probes, offgas, biomass cadence, endpoint assays, sampling limits.
- Controllable factors: allowed to vary, fixed controls, forbidden regions, and cost or time limits.
- Inputs in hand: recipe, limited run ledger, reagent inventory, equipment capacity, prior protocols, and evidence tables.
- Compute and orchestration: local stdlib, optional local extras, optional remote provider smoke, or an explicit cloud adapter.

Expected intake artifacts:

- `operator_intake.md` or filled `references/templates/operator-intake.md`
- `campaign_manifest.draft.json` when enough structure exists
- `missing_operator_items.json` with `blocker`, `warning`, or `assumed_for_wave0`
- `research_tasks.md` or Scientific Swarm evidence-lane issues when literature or context is needed
- `evidence_table.csv` from `references/packs/issue-packs/evidence-executor-v0/` when external evidence collection is part of the campaign

Do not ask for private strain details, confidential media formulations, unpublished sequences, API keys, or raw customer process records. Ask for sanitized summaries or secure-store references instead.

## Response And Assay Semantics

Separate measured assay responses from derived decision metrics before tightening a manifest. Do not copy one assay method across every response just to satisfy a schema warning.

Use this response split:

- Assayed product responses: titer, product-per-biomass, productivity when computed from assayed titer, quality, purity, activity, intracellular or soluble or extracellular product signals. These need `assay_required: true`, assay method, sample fraction, calibration or standard curve, and matrix-effects or extraction-recovery policy.
- Assayed process or byproduct responses: acetate, residual substrate, metabolite or byproduct, biomass when measured offline. These may need a different assay than the product response and a different sample fraction.
- Derived metrics: cost per liter, projected cost at scale, run duration, reactor occupancy, productivity indices derived from existing measured responses, and scheduling burden. These should use `assay_required: false`, `measurement_type: calculated|clock|schedule|derived`, and `sample_fraction: not_applicable`.

For every response, record `class`, `measurement_type`, `assay_required`, `assay_method`, `sample_fraction`, and either assay validation fields or derivation fields. Product and byproduct assays should name calibration or standard-curve basis and matrix-effects policy. Cost and time should point to `cost_projection.csv` or `.json`, recipe math, bulk-pricing assumptions, phase schedule, or harvest timestamp instead of an assay.

If a worker sees SEC-HPLC, LC, GC, enzymatic assay, ELISA, or another physical-execution method assigned to a cost, duration, schedule, or other non-assay metric, it must treat that as a manifest defect. The right fix is to reclassify the response, not to invent a calibration curve.

## Coupled Scale-Up And Downscale Campaigns

When the user asks for both a controlled bioreactor route and a cheaper higher-throughput downscale route, treat it as a coupled multi-arm pre-experiment campaign. Do not flatten plate, flask, and bioreactor work into one naive DOE table.

For a plate or downscale plus 2 L fed-batch request, select or explicitly request these modes when applicable:

- `batch-to-fedbatch-production` for growth, induction or switch, feed, and harvest policy.
- `bioreactor-to-plate-downscale` for plate or deep-well representativeness, oxygen, evaporation, edge effects, fill volume, mixing, and bolus timing.
- `cost-productivity-minimizer` for titer, productivity, run duration, sampling burden, and media or control cost tradeoffs.
- `assay-product-class-planner` for response semantics and assay comparability across whole broth, pellet, supernatant, volatile, activity, quality, or hydrophobic product classes.
- `bioreactor-scale-up` when the user cares about future larger-scale cost or transfer beyond the first benchtop reactor.
- `plate-to-flask` when plate winners need flask confirmation before reactor use.

Campaign arms are a first-class engine and dossier contract requirement for coupled campaigns. Each arm must keep its own purpose, format, run budget, factor space, constraints, response semantics, assay policy, execution capabilities, and bridge role. If the active branch cannot fully execute first-class `campaign_arms`, use linked single-arm manifests as an explicit degraded fallback, write a bridge artifact, and mark the limitation in the dossier instead of pretending the coupling is automatic.

Before handing off any coupled-arm design, verify that the generated rows are physically executable per arm. Current engine or fixture paths may collapse plate-only and bioreactor-only factors into a chimeric table if arm metadata is dropped. If that happens, produce per-arm projections, document the projection method, and mark the original cross-arm table as non-executable.

For categorical design diagnostics, do not use raw string-equality match rate as a correlation or aliasing check. It fails for disjoint categorical label sets. Use contingency-table association such as Cramer's V, and flag pairs above the campaign threshold, commonly 0.8. If categorical factors are perfectly associated, treat them as a confounded operating-mode bundle unless the design is amended before execution.

Check continuous-factor variance after projection. A factor held constant across experimental rows cannot teach its main effect or cost or productivity tradeoff, even if controls vary. Preserve this as a design limitation instead of smoothing it out of the handoff.

Expected coupled-arm artifacts:

- `campaign_arms.json` or `campaign_arms.md` naming each arm, purpose, run budget, format, response semantics, and constraints.
- `experimental_setup.json` and `experimental_setup.md` naming the intended scale-up or downscale target, vessel or format, working volume, duration, run budget, response contract, and claim boundary.
- `horizontal_doe.csv` and `horizontal_doe.json` as the row-wise planning surface for new planned conditions and optimization goals across arms. Per-arm executable CSVs remain authoritative when arms are physically incompatible.
- `plate_arm_manifest.json` for high-throughput batch or batch-plus-bolus scouting.
- `bioreactor_arm_manifest.json` for controlled fed-batch DOE.
- `arm_bridge_policy.md` describing which plate signals can become bioreactor priors and which cannot.
- `pareto_objectives.json` listing titer, productivity, cost per liter, projected larger-scale cost plausibility, run duration, sampling burden, and assay throughput weights.
- `cost_projection.csv` or `cost_projection.json` with reagent, media, and control assumptions, current-scale estimate, and future larger-scale plausibility labels.
- `wave_result_handoff.md` describing how completed plate or flask data will be ingested before rerunning the bioreactor tournament.
- `per_arm_projection_summary.json` with source design path, selected design ID, tournament verdict, per-arm row counts, and vessel-cap checks.
- `categorical_aliasing_report.json` using Cramer's V or another named contingency-table association metric.
- `factor_variance_report.json` or equivalent table showing constant or near-constant factors after projection.

Do not claim "optimized" or "validated" from the coupled campaign unless executed result rows join back to the declared runs and confirmatory validation exists. Before physical work, the correct claim level is a planned multi-arm campaign with explicit assumptions, bridge rules, and first-wave designs.

For Excel or workbook deliverables, distinguish planning templates from filled execution records. Include empty execution templates when they are designed for the specific DoE: pre-execution checklists, deviation-log shells, severity matrices, operator signoff blocks, lot-tracking fields, CPP verification fields, sampling actual or initial columns, and IPC alert or action thresholds. Do not pre-fill operators, real timestamps, lot numbers, deviations, analytical results, ANOVA outputs, Cp or Cpk, or any other actuals from a run that has not happened.

## Reference DOE Posture

Reference DOE software (JMP, Design-Expert, Modde, others) is well-suited to designing experiments once the problem is already shaped. BioSymphony Ferm DoE focuses on the upstream and surrounding work: framing the biological question, checking assay readiness, turning lab reality into constraints, producing executable packets, and deciding when not to run.

Use local DOE generation and diagnostics as a planning fast path. Keep all statistical claims labeled as exact, adapter-backed, approximate, or heuristic. When exact commercial-grade optimality, regulatory statistician review, or site-standard software files are required, export clean tables and assumptions instead of treating local approximations as equivalent.

Add optional DOE adapters only when they remove real decision risk or unblock a concrete workflow. Prioritize them in this order:

1. Import or export bridges for commercial DOE or statistician review: factors, responses, constraints, run table, blocks, randomization, assumptions, and non-parity notes.
2. Diagnostics that catch bad experiments before execution: rank, estimability, aliasing, categorical association, constant factors, replicate or control adequacy, power and noise limits, and prediction-variance labels.
3. Constrained custom-design or augmentation adapters that produce auditable candidate rows under real run budgets and fixed controls.
4. Exact or adapter-backed screening, RSM, or mixture methods only when local labels are too weak for the campaign decision.
5. Bayesian or adaptive adapters after result ingestion, trust scoring, and stopping rules are already working.

Avoid adding a DOE method just because a reference package has it. Add it only if there is a validator, proof artifact, export path, benchmark example, or decision it changes.

## Required Checks

Before dispatching a tracker issue body or accepting a campaign manifest, validate it. The wrapper accepts full manifests, compact demo directories or manifests, task request JSON, sidecar JSON, and tracker-issue Markdown:

```bash
python3 scripts/preflight_check.py path/to/file-or-dir
```

To compile, score, design, and validate a local campaign without remote dependencies:

```bash
python3 scripts/compile_campaign_state.py \
  --manifest examples/xylanase-wxz1-2012/campaign_manifest.json \
  --out .runtime/xylanase-state

python3 scripts/score_campaign_readiness.py \
  --manifest examples/xylanase-wxz1-2012/campaign_manifest.json \
  --out .runtime/xylanase-readiness.json

python3 scripts/propose_wave1_design.py \
  --manifest examples/xylanase-wxz1-2012/campaign_manifest.json \
  --out .runtime/xylanase-designs

python3 scripts/compile_ferm_doe_dossier.py \
  --manifest examples/xylanase-wxz1-2012/campaign_manifest.json \
  --out ferm-doe-dossier

python3 scripts/dossier_check.py ferm-doe-dossier

python3 scripts/ferm_doe_contract_self_check.py ferm-doe-dossier

python3 scripts/plan_wave2.py \
  --campaign-state ferm-doe-dossier/campaign_state.json \
  --results path/to/wave1_results.csv \
  --selected-design ferm-doe-dossier/selected_wave_1_design.csv \
  --out adaptive-wave2-plan

python3 scripts/assay_power.py \
  --campaign-state ferm-doe-dossier/campaign_state.json \
  --out assay-power-check

python3 scripts/sidecar_check.py \
  references/templates/sidecar-compute-policy.json \
  references/templates/sidecar-provider-handoff.json
```

After applying real campaign manifest patches, rerun readiness or campaign scoring against the patched manifest and keep the machine-readable output. Schema-only checks are not enough; populated nested JSON can expose engine bugs that null or empty tests miss. Treat older gate assessments as snapshots that may be superseded by later readiness JSON, final checkpoints, or committed manifest state.

When a later run supersedes older status files, reconcile the campaign state. Update or append a clear supersession note in `_status/CAMPAIGN_STATUS.md`, `_status/OPEN_RISKS.md`, `_status/EVIDENCE_INDEX.md`, and `artifacts/<campaign>/AGENTS.md` as applicable. If old ticket artifacts remain intentionally unchanged, point to the newer readiness JSON or checkpoint that overrides them.

When authoring issue briefs or manifest patches that use engine-validated values, inspect the engine enums first instead of guessing semantically:

```bash
rg "RESPONSE_CLASSES|SAMPLE_FRACTIONS|measurement_type|assay_required" scripts
```

The engine can materialize `factor_space.yaml|json|csv` and `constraint_set.yaml|json|csv` entries from `inputs[]`. Inline manifest factors, responses, and constraints win when IDs conflict, and conflicts are recorded in `input_conflicts`. Multi-arm factor spaces are preserved; set `design_policy.active_factor_space` before design generation when multiple arms are present, or keep linked arm-specific manifests and an explicit bridge artifact.

For optional remote provider execution, the launch bundle must also validate:

- `provider_preflight`: image-pull preflight, actual container-state check, and desired-status-as-intent rule.
- `stage_contract`: `stage_id`, exact `executable_proof` commands, `expected_outputs`, `timeout_minutes`, `progress_ledger`, `done_marker`, `resume_command`, `fail_closed`.
- `image_pull`: image visibility, digest pinning or accepted dev-smoke risk, and secure registry auth for private images.
- `fallback_policy`: no silent fallback and degraded status for any fallback path.
- `provider_handoff_policy`: workers validate and prepare; orchestrator-side mutation is required when worker API reachability fails.

The orchestrator handoff is emitted as `provider_handoff.json` and validates against `references/templates/sidecar-provider-handoff.json`. It must not contain provider secrets.

## Reference Map

- Product brief: `references/docs/product-brief.md`
- Superpowers: `references/docs/superpowers.md`
- Data model: `references/docs/data-model.md`
- Engine implementation: `references/docs/engine-implementation.md`
- Dossier generation: `references/docs/dossier-generation.md`
- BoFire positioning: `references/docs/BOFIRE_POSITIONING.md`
- BoFire constraint patterns: `references/docs/BOFIRE_CONSTRAINT_PATTERNS.md`
- ENTMOOT swap design: `references/docs/ENTMOOT_SWAP_DESIGN.md`
- Backend evaluation findings: `references/docs/BACKEND_EVAL_FINDINGS.md`
- Adapter design notes: `references/docs/ADAPTER_DESIGN_NOTES.md`
- Scale-bridge methodology: `references/docs/SCALE_BRIDGE_METHODOLOGY.md`
- Cost-model realism check: `references/docs/COST_MODEL_REALISM_CHECK.md`
- Reference DOE fast path: `references/docs/reference-doe-fast-path.md`
- High-ROI DOE parity strategy: `references/docs/high-roi-doe-parity-strategy.md`
- Tool registry: `references/docs/TOOL_REGISTRY.md` (machine-readable at `references/docs/tool-registry.json`)
- Sidecar architecture: `references/docs/sidecar-architecture.md`
- Starter study catalog: `references/docs/starter-study-catalog.md`
- Intake template: `references/templates/operator-intake.md`
- Campaign contract template: `references/templates/campaign-contract.md` for readiness capture
- Evidence table template: `references/templates/evidence-table.template.csv`
- Evidence executor worker brief: `references/templates/evidence-executor-agent-brief.md`
- Cost stack template: `references/templates/cost_stack.template.md`
- Pareto literature check template: `references/templates/PARETO_LIT_CHECK.template.md`
- Scale-bridge entry conditions template: `references/templates/scale_bridge_entry_conditions.template.md`
- Sidecar compute policy: `references/templates/sidecar-compute-policy.json`
- Sidecar provider handoff: `references/templates/sidecar-provider-handoff.json`
- Adaptive follow-up wrapper: `scripts/plan_wave2.py`
- Assay power wrapper: `scripts/assay_power.py`
- Fermentation readiness issue pack: `references/packs/issue-packs/fermentation-readiness-v0/`
- Scientific Swarm issue pack: `references/packs/issue-packs/scientific-swarm-v0/`
- Evidence executor issue pack: `references/packs/issue-packs/evidence-executor-v0/`
- Reference DOE utility issue pack: `references/packs/issue-packs/doe-parity-v0/`
- High-ROI DOE parity upgrade issue pack: `references/packs/issue-packs/doe-parity-v1/`
- Adaptive follow-up plus assay power issue pack: `references/packs/issue-packs/adaptive-wave2-assay-power-v0/`
- Self-learning DOE runbook: `references/docs/self-learning-doe-runbook.md`
- DOE learning ledger template: `references/templates/doe-learning-ledger.template.csv`
- DOE hiccup report template: `references/templates/doe-hiccup-report.template.md`

Read only the relevant reference for the current task.

## Closeout Standard

Every worker should finish with:

- validation commands run exactly as written
- exact executable proof commands run before long or remote execution
- artifact paths recorded
- actual provider or container state recorded for remote runs
- `provider_handoff.json` recorded when remote mutation happens outside the worker
- `stage-progress.jsonl` and done or partial marker recorded for long runs
- joined contract self-check status recorded
- source data, transformed data, and synthetic data clearly separated
- fallback events recorded as degraded or partial, never hidden
- caveats for assay readiness, factor feasibility, historical-data trust, and model-based recommendations
- claim level stated without implying optimized, validated, or production-ready conditions unless executed result evidence joins to the planned runs
- installed package version recorded in the dossier (`NOTES.md` or the per-corpus EVIDENCE row) when a campaign exercises an optional adapter (BoFire, ENTMOOT, OMLT, TabPFN, BoTorch) so claims are version-anchored; the tool-registry carries `last_checked` baselines per adapter and `references/docs/BACKEND_EVAL_FINDINGS.md` carries the as-of date for each verified backend, both of which can drift between snapshots

Every campaign closeout should also produce a campaign-local handoff file at `artifacts/<campaign>/AGENTS.md`. Treat this as the canonical resume path for future agents. It should link, at minimum:

- `_status/` files and any final machine-readable readiness output
- `_runbook/` or workbook sources and generated workbook artifacts
- `_report/` or human-readable dossier artifacts
- `_swarm/` citations, notes, and bibliography
- external durable checkpoints and worker logs when present
- durable memory entries or postmortem logs
- branch and commit state, resume commands, and do or don't instructions
- unresolved risks, stale-status caveats, and claim-level boundaries
- status reconciliation notes naming any superseded status snapshots
- portability notes for private adapters that need review before public release

If the campaign generated important learnings, also record a dated note that future agents can find from `artifacts/<campaign>/AGENTS.md`. Do not hide `no_accepted_design`, aliasing, constant-factor, synthetic-ledger, assay-readiness, equipment, procurement, or study-director caveats to make the dossier look cleaner. The caveats are part of the scientific ledger.

## Safety

Do not store private process records, confidential strain details, private sequences, customer batch records, API keys, or tokens in this repo or in any tracker. Use sanitized ledgers and secure-store references.
