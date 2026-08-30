# BoFire positioning in biosymphony-ferm-doe

Status: adapter boundary implemented · 2026-05-15

## The question

`bofire` was listed in `[adaptive]` extras, in `SUPPORTED_BACKENDS`, in
`BACKEND_MODULES`, and as a target backend in the parity matrix
(`parity.py:80`: `target_status = "optional_bofire_botorch_adapter"`),
but there was no BoFire runtime boundary.

That gap is now closed as an optional adapter:

- `src/biosymphony_ferm_doe/adapters/bofire_strategy.py`
- `src/biosymphony_ferm_doe/adaptive_wave2.py` routed dispatch
- `bofire_strategy_report.json` in sequential packets when the route fires

The adapter still preserves the stdlib-first posture. It imports BoFire
only inside the execution path and records a route/fallback report when
BoFire is not installed.

The question this doc answers: should we close that gap by writing a
BoFire-backed adapter, and if so, how much of BoFire's worldview do
we adopt?

## License and funding

BoFire is **free** and **BSD-3-Clause licensed**. You can use it in
commercial work without paying anyone. BoFire is mature and actively
maintained because the **Bayer team employs the maintainers as part of
their day jobs**. Bayer funds the engineering, but the code is fully
open. There is no commercial tier, no enterprise license, no hidden
cost. The strategic risk is upstream priority drift (Bayer's roadmap
differs from yours), not licensing.

## The two framings

**Destination.** "biosymphony becomes a thin manifest layer over BoFire.
Domain replaces our manifest as the source of truth. Strategy replaces
our wave-planner. Manifests serialize to BoFire JSON."

