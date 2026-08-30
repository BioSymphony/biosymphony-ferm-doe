# Biomanufacturing Adaptive Backend Selection

Status: public evaluation surface - current facts checked 2026-08-30

This document records how BioSymphony Ferm DoE should evaluate open-source
adaptive design backends for fermentation and upstream bioprocess planning.
The goal is not to crown a universal optimizer. The goal is to keep the
biomanufacturing layer honest while letting multiple free/open backends compete
on bounded fixture campaigns.

Machine-readable companion:

- `docs/adaptive-backend-evaluation.json`
- `python3 skills/biosymphony-ferm-doe/scripts/adaptive_backend_surface_check.py`
- `nox -s adaptive_backend_surface`

## License Posture

The candidate backends use different licenses. Review both the code license
and any model-weight terms before enabling an optional route:

| Tool | License | Repo signal checked |
| --- | --- | --- |
| BoFire | BSD-3-Clause | Upstream 0.5.0; primary adapter remains on the evaluated `>=0.3.1,<0.4` range |
| BayBE | Apache-2.0 | Upstream 0.15.0; evaluation extra remains pinned to 0.14.3 because 0.15 includes breaking changes |
| BoTorch | MIT | Upstream 0.18.1; repository adapter retains its existing supported range pending evaluation |
| Ax | MIT | Upstream 1.3.1; evaluation extra remains pinned to 1.2.4 |
| ENTMOOT v2 | BSD-3-Clause | Already adopted behind the in-repo adapter |
| OMLT | BSD-3-Clause | PyPI 1.2.2 checked 2026-05-23; optional MIP-over-surrogate route |
| TabPFN | Prior Labs License for code and v2 weights; non-commercial license for default TabPFN-3 weights | Upstream 8.5.0; repository adapter supports `>=8,<9` and requires a runtime token for noninteractive use |

A license grant does not mean "safe to embed without review." Any new adapter
still needs a fixture, a fail-closed report, and a public-release audit before
it becomes a default public route.

## Layering Rule

BioSymphony owns the biomanufacturing contract:

- scale bridge and transfer claims
- assay readiness and response semantics
- evidence dossier and citation ledger
- cost realism and cost stack
- lab handoff packet and execution boundaries
- campaign manifest, missing-info policy, and RED/YELLOW/GREEN readiness

Adaptive backends only propose candidate conditions. They do not become the
source of truth for the campaign.

For a full biomanufacturing workflow, expect **BoFire plus BioSymphony-owned
layers** by default, or **BayBE, Ax, or direct BoTorch instead** when the
fixture campaign proves one of those routes is a better fit. The backend choice
is deliberately swappable. The non-swappable part is the BioSymphony layer:
manifest, evidence, response semantics, cost stack, readiness verdict, and
handoff packet.

## Recommended Routing

Use **BoFire** as the default backend for constrained static DoE/BO:

- media composition
- component levels
- process setpoints
- multi-objective candidate generation
- constraints that BoFire can honor safely

Evaluate **BayBE** next to BoFire:

- low-data or no-data campaigns
- discrete/hybrid design spaces
- transfer learning across related campaigns
- asynchronous result arrival
- substance/categorical encodings

Use **Ax/BoTorch** when the campaign needs custom modeling or infrastructure:

- custom acquisition functions
- cost-aware acquisition such as EI per unit cost
- deeper multi-fidelity modeling
- deployment-oriented adaptive-experiment orchestration
- custom storage or trial lifecycle control

Use **ENTMOOT** for cardinality-heavy combinatorial BO when exact NChooseK
behavior matters more than a GP posterior.

Use **OMLT** when a fitted surrogate should be optimized through a MIP while
preserving hard linear or NChooseK constraints. Treat it as a heavier optional
route, not a default static DoE generator.

Use **TabPFN** only as an operator-requested, token-gated low-data surrogate
pilot. Do not store tokens in the repo, manifests, fixtures, or issue trackers.

Keep **pyDOE/pyDOE3** for static classical DoE baselines and smoke fixtures.

## How Deep Does Each Route Go In This Repo

The registry size and adapter count can suggest parity that the repo does not actually claim. The honest depth ladder below separates current upstream versions from the versions evaluated in this repository:

| Tier | Backends | What's in this repo |
| --- | --- | --- |
| Documented route + smoke + findings | BoFire 0.3.1, OMLT, TabPFN v3, ENTMOOT v2, BoTorch direct | Adapter code under `src/biosymphony_ferm_doe/adapters/`, unit tests under `tests/`, a smoke fixture or sweep result, and load-bearing design decisions captured in [`ADAPTER_DESIGN_NOTES.md`](ADAPTER_DESIGN_NOTES.md). Quantitative constraint-honoring results captured in [`BACKEND_EVAL_FINDINGS.md`](BACKEND_EVAL_FINDINGS.md). For BoFire, the smokes are [`demo-media-cost-bofire/`](../examples/demo-media-cost-bofire/) (linear cost + total mass + NChooseK through `DoEStrategy`) and [`demo-shakeflask-to-2l-bofire/`](../examples/demo-shakeflask-to-2l-bofire/) (`MultiFidelityVarianceBasedStrategy` with parallel-arms fallback). |
| Documented route only | OMLT (MO), TabPFN (MO) | Adapter ships but multi-objective is not exercised on the fixture sweep. Route declines cleanly. |
| Comparison-surface target | BayBE 0.14.3, Ax 1.2.4 | Listed in `docs/adaptive-backend-evaluation.json` as evaluation surface entries. No direct adapter. Single-objective constraint-honoring results captured in [`BACKEND_EVAL_FINDINGS.md`](BACKEND_EVAL_FINDINGS.md). |
| Registry listing | the remaining tool-registry entries | Each row in `docs/TOOL_REGISTRY.md` carries positioning text, adapter status, and a route reason. The registry is a landscape map, not a parity claim. |

