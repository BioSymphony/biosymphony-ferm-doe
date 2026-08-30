# BO-Tools Landscape Survey, 2026-05-16

> Historical snapshot. This survey preserves the tool and repository state
> observed on 2026-05-16. For current upstream versions, licensing, and adapter
> status, use [`../tool-registry.json`](../tool-registry.json).

**Question:** whether ENTMOOT remained useful beside newer AI-based tooling
**Method:** four public-source corpora covering foundation-model BO, constrained BO, bioprocess tools, and BoFire alternatives

---

## TL;DR

The May survey did not identify a 2024-2026 alternative that clearly replaced ENTMOOT v2 for the specific combination of a tree surrogate, hard MIP constraints, and NChooseK. The surveyed foundation-model and language-model approaches either omitted cardinality or left it to the optimizer layer. The resulting plan was to retain the ENTMOOT route and evaluate three bounded alternatives: an LLAMBO warm start, a TabPFN surrogate for small datasets, and BayBE as a second bioprocess-oriented backend. Those were audit-time conclusions; the current registry records which routes were later adopted.

---

## Cross-corpus convergence (signal that 2+ corpora agreed on)

1. **ENTMOOT v2 remains the strongest option for hard NChooseK.** Three of four corpora converge: nothing in 2024-2026 supplants the "tree surrogate + MIP-encoded cardinality" combination. "ENTMOOT v2's tree-MIP remains the cleanest fix" and "Nothing in 2024-2026 directly supplants it for the 'tree surrogate + hard MIP constraint + NChooseK' combination" appear nearly verbatim across two independent corpus syntheses.

2. **AI-native BO inner-loop is a trap.** Two corpora warn against putting an LLM in the acquisition seat. Gupta et al. (arXiv 2509.21403) "LLM-only BO agents show no sensitivity to experimental feedback" (label permutation test). BoFire's PR #749 LLM Strategy is "research-grade per author"; do not trust load-bearing.

