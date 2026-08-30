# Orchestrator Boundary

BioSymphony Ferm DoE is built for capable long-horizon agents, not as a
closed standalone application. A user may run it through Codex, Claude Code,
Symphony plus Linear, a goal-driven coordinator, or another agent harness
that can read files, edit manifests, run validators, dispatch workers, and use
local or cloud resources.

This matters when reviewing "missing pieces." Some gaps belong in this repo.
Many do not. If a capable orchestrator can fill a step from durable contracts,
templates, validators, and handoff artifacts, the repo does not need to embed
that step as product machinery.

## What This Repo Should Own

- Campaign contracts: manifests, task requests, sidecar packs, issue templates,
  and schema-level expectations.
- Deterministic checks: validators, readiness scoring, artifact contract checks,
  and fail-closed route reports.
- Planning artifacts: factor spaces, constraints, design candidates, dossiers,
  run packets, follow-up rules, and evidence table formats.
- Claim boundaries: readiness verdicts, planning vs execution labels, scale
  bridge limits, cost-stack honesty, and negative-control expectations.
- Reusable worker briefs: evidence execution, assay readiness, factor audit,
  design tournament, remote smoke, and closeout instructions.
- Resume paths: `AGENTS.md` handoffs, dated notes, ledgers, and
  machine-readable closeouts.

The repo adds value by making a capable agent's work structured,
auditable, resumable, and safer. The agent's decisions remain visible in the
manifest and handoff artifacts.

## What The Orchestrator Should Own

- Turning a user's high-level goal into the next bounded task or issue graph.
- Deciding whether work runs locally, in a tracker-backed lane, or on an
  approved cloud lane.
- Sequencing and monitoring workers, including Symphony plus Linear workers or
  goal-driven task runners.
- Reading messy inputs, asking a small number of high-leverage questions, and
  making explicit assumptions when the user chooses to proceed.
- Installing optional extras in an isolated environment when a route needs
  them, then recording dependency and compute evidence.
- Fetching, validating, hashing, and cleaning up remote artifacts when paid
  provider resources are used.
- Writing final synthesis, report sections, and operator-facing explanations
  from the durable artifacts.

These are orchestration responsibilities. They should be expressed as
contracts and runbooks here, not reimplemented as a permanent in-repo daemon.

## Missing Versus Orchestratable

Treat something as a real repo gap when one of these is true:

- The agent cannot tell what artifact to create next.
- The expected input, output, acceptance check, or fail-closed behavior is not
  specified anywhere.
- A claim cannot be validated or bounded by an existing check.
- A safety boundary is ambiguous enough that a capable agent could plausibly
  overclaim lab readiness, scale transfer, cost realism, or remote success.
- The same manual judgment is repeated across campaigns and should become a
  reusable template, validator, or ledger field.

Do not treat something as a repo gap merely because:

- There is no GUI, background daemon, or all-in-one workflow runner.
- Linear, Symphony, Codex, or Claude Code is expected to create and sequence the
  work graph.
- The next step is obvious to a capable agent after reading the manifest,
  handoff, and validator output.
- Optional cloud execution is present only as a launch bundle, provider
  handoff, or remote-worker contract.
- A report section needs synthesis from existing artifacts rather than another
  deterministic engine command.

The useful question is: "Can an agent like Codex resume this campaign, know the
next safe action, run it with local or cloud resources, and leave auditable
artifacts?" If yes, the workflow may be complete enough even without more
built-in automation.

## Goal-Driven Orchestration Patterns

A goal-driven setup should translate the user's goal into:

1. A campaign manifest or task request.
2. A small set of bounded artifacts to produce first.
3. A local validation command.
4. Optional issue packs for parallel research, feasibility, design, or review.
5. Optional provider launch bundles for remote execution.
6. A closeout file that records outputs, validation, assumptions, and next
   actions.

Symphony plus Linear follows the same shape, but the bounded artifacts become
Linear issues with dependencies, acceptance criteria, and outcome comments.
Most work should remain in Backlog until the first readiness wave proves the
contract loop.

Use `ferm-doe agent-brief <campaign_dir>` to generate a compact JSON or
Markdown kickoff artifact for this pattern.

## Compute Boundary

Local and cloud lanes are interchangeable only when they preserve the same
contract:

- explicit inputs
- exact command or worker brief
- timeout and budget policy
- progress or heartbeat signal for long runs
- expected artifacts
- validation commands
- hash/cleanup evidence for remote runs
- claim boundary

Remote providers are execution substrates. They do not become the campaign
brain. A provider `RUNNING` state, cloud console screenshot, or worker
heartbeat is not success; success requires fetched artifacts, validation,
hashes, and cleanup proof when cleanup is declared.

## Review Heuristic

When reviewing this repo, avoid scoring it like a monolithic app. Score it like
an agent skill pack:

- Does it help a capable agent start from a messy bioprocess goal?
- Does it force the agent to leave structured evidence instead of prose only?
- Does it preserve the difference between planning, validation, and physical
  execution?
- Does it let the user choose local or cloud resources without changing the
  scientific contract?
- Does it make pause/resume and multi-agent handoff concrete?

If those answers are yes, the repo is doing the intended job even when a
human-agent orchestrator supplies the glue.
