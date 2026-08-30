# Glossary

Short definitions for the terms used throughout this repository. The entries are grouped by object type.

## Campaign and state

**Campaign manifest.** A single `campaign_manifest.json` file that holds the durable state of one DoE campaign. The agent and the human both read and write it across many turns. The JSON Schema is at [`../schemas/campaign_manifest.schema.json`](../schemas/campaign_manifest.schema.json).

**Campaign directory.** The folder that contains the manifest plus `inputs/`, `expected/`, and optional `dossier/` and `wave2/` subfolders. The CLI commands always take a directory, not the JSON file directly.

**Campaign ID.** Stable identifier inside the manifest. Used to map a campaign to a Linear issue, a tracker entry, or a sub-agent's task scope.

**Arm.** A self-contained set of factors, responses, and design rules within one campaign, when the campaign covers more than one scale or platform at once. The split-plot fed-batch and multi-arm scale-transfer demos both use arms. Arms live in `campaign_arms[]`.

**First batch, follow-up batch, checkpoint labels.** A "wave" is the repo's checkpoint label for a batch of runs whose results are reviewed before the next action is chosen. `wave1` means the first planned batch; `wave2` means the follow-up planning packet produced after first-batch results pass QC and assay review. It is not a predetermined campaign schedule: the next action can be confirm, narrow, expand, pause, stop, or change scale. In prose, use "first batch," "follow-up batch," "next experiment round," or "adaptive next step"; stable identifiers such as `plan-wave2` and `planned_wave2_design` remain in commands and artifacts.

## Profiles and claims

**Profile.** A named campaign shape that controls which validator checks fire as errors vs warnings. Registered profiles: `screening`, `optimization_rsm`, `mixture`, `split_plot_fed_batch`, `scale_up_bridge`, `scale_down_qualification`, `confirmation`, `sequential_augmentation`, `custom`. See [`PROFILES.md`](PROFILES.md).

**Claim level.** A provenance label on every artifact that describes how rigorously it was produced. Common values: `exact` (computed exactly), `adapter_backed` (produced by a recognized adapter), `approximate` (follows the pattern, did not compute exact properties), `heuristic` (sensible structure, statistician review advised), `planned_wave2_design` (follow-up candidates from the closed-loop planner), `bayesian_optimization_planned` (BoTorch BO output), `public_synthetic_demo` (public fixture).

**Readiness verdict.** Output of `ferm-doe validate`. Three colors: GREEN (meets the declared readiness checks; separate execution review still applies), YELLOW (planning artifact with stated caveats; physical evidence or assay readiness may still be needed), RED (structural error or missing required block). Public demos sit at YELLOW by design.

**Readiness axes.** The validator reports a per-axis state covering responses, factors, arms, scale_context, doe, decision_rules, evidence, and feasibility. `worst_axis` in the summary points at the axis driving the verdict.

**Non-claim.** An explicit statement of what an artifact does not assert. Every generated artifact carries one. See [`../NON_CLAIMS.md`](../NON_CLAIMS.md).

## Design objects

**DoE family.** A named design generator: `full_factorial`, `fractional_factorial`, `plackett_burman`, `definitive_screening`, `central_composite`, `box_behnken`, `latin_hypercube`, `scheffe_mixture`, `optimal_d`, `optimal_i`, `extreme_vertices_mixture`, `split_plot`, `custom_constrained`, `sequential_augmentation`. See [`DOE_FAMILIES.md`](DOE_FAMILIES.md) for the taxonomy, [`DOE_FAMILY_RECIPES.md`](DOE_FAMILY_RECIPES.md) for the swap recipe.

**Hard-to-change factor.** A factor that is expensive to change run-to-run because it cascades through the controller or the equipment. Temperature setpoint, DO setpoint, vessel choice. Annotated with `hard_to_change: true` and handled by the `split_plot` family.

**Whole plot / sub-plot.** In a split-plot design, the whole plot is the block defined by hard-to-change factors; sub-plots vary the easy-to-change factors inside that block. The design CSV carries a `whole_plot_id` column so the run order honors the structure.

**NChooseK constraint.** Cardinality constraint: out of `N` candidate ingredients or factor levels, a declared minimum and maximum number are active in any run while the rest are held at zero. It is common in media composition. For Bayesian optimization, this repository routes load-bearing NChooseK constraints through ENTMOOT or OMLT because its supported BoFire 0.3.x adapter retains a documented compatibility limit.

**Mixture constraint.** All mixture components sum to a fixed total (usually 1.0 or 100 percent). Lives in the manifest as a constraint declaration; the validator checks the sum tolerance on design rows.

**Forbidden combination.** A region of factor space the operator declares off-limits. Stored as a constraint with a `when` clause; the design generator and adapters honor it.

## Adapters and routing

