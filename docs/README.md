# BioSymphony Ferm DoE Docs

This repo is a skill you point a coding agent at. Start with the agent prompt and the demo, then branch into the domain or adapter surface you need.

## Start Here

- [`../README.md`](../README.md): install, agent prompt, CLI surface, FAQ.
- [`AGENT_QUICKSTART.md`](AGENT_QUICKSTART.md): extended agent prompt and first commands with expected outputs.
- [`product-brief.md`](product-brief.md): one-page thesis and product unit.
- [`VISUAL_OVERVIEW.md`](VISUAL_OVERVIEW.md): diagrams for experiment inputs, scale-transfer criteria, and DoE family selection.
- [`USE_CASES.md`](USE_CASES.md): workflow chooser and copy-paste agent requests.
- [`WORKFLOWS.md`](WORKFLOWS.md): local, agent, Linear, issue-pack, and cloud-resource workflow map.
- [`GLOSSARY.md`](GLOSSARY.md): short definitions of campaign, profile, claim level, scale context, arm, first-batch/follow-up checkpoints, run packet, dossier, adapter, kLa, NChooseK, and the rest.
- [`CLI_REFERENCE.md`](CLI_REFERENCE.md): single-page index of every `ferm-doe` subcommand.
- [`ADAPTER_MAP.md`](ADAPTER_MAP.md): capability-centric map of optional extras.
- [`superpowers.md`](superpowers.md): capability index.
- [`PUBLIC_ADOPTION_PATH.md`](PUBLIC_ADOPTION_PATH.md): from first clone, to repo-local skill, to agent harness.
- [`../examples/README.md`](../examples/README.md): demo chooser and expected validation statuses.

## Core Contracts

- [`PROFILES.md`](PROFILES.md): profile registry and composition rules.
- [`CONTRACTS.md`](CONTRACTS.md): public task request and design-packet contracts.
- [`data-model.md`](data-model.md): durable state model, result joins, and follow-up artifacts.
- [`dossier-generation.md`](dossier-generation.md): planning packet generation and contract checks.
- [`../schemas/campaign_manifest.schema.json`](../schemas/campaign_manifest.schema.json): manifest schema.
- [`../schemas/task_request.schema.json`](../schemas/task_request.schema.json): bounded agent task request schema.
- [`../schemas/tables/`](../schemas/tables): tabular input/output contracts.

## Planning Workflows

- [`DOE_FAMILIES.md`](DOE_FAMILIES.md): supported design families and claim levels.
- [`DOE_FAMILY_RECIPES.md`](DOE_FAMILY_RECIPES.md): manifest-patch recipes for swapping `doe.family` across the 14 supported generators.
- [`ADAPTIVE_WAVE2.md`](ADAPTIVE_WAVE2.md): first-batch result ingestion and follow-up planning.
- [`WAVE2_BOTORCH.md`](WAVE2_BOTORCH.md): follow-up walkthrough with the BoTorch backend (qEI / qUCB).
- [`adaptive-wave2-assay-power-v0.md`](adaptive-wave2-assay-power-v0.md): assay-power policy used by `ferm-doe assay-power`.
- [`SELF_LEARNING_DOE.md`](SELF_LEARNING_DOE.md): learning ledger, hiccup review, and negative memory.
- [`self-learning-doe-runbook.md`](self-learning-doe-runbook.md): operational runbook for the self-learning loop.
- [`SCALE_BRIDGE.md`](SCALE_BRIDGE.md): scale-up and scale-down framework.
- [`SCALE_BRIDGE_METHODOLOGY.md`](SCALE_BRIDGE_METHODOLOGY.md): bridge entry conditions and qualification protocol.
- [`COST_MODEL_REALISM_CHECK.md`](COST_MODEL_REALISM_CHECK.md): five-stack cost honesty pattern.

## Lessons And Methodology

- [`CROSS_CAMPAIGN_LESSONS.md`](CROSS_CAMPAIGN_LESSONS.md): methodology lessons distilled from running multiple campaigns end to end.
- [`starter-study-catalog.md`](starter-study-catalog.md): public starter-study curation.

## Agent Workflows