The repo does not currently have a worked-exemplar tier (a single end-to-end campaign with a cumulative dossier and a publication-style methods argument). Backends sit at the documented-route-plus-smoke depth and rely on the cross-cutting docs (BACKEND_EVAL_FINDINGS, ADAPTER_DESIGN_NOTES, BOFIRE_CONSTRAINT_PATTERNS, ENTMOOT_SWAP_DESIGN, SCALE_BRIDGE_METHODOLOGY) for the load-bearing context.

The May 2026 sweep's OMLT, ENTMOOT, and BoFire findings are documented in [`BACKEND_EVAL_FINDINGS.md`](BACKEND_EVAL_FINDINGS.md). The non-obvious adapter design decisions that make those findings reproducible (OMLT lower-coupling, TabPFN Gaussian-approximation posterior wrap, the BoTorch direct cost-weighting trap, the MO BO sequential-mode RAM lever) live in [`ADAPTER_DESIGN_NOTES.md`](ADAPTER_DESIGN_NOTES.md).

## What Not To Do

- Do not replace the BioSymphony manifest with a BoFire `Domain`, BayBE
  `Campaign`, or Ax `Experiment`.
- Do not claim backend recommendations are lab-ready until readiness gates,
  assay semantics, scale bridge, cost stack, and handoff packet checks pass.
- Do not treat a backend's optimizer success as evidence of biomanufacturing
  transferability.
- Do not route dynamic feed ramps, oxygen-transfer modeling, or batch-record
  semantics into these BO libraries by default.

## Smoke-Test Surface

Another agent can smoke test the backend surface without changing engine
behavior:

```bash
python3 skills/biosymphony-ferm-doe/scripts/adaptive_backend_surface_check.py \
  docs/adaptive-backend-evaluation.json

python3 skills/biosymphony-ferm-doe/scripts/tool_registry_check.py \
  docs/tool-registry.json

nox -s adaptive_backend_surface
```

For live import smoke only, install optional extras explicitly:

```bash
nox -s adaptive_backend_live_imports
```

Manual equivalent, using Python 3.11-3.13 because BayBE 0.14.3 declares
`python <3.14`:

```bash
python3.11 -m venv .runtime/backend-eval-venv
.runtime/backend-eval-venv/bin/python -m pip install -e ".[adaptive,backend-eval,entmoot,dev]"
.runtime/backend-eval-venv/bin/python skills/biosymphony-ferm-doe/scripts/adaptive_backend_surface_check.py \
  docs/adaptive-backend-evaluation.json \
  --live-imports
```

Live import success is not enough to promote an adapter. Promotion requires a
fixture campaign that writes a route report, declares fallback behavior, and
proves the emitted candidates satisfy the relevant BioSymphony contract.

## First Fixture Campaigns

Starter fixture plans live under `examples/adaptive-backend-eval/<scenario_id>/`.
Each directory has a synthetic `campaign_manifest.json`, a small prior-run CSV,
and a `smoke_plan.json` that names expected artifacts under `.runtime/`.

1. `static_constrained_media`

   Primary: BoFire. Compare BayBE and pyDOE/stdlib baselines. Acceptance:
   candidate rows satisfy cost, total-carbon, and factor-bound constraints.

2. `low_data_hybrid_transfer`

   Primary: BayBE. Compare BoFire fallback. Acceptance: fixture can ingest a
   small prior-run table, recommend candidates, and serialize the campaign
   state without becoming the manifest source of truth.

3. `cost_aware_multiobjective`

   Primary: BoTorch direct or Ax/BoTorch. Acceptance: cost-aware acquisition is
   explicit, and cost reporting still uses the BioSymphony cost-stack template.

4. `cardinality_heavy_media`

   Primary: ENTMOOT. Compare BoFire post-hoc cardinality filtering. Acceptance:
   every candidate satisfies min/max active-component constraints.

5. `adaptive_orchestration`

   Primary: Ax. Compare BoTorch, BoFire, and stdlib fallback. Acceptance: trial
   lifecycle, storage/resume assumptions, and disable path are explicit; manifest
   remains canonical.

6. `scale_bridge_planning`

   Primary: BioSymphony-owned scale bridge with backend support only. Acceptance:
   no backend may claim transferability unless scale-bridge entry conditions
   pass.
