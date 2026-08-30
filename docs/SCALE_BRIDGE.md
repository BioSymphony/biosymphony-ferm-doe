# Scale Bridges

A scale bridge connects two operating scales (plate, microtiter, microbioreactor, shake flask, bench, pilot, manufacturing) by an explicit criterion. The skill supports three directions: `scale_up`, `scale_down`, and `round_trip`.

## Why a separate framework

Most fermentation DoE failures at scale come from the bridge itself: a small-scale design that gives a clean answer at 2 L because it is mass-transfer-limited differently than the 200 L vessel. The factor space rarely changes the answer once that bridge is wrong. The skill makes the bridge an explicit, validatable object instead of an implicit assumption.

## Schema

`scale_context` carries:

- `direction`: scale_up | scale_down | round_trip | lateral
- `from_scale` and `to_scale`: each a scale endpoint with vessel, working volume, geometry (H/D, impeller D/T, n_impellers, impeller_type, sparger_type), and engineering targets (kLa, P/V, tip_speed, mix_time, DO setpoint, OUR, RQ, VVM, shear_indicator)
- `bridge_strategy`: `primary_criterion` + `secondary_criteria` + `rationale`
- `bridge_factors`: split into `transferable`, `needs_retuning`, `not_applicable`
- `known_offsets[]`: recorded discrepancies between scales the agent should preserve in interpretation
- `qualification_evidence[]`: references to evidence_table rows
- `recapitulation_criterion`: required by `scale_down_qualification`. States which metric, which tolerance, and which state qualifies the small scale.

## Picking a primary criterion

| Criterion | Use when | Caveats |
|---|---|---|
| `kLa` | Aerobic microbial culture, OTR-limited active phase | Easy to match by RPM tuning; doesn't preserve shear |
| `p_per_v` | Mammalian cell culture, shear-sensitive systems | Can preserve mixing energy but not OTR |
| `tip_speed` | Shear-sensitive systems, fragile cell lines | Conservative; can leave OTR low |
| `mix_time` | Substrate-pulse-sensitive cultures, fed-batch with sharp feed | Hard to measure; often inferred |
| `do_control` | When DO control is the dominant operational constraint | Implicit kLa match if DO probe response is comparable |
| `our` | Off-gas-instrumented vessels | Direct metabolic match; requires off-gas at both scales |
| `rq` | Substrate selection regime matters | Only meaningful with off-gas |
| `vvm` | Aeration-volume-limited regimes | Not equivalent to kLa across scales |
| `geometric_similarity` | When geometry is preserved (rare) | Aspirational; usually a partial match only |
| `custom` | Domain-specific criterion (CO2 stripping, foaming index, etc.) | State the math in `bridge_strategy.rationale` |

## Downscale qualification

`scale_down_qualification` is asymmetric: the small scale must recapitulate the large scale. The `recapitulation_criterion` declares which metric and what tolerance qualifies the small scale. Until executed runs satisfy that tolerance, the campaign stays YELLOW.

A common pattern: composite score = (titer ratio) × (OUR shape distance penalty), threshold ≥ 0.85. The exact composition is up to the agent and user; the schema does not prescribe it.

## Bridge factors

Factors split into three buckets:

- `transferable`: values transfer 1:1 (temperature, pH, DO setpoint)
- `needs_retuning`: values must be adjusted at the new scale (RPM, feed rate, gas flow)
- `not_applicable`: factor exists at one scale only (e.g., a microbioreactor-specific control)

Validator warns if any of the three is empty. A long-running agent should fill each as the bridge framing matures.

## Known offsets

When historical evidence shows a systematic difference between scales, record it in `known_offsets[]` with axis, description, magnitude, and evidence_id. This carries forward into how follow-up results are interpreted.

## Engineering recipe derivation

`ferm-doe scale-recipe <campaign> --out scale_recipe.json --md-out scale_recipe.md` derives planning setpoints for both endpoints from `scale_context`. For each scale, the recipe solves for:

- agitation RPM
- sparge / gas flow rate (from `vvm`)
- agitator power total + per impeller
- tip speed
- Nienow mix time
- resulting kLa at the chosen P/V and superficial gas velocity

Built-in correlations:

- **kLa.** Van't Riet (1979) with organism-class presets: `microbial_coalescing` (`c=0.026, a=0.4, b=0.5`), `microbial_non_coalescing` (`c=0.002, a=0.7, b=0.2`), `mammalian_shear_sensitive`, `yeast`. Override via `scale_context.correlation_overrides.kla.{c,a,b}`.
- **Power.** `P = N_p * rho * N^3 * D^5`. Power numbers default by impeller_type (Rushton 5.5, pitched-blade 1.27, marine 0.35, Lightnin A310 0.30, A315 0.84). Override via `engineering_targets.power_number` or `correlation_overrides.power_number`.
- **Mix time.** Nienow `N * t_m = c_m`; defaults by impeller_type. Override via `engineering_targets.mix_time_constant`.
- **Liquid density.** Default 1000 kg/m³. Override via `correlation_overrides.liquid_density_kg_per_m3`.

The output is labeled `claim_level: engineering_recipe_planned`. The recipe is a starting point; vessel kLa-vs-RPM characterization must qualify the correlation choice before physical execution. The recipe warns when declared `engineering_targets` (RPM, P/V, tip speed) disagree with solved values by more than 20%; a large warning is the signal to revise VVM, geometry, or the chosen primary criterion before locking the design.

## Anti-patterns

- Declaring a scale-bridge profile without `scale_context`. Validator returns RED.
- Declaring a primary criterion but no engineering target value at one of the endpoints. Validator warns.
- Treating geometry as preserved without recording H/D and impeller D/T silently weakens the bridge.
- Treating cost or schedule as a scale-bridge response. Those belong in feasibility constraints, not responses.
- Reading `scale_recipe.json` as a lab-validated transfer. It is a planning recipe; correlation choice must be qualified for the specific vessel and broth.
