# CLI Reference

Single-page index of every `ferm-doe` subcommand. Grouped by lifecycle stage. For glossary terms, see [`GLOSSARY.md`](GLOSSARY.md). For the optional extras that activate specific backends, see [`ADAPTER_MAP.md`](ADAPTER_MAP.md).

The CLI is stdlib-only at runtime. Optional extras route through adapters that degrade to a `not_available` report when the extra is missing.

## Discovery

| Command | Purpose | Example |
|---|---|---|
| `ferm-doe doctor` | Report repo capability and optional backend readiness. | `ferm-doe doctor` |
| `ferm-doe list-campaigns` (alias: `catalog`) | Catalog campaign manifests and capabilities under a root. | `ferm-doe list-campaigns examples` |
| `ferm-doe inspect-campaign` (alias: `inspect`) | Summarize a campaign directory and suggested next commands. | `ferm-doe inspect-campaign examples/demo-pb-screening-public` |
| `ferm-doe tool-registry` | Validate the curated external-tool registry. | `ferm-doe tool-registry` |

## Validation and gating

| Command | Purpose | Example |
|---|---|---|
| `ferm-doe validate` | Validate a campaign directory; reports the readiness verdict and `failed_check_ids`. | `ferm-doe validate examples/demo-pb-screening-public --summary` |
| `ferm-doe audit` | Scan a repo tree for public-safety blockers. | `ferm-doe audit .` |
| `ferm-doe check-dossier` | Check the compact public dossier contract surface. | `ferm-doe check-dossier examples/demo-xylanase-public` |
| `ferm-doe validate-task-request` | Validate a bounded agent task request JSON contract. | `ferm-doe validate-task-request templates/task_request.template.json` |
| `ferm-doe assay-power` | Evaluate response-level assay-power policy. | `ferm-doe assay-power examples/demo-xylanase-public` |

`--summary` returns the short JSON form (verdict, error_count, warning_count, failed_check_ids, worst_axis). Omit it to get the full per-check output. `--out PATH` writes JSON to a file; good for agent pipes. See [`AGENT_QUICKSTART.md`](AGENT_QUICKSTART.md) for the loop pattern.

## Agent orchestration

| Command | Purpose | Example |
|---|---|---|
| `ferm-doe agent-brief` (alias: `brief`) | Build an agent kickoff brief for orchestration. | `ferm-doe agent-brief examples/demo-pb-screening-public --goal "Plan next-round DOE." --out /tmp/brief.json --md-out /tmp/brief.md` |
| `ferm-doe engine route-task-request` | Validate and route an engine task-request contract. | `ferm-doe engine route-task-request templates/engine_task_request.template.json` |
| `ferm-doe engine generate-issue-pack` | Generate Markdown issue bodies for Linear, GitHub Issues, or an orchestrator. | `ferm-doe engine generate-issue-pack --manifest examples/reference-doe-custom-design/campaign_manifest.json --out /tmp/issues --pack fermentation-readiness-v0` |

See [`ISSUE_PACK_COOKBOOK.md`](ISSUE_PACK_COOKBOOK.md) for the pack chooser and [`ISSUE_PACK_GENERATION.md`](ISSUE_PACK_GENERATION.md) for the end-to-end runbook.

## Design

| Command | Purpose | Example |
|---|---|---|
| `ferm-doe recommend-family` | Suggest a DoE family from manifest factors, profiles, and priors. | `ferm-doe recommend-family examples/demo-pb-screening-public` |
| `ferm-doe generate-design` | Generate a first-batch design CSV from the manifest's `doe.family`. | `ferm-doe generate-design examples/demo-pb-screening-public --out /tmp/wave1.csv --metadata-out /tmp/wave1.meta.json --seed 0` |
| `ferm-doe doe-power` | Per-coefficient minimum-detectable-effect (MDE) from the design matrix at target power. | `ferm-doe doe-power examples/demo-pb-screening-public --sigma 0.5 --out /tmp/power.json --md-out /tmp/power.md` |
| `ferm-doe engine propose-design` (alias: `propose-designs`) | Generate multiple candidate DoE designs for tournament comparison. | `ferm-doe engine propose-design --manifest M.json --out /tmp/candidates` |
| `ferm-doe engine compare-designs` (alias: `tournament`) | Run the design tournament: scores candidate designs across statistical quality, feasibility, cost, robustness. | `ferm-doe engine compare-designs --manifest M.json --out /tmp/tournament` |

See [`DOE_FAMILIES.md`](DOE_FAMILIES.md) for the family taxonomy and [`DOE_FAMILY_RECIPES.md`](DOE_FAMILY_RECIPES.md) for swap recipes.

## Scale, sampling, goals, cost

