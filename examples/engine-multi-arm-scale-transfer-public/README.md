# `engine-multi-arm-scale-transfer-public`: multi-arm scale transfer

Public-safe engine regression fixture with two coupled campaign arms: a plate-scale downscale arm and a 2 L reactor target arm. Demonstrates the mission-control path for scale-transfer work where one campaign carries two arms with shared learning.

## What this demo shows

- **Two campaign arms** with separate factor spaces, response definitions, and DoE families: a downscale plate arm and a reactor target arm.
- **Planned experimental setup artifacts** for each arm, with horizontal review rows that compare both arms in one document.
- **Optimization goals** composed across titer, productivity, cost, acetate, and bridge confidence.
- **Scale recipe and bridge qualification adapters** that produce per-arm engineering recipes.
- **Adaptive follow-up `scale_or_downscale` eligibility**: the planner can recommend a controlled re-bridge between arms when first-batch evidence supports it.

## First command

```bash
ferm-doe validate examples/engine-multi-arm-scale-transfer-public --summary
```

Then exercise the multi-arm path:

```bash
ferm-doe scale-recipe examples/engine-multi-arm-scale-transfer-public \
  --out /tmp/multi-arm/scale_recipe.json \
  --md-out /tmp/multi-arm/scale_recipe.md

ferm-doe finalize examples/engine-multi-arm-scale-transfer-public \
  --out /tmp/multi-arm/run_packet.md \
  --json-out /tmp/multi-arm/run_packet.json
```

## What you should see

- **`validate --summary`**: status `YELLOW`, `error_count == 0`. Both arms validate as planning artifacts.
- **`scale-recipe`**: writes a per-arm recipe with kLa, P/V, tip-speed, and mixing-time targets, plus a bridge-confidence rollup.
- **`finalize`**: stitches both arms into one review-ready planning packet with goals, decision rules, stop rules, sampling plans, and a multi-arm summary table.

## Non-claims

Synthetic public-safe fixture. The dossier is a planning artifact only. Multi-arm scale transfer requires executed bridge evidence before any claim of recapitulation. See [`../../NON_CLAIMS.md`](../../NON_CLAIMS.md).