This is wrong. It abandons the moat (see *What biosymphony actually
does that BoFire doesn't*) for a substrate, and exposes the project
to BoFire's release cadence and roadmap.

**Powerup.** "biosymphony has a BoFire-backed adapter that activates
when a campaign needs Bayes opt under constraints or with multiple
objectives. Manifest stays canonical; adapter translates at the
boundary."

This is right. It closes a real correctness gap (manifest accepts
`constraints[]` that the engine currently ignores) without surrendering
the fermentation-specific layer.

## What biosymphony actually does that BoFire doesn't

1. **Fermentation time/phase modeling**, including induction timing,
   fed-batch feed profiles, and harvest decisions. BoFire models
   reaction-step DoE, not multi-phase processes.
2. **Cumulative-dossier evidence across campaigns**, including
   CITATIONS / EVIDENCE / NOTES / BibTeX. BoFire serializes per-campaign,
   not cross-campaign.
3. **Handoff packet artifacts**, including run packets, operator intake,
   and equipment-capacity tracking. BoFire targets the modeler; biosymphony
   targets the bench scientist.
4. **Parity-matrix honesty.** The engine refuses to claim full
   reference-DoE parity without validation artifacts. BoFire ships
   features; biosymphony ships qualified claims.
5. **Stdlib-first core.** The engine runs on a base Python install.
   BoFire requires PyTorch + GPyTorch + its own runtime.
6. **Example pedagogy.** Designed to be teachable, not just
   functional.

None of those overlap with BoFire's strengths. Sublimating them to
BoFire would lose the moat.

## What BoFire is actually good at

Strip the marketing and the load-bearing differentiation is narrower
than the docs make it look:

1. **Constrained DoE generation.** Augmented D-optimal under linear,
   nonlinear, and n-choose-k constraints. Their flagship.
2. **Multi-objective Bayes opt.** qNEHVI / qParEGO on tap with
   reasonable defaults. Pareto frontier, not scalarized objective.
3. **Mixed continuous/discrete/categorical search spaces** with
   constraints, handled natively, including conditional infeasibility.
4. **Multi-fidelity planning.** Low-fidelity evaluations can inform
   the same model that learns higher-fidelity evaluations. The inspected
   `0.3.1` API exposes `MultiFidelityStrategy`; it is sequential and
   requires every declared fidelity to have at least one observation.
5. **LLM-warmstart Strategy.** Promising for dossier-informed BO,
   but not part of this adapter yet. Treat it as research-grade until a
   tagged release and validation artifact make it load-bearing.

## When to reach for BoFire (the routing rule)

```
If (
   campaign.constraints[] has any non-box constraint
   OR campaign.responses[] has >=2 directions to optimize
   OR campaign treats plate / flask / bioreactor as multi-fidelity arms
   OR the operator requested --backend bofire
)
AND the requested backend is not a hard-off backend such as stdlib/botorch
THEN dispatch the wave-N adaptive step to adapters/bofire_strategy

If BoFire is importable, the adapter tries to emit BoFire-backed
candidates. If BoFire is missing or a manifest constraint cannot yet be
translated safely, the adapter writes `bofire_strategy_report.json` and
falls back to the existing stdlib augmentation path.
```

This is opt-in and load-bearing only when the manifest declares
something the current engine cannot honestly serve.

## High-ROI fermentation scenarios

These are the cases where the BoFire-backed adapter would deliver
measurable, defensible wins over today's `botorch_wave2.py`. Anchor
new adapter work on hitting at least three of these.

### Scenario A, constrained media optimization

Manifest declares 5 carbon sources, a trace-metals package (binary),
and a vitamin cocktail level (continuous). Constraints:

- Total carbon ≤ 100 g/L (linear constraint on a continuous sum)
- At most 2 carbon sources at > 0 (n-choose-k)
- Trace metals present only when vitamin cocktail level > 1× (conditional)

**Today:** stdlib design generators emit full-factorial / box-sample
points. They ignore everything but `low` / `high`. Designs include
many infeasible rows; experimenters drop them by hand. A 32-run plate
study can lose 40-60% of vessels to manually-filtered infeasibility.

**With BoFire adapter:** augmented D-optimal under constraints. Every
row in the generated design is feasible. Same vessel count, all
informative.

**Measurable win:** % of generated runs that are interpretable
post-handoff. Target: ≥ 95%.

### Scenario B, multi-objective Pareto search

Cell-line optimization with simultaneous targets:

- Maximize titer (g/L final)
- Maximize specific productivity (qP, pg/cell/day)
- Minimize lactate at harvest (g/L)
- Minimize ammonia at harvest (mM)

**Today:** `botorch_wave2.py` does single-objective qEI. The only way
to handle four objectives is to scalarize with weights ("titer −
α·lactate − β·ammonia + γ·qP"), and those weights are guesses that
encode arbitrary preferences. You cannot answer "what is the trade-off
between titer and lactate?"; you only get one number.

**With BoFire adapter:** qNEHVI (hypervolume-based BO) explicitly
targets the Pareto frontier. After N runs, you have a set of designs
spanning the trade-off surface, ready to present to the scientist as
options.

**Measurable win:** a Pareto front instead of a single optimum.
Decision-quality improvement, not just numerical improvement.

### Scenario C, plate to flask to bioreactor scale-bridge

Three scales as fidelity tiers:

- Plate (96-DW): cheap, 4-day cycle, low-fidelity signal
- Flask (250 mL): medium cost, 7-day cycle, mid-fidelity
- Bioreactor (5 L): expensive, 14-day cycle, high-fidelity

**Today:** three independent BO arms with hand-rolled coupling rules
("top 6 plate conditions advance to flask"). The plate-to-flask transfer
is qualitative; plate runs that don't make the cut contribute nothing
to the flask BO posterior. Scale-up math is brittle.

**With BoFire multi-fidelity adapter:** plate / flask / bioreactor
become fidelity levels of the same model when the factor space is shared
enough to support that translation. Plate data plus flask data can then
inform target-scale suggestions under the explicit fidelity labels.

**Measurable win:** the same plate budget yields a sharper flask
posterior. Quantifiable as posterior variance reduction at flask
points after the same plate run count.

### Scenario D, mixed categorical search with conditional infeasibility

Production-strain screening across:

- Strain (categorical: 8 strains)
- Inducer (categorical: 3 inducers; strain S1 doesn't support I3)
- Inducer concentration (continuous, range depends on inducer)
- Temperature shift, pH, stir rate (continuous)

**Today:** stdlib generators encode categoricals as one-hot and ignore
the (S1, I3) conditional infeasibility. Designs may pick (S1, I3) which
experimenters manually drop.

**With a future BoFire adapter extension:** conditional constraints
plus categorical GPs could handle this without wasted vessels. The current
adapter recognizes this pattern as BoFire-shaped but fails closed unless
the conditional can be represented as a supported linear constraint.

**Measurable win:** zero hand-filtering of infeasible runs.

### Scenario E, dossier-informed BO warmstart (future adapter)

The cumulative-dossier architecture aggregates literature evidence into
CITATIONS.json + EVIDENCE/\*. Today that evidence informs the human's
intuition (which then bounds the manifest's factor ranges). It does
not enter the BO posterior.

**With BoFire main LLM-Strategy adapter:** dossier evidence feeds the
GP prior. first-batch starts with a non-flat mean function over the search
space, derived from prior fermentation studies of similar molecules.

**Measurable win:** first-batch runs spend less budget exploring regions
that prior literature already characterized.

Note: LLM warmstart is research-grade. Evaluate carefully before
claiming the win in a parity report.

## When BoFire is the wrong tool (anti-patterns)

- **Single-objective, box-constrained, no multi-fidelity.** Current
  `botorch_wave2.py` is faster, simpler, and adequate. Reaching for
  BoFire is overhead.
- **Pre-DoE EDA, power calc, or sample-size scoping.** BoFire does
  not address this surface at all.
- **Handoff packet artifacts.** Run packets, operator intake, and
  equipment-capacity tracking are entirely biosymphony's job.
- **Cumulative-dossier authoring.** Future warmstart adapters may consume
  dossier evidence; BoFire does not produce the dossier.
- **Time/phase profile design**, such as fed-batch feed strategies and
  induction ramps. BoFire treats time as out-of-scope.
- **Replacing manifest with Domain.** Domain is BoFire's contract;
  manifest is yours. Translate at the boundary; do not adopt.

## Implementation sequencing

1. **Done (2026-05-15)**: Pin `bofire>=0.3.1,<0.4` in `[adaptive]`
   extras. Add `adapters/bofire_strategy.py` with no top-level BoFire
   import. Add route reporting and stdlib fallback. Per-symbol
   compatibility checked against the public adapter surface on 2026-05-15: v0.3.1
   contains `qLogNEHVI`, `DOptimalityCriterion(formula="linear")`,
   `LinearInequalityConstraint.from_smaller_equal`, `NChooseKConstraint`
   with `none_also_valid`, `MultiFidelityStrategy.make`, and `TaskInput`,
   covering every symbol the adapter imports. The upper bound exists
   because the post-PR #705 surface renamed `MultiFidelityStrategy` to
   `MultiFidelityVarianceBasedStrategy` and made `TaskInput` abstract.
   BoFire 0.4 and 0.5 have since shipped, but this adapter has not been
   evaluated against them; keep the primary range unchanged until it is.
2. **Done (2026-05-15)**: Integrate routed dispatch in follow-up planning.
   `plan-wave2` writes `bofire_strategy_report.json` when the route
   fires and only materializes BoFire candidates when execution succeeds.
3. **Current supported translation subset**: continuous/discrete/
   categorical inputs, `TaskInput` scale fidelity, continuous outputs,
   linear constraints (including cost budgets expressed as
   `Σ $/g × g/L ≤ $/L`), n-choose-k constraints, and binary-threshold
   conditionals that can be safely linearized, such as
   `trace_metals=1 => vitamins_x>=1`.
4. **Current fail-closed subset**: forbidden constraints and general
   conditionals are recognized for routing but block BoFire execution
   until the adapter can translate them without silently dropping
   feasibility logic.
5. **Done (2026-05-15)**: update the "Bayesian Optimization" parity
   row from planned adapter to routed BoFire adapter with stdlib
   fallback, and recognize executed BoFire utility manifests.
6. **Done (2026-05-15)**: Live `BofireMediaCostLiveExecutionTests`
   behind `@skipUnless(adapters.is_available("bofire"))` in
   `tests/test_optional_adapters.py`. Skips cleanly locally; runs and
   asserts row-level feasibility (carbon mass, cardinality, cost) on
   any environment with `bofire>=0.3.1,<0.4` installed.
7. **Done (2026-05-15)**: Stdlib-only HTML reporter at
   `src/biosymphony_ferm_doe/reporters/bofire_html.py`. Consumes
   `bofire_strategy_report.json` and renders a single self-contained
   HTML file with embedded CSS, JSON-LD provenance, and per-row
   cost/carbon/cardinality verification. No Jinja2, Plotly, or external
   asset dependencies; can be sent as a single file. Plotly-inline path
   deferred to v2 behind a `[report]` extras group when a concrete
   charting need lands.
8. **Done (2026-05-15)**: First demo fixture at
   `examples/demo-media-cost-bofire/`, a cost-constrained media DoE
   with five carbon sources, four nitrogen sources, total-carbon mass
   constraint, 1-or-2 active carbons cardinality, and $0.80/L budget
   (bulk process-grade pricing per agent C 2026-05-15 research).
9. **Next**: Multi-objective Pareto smoke (e.g., titer + lactate +
    qP). Manifest declares ≥2 directions; adapter routes to
    `MoboStrategy + qLogNEHVI`; reporter learns to render a Pareto
    frontier table.
10. **Next, after BoFire 0.4 tags**: multi-fidelity scale-bridge smoke
    (plate to flask to bioreactor as fidelity tiers). Requires the
    `MultiFidelityVarianceBasedStrategy` rename in the adapter; gate
    behind a `bofire>=0.4,<0.5` extras upgrade.

## The "don't do it" case

If near-term campaigns are always single-objective with box constraints
and never need scale-bridge multi-fidelity, then the BoFire promise in
the parity matrix is dead weight. The honest move is to retire it:

- Drop `bofire` from `[adaptive]` extras
- Remove from `SUPPORTED_BACKENDS` and `BACKEND_MODULES`
- Change `parity.py` `target_status` to `optional_botorch_adapter`
- Close the corresponding issue-pack ticket
  (`packs/issue-packs/doe-parity-v0/issues/06-augment-and-bayesopt.md`)

The current half-state (listed but unused) is the worst of both. Keep
the promise as a real adapter, or retire it cleanly. Do not leave it
ambiguous.
