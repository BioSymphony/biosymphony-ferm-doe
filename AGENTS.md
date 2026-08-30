# BioSymphony Ferm DoE Agent Guide

Public workspace for BioSymphony Ferm DoE.

## Mission

Help users and their agents drive long-horizon, multi-agent bioprocess design campaigns from intake through follow-up. The repo is a skill any agent harness can pick up: Symphony with Linear, Claude Code workers with Linear, Codex CLI, OpenAI Agents SDK, or a custom orchestrator, running on a laptop, in CI, or behind AWS Lambda or Modal. The agent and the human share one durable artifact (`campaign_manifest.json`), pause, resume, hand off, and converge on a fermentation campaign that is ready for review.

The repo ships:

- profile registry (screening, optimization_rsm, mixture, split_plot_fed_batch, scale_up_bridge, scale_down_qualification, confirmation, sequential_augmentation, custom)
- scale_context block (multi-criterion: kLa, P/V, tip_speed, mix_time, DO, OUR, RQ, VVM, geometric_similarity, custom)
- multi-arm (`arms[]`) campaigns
- per-axis readiness state (responses, factors, arms, scale_context, doe, decision_rules, evidence, feasibility)
- decision_rules / stop_rules / risk_register / assumptions blocks
- DoE family taxonomy with minimum-runs guidance
- a curated BO/DoE and sidecar registry with documented adapter routing (`docs/TOOL_REGISTRY.md`, `docs/tool-registry.json`)
- BoFire, ENTMOOT v2, OMLT, TabPFN, BoTorch, pyDOE3, SALib, scipy, PubMed MCP adapters that degrade cleanly when the optional extra is absent
- a cumulative dossier pattern (per-corpus swarm plus integrator plus harvester) backed by `provenance.py` and `rocrate_retrofit.py`
- a cost-model honesty stack (simulator, bulk reagent, fully-loaded COGS, CMO, range)
- JSON Schema for the manifest plus Frictionless table contracts for CSV inputs
- issue-pack and task-request contracts that let an orchestrator fan work across parallel sub-agents and converge results
- AWS Lambda and Modal scaffolds so the same commands run from a laptop, from CI, or behind a stateless cloud endpoint
- public-safety audit and validators

## Public Safety Rules

Do not add:

- private strain details
- unpublished sequences
- customer batch records
- confidential media formulations
- API keys or provider credentials
- private workstation paths
- private issue-tracker / team / project identifiers
- raw private campaign artifacts

Use synthetic or public-source examples only, label synthetic data clearly.

## Current State

- README plus workflow images
- public-safe `SKILL.md` with long-agent loop
- canonical `NON_CLAIMS.md`
- profile registry (9 profiles), scale_bridge framework, DoE family taxonomy (14 families), JSON Schema, table contracts
- adapters for BoFire, ENTMOOT v2, OMLT, TabPFN, BoTorch, pyDOE3, SALib, scipy, PubMed MCP
- public demos: twelve campaign-shaped demos covering screening (xylanase, PB screening, warnings-walkthrough), scale_down_qualification (scale-bridge), split_plot_fed_batch, BoFire routes (media cost, shakeflask-to-2L), ENTMOOT NChooseK smoke, multi-arm scale transfer, reference DOE custom design, public-paper starter (xylanase-wxz1-2012), and product-class starter (yeast-isoprenoid-2L-fedbatch); plus the `adaptive-backend-eval` and `starter-studies` auxiliary fixtures
- reference docs: GLOSSARY, CLI_REFERENCE, ADAPTER_MAP, DOE_FAMILY_RECIPES, WAVE2_BOTORCH, ISSUE_PACK_GENERATION, BACKEND_EVAL_FINDINGS, ADAPTER_DESIGN_NOTES
- Python package scaffold (stdlib-only at runtime; optional extras route through adapters)
- AWS Lambda and Modal deploy scaffolds in `deploy/`
- public-safety tests, per-validator tests, adapter tests, dossier provenance tests; 455 tests pass with 38 expected skips

## Long-Agent Loop

See `skills/biosymphony-ferm-doe/SKILL.md`. Summary: intake, readiness gate, factor framing, scale framing, DoE selection, run packet, follow-up review. Refuse on missing required blocks for declared profiles, missing assayed-response contracts, and public-safety violations. Warn on profile-advised gaps and DoE family minimum-runs shortfalls.

## Key Pattern And Convention

- Treat public examples as synthetic contract fixtures, not campaign records.
- Keep campaign routing explicit through `task_request` contracts; do not activate heavy campaign workflows for ordinary validation or docs tasks.
- Keep issue packs tracker-neutral until a private campaign maps pack-local IDs to a tracker.
- Preserve arm scope in DOE artifacts: per-arm design CSVs are authoritative; horizontal DOE tables are review surfaces.
- Prefer stdlib/offline code paths in the public package; optional scientific dependencies must degrade cleanly.
- Bounded workers (parallel sub-agents, swarm corpora, integrator and harvester roles) are coordinated through `task_request` contracts and the cumulative-dossier pattern, not ad-hoc dispatch.
- One coherent dossier per campaign (`CITATIONS.json`, `NOTES.md`, `SOURCES.bib`, per-corpus `EVIDENCE.csv`), not N isolated reports.

## Risks To Watch

- Do not turn public demos into implied lab-validation or production-readiness claims.
- Watch for accidental private paths, provider IDs, issue-tracker IDs, private biological details, or copied article tables before release.
- Keep scale-transfer wording at planning or qualification status unless executed bridge evidence is present.
- Keep warnings deterministic so public demos remain useful regression fixtures.
- When BoFire's `SoboStrategy` plus `NChooseK` is requested, route to ENTMOOT v2 or OMLT, or enforce cardinality post-hoc. The repository's supported BoFire 0.3.x adapter retains this compatibility limit; do not generalize it to untested upstream releases.
- When the simulator drives the planner, declare `simulator.fidelity_level` on the manifest and run the literature pressure-test template before sealing a campaign.

## Next Best Work

1. Keep all demos complete, deterministic, and clearly synthetic; the diagnostic walkthrough should continue to surface intentional guidance warnings.
2. Extend validators only with public-safe logic and fixtures.
3. Keep `make release-check` passing before any public push.
4. Add new demos under public-safe artifact folders when more profiles see use.
5. Re-run history and tree scans before first remote publication.
6. When new DoE adapters land, label their claim level and route reason in the tool registry.

## Claim Boundaries

This repo validates measurement readiness, manifest structure, and profile fit before lab work. It does not validate actual lab measurements unless result rows are ingested with provenance and QC evidence.

Do not claim optimized, validated, production-ready, or GxP-ready behavior.
