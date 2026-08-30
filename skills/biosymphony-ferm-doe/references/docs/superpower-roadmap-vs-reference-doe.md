# Planning Roadmap vs Reference DOE

## Point Of View

Commercial DOE software is already strong at classical and modern DOE once the experiment has been statistically framed. BioSymphony Ferm DoE should not pretend that a generic checklist beats that baseline.

The planning workflow starts earlier and covers more context:

```text
messy bioprocess ask
  -> campaign state compiler
  -> scientific readiness gates
  -> multi-agent strategy tournament
  -> DOE backend selection and scoring
  -> review-ready planning dossier
  -> tracker issue DAG
  -> result ingestion and follow-up planner
```

The repo should pair documents with structured campaign state, validators, design scoring, and memory. Those artifacts give an agent enough context to plan and review work consistently.

## Current State

```mermaid
flowchart LR
  A["What exists now"] --> B["Campaign state compiler"]
  A --> C["Readiness gates and workflow checks"]
  A --> D["Constraint and model-matrix core"]
  A --> E["reference DOE candidates"]
  A --> F["Tournament and dossier compiler"]
  A --> G["follow-up ingestion and memory"]

  B --> H["Typed campaign artifacts"]
  C --> I["RED/YELLOW/GREEN gatekeeping"]
  D --> J["Rank, estimability, D/I/A/G, FDS labels"]
  E --> K["Screening, RSM, mixture, space filling, custom optimal"]
  F --> L["Planning packet plus parity reports"]
  G --> M["Confirm/narrow/expand/pause/stop/scale"]
```

Current status: local engine baseline. It has structured campaign compilation, deterministic DOE candidates, model-matrix diagnostics, design comparison, readiness checks, dossier generation, dry-run issue packs, and follow-up ingestion. It does not claim complete commercial DOE statistical parity where local implementations are labeled approximate or heuristic.

## Reference DOE Baseline

Commercial DOE documentation sets a real benchmark:

- Custom design support for real constraints, process limitations, and budgets.
- Screening support for full factorial, fractional factorial, Plackett-Burman, mixed-level screening, and definitive screening designs.
- Response-surface, mixture, space-filling, and augmentation workflows.
- Design evaluation with power analysis, prediction variance profiles, fraction-of-design-space plots, alias matrices, correlations, and efficiency diagnostics.
- Optimality criteria including D-, I-, A-, Bayesian, and alias-optimal variants.

Implication: BioSymphony Ferm DoE should not compete by manually rephrasing DOE. It is designed to cover the surrounding work: problem formation, evidence gathering, assay/process readiness, phase-aware bioprocess planning, agent tournaments, planning packets, and adaptive campaign memory.

## Where BioSymphony Must Be Better

| Layer | Reference DOE Strength | BioSymphony Ferm DoE Planning Strength |
| --- | --- | --- |
| Factor table | Strong once factors are known | Infer and challenge candidate factors from biology, vessel, product class, phases, observability, prior data, and literature |
| Experimental design | Strong optimal/custom designs | Choose among DOE strategies using campaign context, feasibility, assay risk, and future follow-up value |
| Constraints | Strong mathematical restrictions | Convert lab reality into constraints: sampling load, pH/base demand, feedability, foam, oxygen demand, cost ceiling, run duration |
| Response definition | User supplied | Force response semantics: titer, productivity, yield, product per biomass, quality, whole-broth vs pellet-associated product |
| Scale transfer | Not the main product | Treat flask-to-bioreactor, scale-up, and downscale as first-class workflow modes |
| Literature priors | Outside reference DOE | Dispatch agents to PubMed, bioRxiv, Google Scholar, protocols, and prior runs, then convert evidence into factor priors |
| Planning packet | Table-centric | Produce a run-sheet draft, sampling schedule, reagent plan, capture schema, control strategy, and follow-up rules |
| Campaign memory | Manual | Store negative-result memory and feed it into the next compiler pass |

## Target Architecture

