# Changelog

All notable changes to this project will be documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [Semantic Versioning](https://semver.org/), with pre-alpha tags through `0.x`.

## [Unreleased] - 2026-08-30 tool and documentation refresh

### Added

- Registry checks now reject non-public source paths, missing documentation paths, unsynchronized public mirrors, optional extras without registry coverage, and adapter route or claim drift.
- Restricted adaptive backends now require an explicit license gate. TabPFN records separate terms for the code, v2 weights, and default TabPFN-3 weights.

### Changed

- Refreshed all 49 registry entries against current official package or repository information. The generated registry now separates the repository's supported requirement from the latest observed upstream release.
- Added SciPy and Plotly to the registry and corrected BoTorch, SALib, pyDOE3, Nox, Frictionless, RO-Crate, GROBID, Atlas, and related tool records.
- Replaced the mutable BoFire `main` dependency in the separate NChooseK DoE evaluation extra with a Python 3.11 or newer BoFire 0.4.1 pin. The primary verified BoFire adapter remains on `>=0.3.1,<0.4`.
- Marked the May 2026 BoFire and backend findings as dated compatibility evidence. Closed upstream issues no longer appear as current failures, and no later-release compatibility is implied.
- Tightened README, skill, reference, and demo language around readiness, scale transfer, optimization, execution, and backend comparisons.

## [Unreleased] - 2026-05-26 public-launch polish

### Changed

- `README.md` Start Here now includes a three-command fresh-clone smoke test and the expected `YELLOW`/`error_count == 0` result, so first-time users can verify the repo before choosing an agent harness.
- Package, citation, README, and GitHub discovery metadata now use AI-agent-ready experiment-design positioning and broader discovery topics (`python`, `experimental-design`, `bayesian-optimization`, `optimization`, `ai-agents`) instead of internal workflow labels.
- PubMed adapter fixtures and tests now use generic xylanase / autoinduction public-reference wording instead of residual private-adjacent example text.
- Public-release scanner tests now use generic private-path fixtures rather than contributor-specific local handles.
- A research survey note now says "mature packaging" rather than "production-ready" so backend maturity language cannot be confused with a repo claim.
- README-facing diagrams now use review-boundary language instead of execution-readiness language, and the public agent-loop SVG labels were shortened to avoid overlap at README width.
- CI now installs the package before the matrix release gate, uses the OSS gitleaks CLI instead of the licensed GitHub Action wrapper, and the adaptive-backend surface keeps the Python 3.10 `tomli` fallback aligned with the rest of the package.

## [Unreleased] - 2026-05-26 memory-pattern entry-surface nudge

### Changed

- `README.md` "Run the demo with your agent" gets a one-paragraph nudge at the end of the real-campaign instruction: at closeout, ask the agent to write `artifacts/<campaign>/AGENTS.md` and to record hiccups, excluded results, and arm-scoped negative memory in the self-learning ledger and review files. Names `docs/SELF_LEARNING_DOE.md` as the canonical doc and frames the artifacts as portable memory across agent runtimes.
- `docs/AGENT_QUICKSTART.md` "What The Agent Should Do" gets a matching paragraph: campaign-local handoff at `artifacts/<campaign>/AGENTS.md`, the self-learning trio (`learning_ledger.csv`, `hiccup_review.md`, `negative_result_memory.json`), pointer to `docs/SELF_LEARNING_DOE.md`, and the agent-runtime-agnostic framing.

## [Unreleased] - 2026-05-26 version-anchoring nudges

### Changed

- `skills/biosymphony-ferm-doe/SKILL.md` Closeout Standard gains one line: when a campaign exercises an optional adapter (BoFire, ENTMOOT, OMLT, TabPFN, BoTorch), record the installed package version in the dossier (`NOTES.md` or per-corpus EVIDENCE row) so claims are version-anchored. Points at the tool-registry `last_checked` baselines and `BACKEND_EVAL_FINDINGS.md` as-of dates as drift anchors.
- `docs/TOOL_REGISTRY.md` opening gains one paragraph naming `last_checked` dates and `current_signal` text as baselines captured on a specific day, with a re-confirm-the-installed-version reminder before relying on findings, especially for upstream branches under active development like `bofire main`.

## [Unreleased] - 2026-05-26 public-content review

### Removed

- A campaign-specific worked-exemplar artifact set and methods-note draft were removed from the public surface. The retained lessons now live as generic methodology, validation, and cost-stack guidance rather than as raw campaign artifacts.

### Changed

- `docs/BIOMANUFACTURING_ADAPTIVE_BACKENDS.md` depth ladder dropped the "Worked exemplar" tier (no backend currently rises to that level). BoFire 0.3.1 now sits at "Documented route + smoke + findings" alongside OMLT, TabPFN v3, ENTMOOT v2, and BoTorch direct, with the two existing demo-*-bofire fixtures named as the smokes.
- `docs/OPEN_DATA_PUBLICATION_STRATEGY.md` rewritten as generic open-data guidance. The strategy (Zenodo + RO-Crate 1.2 + Process Run Crate 0.5 + DataCite 4.5 + MECA bundle path + ELN export path + CC-BY-4.0/CC0/MIT license stack + redaction checklist + deposit checklist + citation template) is preserved without campaign-specific worked examples.
- `docs/SCALE_BRIDGE_METHODOLOGY.md` genericized around BL21 periplasmic expression. The methodology content (kLa correlations, sulfite calibration, OTR derivations, P/V calculations, mix-time estimates, scale-down equations, and the published reference set) is preserved.
- `docs/GLOSSARY.md` dossier definition rewritten to describe the structure without pointing at a now-deleted example; cross-link added to `dossier-generation.md`.
- Docs, templates, tests, and release allowlists were refreshed to point at public synthetic fixtures and public-paper starters instead of removed campaign-specific artifacts.

### Added

- `tests/fixtures/pubmed/sample-fallback-citations.json`: minimal synthetic test fixture (two generic biomanufacturing references) used as the PubMed adapter's canonical fallback path.

## [Unreleased] - 2026-05-25 polish wave

### Added

- Six reference docs wired into `docs/README.md`: `GLOSSARY.md` (campaign, profile, claim level, scale context, NChooseK, kLa, and the rest), `CLI_REFERENCE.md` (single-page index of every `ferm-doe` subcommand grouped by lifecycle stage), `ADAPTER_MAP.md` (capability-centric "I want to do X → install Y → CLI Z" map), `DOE_FAMILY_RECIPES.md` (manifest-patch recipes for swapping `doe.family` across the 14 supported generators), `WAVE2_BOTORCH.md` (qEI / qUCB walkthrough with documented short-circuit reasons), `ISSUE_PACK_GENERATION.md` (runbook for `engine generate-issue-pack` with Symphony, Claude Code + Linear, and generic-orchestrator integration patterns).
- Three campaign-shaped public examples: `examples/reference-doe-custom-design/` (custom constrained fixture for reference-DoE parity checks), `examples/yeast-isoprenoid-2l-fedbatch/` (product-class starter for a hydrophobic-product 2 L fed-batch case with derived productivity and cost responses), `examples/xylanase-wxz1-2012/` (public-paper-derived starter from Cui & Zhao 2012, DOI 10.3390/ijms130810630, CC BY 3.0, normalized into the manifest contract).
- `make help` target listing every common make target with a one-line summary, grouped by sharing gate, tests/validators, inspect, optional smokes, public-safety scans, and housekeeping.
- Two backend-depth docs recorded the May 2026 evaluation: `docs/BACKEND_EVAL_FINDINGS.md` covered the six-fixture results, and `docs/ADAPTER_DESIGN_NOTES.md` documented the OMLT coupling rule, TabPFN posterior approximation, ENTMOOT cardinality semantics, BoTorch cost-weighting risk, and multi-objective memory controls. These entries describe the evaluation state on that date; later upstream status appears in the current tool registry.
- Depth-ladder section added to `docs/BIOMANUFACTURING_ADAPTIVE_BACKENDS.md` ("How Deep Does Each Route Go In This Repo") that explicitly maps backends to tiers (worked exemplar, documented route + smoke + findings, documented route only, comparison-surface target, registry listing) so the "37 tools, 9 adapters" framing does not read as implicit parity.

### Changed

- README reframed as agent-skill-first. Tagline: "A multi-agent skill for constraint-aware experimental design in fermentation and biomanufacturing." Opening describes Symphony, Claude Code + Linear, Codex CLI, OpenAI Agents SDK, and custom orchestrators as supported harnesses, with hand-driven CLI as a parallel path rather than the primary one.
- `docs/README.md` tiered: Start Here / Core Contracts / Planning Workflows / Lessons and Methodology / Agent And Evidence / Adaptive Backends / Internals And Roadmap / Public Release / Scope And Policy. `NON_CLAIMS.md` moved out of Start Here into Scope and Policy.
- AGENTS.md "Current State" refreshed: 12 campaign-shaped demos + 2 aux fixtures, 9 profiles, 14 DoE families, adapters including OMLT and TabPFN, AWS Lambda and Modal deploy scaffolds, the six new reference docs, 455 tests pass + 38 expected skips.
- RO-Crate canonical URL fixed in `skills/biosymphony-ferm-doe/scripts/rocrate_retrofit.py` (was lowercase `biosymphony/ferm-doe`, now canonical `BioSymphony/biosymphony-ferm-doe`).
- README Topics line: hyphenated `computational-planning`, added `biomanufacturing`.
- Tone pass: replaced "unlocks" with "activates" in a README cross-link to `ADAPTER_MAP.md`; fixed two "X not Y" constructions in `docs/SCALE_BRIDGE.md` and `examples/demo-shakeflask-to-2l-bofire/README.md`.
- `docs/BACKEND_EVAL_FINDINGS.md` gets an explicit "Provenance and reproducibility" section that names the layering: the sweep ran in a separate workspace; the public repo ships the fixtures, the adapter code, the validators, and the methodology lessons; the runner scripts and raw per-run outputs stay outside the public package as operational state. A contributor with a clean clone can rebuild and re-run the sweep from the public pieces.
- `AGENTS.md` "Current State" and `skills/biosymphony-ferm-doe/SKILL.md` "Reference Map" updated to point at the two new depth docs (`BACKEND_EVAL_FINDINGS.md`, `ADAPTER_DESIGN_NOTES.md`) so an agent reading either entry surface finds them.

## [Unreleased] - 2026-05-23 public-readiness refresh

### Added

- Public adaptive-backend evaluation surface: `docs/BIOMANUFACTURING_ADAPTIVE_BACKENDS.md`, `docs/adaptive-backend-evaluation.json`, `examples/adaptive-backend-eval/`, `src/biosymphony_ferm_doe/adaptive_backend_surface.py`, and `skills/biosymphony-ferm-doe/scripts/adaptive_backend_surface_check.py`. This lets BoFire, BayBE, Ax/BoTorch, ENTMOOT, OMLT, and TabPFN be compared while keeping BioSymphony's manifest, readiness, assay, scale, cost, evidence, and handoff layers authoritative.
- OMLT optional adapter (`adapters/omlt_strategy.py`) for MIP-optimized surrogate planning over linear and NChooseK constraints. The adapter is import-safe without optional dependencies and degrades to explicit `not_available` or `solver_unavailable` reports.
- TabPFN optional adapter (`adapters/tabpfn_strategy.py`) for token-gated low-data surrogate planning. No token is stored; the adapter remains inactive unless the operator supplies `TABPFN_TOKEN` at runtime.
- Smoke-artifact semantic contract (`docs/schemas/smoke-artifact-contract.json`, `scripts/_contract_emitter.py`, `scripts/validate_smoke_artifacts.py`) so generated backend-smoke artifacts cannot claim `PASS` while containing constraint violations, unknown route selections, or incompatible fallback state.
- `make adaptive-backend-surface`, `make public-ready`, `nox -s adaptive_backend_surface`, and `nox -s adaptive_backend_live_imports` for local public-switch readiness checks.

### Changed

- ENTMOOT NChooseK coupling now enforces a strictly positive minimum active amount when the binary indicator is on, closing the ON-but-zero candidate leak in addition to the existing `min_count` cardinality guard.
- Tool registry expanded from 36 to 37 entries and refreshed for Ax, BayBE, OMLT, TabPFN, and the adaptive-backend public surface.
- `make release-check` now includes adaptive-backend surface validation and scans a broader public surface, including security/contribution metadata, deploy scaffolding, scripts, adaptive-backend fixtures, and public example families.
- Deployment scaffolds now default to minimal auth, throttling, generic runtime errors, and provider-neutral handoff commands so public examples do not imply open unauthenticated endpoints.
- All public example manifests now carry public-safe synthetic inputs and expected readiness handoffs, and `make validate-all` covers every top-level example manifest instead of only the original demo loop.

## [Unreleased] - 2026-05-21 refresh

### Added

- BoFire adapter (`adapters/bofire_strategy.py`) that routes constrained DoE and Bayesian optimization through `DoEStrategy`, `SoboStrategy`, and `MultiFidelityVarianceBasedStrategy`, with full domain translation and a "not_available" report path when the optional extra is absent. Positioning at `docs/BOFIRE_POSITIONING.md`; constraint patterns including the `SoboStrategy` plus `NChooseK` trap (upstream issue #450) at `docs/BOFIRE_CONSTRAINT_PATTERNS.md`.
- ENTMOOT v2 adapter (`adapters/entmoot_strategy.py`) for NChooseK Bayesian optimization with cardinality-aware `min_count` constraints, the documented swap when BoFire's `SoboStrategy` plus `NChooseK` stalls. Swap design rationale and three documented risks at `docs/ENTMOOT_SWAP_DESIGN.md`.
- PubMed MCP adapter (`adapters/pubmed_mcp.py`) that pulls evidence rows into the cumulative dossier through the public PubMed MCP server with stable provenance.
- SALib sensitivity adapter (`adapters/salib_sensitivity.py`) for Sobol and Morris sensitivity over first-batch result rows.
- Reporters module (`reporters/`) including a BoFire HTML report with embedded pipeline SVG, constraint feasibility slice, per-candidate cost stack, and design coverage heatmap. Plotly figures require the `[report]` extra; the report renders cleanly without it using inline SVG.
- Curated BO/DoE registry at `docs/TOOL_REGISTRY.md` and `docs/tool-registry.json`, loaded by `src/biosymphony_ferm_doe/tool_registry.py` with positioning, adapter status, and route reasons for each entry.
- Scale-bridge methodology document at `docs/SCALE_BRIDGE_METHODOLOGY.md` covering sulfite kLa calibration, PreSens DO patch entry conditions, baffled-flask qualification, and the scale-down O2 trap. Companion to `docs/SCALE_BRIDGE.md`.
- Cumulative dossier swarm pattern at `docs/SWARMS_AND_EVIDENCE.md` and `docs/dossier-generation.md`. One coherent dossier per campaign (`CITATIONS.json`, `NOTES.md`, `SOURCES.bib`, per-corpus `EVIDENCE.csv`), backed by `src/biosymphony_ferm_doe/provenance.py` and the `rocrate_retrofit` script. Replaces the prior pattern of N isolated reports per campaign.
- Cost-model realism stack at `docs/COST_MODEL_REALISM_CHECK.md` and `templates/cost_stack.template.md`. Five tiers: simulator number, plus bulk-reagent number, plus fully-loaded shake-flask COGS, plus CMO benchmark, plus a stated range. Documents the IPTG-to-lactose autoinduction lever.
- Frictionless-compatible table contracts via `src/biosymphony_ferm_doe/table_contracts.py` and `schemas/tables/` (run ledger, evidence, equipment, reagent, design, results). Validation runs stdlib by default; full Frictionless validation lights up with the `[contracts]` extra.
- Open-data publication strategy at `docs/OPEN_DATA_PUBLICATION_STRATEGY.md` mapping a campaign artifact set to a publishable open-data drop (Zenodo, FigShare, Dryad).
- Simulator v2 spec at `docs/SIMULATOR_V2_SPEC.md` (SPEC ONLY status; not yet implemented). Documents the lactose dose-response term gap surfaced by public-safe simulator stress testing.
- Compact BoFire demos: `examples/demo-shakeflask-to-2l-bofire/` (scale-bridge with historical ledger ingest) and `examples/demo-media-cost-bofire/` (linear cost and total-mass constraint screening).
- ENTMOOT NChooseK smoke at `examples/entmoot-nchoosek-smoke/` showing the cardinality-aware Bayesian optimization route.
- Yeast isoprenoid scaffold at `examples/yeast-isoprenoid-2l-fedbatch/` for a hydrophobic-product shake-flask to 2 L fed-batch case.
- New skill scripts: `run_bofire_smoke.py` (BoFire route smoke that runs with or without the extra), `tool_registry_check.py` (validates the curated registry), `table_contracts.py` (validates all CSV inputs against the table contracts), `rocrate_retrofit.py` (retrofit an existing campaign artifact set into an RO-Crate 1.2 / Process Run Crate 0.5 metadata file), `prepare_provider_handoff.py` (compose a provider-handoff bundle without launching paid resources).
- New templates: `cost_stack.template.md` (five-tier cost honesty stack), `PARETO_LIT_CHECK.template.md` (sealed-winner literature pressure-test before campaign close), `scale_bridge_entry_conditions.template.md` (baffled flask, sulfite kLa, DO patch entry conditions), `sidecar-compute-policy.json`, `sidecar-provider-handoff.json`.
- New schema: `schemas/task_request.schema.json` (bounded public-safe task requests), `schemas/tables/` (six Frictionless-compatible table contracts).
- New tests (~19 added): `test_entmoot_adapter.py`, `test_pubmed_adapter.py`, `test_table_contracts.py`, `test_tool_registry.py`, `test_dossier_provenance.py`, `test_module_readiness.py`, `test_preflight_check.py`, additional adapter and module coverage.
- `pyproject.toml` optional-dependency groups for `bofire`, `entmoot`, `sensitivity`, `report`, `contracts`, plus an updated `all` umbrella.

### Changed

- `SKILL.md` rewritten with the methodology body stripped down to the runtime-essential loop; methodology content moved into dedicated docs (`SCALE_BRIDGE_METHODOLOGY.md`, `BOFIRE_POSITIONING.md`, `ENTMOOT_SWAP_DESIGN.md`, `dossier-generation.md`).
- `README.md` rewritten so the pitch matches the first batch surface. Three honest differentiators (literature-aware planning, scale-bridge-first design, comfortable saying no) plus the secondary capabilities (tool registry, cost stack, durable manifest).
- `Makefile` `release-check` target now scans the public top-level set plus the new docs and example surface.

## [Earlier work] (pre-2026-05-21 refresh)

### Added

- Public-safe adaptive follow-up planner (`ferm-doe plan-wave2`) that emits result ingestion, assay-power, recommendation, augment-design, negative-memory, learning-ledger, and manifest-patch artifacts with `planned_wave2_design` claims.
- Response-level assay-power evaluator (`ferm-doe assay-power`) with stdlib-only checks for MDE, expected effect, noise/CV, replicates, target power, LOD/LOQ, dynamic range, matrix recovery, and turnaround.
- Manifest schema slots for `adaptive_wave2`, `assay_power_policy`, bridge policy, self-learning policy, and adaptive actions.
- Self-learning DoE runbook, hiccup review template, learning ledger template, follow-up results template, and public issue pack for adaptive follow-up work.
- Recommendations honor `adaptive_wave2.allowed_actions`: actions outside the allowed list downgrade to `pause` with `original_recommended_action` recorded.
- Augment rows for `narrow` recommendations use non-zero step multipliers (-1, +1, -2) so candidates do not duplicate the locked best row.
- Stdlib-only first-batch design generators (`ferm-doe generate-design`) for full factorial, fractional factorial (with standard or operator-supplied generators), Plackett-Burman (n ∈ {8, 12, 16, 20, 24}), definitive screening (k ∈ {3..6, 9, 10}), central composite (face-centered, rotatable, orthogonal), Box-Behnken (k ∈ {3, 4}), Latin hypercube, and Scheffé mixture (simplex-lattice and simplex-centroid). D-optimal, I-optimal, and extreme-vertices-mixture emit at `claim_level: heuristic` via coordinate exchange / constraint enumeration.
- Scale-bridge engineering recipe (`ferm-doe scale-recipe`) derives runnable RPM, sparge / gas flow, agitator power, tip speed, mix time, and resulting kLa at both `from_scale` and `to_scale` from the manifest's `scale_context`. Built-in Van't Riet kLa correlations (coalescing / non-coalescing / shear-sensitive) plus impeller-type-keyed power-number and Nienow mix-time presets, with operator overrides via `correlation_overrides`. Output is labeled `claim_level: engineering_recipe_planned` and renders as both JSON and a markdown run-recipe document. The recipe records which correlation drove each line and warns when declared targets disagree with solved values by more than 20%.
- Derringer-Suich optimization goals (`ferm-doe goals`) emit weighted-geometric-mean desirability formulations from `responses[].objective_lower / objective_upper / objective_target / objective_shape / objective_weight` or, as a fallback, numeric `decision_rules[]` thresholds scoped to a response. Linear / quadratic / step desirability shapes supported. Output is labeled `claim_level: optimization_goal_formulated`.
- follow-up planner (`ferm-doe plan-wave2`) now consumes goals when they are computable from the manifest. Best-run selection uses composite desirability across all declared objectives instead of single-response scoring; the recommendation records `scoring_mode` (`desirability` or `single_response`) and `best_desirability` when applicable. `optimization_goals.json` is written alongside the other follow-up artifacts when goals are formulable.
- Stdlib OLS first-batch analysis (`ferm-doe analyze`) emits effect estimates with permutation p-values (default 1000 draws) and residual-bootstrap 95% CIs, lack-of-fit decomposition (when replicate or center-point clusters exist), R^2 / adjusted R^2 / RMSE / residual summary, half-normal plot data, and a follow-up signal block (per-factor ascent signs and active-factor list). Supports linear main effects, two-factor interactions, and quadratic terms based on `doe.model_terms`. Categorical factors are treatment-coded; mixture and temporal-profile factors are skipped with a warning. Output is labeled `claim_level: wave1_analysis_planned`.
- Closed-loop adaptive follow-up: `ferm-doe plan-wave2` runs the OLS analysis automatically when ≥4 usable result rows exist, writes `wave1_analysis.json` alongside the other artifacts, and feeds the per-factor ascent signal into the augment-row generator. Active factors get tighter steps (5% vs legacy 10%) biased along the ascent direction; inactive factors hold at the best-row value for `narrow` and at center for `expand`. Augment rows are tagged `scoring_mode: model_informed` when the closed-loop path drives them; the legacy symmetric narrowing path is preserved as a fallback when analysis short-circuits.
- One-document run-packet composer (`ferm-doe finalize`) stitches manifest, readiness verdict, optimization goals, scale-bridge engineering recipe, assay-power readiness, first-batch design, first-batch results (when a results CSV is provided), first-batch OLS analysis, follow-up plan (when a `wave2_recommendation.json` exists), risks, stop rules, assumptions, and biosafety triggers into one shippable markdown document with a JSON sidecar. Each section degrades gracefully when its inputs are missing and records why it was skipped. Output is labeled `claim_level: run_packet_planning_compose`.
- Quadratic-aware closed-loop follow-up: when the fitted first-batch model includes quadratic and / or interaction terms, the analysis now solves `∇y = 0` for the predicted stationary point (RSM-style) and emits its location in both coded and engineering units. The augment-row generator interpolates `narrow` rows toward the predicted optimum at 25% / 50% / 75% of the distance from the best run when the optimum is interior to the declared factor ranges, and falls back to ascent-direction shifts when the stationary point is exterior or there is no curvature. Augment rows produced via the optimum-targeted path carry `scoring_mode: model_informed_optimum`; ascent-direction rows carry `model_informed`; legacy symmetric rows carry no scoring_mode.
- DoE family recommender (`ferm-doe recommend-family`) emits a ranked list of family candidates with stated reasons and expected run counts from the manifest's factors, profiles, and operator-supplied curvature / interactions priors. Three canonical paths: mixture (Scheffé / extreme-vertices), split-plot (any `hard_to_change` factor), and the main screening / optimization / scale-bridge branch with explicit decision-path logging. Optional `--budget` filter drops candidates whose run count exceeds the cap and records the drop reason. Output is labeled `claim_level: family_recommendation_planning`.
- Multi-arm bridge qualification (`ferm-doe bridge-qualification`) generates the qualification design rows at the `to_arm` scale that bridge to a `from_arm` reference under a declared scale criterion (kLa, P/V, tip speed, etc.). Default emits N recipe-matched center-point replicates with all transferable factors held at midpoint and retuned setpoints pulled from the scale recipe; optional `--perturbation-pct` adds ±pct excursions on each transferable factor for sensitivity. Inferred from `arms[].bridge_to` when not specified; explicit `--from-arm` / `--to-arm` flags supported. Output is labeled `claim_level: bridge_qualification_planning`.
- Sampling-plan generator (`ferm-doe sampling-plan`) emits a per-sample schedule for fed-batch / perfusion campaigns from `responses[]` and an optional `sampling_policy` block on the manifest (`run_duration_h`, `phases[]`, per-response `frequency_h` / `active_window_h` / `sample_volume_ml`). Falls back to heuristic defaults (48 h run, 4 h frequency, 1 mL volume, lag/active/stationary phases) when policy is absent. Skips `derived` and `clock` measurement types automatically. Outputs CSV (sample_id, time_h, response_id, phase, volume, rationale) plus markdown summary plus JSON sidecar with totals (n_samples, total_volume_ml, samples_per_response, samples_per_phase). Output is labeled `claim_level: sampling_plan_planning`.
- Design-level power analysis (`ferm-doe doe-power`) computes per-coefficient minimum detectable effect from the design matrix via `Var(β_i) = σ^2 · (X^T X)^(-1)_{ii}` and `MDE_i = (z_{α/2} + z_β) · SE(β_i)`. Operator supplies `--sigma` (residual standard deviation in the response's units); defaults `α = 0.05`, `target_power = 0.8`. The result table flags per-coefficient `expected_passes_mde: true | false` against the primary response's `assay_power_policy.expected_effect_size` when declared. Output is labeled `claim_level: doe_power_planning`. Distinct from `assay-power`, which covers response-level assay readiness rather than design-level coefficient resolution.
- `ferm-doe finalize` now includes `family_recommendation`, `bridge_qualification`, and `sampling_plan` sections in addition to the original eight, so the run packet covers every applicable subcommand's output. Each new section degrades gracefully (e.g., `bridge_qualification` skips when no `arms[]` declare `bridge_to`).
- `examples/demo-pb-screening-public/README.md` rewritten to walk through the full ten-step closed-loop demo (validate → recommend-family → generate-design → doe-power → goals → assay-power → sampling-plan → analyze → plan-wave2 → finalize).
- Cost / resource rollup (`ferm-doe cost-rollup`) aggregates first-batch run count (from `doe.n_runs` or generated design), sampling-plan totals (n_samples, total_volume_ml, run_duration_h), and an optional follow-up run estimate against operator-declared unit costs (`resource_costs.per_run_cost`, `per_sample_cost`, `per_volume_ml_cost`, `per_run_duration_h_cost`, `wave2_runs_estimate`). CLI flags override manifest values per invocation. Output is labeled `claim_level: cost_rollup_planning`; the non-claim spells out that the rollup multiplies declared unit costs against artifact-derived counts and does not estimate yields, throughput, or staff time.
- Optional adapter layer (`src/biosymphony_ferm_doe/adapters/`) lets advanced users opt into established libraries without breaking the stdlib runtime moat. First adapter shipped: `scipy_pvalues`. When `pip install biosymphony-ferm-doe[scipy]` is present, `analyze` adds proper Student-t two-sided p-values per coefficient (alongside the existing permutation p-values), and `doe-power` switches its critical value from the normal approximation to the Student-t quantile at `df_residual` (recorded via `critical_basis: student_t`). Falls back to the stdlib path when scipy is absent. Adapter scaffolding (`adapters/__init__.py`) provides `get_adapter(name)` and `is_available(name)` registry helpers; placeholder modules for `nist_citations`, `pydoe3_designs`, and `botorch_wave2` are populated in subsequent commits.
- NIST citations adapter (`adapters/nist_citations.py`) populates a citation table mapping each supported DoE family to the relevant NIST/SEMATECH e-Handbook chapter URL plus a one-line selection rule. Designs that are post-handbook (Definitive Screening, Latin Hypercube) cite primary literature directly (Jones-Nachtsheim 2011, McKay-Beckman-Conover 1979). `recommend_family` now embeds the citation in each candidate so the decision path is traceable to the canonical reference. Pure-data adapter; no external dependency.
- pyDOE3 adapter (`adapters/pydoe3_designs.py`) extends Box-Behnken to k ≥ 5 (the stdlib path covers k ∈ {3, 4} only) and provides maximin Latin Hypercube via `pyDOE3.lhs(criterion='maximin')`. `generate_design` checks adapter availability and routes through pyDOE3 when applicable; the result records `metadata.backend: 'pydoe3'`. Falls back to the stdlib path otherwise. Install via `pip install biosymphony-ferm-doe[pydoe3]`.
- BoTorch adapter (`adapters/botorch_wave2.py`) replaces the stdlib closed-loop's geometric narrowing with Gaussian-process surrogate + acquisition-function follow-up. Fits a `SingleTaskGP` to the result rows in coded space, optimizes the chosen acquisition (`qExpectedImprovement` default; `qUpperConfidenceBound` available) over the unit hypercube, and emits `n_candidates` next-batch points. Output labeled `claim_level: bayesian_optimization_planned`; emits `bo_wave2_plan.json` and `bo_wave2_design.csv` with `scoring_mode: bayesian_optimization` per row. Used via `ferm-doe plan-wave2 --backend botorch [--acquisition qei|qucb] [--bo-n-candidates N]`. Falls back to a clear error message when BoTorch isn't installed. Install via `pip install biosymphony-ferm-doe[botorch]` (heavy: pulls torch + botorch + gpytorch).
- Validator now reports module readiness via five new warning checks: `module-readiness-goals` (objective bounds OR numeric scoped decision rules present), `module-readiness-scale-recipe` (kLa / P/V / tip_speed declared at from_scale), `module-readiness-bridge-qualification` (arms[] declare bridge_to AND scale_context present), `module-readiness-sampling-plan` (at least one assayed or instrument response), and `module-readiness-cost-rollup` (resource_costs block carries at least one non-zero unit cost). The agent reads these from `failed_check_ids` and either fixes the manifest or accepts the limitation before running the corresponding subcommand. Demos updated to declare `objective_lower / objective_upper` so the existing readiness expectations remain clean.
- Cloud deployment scaffolding (`deploy/`) ships two reference deployments: AWS Lambda for the lightweight stdlib subcommands behind API Gateway (`deploy/aws-lambda/`) and Modal for the heavy BoTorch BO follow-up endpoint (`deploy/modal/`). Single dispatch Lambda handler routes 12 actions by event payload; SAM template exposes them as `/v1/{action}` POST endpoints. Modal scaffold deploys the BoTorch adapter as a CPU function by default with a one-line GPU flag flip for portfolios past n ~1000. Both scaffolds are deliberately reference-only and now include minimal auth/throttle/error-handling defaults, but they show the runtime split: same Python module serves laptop installs, Lambda hosting, and Modal/GPU endpoints.

### Changed

- Validator now recognizes adaptive follow-up policy, optional assay-power readiness gates, self-learning setup, and bridge-policy warnings without changing legacy single-wave demo behavior.
- Public skill and non-claims now describe adaptive follow-up outputs as planning artifacts rather than optimization or validated transfer.
- `docs/DOE_FAMILIES.md` and `README.md` FAQ rewritten to reflect that the repo now generates first-batch designs in stdlib instead of deferring to a harness adapter.
- `SKILL.md` step 5 renamed to "DoE selection and generation" and points the agent at `ferm-doe generate-design` to produce `expected/selected_wave_1_design.csv`.

## [0.1.0a0] - 2026-05-05

First public-prep release. Pre-alpha; schema and validator behavior may change.

### Added

- Profile registry (`screening`, `optimization_rsm`, `mixture`, `split_plot_fed_batch`, `scale_up_bridge`, `scale_down_qualification`, `confirmation`, `sequential_augmentation`, `custom`). Profiles are composable.
- `arms[]` block for multi-arm campaigns (reference / target / qualification, etc.).
- `scale_context` block: `from_scale`, `to_scale`, geometry, engineering targets (kLa, P/V, tip speed, mix time, DO, OUR, RQ, VVM, custom), `bridge_strategy`, `bridge_factors`, `known_offsets`, `qualification_evidence`, `recapitulation_criterion`.
- Per-axis `readiness` state (responses, factors, arms, scale_context, doe, decision_rules, evidence, feasibility) replacing the prior single string enum.
- Factor-type taxonomy: `numeric`, `categorical`, `ordinal`, `mixture`, `temporal_profile`, `block`, `hard_constraint`.
- DoE family taxonomy with minimum-runs guidance: definitive_screening, plackett_burman, fractional_factorial, full_factorial, central_composite, box_behnken, optimal_d, optimal_i, scheffe_mixture, extreme_vertices_mixture, split_plot, custom_constrained, sequential_augmentation.
- `decision_rules`, `stop_rules`, `risk_register`, `assumptions`, `waves` blocks.
- JSON Schema (`schemas/campaign_manifest.schema.json`).
- Four public demos: `demo-xylanase-public` (screening), `demo-scale-bridge-public` (scale_down_qualification), `demo-split-plot-fedbatch-public` (split_plot_fed_batch), `demo-warnings-walkthrough-public` (diagnostic).
- CLI `--summary` mode, `--out FILE`, and `# audit-skip: <reason>` line markers.
- Renamed console script from `ferm-doe-public` to `ferm-doe`.
- Optional `make secret-scan` target (gitleaks) and matching CI step.
- Agent harness configs: `agents/openai.yaml`, `agents/claude.md`, `agents/generic.md`, `agents/linear.md`.
- Documentation: `docs/PROFILES.md`, `docs/SCALE_BRIDGE.md`, `docs/DOE_FAMILIES.md`, `docs/AGENT_HARNESSES.md`, canonical `NON_CLAIMS.md`.
- Manifest and run-packet templates in `templates/`.
- CI matrix: Python 3.10 / 3.11 / 3.12 / 3.13.
- `BIOSAFETY.md`: scope statement, framework references (WHO BMBL 4th ed, NIH Guidelines, CDC/NIH BMBL, NIH DURC 2024), and the agent's biorisk-relevance heuristic. The skill does not gate on biosafety; the agent surfaces a focused question to the operator when the manifest signals biorisk-relevant context, then proceeds.
- Biosafety-relevant-context paragraph in `SKILL.md` and a brief bullet in each `agents/*.md` config.
- One sentence in `NON_CLAIMS.md` pointing campaigns involving high-containment work, recombinant DNA at scale, or operator-judged dual-use research toward IBC review and the frameworks listed in `BIOSAFETY.md`.
- `biosafety-aware` topic on the README and `biosafety` keyword in `pyproject.toml` and `CITATION.cff`.

### Changed

- Validator philosophy: guidance, not gating. Most checks emit warnings; errors reserved for structural/public-safety failures and contradictory declarations.
- `cli.py` reduced to a thin dispatcher; engine moved to `validators.py`.
- Factor-type checks (mixture, categorical, etc.) emit warnings on absence; errors reserved for contradictory bounds.
- `make release-check` now validates all four demos (three clean, one diagnostic).

### Notes

- Stdlib-only at runtime. The JSON Schema is for consumers; runtime validation is hand-rolled in stdlib for the moat.
- All demos use synthetic or public-source data only. Engineering numerical targets in the scale-bridge demo are illustrative placeholders.
- Pre-alpha: API and schema may change before `0.1.0`.