**Adapter.** Optional integration with an external library. Each adapter degrades to a `not_available` report when its extra is missing, so the demos run on a clean install. Adopted adapters: BoFire, ENTMOOT v2, BoTorch, OMLT, TabPFN, pyDOE3, SALib, scipy, PubMed MCP. See [`ADAPTER_MAP.md`](ADAPTER_MAP.md).

**Adopted optional.** An adapter that is wired in and tested but only activates when the user installs its extra. The repo never imports the optional dependency unless the adapter actually runs.

**Backend.** The runtime that produces a design or a follow-up candidate. `stdlib` is the default (no scientific dependencies); `bofire`, `botorch`, `entmoot`, `omlt`, `tabpfn` are alternate backends behind their adapters.

**Acquisition function.** In Bayesian optimization, the rule that picks the next batch of candidates from the surrogate's posterior. BoTorch's `qei` (q-Expected Improvement) is the standard baseline; `qucb` (q-Upper Confidence Bound) tunes explore vs exploit. See [`WAVE2_BOTORCH.md`](WAVE2_BOTORCH.md).

## Scale and bridge

**Scale context.** The block on the manifest that names from-scale and to-scale endpoints plus the bridge strategy. Carries vessel geometry, working volume, primary criterion, and secondary criteria. See [`SCALE_BRIDGE.md`](SCALE_BRIDGE.md).

**Bridge criterion.** The engineering target that should match across scales. Common choices: kLa (oxygen mass transfer coefficient), P/V (volumetric power), tip speed, mixing time, OUR (oxygen uptake rate), RQ (respiratory quotient), VVM (gas flow per working volume per minute), geometric similarity.

**kLa.** Volumetric oxygen mass transfer coefficient. Most common scale-up criterion for aerobic microbial fermentation.

**P/V.** Volumetric power input. Often used for mammalian and shear-sensitive systems where matching kLa would require unsafe agitation.

**Tip speed.** Linear velocity at the impeller tip. Shear proxy. Constrained for sensitive cell lines.

**Recapitulation.** What a scale-down qualification is trying to achieve: reproducing the larger-scale behavior at the smaller scale. Required by the `scale_down_qualification` profile.

## Outputs

**Run packet.** A single review-ready planning document in Markdown plus its JSON twin that stitches every available artifact together: readiness verdict, family recommendation, goals, assay-power, sampling plan, design preview, first-batch analysis, follow-up plan, risks, stop rules, assumptions. Produced by `ferm-doe finalize`.

**Dossier.** A campaign's cumulative evidence record: `CITATIONS.json`, `NOTES.md`, `SOURCES.bib`, per-corpus `EVIDENCE.csv`. Built across phases of a campaign; the structure and the per-corpus swarm / integrator / harvester roles are defined in [`SWARMS_AND_EVIDENCE.md`](SWARMS_AND_EVIDENCE.md). The dossier-generation runbook lives in [`dossier-generation.md`](dossier-generation.md).

**Issue pack.** A set of Markdown issue bodies generated from a manifest, intended for Linear, GitHub Issues, or an orchestrator's queue. Each pack is a bounded work graph with dependencies and acceptance criteria. See [`ISSUE_PACK_COOKBOOK.md`](ISSUE_PACK_COOKBOOK.md) and [`ISSUE_PACK_GENERATION.md`](ISSUE_PACK_GENERATION.md).

**Negative result memory.** A record of failures, exclusions, and known-bad regions of factor space, produced by `plan-wave2`. Future campaigns read it to avoid replaying mistakes.

**Learning ledger.** A CSV row per planning checkpoint that records the recommendation, the ascent signal, and what changed. Lives at `wave2/learning_ledger.csv` when the self-learning option is on.

## Workflow terms

**Task request.** A bounded, machine-readable contract for a single agent unit of work. JSON Schema at [`../schemas/task_request.schema.json`](../schemas/task_request.schema.json). Validated by `ferm-doe validate-task-request`.

**Stop rule.** A condition in the manifest that, when fired, escalates the campaign to a pause or a human review. Example: `flatness_threshold_reached` or `budget_exhausted`.

**Decision rule.** A condition that drives the planner's recommendation between experiment rounds. Example: confirm the winner if the best-row response is within tolerance of the goal; expand if the winner is on a factor boundary.

**Goal (Derringer-Suich desirability).** A composite objective formulated from response targets and bounds. Produced by `ferm-doe goals`. Each response gets a desirability score in [0, 1]; the campaign desirability is the geometric mean. See [`goals.py`](../src/biosymphony_ferm_doe/goals.py) for the formulation.

**Tool registry.** The curated set of BO/DoE and sidecar tools the repo tracks, with adapter status (adopted, evaluate_next, watch, boundary_only, avoid, compatibility_only). Lives at [`tool-registry.json`](tool-registry.json) and is summarized in [`TOOL_REGISTRY.md`](TOOL_REGISTRY.md).