```mermaid
flowchart TD
  U["Scientist ask"] --> C["Campaign State Compiler"]

  C --> S1["System state: organism, product, vessel, phases"]
  C --> S2["Inputs: recipe, reagents, prior runs, literature"]
  C --> S3["Observability: pH, DO, offgas, biomass, assays"]
  C --> S4["Constraints: cost, time, capacity, sampling, controls"]
  C --> S5["Goals: titer, productivity, yield, robustness, cost"]

  S1 --> R["Readiness Gate Engine"]
  S2 --> R
  S3 --> R
  S4 --> R
  S5 --> R

  R --> T["Multi-Agent Design Tournament"]
  T --> A["Classical DOE lane"]
  T --> B["Adaptive/Bayesian lane"]
  T --> P["Process-engineering lane"]
  T --> Q["Assay skeptic lane"]
  T --> L["Literature-prior lane"]
  T --> K["Cost/time lane"]

  A --> J["Adjudicator"]
  B --> J
  P --> J
  Q --> J
  L --> J
  K --> J

  J --> D["Selected design and control-run plan"]
  D --> O["ferm-doe-dossier"]
  O --> X["Tracker issue DAG"]
  O --> Y["Optional remote evaluation bundle"]
  O --> Z["follow-up decision rules"]
  Z --> C
```

## Workflow Modes

Packs should represent bounded workflow modes. They should accelerate the planner without limiting reasoning.

| Mode | What It Handles | Non-Negotiable Guardrails | Decision Test |
| --- | --- | --- | --- |
| `autonomous-multi-agent-doe-planner` | Any culture or fermentation optimization ask | Must produce competing design strategies, not one default DOE | Does the planner produce a tournament and adjudication rubric? |
| `shake-flask-to-benchtop-bioreactor` | Flask recipe to controlled pH/DO/feed run | Must address pH drift removal, oxygen transfer, inoculum basis, foam, feedability, and response comparability | Does it catch what breaks when moving from uncontrolled flask to controlled reactor? |
| `batch-to-fedbatch-production` | Growth phase, induction/switch, production feed, harvest | Must separate growth and production factor spaces | Does it prevent one flat DOE from mixing phase-specific knobs? |
| `bioreactor-scale-up-planner` | 2 L to larger scale | Must address kLa/OTR, mixing, heat, pH/base demand, sensor/control differences | Does it turn scale transfer into constraints, not vibes? |
| `bioreactor-to-plate-downscale` | Cheaper scouting route | Must address evaporation, edge effects, oxygen, mixing, fill volume, assay throughput, scale relevance | Does it tell us what plate results can and cannot mean? |
| `biomanufacturing-cost-productivity-minimizer` | Titer/productivity/cost/time tradeoff | Must score final titer against productivity, cost per L, run length, and sampling burden | Does it recommend an earlier harvest if economics support it? |
| `assay-product-class-planner` | Product-class response semantics | Must distinguish extracellular, intracellular, pellet-associated, volatile, activity, quality | Does it block a wrong response definition before DOE? |

## Pack Design Rule

A pack is allowed only if it provides at least one of these:

- a schema the planner must fill
- a validator that can fail
- a scoring function or objective transform
- a known failure-mode lint
- an issue graph that saves orchestration time
- a benchmark example with expected outputs

If a pack is only advice that a strong planner can invent in one paragraph, do not add it.

## What To Harden Next

1. Optional DOE adapters
   - Add pyDOE3/SciPy/statsmodels/scikit-learn adapters where they improve exactness.
   - Keep stdlib fallback and metric labels.

2. Bayesian and augmentation adapters
   - Add BoFire/BoTorch only behind optional extras.
   - Preserve local augment-design fallback for users without GPU/cloud.
   - **BoFire scope:** treat as a focused powerup (constrained DoE,
     multi-objective BO, multi-fidelity scale-bridge), not a runtime
     replacement. Routing rule and high-ROI scenarios in
     [`BOFIRE_POSITIONING.md`](BOFIRE_POSITIONING.md). Defer adapter
     until BoFire 0.4 ships (multi-fidelity PR #705 and LLM-Strategy
     PR #749 are on main but not yet tagged).

3. More fermentation examples
   - Add sanitized public/synthetic ledgers for plate, flask, fed-batch, downscale, and mixture-media cases.
   - Keep public paper data separate from inferred or synthetic planning data.

4. Optional remote-compute dry-run bundle
   - Only after local tests and dossier checks are boring.
   - No live launch unless explicitly requested.

5. UI or notebook surface
   - Defer until the file/CLI contract remains stable across real campaigns.

## Success Criteria

The workflow is valuable when it improves the decision made before a lab run.

For every workflow, ask:

1. Did it prevent a bad experiment?
2. Did it discover a better objective or response definition?
3. Did it make scale transfer explicit?
4. Did it create a design that is more feasible under the stated constraints than a generic DOE table?
5. Did it produce artifacts the lab can review and adapt without losing context?
6. Did it produce rules for what to do after results arrive?

If the answer is no, the pack adds documentation without adding an operational capability.
