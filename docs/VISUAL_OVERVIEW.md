# Visual Overview

These diagrams summarize the main design questions in the repo: what varies, what is constrained, how scale transfer is handled, and which DoE family fits the campaign.

## Experiment Design Map

```mermaid
flowchart LR
  subgraph IN["Inputs"]
    direction TB
    O("objective") ~~~ R("responses") ~~~ F("factors") ~~~ C("constraints") ~~~ S("scale context")
  end
  subgraph CH["Design choices"]
    direction TB
    FAM("DoE family") ~~~ RB("runs & blocks") ~~~ RC("replicates & controls")
  end
  subgraph OUT["Outputs"]
    direction TB
    DM("design matrix") ~~~ RP("run plan") ~~~ MP("measurement plan") ~~~ NW("follow-up options")
  end
  IN ==> CH ==> OUT
  classDef proc fill:#fffdf8,stroke:#2b2926,color:#2b2926,stroke-width:1.5px;
  class O,R,F,C,S,FAM,RB,RC,DM,RP,MP,NW proc;
  style IN fill:#efeadd,stroke:#d9d2c0,color:#1b1b18;
  style CH fill:#efeadd,stroke:#d9d2c0,color:#1b1b18;
  style OUT fill:#efeadd,stroke:#d9d2c0,color:#1b1b18;
```

Start from the experiment inputs: objective, responses, factors, constraints, and scale context. These determine the DoE family, run structure, blocking, replication, controls, and measurement plan.

The useful check is direct: define what varies, what stays fixed, and what will be measured.

## Scale Transfer Criteria

```mermaid
flowchart LR
  SRC("source scale<br/>qualified data or stated basis"):::hero --> BR{"bridge criteria<br/>kLa · P/V · tip-speed<br/>mix-time · OUR · RQ · VVM<br/>geometric similarity"}:::gate
  BR -->|"all criteria met"| MATCH("Match → review"):::go --> TGT("target scale<br/>planning hypothesis"):::proc
  BR -->|"some gaps"| GAP("Gap → measure / estimate"):::gate
  BR -->|"not qualified"| RED("Revise → review the bridge"):::block
  classDef hero fill:#1b1b18,stroke:#d9d2c0,color:#ffffff,stroke-width:1.5px;
  classDef proc fill:#fffdf8,stroke:#2b2926,color:#2b2926,stroke-width:1.5px;
  classDef gate fill:#fffdf8,stroke:#b0892f,color:#8a6a1f,stroke-width:1.5px;
  classDef go fill:#fffdf8,stroke:#6f7d3f,color:#566230,stroke-width:1.5px;
  classDef block fill:#fffdf8,stroke:#bf5a3c,color:#a44a2f,stroke-width:1.5px;
```

Scale-up and scale-down decisions depend on criteria such as `kLa`, `P/V`, tip speed, mix time, DO/OUR, VVM, and geometry. The design should show what is measured, estimated, or missing before choosing the next run set.

The transfer review should record one of three outcomes: match, gap, or redesign.

## DoE Family Selection

```mermaid
flowchart LR
  Q{"What is the<br/>situation?"}:::hero
  Q -->|"many factors to screen"| SC("Screening<br/>PB · fractional"):::proc
  Q -->|"curved response surface"| RSM("RSM<br/>CCD · Box-Behnken"):::proc
  Q -->|"media / feed blend"| MX("Mixture<br/>simplex · extreme-vertices"):::proc
  Q -->|"hard-to-change setpoints"| SP("Split-plot"):::proc
  Q -->|"scale transfer"| SB("Scale bridge"):::proc
  Q -->|"after first batch"| SA("Sequential augmentation"):::go
  classDef hero fill:#1b1b18,stroke:#d9d2c0,color:#ffffff,stroke-width:1.5px;
  classDef proc fill:#fffdf8,stroke:#2b2926,color:#2b2926,stroke-width:1.5px;
  classDef go fill:#fffdf8,stroke:#6f7d3f,color:#566230,stroke-width:1.5px;
```

The DoE family changes run count, blocking, replication, and interpretation. Common routes include:

- screening for many factors
- RSM for curved response surfaces
- mixture designs for media blends
- split-plot designs for hard-to-change setpoints
- scale bridge designs for transfer criteria
- sequential augmentation after first-batch

The same campaign can move between families as data arrives.
