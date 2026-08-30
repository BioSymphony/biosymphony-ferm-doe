# `demo-pb-screening-public`: closed-loop walkthrough

A 7-factor Plackett-Burman screen on synthetic public-safe fermentation data, used to exercise the full end-to-end loop: design, then analyze, then plan follow-up, then finalize.

## What this demo shows

- **Plackett-Burman 8-run design** generated in stdlib (no external DoE library).
- **Goals formulated** from `responses[].objective_lower / objective_upper` (Derringer-Suich desirability).
- **first-batch results synthesized** in `inputs/wave1_results.csv` so the analyzer has something to fit.
- **OLS analysis** with permutation p-values and bootstrap CIs.
- **Closed-loop follow-up** that uses the analysis's active-factor list and per-factor ascent signs to bias narrow rows.
- **One-document run packet** that stitches everything together.

## Steps

```bash
# 1) Validate the manifest (should report YELLOW with no errors).
ferm-doe validate examples/demo-pb-screening-public --summary

# 2) Get a family recommendation (decision tree).
ferm-doe recommend-family examples/demo-pb-screening-public

# 3) Generate the first-batch design (8 runs, claim_level: exact).
ferm-doe generate-design examples/demo-pb-screening-public \
  --out /tmp/demo-pb/wave1_design.csv \
  --metadata-out /tmp/demo-pb/wave1_design.metadata.json \
  --seed 0

# 4) Run design-level power: MDE per coefficient at the chosen design and σ.
ferm-doe doe-power examples/demo-pb-screening-public \
  --sigma 2.0 \
  --out /tmp/demo-pb/doe_power.json \
  --md-out /tmp/demo-pb/doe_power.md

# 5) Formulate optimization goals (titer maximize 0..30, run_cost minimize 100..1000).
ferm-doe goals examples/demo-pb-screening-public --out /tmp/demo-pb/goals.json

# 6) Evaluate response-level assay-power readiness.
ferm-doe assay-power examples/demo-pb-screening-public

# 7) Generate a sampling schedule for the run.
ferm-doe sampling-plan examples/demo-pb-screening-public \
  --out /tmp/demo-pb/sampling.csv \
  --md-out /tmp/demo-pb/sampling.md

# 8) Analyze the synthesized first-batch results.
ferm-doe analyze examples/demo-pb-screening-public \
  --results examples/demo-pb-screening-public/inputs/wave1_results.csv \
  --out /tmp/demo-pb/wave1_analysis.json \
  --md-out /tmp/demo-pb/wave1_analysis.md \
  --seed 0

# 9) Plan follow-up with closed-loop analysis automatically wired in.
ferm-doe plan-wave2 examples/demo-pb-screening-public \
  --results examples/demo-pb-screening-public/inputs/wave1_results.csv \
  --out-dir /tmp/demo-pb/wave2 \
  --remaining-budget 3

# 10) Compose every artifact into one review-ready planning packet.
ferm-doe finalize examples/demo-pb-screening-public \
  --out /tmp/demo-pb/run_packet.md \
  --json-out /tmp/demo-pb/run_packet.json \
  --results examples/demo-pb-screening-public/inputs/wave1_results.csv
```

## What you should see

- **Step 2** recommends `plackett_burman` (k=7, screening, default priors); matches the manifest's choice.
- **Step 4** reports per-coefficient MDE; with σ=2.0 and 8 runs / 8 parameters, df_residual = 0 so all main-effect coefficients have the same SE under the orthogonal PB structure. Compare MDE values against the expected effect of 20 g/L declared in the manifest's `assay_power_policy`.
- **Step 7** schedules 24 samples (12 each for titer and biomass-instrument) over the default 48 h run, totalling 24 mL volume drawn.
- **Step 8** identifies `carbon_g_l` as the active factor (the synthetic surface was constructed so it drives titer most strongly).
- **Step 9** produces 3 augment rows in `wave2/augment_design.csv`, each tagged `scoring_mode: model_informed` because closed loop is using the analysis's per-factor ascent signs. Active factors get tighter steps biased along the ascent direction; inactive factors hold at the best-row value.
- **Step 10** writes a single `run_packet.md` with sections for readiness, family recommendation, goals, assay-power, sampling plan, first-batch design preview, results summary, analysis with coefficient table, follow-up plan, risks, stop rules, and assumptions. No biosafety section; the manifest does not declare any biorisk-relevant signals.

## Non-claims

This is a synthetic public-safe demo. Numbers in `wave1_results.csv` are illustrative; the readiness verdict stays `YELLOW` because the assay readiness is `planned`. See [`../../NON_CLAIMS.md`](../../NON_CLAIMS.md).