3. **BoFire stays on 0.3.1 floor; 0.4 not imminent.** Inspection of BoFire main directly: no release branch, three NChooseK PRs (#693, #747, #753) still under review, PR #760 (`fixed_parameter`) opened 2026-05-14 means feature-add mode is ongoing. No `LlmStrategy` exists in mainline as of inspection; the practitioner-facing trio (BoFire + BayBe + obsidian) is the Siska 2026 guide consensus.

4. **AGPL is the load-bearing license risk in 2024-2026 bioprocess OSS.** Three relevant Jülich tools (estim8, bletl, calibr8) are AGPL-3.0; boundary-only. `pysamoo` reinforces this. The pattern is universal: academic bioprocess Python is drifting toward AGPL.

5. **Foundation-model surrogates (TabPFN, PFNs4BO) compose with, do not replace, existing MIP constraint logic.** "Foundation-model surrogates compose naturally with ENTMOOT-style MIP constraint logic at the optimizer layer, but the integration is bespoke." BoFire PR #731 brings TabPFN-style PFN surrogate into the framework but as a Strategy, not as a constraint-handler.

6. **Cost-aware BO is BoTorch-direct territory.** All four corpora agree: BoFire has no `ExpectedImprovementWithCost`; Ax exposes it only via BoTorch passthrough. For genuinely cost-anchored Pareto search, a sibling `adapters/botorch_cost_aware.py` is the cleanest path.

---

## Cross-corpus divergence (gaps and disagreements)

1. **Atlas's NChooseK support was unclear.** One source described known and unknown constraints but indicated that NChooseK would rely on rejection or penalties rather than a MIP encoding. Another noted that the tutorials did not exercise the relevant constraint handling. The survey therefore treated Atlas as an unknown-feasibility watch item, not an NChooseK route.

2. **BoFire's `LlmStrategy` status.** One corpus: "Searched, no `LlmStrategy` exists" in mainline. Another corpus: PR #749 LLM Strategy was **merged 2026-04-30**. Reconciliation: the first inspected the 0.3.1 release surface (correct that it does not exist there); the second inspected main (correct that it merged after 0.3.1 tagged). Treat as "exists on main, not in released 0.3.1, research-grade per author."

3. **Ax positioning.** Some corpora barely mention Ax; one positions Ax 1.2.4 as the strongest competitor and "natural backup adapter" with SEBO/BONSAI cardinality work in progress. Another places Ax/BoTorch SEBO as "soft sparsity, not NChooseK replacement." Net: Ax is a credible backup but not actionable today; track SEBO promotion from alpha (Ax issue #3828) and BONSAI pruning maturity.

4. **GIT-BO maturity.** Flagged as "the most exciting recent result" for foundation-model BO but "reference implementation appears not-yet-public." No other corpus surveyed it. Treat as research-watch only.

5. **Multi-fidelity scale bridge.** Martens et al. (arXiv 2508.10970, Aug 2025) described end-to-end MFBBO on a CHO simulator. BoFire PR #705 merged on 2026-05-11, but the May compatibility check found that `MultiFidelityVarianceBasedStrategy` rejected non-box constraints, recorded in issue #761. The survey found no concrete route that jointly handled multi-fidelity and NChooseK.

---

## Five most actionable findings

### 1. Route ENTMOOT through BoFire's `EntingStrategy`, not a fresh adapter

**Finding:** BoFire already ships `EntingStrategy` as a wrapper and the BoFire CHANGELOG bumps `entmoot>=2.1.1`. Our `docs/ENTMOOT_SWAP_DESIGN.md` proposes a parallel `adapters/entmoot.py`.

**Evidence:** "ENTMOOT v2.0.2 ... BoFire ships an `EntingStrategy` wrapper." "BoFire's EntingStrategy is the existing route."

**What changes:** Pivot the ENTMOOT swap design from "build new ENTMOOT adapter from scratch" to "route through BoFire's `EntingStrategy` + add adapter-side `min_count` patch". The three documented risks in `ENTMOOT_SWAP_DESIGN.md` survive, but they become local patches to a BoFire-routed path, not a parallel codepath.

**Effort estimate:** Original design was 2-3 weeks (m1 + m2 + m3 milestones). BoFire-routed approach is roughly 1 week: thin wrapper that delegates to BoFire's `EntingStrategy` + the `min_count` MIP supplement + adapter integration. Same test coverage (Pyomo expression assertion, live-execution feasibility).

### 2. Add BayBe (Merck KGaA, Apache-2.0) as registry P1 evaluate_next

**Finding:** BayBe 0.14.3 (2026-02-10) is the highest signal-to-risk new entrant: Apache-2.0, 462 stars, Merck-backed, cited as one of three practitioner-facing tools in the Siska 2026 BO guide (alongside BoFire and obsidian).

**Evidence:** Full feature surface (hybrid continuous/discrete/categorical, MORDRED chemistry encodings, transfer learning across campaigns, SHAP interpretability, full serializability).

**What changes:** Add `baybe` to `docs/tool-registry.json` as P1 evaluate_next; document as "BoFire alternative when SoboStrategy + NChooseK trap keeps biting OR when distribution requires Apache-2.0 vs BSD." Pilot via a small fixture campaign before any commit.

**Effort estimate:** 0.5 days for registry entry; ~2-3 days for a fixture comparison campaign (same Phase 2 manifest, side-by-side BayBe vs BoFire BO with same training data).

### 3. Pilot LLAMBO warmstart via OptunaHub sampler

**Finding:** LLAMBO (ICLR 2024) was the only LLM-BO entry in this survey with an OptunaHub package. It requires the Python package and credentials for an external model service. The cited feedback-sensitivity limit supports a warm-start-only scope.

**What changes:** Add `--use-llambo-warmstart` flag to first-batch design generator. Test scope: "does an LLM seed beat Latin hypercube for the first 5-10 trials?" Failure mode is contained.

**Effort estimate:** ~2 days for Optuna shim around the existing objective evaluator + a small A/B fixture.

### 4. Pilot TabPFN v2 as alternative surrogate

**Finding:** The surveyed campaign shape used 16 to 50 rows, mixed continuous and categorical factors, and no analytical gradient. That shape was close to the reported TabPFN v2 training distribution.

**Evidence:** Strongest packaging signal in this survey. GIT-BO (arXiv 2505.20685) demonstrated TabPFN v2 + active subspace beats SAASBO/TuRBO/BAxUS up to 500 D with no online retraining.

**What changes:** Sibling experiment, swap GP-fit with TabPFN forward pass inside a BoTorch loop, side-by-side benchmark against BoFire GP on a stabilized Phase 1 dataset. Constraints stay with the optimizer layer (BoFire or ENTMOOT).

**Effort estimate:** ~3-4 days for a BoTorch-compatible TabPFN surrogate wrapper + benchmark harness; gated as future work, not blocking.

### 5. Document AGPL boundary explicitly in registry for Jülich bioprocess stack

**Finding:** Three high-relevance bioprocess tools (estim8 v0.1.5 May 2026, bletl v1.7.1 Apr 2026, calibr8) are AGPL-3.0. Previous bioprocess survey did not flag bletl's AGPL status.

**What changes:** Add `bletl` and `estim8` to registry as `watch` / `boundary_only` so that AGPL is documented before any agent accidentally proposes embedding. Add a note to the existing `cobrapy` and `pysamoo` AGPL entries cross-referencing.

**Effort estimate:** ~30 minutes for the registry diff. No code work.

---

## Updated landscape table

| Tool / approach | Maturity | NChooseK support | Bioprocess fit | License | Action |
|---|---|---|---|---|---|
| **ENTMOOT v2.0.2** | Production, MIP-encoded | **Native (binary-sum ≤ k)** | Strong | BSD-3 | Route via BoFire EntingStrategy + min_count patch |
| **BoFire 0.3.1** | Production, Bayer-funded | First-class type but SoboStrategy stalls (#450); DoE+IPOPT works | Strong | BSD-3 | Stay on floor; track PR #693, #747 |
| **BoFire main (PR #749 LLM)** | Research-grade per author | Inherits | Medium | BSD-3 | Watch; do not pin |
| **BayBe (Merck KGaA)** | Production, 462 stars, v0.14.3 | Same as BoFire surface | Strong | **Apache-2.0** | **Add P1 / evaluate_next** |
| **obsidian (Merck & Co.)** | Production, 46 stars, v0.8.6 | API-level | Strong (Dash UI for process scientists) | **GPL-3.0** | Add P2 / watch / boundary_only |
| **estim8 (Jülich)** | Production, v0.1.5 (May 2026) | N/A (parameter estimation) | Strong (FMI bridge) | **AGPL-3.0** | Add watch / boundary_only |
| **bletl (Jülich)** | Production, v1.7.1 (Apr 2026) | N/A (data parser) | Strong (BioLector ingest) | **AGPL-3.0** | Add watch / boundary_only |
| **ProcessOptimizer (Novo Nordisk)** | Production, BSD-3 | None | Strong (pharma-affiliated) | BSD-3 | Add as scikit-optimize migration target |
| **TabPFN v2** | Production (Prior Labs) | None (surrogate-only) | Strong (small-data tabular) | Apache-2.0 | Pilot as drop-in BoTorch surrogate |
| **LLAMBO** | Optuna-packaged, MIT | None (cat→random) | Medium (warmstart only) | MIT | Pilot warmstart only |
| **BORA** | Conference-mature, no stable pkg | Inherits | Strong in the surveyed evidence | Paper code only | Defer until a reference implementation ships |
| **GIT-BO** | ICML 2025 workshop | Not addressed | Medium (small-D doesn't need 500-D) | Code TBD | Watch for stable release |
| **PFN-CEI** | Journal-mature, single group | Inequality only (18-var cap) | Medium | BoTorch + PFNs4BO | Defer; inequality-only, no cardinality |
| **BoTorch direct (EIpu)** | Production, Meta | Manual via narrow-Gaussian | Strong (cost-aware bio) | MIT | Sibling adapter when cost is primary response |
| **Ax 1.2.4** | Production, Meta, 2.7k stars | SEBO alpha + BONSAI pruning | Medium (heavier translation cost) | MIT | Watch SEBO promotion (Ax #3828); do NOT build adapter |
| **Atlas (Aspuru-Guzik)** | Active main, no tagged release | Param-constraint (not MIP) | Strong (self-driving lab) | MIT | Watch for unknown-feasibility use case |
| **pyBOWIE (2025)** | New, single-author | Black-box only | Medium (GP + auto kernel) | TBD | Watch; 1-day smoke test possible |
| **OMLT + Gurobi-ML / PySCIPOpt-ML** | Stable substrate | Possible if user encodes | Substrate | mix BSD/Apache | Long-horizon ENTMOOT successor path |

---

## What this means for ENTMOOT adapter work

**Recommendation:** Pivot, do not cancel.

The original `docs/ENTMOOT_SWAP_DESIGN.md` proposes a parallel `adapters/entmoot.py` that translates manifests directly to `entmoot.ProblemConfig`. BoFire already ships an `EntingStrategy` wrapper, and the BoFire CHANGELOG bumps `entmoot>=2.1.1`. This means:

- **BoFire's wrapper already covered part of the translation.** A parallel implementation would duplicate that work.
- **The three documented risks applied to either route at survey time.** They were missing `min_count` emission, a `gurobipy>=11` dependency, and a `_fantasy_tell` tie cycle. The delivered in-repo ENTMOOT adapter later addressed all three at its boundary.
- **Routing decision becomes cleaner.** With `EntingStrategy` accessible inside `adapters/bofire_strategy.py`, the dispatch rule is: "Domain has NChooseKConstraint AND single-objective → route to `EntingStrategy` instead of `SoboStrategy`." No new adapter package needed; route stays inside the existing BoFire adapter boundary.

**Concrete pivot:**

1. Add `_route_to_enting_when_nchoosek` branch inside `adapters/bofire_strategy.py`. Mirror the BoFire-wrapper API.
2. Subclass BoFire's `NChooseKConstraint` translator to emit the missing `Σ z_i ≥ min_count` Pyomo expression (the same risk-1 patch the original swap design proposed, but applied at the BoFire boundary instead of in a parallel adapter).
3. Probe `pyo.SolverFactory("gurobi").available()` when the strategy starts. If it is unavailable, try HiGHS, GLPK, and SCIP in that order. Document the solver requirement in the `[adaptive]` extra.
4. Keep the design doc as the methodological reference; add a status note at the top: "Pivoted 2026-05-16: route through BoFire `EntingStrategy` rather than parallel adapter. Three risks unchanged; mitigation patches stay local to the routing layer."

If BoFire's `EntingStrategy` turns out to be missing a critical hook at the wrapper layer (e.g., cannot inject a custom MIP block), fall back to the original parallel-adapter design.

## What this means for BoFire stance

**Audit-time decision: stay on 0.3.1.** BoFire 0.4 and 0.5 have since shipped, and issue #761 is closed. The primary adapter range remains unchanged because later releases have not been evaluated against the public compatibility fixtures.

**Track these PRs in `docs/BOFIRE_POSITIONING.md`:**

- **#693 MCTS-based ACQF for NChooseK**, direct upstream fix to #450
- **#747 BONSAI-style greedy pruning for NChooseK**, alternative fix
- **#740 Nonlinear constraints integration**, relevant to native nonlinear cost constraints
- **#705 Multi-Output Multi-Fidelity** (merged 2026-05-11), the strategy exercised by issue #761
- **#731 PFN Surrogate**, future warmstart path
- **#749 LLM Strategy** (merged 2026-04-30), research-grade; evaluate when 0.4 tags

**Audit-time decision: do not build against a moving main branch.** That timing note is historical; the repository now uses a tagged 0.4.1 candidate for its separate NChooseK DoE evaluation lane.

**Evaluate BayBE as a second bioprocess-oriented option.** Its Apache-2.0 license and narrower surface made it a useful comparison route beside BoFire. The current evaluation extra remains pinned to BayBE 0.14.3; upstream 0.15.0 includes breaking changes.

## What this means for AI-native exploration

**Two cheap pilots worth scheduling, neither blocking:**

1. **LLAMBO warmstart (2-day pilot).** Add `--use-llambo-warmstart` to first-batch design generator via OptunaHub sampler. Compare first-batch performance against Latin hypercube on a stabilized Phase 1 dataset. Scope: warmstart only; the Gupta 2024 negative result makes inner-loop unsupervised use unethical.

2. **TabPFN v2 surrogate.** Build a BoTorch-compatible forward-pass wrapper and compare it with the BoFire GP surrogate on the same training data. Keep constraints in the optimizer layer. This route was later delivered as the optional TabPFN adapter; current license terms are recorded in the tool registry.

**Defer:**

- **BORA / Reasoning BO** until reference implementations land. Patterns are correct; code is not packaged.
- **PFN-CEI**, inequality-only, 18-var cap. Useful for "total cost ≤ $X" but not for cardinality.
- **GIT-BO**, workshop 2025, code unclear. Watch for stable release.

**Reject:**

- **Replacing the BO inner loop with an LLM.** Gupta et al. (arXiv 2509.21403) reported that the evaluated LLM agents were insensitive to experimental feedback. Do not use this route for load-bearing candidate selection.

**One bounded pattern to evaluate:** BO-ICL (Ramos et al., ACS Central Science 2025) reported that a frozen GPT-3.5 surrogate identified a near-optimal multi-metallic catalyst in six iterations from 3,700 candidates. A future evaluation could limit the model to commentary on rejected candidates in `NOTES.md`; it must not control the optimization loop.

---

## Cumulative citations (consolidated, deduplicated)

### LLM-guided + Foundation-Model BO

1. Liu, T., Astorga, N., Seedat, N., van der Schaar, M. (2024). *Large Language Models to Enhance Bayesian Optimization* (LLAMBO). ICLR 2024. arXiv:2402.03921. https://arxiv.org/abs/2402.03921. Repo: https://github.com/tennisonliu/LLAMBO
2. Lopez-Concepcion, A. et al. (2025). *Language-Based Bayesian Optimization Research Assistant (BORA)*. IJCAI 2025. arXiv:2501.16224. https://arxiv.org/abs/2501.16224
3. Hu, X. et al. (2025). *Reasoning BO: Enhancing Bayesian Optimization with the Long-Context Reasoning Power of LLMs*. arXiv:2505.12833.
4. Chang, Y.-T. et al. (2025). *LLINBO: Trustworthy LLM-in-the-Loop Bayesian Optimization*. arXiv:2505.14756.
5. Mahammadli, M. et al. (2024). *Sequential Large Language Model-Based Hyperparameter Optimization* (SLLMBO). arXiv:2410.20302.
6. Yang, C. et al. (2023). *Large Language Models as Optimizers* (OPRO). ICLR 2024. arXiv:2309.03409. Repo: https://github.com/google-deepmind/opro
7. **Gupta, R., Hartford, J., Liu, B. (2024). *LLMs for Bayesian Optimization in Scientific Domains: Are We There Yet?* arXiv:2509.21403.** (Load-bearing negative result.)
8. Hollmann, N. et al. (2025). *Accurate predictions on small data with a tabular foundation model* (TabPFN v2). Nature 626, 357-364. doi:10.1038/s41586-024-08328-6. Repo: https://github.com/PriorLabs/TabPFN
9. Müller, S., Feurer, M., Hollmann, N., Hutter, F. (2023). *PFNs4BO: In-Context Learning for Bayesian Optimization*. ICML 2023. arXiv:2305.17535. Repo: https://github.com/automl/PFNs4BO
10. Yu, R. et al. (2025). *Fast and accurate Bayesian optimization with pre-trained transformers for constrained engineering problems* (PFN-CEI). Structural and Multidisciplinary Optimization 68. doi:10.1007/s00158-025-03987-z. Repo: https://github.com/rosenyu304/BOEngineeringBenchmark
11. *GIT-BO: High-Dimensional Bayesian Optimization with Tabular Foundation Models*. ICML 2025 Workshop. arXiv:2505.20685.
12. Ramos, M. C. et al. (2025). *Bayesian Optimization of Catalysis with In-Context Learning* (BO-ICL). ACS Central Science. doi:10.1021/acscentsci.5c02418. Preprint arXiv:2304.05341.
13. Feuer, B. et al. (2024). *TuneTables: Context Optimization for Scalable Prior-Data Fitted Networks*. NeurIPS 2024.
14. Akke, M. et al. (2025). *When Do LLMs Improve Bayesian Optimization?* NeurIPS 2025.
15. OptunaHub LLAMBO sampler: https://hub.optuna.org/samplers/llambo/
16. OptunaHub PFNs4BO sampler: https://hub.optuna.org/samplers/pfns4bo/

### Constrained / Cardinality BO

17. Thebelt, A. et al. *ENTMOOT: A Framework for Optimization over Ensemble Tree Models.* Comput. Chem. Eng. 151 (2021). arXiv:2003.04774. Repo: https://github.com/cog-imperial/entmoot
18. Thebelt, A. et al. *Tree ensemble kernels for Bayesian optimization with known constraints over mixed-feature spaces.* NeurIPS 2022. arXiv:2207.00879
19. Mistry et al. *Mixed-integer convex nonlinear optimization with gradient-boosted trees embedded.* INFORMS J. Comput. 33 (2021): 1103-1119.
20. Ceccon, F., Tsay, C. et al. *OMLT: Optimization & Machine Learning Toolkit.* JMLR 23 (2022). Repo: https://github.com/cog-imperial/OMLT
21. Turner, M. et al. *PySCIPOpt-ML: Embedding Trained Machine Learning Models into Mixed-Integer Programs.* OR 2024 Proceedings, Springer 2024. arXiv:2312.08074. Repo: https://github.com/Opt-Mucca/PySCIPOpt-ML
22. Bonami, P. et al. *Gurobi Machine Learning Manual* v1.5.4, May 2025. https://gurobi-machinelearning.readthedocs.io/
23. Morlet-Espinosa, J. *pyBOWIE: A Python Library for Constrained Mixed-Integer Bayesian Optimization with Superlevel Set Filtration.* Ind. Eng. Chem. Res. 64(9):4942-4965 (2025). doi:10.1021/acs.iecr.4c03154. Repo: https://github.com/JavierMorlet/pyBOWIE
24. Morlet-Espinosa, J. *A Bayesian optimization approach for data-driven mixed-integer nonlinear programming problems.* AIChE J. 70 (2024). doi:10.1002/aic.18448
25. Deshwal, A. et al. *Bayesian Optimization over High-Dimensional Combinatorial Spaces via Dictionary-based Embeddings* (BODi). AISTATS 2023. arXiv:2303.01774. Repo: https://github.com/aryandeshwal/BODi
26. Papenmeier, L., Nardi, L., Poloczek, M. *Bounce: Reliable High-Dimensional Bayesian Optimization for Combinatorial and Mixed Spaces.* NeurIPS 2023. arXiv:2307.00618. Repo: https://github.com/lpapenme/bounce
27. Liu, S. et al. *Sparse Bayesian Optimization* (SEBO). AISTATS 2023. arXiv:2203.01900. Ax docs: https://ax.dev/docs/tutorials/sebo/
28. Eriksson, D., Poloczek, M. *Scalable Constrained Bayesian Optimization* (SCBO). AISTATS 2021. arXiv:2002.08526.
29. *Feasibility-Driven Trust Region Bayesian Optimization* (FuRBO). arXiv:2506.14619 (June 2025).
30. Li, Z. et al. *Constrained Multi-objective Bayesian Optimization through Optimistic Constraints Estimation* (COMBOO). AISTATS 2025. arXiv:2411.03641.
31. Hickman, R. J. et al. *Atlas: a brain for self-driving laboratories.* Digital Discovery (2025). doi:10.1039/D4DD00115J. Repo: https://github.com/aspuru-guzik-group/atlas
32. Hickman, R. J. et al. *Anubis: Bayesian optimization with unknown feasibility constraints for scientific experimentation.* Digital Discovery 4:2104-2122 (2025). doi:10.1039/D5DD00018A
33. Guinet, G., Rana, S., Cawley, R. *Pareto-efficient Acquisition Functions for Cost-Aware Bayesian Optimization.* arXiv:2011.11456.
34. Sun, K. et al. *Scalable Bayesian Optimization via Focalized Sparse Gaussian Processes* (FocalBO). NeurIPS 2024. arXiv:2412.20375.

### Bioprocess-specific tools

35. FedBatchDesigner repo, https://github.com/julibeg/FedBatchDesigner (v Publication-Snapshot 2025-07-11)
36. FedBatchDesigner paper, https://pubs.acs.org/doi/10.1021/acssynbio.5c00357 (ACS Synth. Biol.)
37. **BayBe repo, https://github.com/emdgroup/baybe (v0.14.3, 2026-02-10, 462 stars, Apache-2.0)**
38. BayBe paper, *Digital Discovery* 2025, doi:10.1039/D5DD00050E
39. **obsidian repo, https://github.com/MSDLLCpapers/obsidian (v0.8.6, 2025-03-20, GPL-3.0)**
40. **estim8 repo, https://github.com/JuBiotech/estim8 (v0.1.5, 2026-05-12, AGPL-3.0)**
41. **bletl repo, https://github.com/JuBiotech/bletl (v1.7.1, 2026-04-15, AGPL-3.0)**
42. ProcessOptimizer repo, https://github.com/novonordisk-research/ProcessOptimizer (BSD-3)
43. ProcessOptimizer paper, *J. Chem. Inf. Model.* 2025, doi:10.1021/acs.jcim.4c02240
44. BioKernel, https://2025.igem.wiki/imperial/Model + https://gitlab.igem.org/2025/software-tools/imperial (license TBD)
45. BioSTEAM repo, https://github.com/BioSTEAMDevelopmentGroup/biosteam (v2.53.9)
46. AMICI v0.34.0, https://pypi.org/project/amici/
47. JuBiotech org, https://github.com/JuBiotech (calibr8, murefi, estim8, bletl ecosystem)
48. **Siska et al. *A Guide to Bayesian Optimization in Bioprocess Engineering.* Biotechnology and Bioengineering 2026 (Wiley) / arXiv:2508.10642.** PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC13003447/
49. **Martens et al. *Holistic Bioprocess Development Across Scales Using Multi-Fidelity Batch Bayesian Optimization.* arXiv:2508.10970 (Aug 2025).**
50. Lapierre et al. *Multi-cycle high-throughput growth media optimization using batch Bayesian optimization.* J. Chem. Tech. & Biotech. 2025, doi:10.1002/jctb.7860
51. *Nature Communications* 2025, s41467-025-61113-5 (cell culture media via BO)
52. *Current Opinion in Biotechnology* 2025, S0958166925001363 (AI in bioprocess automation)
53. FermBench, https://www.sciencedirect.com/science/article/pii/S2666920X26000391
54. ChemAgents, https://pubs.acs.org/doi/10.1021/jacs.4c17738
55. Synonym Scaler, https://scaler.bio
56. TetraScience Media Formulation Assistant, https://www.tetrascience.com/scientific-outcomes/cell-media-formulation
57. DataHow / Eppendorf integration, https://datahow.ch/

### Framework landscape

58. BoFire repo / commits, https://github.com/experimental-design/bofire (v0.3.1 + main 2026-05-11)
59. BoFire CHANGELOG, https://github.com/experimental-design/bofire/blob/main/CHANGELOG.md
60. BoFire PR #705 Multi-Output Multi-Fidelity (merged 2026-05-11)
61. BoFire PR #749 LLM Strategy (merged 2026-04-30)
62. BoFire PR #693 MCTS ACQF for NChooseK (open)
63. BoFire PR #747 BONSAI NChooseK pruning (open)
64. BoFire PR #740 Nonlinear constraints integration (open)
65. BoFire PR #731 PFN Surrogate (open)
66. BoFire PR #752 True NChooseK for DoE
67. BoFire issue #450, Slow optimization for high-dim NChooseK
68. BoFire issue #761 (opened 2026-05-16), MultiFidelityVarianceBasedStrategy + non-box constraints
69. Ax 1.2.4 release notes, https://github.com/facebook/Ax/releases/tag/1.2.4
70. Ax SEBO tracking, https://github.com/facebook/Ax/issues/3828
71. BoTorch 0.17.0, https://github.com/pytorch/botorch/releases/tag/v0.17.0
72. BoTorch 0.14.0 (PFN + classifier constraints), https://github.com/pytorch/botorch/releases/tag/v0.14.0
73. BoTorch `ExpectedImprovementWithCost`, https://botorch.org/api/acquisition.html#botorch.acquisition.cost_aware
74. Google Vizier 0.1.24, https://github.com/google/vizier
75. Trieste 4.5.1, https://github.com/secondmind-labs/trieste
76. Optuna 4.8.0, https://github.com/optuna/optuna/releases/tag/v4.8.0
77. NEXTorch, https://github.com/VlachosGroup/nextorch (unmaintained since 2021)
78. GPflowOpt, https://github.com/GPflow/GPflowOpt (unmaintained since 2020-12)

### Related Repository Docs

79. `docs/BOFIRE_POSITIONING.md` (canonical adapter-not-destination doc, 2026-05-15)
80. `docs/BOFIRE_CONSTRAINT_PATTERNS.md` (BoFire constraint compat matrix)
81. `docs/ENTMOOT_SWAP_DESIGN.md` (2026-05-16)
82. `docs/open-source-bioprocess-tool-survey-2026-05-15.md` (predecessor survey)
83. `docs/tool-registry.json` (current registry)

---

## Proposed registry updates

Summary:

**ADD (new tool_id entries):**

- `baybe`, Apache-2.0, P1 evaluate_next, BoFire alternative
- `obsidian`, GPL-3.0, P2 watch / boundary_only, Dash UI exemplar
- `estim8`, AGPL-3.0, P2 watch / boundary_only, FMI bridge
- `bletl`, AGPL-3.0, P2 watch / boundary_only, BioLector parser (explicit AGPL flag)
- `processoptimizer`, BSD-3, P2 watch, scikit-optimize migration target
- `tabpfn_v2`, Apache-2.0, P2 watch, foundation-model surrogate pilot candidate
- `llambo`, MIT, P2 watch, LLM warmstart pilot via OptunaHub
- `omlt`, BSD-3, P2 watch, long-horizon MIP+ML substrate

**MODIFY (existing entries):**

- `bofire`, refresh `last_checked` to 2026-05-16; expand `risks` to add issue #761 status; add `watch_prs` field with #693, #747, #740, #731
- `entmoot`, refresh `last_checked`; update `current_signal` to note BoFire EntingStrategy wrapper exists; update `claim_level` from `design_only_not_implemented` to `pivoted_to_bofire_routing`
- `atlas`, refresh `current_signal` to clarify "watch for unknown-feasibility constraint use case, not NChooseK"
- `scikit_optimize`, add `migration_target: "processoptimizer"`
- `botorch_direct`, refresh `current_signal` with 2026 status; clarify "cost-aware sibling adapter, not displacement"
- `fedbatchdesigner`, update `current_signal` with July 2025 publication snapshot details

**DO NOT add (out of scope or risk):**

- Commercial platforms (Scaler, TetraScience, DataHowLab, MODDE, Synthace, Riffyn), watchlist references in markdown survey only
- BORA, Reasoning BO, GIT-BO, defer until reference implementations ship
- PFN-CEI, inequality-only, 18-var cap; revisit if problem space shifts
- BioKernel, license TBD
- Ax, credible backup but actionable only if BoFire stalls >6 months