| Command | Purpose | Example |
|---|---|---|
| `ferm-doe scale-recipe` | Derive an engineering recipe at `to_scale` (RPM, sparge, agitator power, kLa) from `scale_context`. | `ferm-doe scale-recipe examples/demo-scale-bridge-public --out /tmp/recipe.json --md-out /tmp/recipe.md` |
| `ferm-doe bridge-qualification` | Generate qualification design rows that bridge from-arm to to-arm. | `ferm-doe bridge-qualification examples/demo-scale-bridge-public --out /tmp/bridge.csv` |
| `ferm-doe sampling-plan` | Per-sample schedule for fed-batch or perfusion runs. | `ferm-doe sampling-plan examples/demo-scale-bridge-public --out /tmp/sampling.csv --md-out /tmp/sampling.md` |
| `ferm-doe goals` | Formulate Derringer-Suich desirability goals from responses and decision rules. | `ferm-doe goals examples/demo-xylanase-public --out /tmp/goals.json` |
| `ferm-doe cost-rollup` | Roll up first-batch, sampling, and follow-up estimates into a planning budget. | `ferm-doe cost-rollup examples/demo-xylanase-public --out /tmp/cost.json` |

## first-batch analysis

| Command | Purpose | Example |
|---|---|---|
| `ferm-doe analyze` | Fit OLS to first-batch results; emit effect estimates with permutation p-values, residual bootstrap CIs, lack-of-fit, half-normal plot data. | `ferm-doe analyze examples/demo-pb-screening-public --results examples/demo-pb-screening-public/inputs/wave1_results.csv --out /tmp/analysis.json --md-out /tmp/analysis.md --seed 0` |

## follow-up planning

| Command | Purpose | Example |
|---|---|---|
| `ferm-doe plan-wave2` | Plan follow-up from first-batch result rows. Backends: `stdlib` (default closed-loop), `botorch` (GP + qEI/qUCB). | `ferm-doe plan-wave2 examples/demo-pb-screening-public --results examples/demo-pb-screening-public/inputs/wave1_results.csv --out-dir /tmp/wave2 --remaining-budget 3` |
| `ferm-doe plan-wave2 --backend botorch` | Same, with Gaussian-process surrogate and acquisition function. Requires `pip install biosymphony-ferm-doe[botorch]`. | `ferm-doe plan-wave2 ... --backend botorch --acquisition qei --bo-n-candidates 6` |
| `ferm-doe engine ingest-results` | Ingest completed batch results and recommend follow-up (engine path, more options). | `ferm-doe engine ingest-results --manifest M.json --results R.csv --out /tmp/ingest` |

See [`ADAPTIVE_WAVE2.md`](ADAPTIVE_WAVE2.md) for the conceptual model and [`WAVE2_BOTORCH.md`](WAVE2_BOTORCH.md) for the BoTorch walkthrough.

## Finalize

| Command | Purpose | Example |
|---|---|---|
| `ferm-doe finalize` | Compose every available artifact into one review-ready planning run packet (Markdown + JSON). | `ferm-doe finalize examples/demo-pb-screening-public --results examples/demo-pb-screening-public/inputs/wave1_results.csv --out /tmp/run_packet.md --json-out /tmp/run_packet.json` |

## Engine: full dossier flow

The `engine` umbrella holds the broader dossier and campaign-state surface. Most top-level commands above have an `engine ...` equivalent that exposes more knobs.

| Command | Purpose |
|---|---|
| `ferm-doe engine compile-state` | Manifest plus inputs and constraints become `campaign_state.json`, `missing_info.json`, selected workflow modes. |
| `ferm-doe engine score-readiness` (alias: `readiness`) | Full per-axis readiness scoring with feasibility and assay-readiness inputs. |
| `ferm-doe engine compile-dossier` | Compile the complete `ferm-doe-dossier/` with design candidates, comparison, parity report, selected design, lab packet, result template, follow-up rules, provenance, verdict. |
| `ferm-doe engine compile-swarm-plan` | Optional Scientific Swarm planning artifacts (per-corpus evidence lanes, observability plan). |
| `ferm-doe engine check-dossier` | Validate the dossier artifacts produced above. |
| `ferm-doe engine contract-self-check` (alias: `self-check`) | Join dossier artifacts and audit claims against the public claim boundary. |

## Engine: utility surface

Optional reference DOE utilities, useful when comparing against JMP / Design-Expert / Modde or driving custom-optimal flows.

| Command | Purpose |
|---|---|
| `ferm-doe engine utility check-deps` | Report optional utility dependency status. |
| `ferm-doe engine utility custom-optimal` | Custom-optimal row selection. |
| `ferm-doe engine utility augment-design` | Generate augment-design rows for next sequential batch. |
| `ferm-doe engine utility profiler` | Fit a local profiler and write an operating-window report. |
| `ferm-doe engine utility simulate-design` | Deterministic design simulation and power proxy. |
| `ferm-doe engine utility assay-power` | Engine-side assay-power policy assessment. |
| `ferm-doe engine utility doe-export` | Export and import simple DoE CSV artifacts. |
| `ferm-doe engine utility benchmark-doe` | Synthetic reference-DOE benchmark harness. |

## Global flags

Most commands accept:

- `--summary` for a short JSON form
- `--out PATH` to write JSON instead of stdout
- `--md-out PATH` to write a Markdown twin where it exists
- `--seed N` to make stochastic outputs deterministic

`--help` after any subcommand prints its full flag list.
