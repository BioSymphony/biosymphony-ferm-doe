# High-ROI DOE Parity Strategy

BioSymphony Ferm DoE should respect commercial DOE software without trying to become a rigid clone of it too early.

The highest ROI is not "reimplement every DOE family." The highest ROI is making the experiment worth designing in the first place, then giving statisticians and DOE tools clean, auditable inputs when exactness matters.

## Product Stance

Commercial DOE tools are strong after the problem has been statistically framed. BioSymphony Ferm DoE should be strongest before and around that moment:

- define the real response and objective
- detect missing or weak assays
- turn vessel, sampling, reagent, analytics, and staffing reality into constraints
- separate plate/flask/reactor arms and phase-specific factors
- gather evidence and prior-run caveats
- produce a planning packet for lab review
- pre-register what follow-up will do with results
- export clean DOE tables when commercial software or statistician review is appropriate

Local DOE generation is a fast planning path. It should be useful, deterministic, and honest about exact versus approximate metrics. It should not claim JMP/Design-Expert/Modde parity unless a matching method is adapter-backed and the parity evidence is documented.

## Highest-ROI Work

### 1. DOE Export And Round-Trip

Build clean export artifacts that a DOE/statistics user can inspect or import:

- factor table with units, types, bounds, categorical levels, fixed controls, hard-to-change flags, and arm IDs
- response table with direction, measurement type, assay method, sample fraction, transformation, and acceptance criteria
- constraint table with forbidden combinations, mixture sums, run exclusions, capacity limits, and rationale
- run table with run IDs, blocks, randomization, controls, decoys, and holdout/fixed rows
- `assumptions_and_nonparity.md` stating which local metrics are approximate or heuristic

Why this is high ROI: it lets BioSymphony own scientific readiness while letting commercial/statistician workflows own exact design refinement when needed.

### 2. Bad-Experiment Diagnostics

Prioritize validators that prevent wasted physical execution work:

- rank and estimability failures
- categorical aliasing using Cramer's V or equivalent contingency-table metrics
- constant or near-constant factors after projection
- over-budget sampling or analytics throughput
- missing controls, missing replicates, weak center/lack-of-fit structure
- assay dynamic range, matrix effects, standard curve, and turnaround blockers
- synthetic or low-trust historical data masquerading as validation

Why this is high ROI: a simple diagnostic that says "do not run this yet" saves more than an elaborate DOE family that produces a polished but unlearnable plan.

### 3. Constrained Custom Design And Augmentation

Improve constrained selection where it changes actual lab decisions:

- respect fixed controls and already-committed rows
- handle hard run budgets and vessel/plate capacity
- preserve randomization/blocking constraints
- output an auditable selection trace
- support augmentation after first-batch results

Why this is high ROI: fermentation teams frequently need "best next 8-16 runs under messy constraints," not a full catalog of idealized designs.

### 4. Result-Ingestion Loop

Harden the loop from physical-execution results back into planning:

- ingest executed results with provenance and trust scores
- exclude QC-failed, excluded, and low-trust rows from recommendation logic
- preserve negative-result memory and excluded regions
- update response noise, replicate assumptions, and assay-power status
- recommend confirm, narrow, expand, pause, stop, downscale, or scale
- generate follow-up candidate rows with pre-registered decision rules and a `planned_wave2_design` claim boundary

Why this is high ROI: the system becomes a campaign planner, not a one-shot document generator.

### 5. Optional Exact Adapters

Add exact or adapter-backed methods only after the workflow needs them:

- custom optimality metrics when local approximations decide between competing designs
- exact screening/RSM/mixture generators when a user or statistician needs a familiar design class
- Bayesian/adaptive adapters only after result ingestion and stopping rules are reliable

Every adapter should emit a `utility_manifest.json` with backend, dependency status, method labels, artifacts, and caveats.

## Lower-ROI For Now

Defer these unless a real campaign forces them:

- full commercial DOE parity across every design family
- GUI-first DOE construction
- automatic proprietary software file generation before CSV round-trip is stable
- Bayesian optimization before empirical ingestion is trustworthy
- full GxP validation package
- autonomous purchasing or inventory reservation
- robotics, LIMS, ELN, or real-time PAT/control integration

## Decision Rule

Before adding DOE capability, ask:

1. Will this prevent a bad experiment?
2. Will it make a design more feasible under its stated constraints?
3. Will it clarify a response, assay, constraint, or scale-transfer assumption?
4. Will it produce a proof artifact a scientist/statistician can audit?
5. Will it improve follow-up decisions after results arrive?

If the answer is no, keep it as an optional adapter idea, not a core skill rule.