- [`AGENT_HARNESSES.md`](AGENT_HARNESSES.md): Claude Code, OpenAI Agents SDK, Codex CLI, and generic harnesses.
- [`ORCHESTRATOR_BOUNDARY.md`](ORCHESTRATOR_BOUNDARY.md): boundary between this skill pack and capable orchestrators.
- [`SWARMS_AND_EVIDENCE.md`](SWARMS_AND_EVIDENCE.md): research-support and source-tracking pattern for design rationale.
- [`sidecar-architecture.md`](sidecar-architecture.md): swappable sidecar packs and provider handoff boundaries.
- [`ISSUE_PACK_COOKBOOK.md`](ISSUE_PACK_COOKBOOK.md): issue-pack commands and pack chooser.
- [`ISSUE_PACK_GENERATION.md`](ISSUE_PACK_GENERATION.md): end-to-end runbook for `engine generate-issue-pack`, output anatomy, and orchestrator integration patterns.
- [`diagrams/agent-loop-public.mmd`](diagrams/agent-loop-public.mmd): source for the README public agent-loop diagram.
- [`../agents/`](../agents): runtime-specific agent configs.
- [`../packs/README.md`](../packs/README.md): goal, input, and issue packs.

## Adaptive Backends

- [`TOOL_REGISTRY.md`](TOOL_REGISTRY.md): curated BO/DoE tool registry.
- [`tool-registry.json`](tool-registry.json): machine-readable registry.
- [`BIOMANUFACTURING_ADAPTIVE_BACKENDS.md`](BIOMANUFACTURING_ADAPTIVE_BACKENDS.md): BoFire, BayBE, Ax/BoTorch, ENTMOOT, OMLT, and TabPFN routing surface plus the depth ladder.
- [`BACKEND_EVAL_FINDINGS.md`](BACKEND_EVAL_FINDINGS.md): dated six-fixture findings across seven backends, including the May 2026 OMLT and BoFire evaluation notes.
- [`ADAPTER_DESIGN_NOTES.md`](ADAPTER_DESIGN_NOTES.md): non-obvious adapter design decisions (OMLT lower-coupling, TabPFN Gaussian-approximation posterior wrap, BoTorch cost-weighting trap, MO BO memory knobs).
- [`adaptive-backend-evaluation.json`](adaptive-backend-evaluation.json): backend comparison fixture.
- [`BOFIRE_POSITIONING.md`](BOFIRE_POSITIONING.md): BoFire route boundaries.
- [`BOFIRE_CONSTRAINT_PATTERNS.md`](BOFIRE_CONSTRAINT_PATTERNS.md): strategy and constraint compatibility.
- [`ENTMOOT_SWAP_DESIGN.md`](ENTMOOT_SWAP_DESIGN.md): ENTMOOT v2 NChooseK adapter design.
- [`reference-doe-fast-path.md`](reference-doe-fast-path.md): reference DOE utility path.
- [`open-source-bioprocess-tool-survey-2026-05-15.md`](open-source-bioprocess-tool-survey-2026-05-15.md): bioprocess-specific landscape scan.
- [`research/bo-tools-survey-2026-05-16.md`](research/bo-tools-survey-2026-05-16.md): broader BO-tools landscape (LLAMBO, TabPFN v2, BayBE, BoFire main) that informed the ENTMOOT swap and TabPFN adapter routes.

## Technical Reference And Roadmap

- [`engine-implementation.md`](engine-implementation.md): what the local engine implements today.
- [`SIMULATOR_V2_SPEC.md`](SIMULATOR_V2_SPEC.md): simulator v2 spec (SPEC ONLY; not yet implemented).
- [`high-roi-doe-parity-strategy.md`](high-roi-doe-parity-strategy.md): parity strategy notes against commercial DoE tools.
- [`superpower-roadmap-vs-reference-doe.md`](superpower-roadmap-vs-reference-doe.md): roadmap delta against the reference DOE surface.

## Public Release

- [`PUBLIC_SECURITY_MODEL.md`](PUBLIC_SECURITY_MODEL.md): local-first privacy and deployment hardening boundary.
- [`RELEASE_READINESS_CHECKLIST.md`](RELEASE_READINESS_CHECKLIST.md): local public-switch checklist.
- [`PUBLIC_RELEASE_PREP.md`](PUBLIC_RELEASE_PREP.md): local release checklist.
- [`OPEN_DATA_PUBLICATION_STRATEGY.md`](OPEN_DATA_PUBLICATION_STRATEGY.md): open artifact packaging strategy.

## Scope And Policy

- [`../NON_CLAIMS.md`](../NON_CLAIMS.md): what the repo does not claim.
- [`../BIOSAFETY.md`](../BIOSAFETY.md): biosafety scope.
- [`../SECURITY.md`](../SECURITY.md): security policy.
