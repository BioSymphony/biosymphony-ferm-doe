# BioSymphony Tool Registry

- Status: `PASS`
- Tools: `49`
- Findings: `0 errors`, `0 warnings`
- Checked on: `2026-08-30`
- Pyproject alignment: `13` packages across `15` extras
- Action lanes: `4` nox lanes, `0` remote lanes

`Supported` is the repository requirement. `Upstream` is the newest official release observed on the checked date; it is not an adapter-compatibility claim.

| Tool | Priority | Status | Supported | Upstream | Checked | Extra | Claim | Route |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bofire | P0 | adopted_optional | bofire>=0.3.1,<0.4 | 0.5.0 | 2026-08-30 | bofire | bofire_adapter_planning | non_box_constraints, multi_objective_responses, scale_fidelity_structure, ... |
| frictionless | P0 | adopted_optional | frictionless>=5,<6 | 5.19.0 | 2026-08-30 | contracts | contract_validation | table_contracts |
| nox | P0 | adopted_optional | nox>=2024.4 | 2026.8.17 | 2026-08-30 | dev | execution_lane | local_validation, optional_lanes |
| pubmed_mcp_adapter | P0 | adopted_optional |  |  | 2026-08-30 |  | fixture_normalization_and_harness_mediated_enrichment | dossier_citation_enrichment, bibtex_export |
| ro_crate | P0 | adopted_optional |  | 1.3.0 spec; 0.15.1 rocrate | 2026-08-30 |  | provenance_metadata | compile_dossier, workflow_run_provenance, profile_validation_candidate |
| salib | P0 | adopted_optional | SALib>=1.5.2 | 1.5.2 | 2026-08-30 | sensitivity | sensitivity_screening | sensitivity_screening, assumption_attack, scale_recipe_uncertainty |
| scipy | P0 | adopted_optional | scipy>=1.11 | 1.18.1 | 2026-08-30 | scipy | adapter_backed_statistical_analysis | analysis_pvalues, doe_power_quantiles, qmc_space_filling |
| ax | P1 | evaluate_next | ax-platform==1.2.4 | 1.3.1 | 2026-08-30 | backend-eval | not_yet_evaluated | adaptive_orchestration_pilot, custom_generation_strategy, botorch_infrastructure |
| baybe | P1 | evaluate_next | baybe==0.14.3; python_version < '3.14' | 0.15.0 | 2026-08-30 | backend-eval | not_yet_evaluated | bofire_alternative_adapter, categorical_substance_encoding, transfer_learning_across_campaigns, ... |
| biosteam | P1 | evaluate_next |  | 2.53.11 | 2026-08-30 |  | economic_context_sidecar | cost_rollup_sidecar, downstream_context |
| botorch | P1 | adopted_optional | botorch>=0.9 | 0.18.1 | 2026-08-30 | botorch | bayesian_optimization_planned | experimental_adaptive_adapter |
| cwl | P1 | watch |  | cwltool 3.2.20260720092025 | 2026-08-30 |  | workflow_provenance_sidecar | portable_handoff_bundle |
| eln_file_format | P1 | evaluate_next |  |  | 2026-06-21 |  | interchange_candidate | eln_export_candidate, run_packet_interchange, ro_crate_profile_reference |
| entmoot | P1 | adopted_optional | entmoot==2.1.1 | 2.1.1 | 2026-08-30 | entmoot | entmoot_adapter_planning | nchoosek_cardinality_bo, tree_based_surrogate, in_repo_adapter |
| fedbatchdesigner | P1 | evaluate_next |  | snapshot-20250711 | 2026-08-30 |  | reference_sidecar | fed_batch_reference_example |
| grobid_fulltext | P1 | evaluate_next |  | 0.9.1 | 2026-08-30 |  | evidence_extraction_sidecar | public_pdf_structuring, dossier_evidence_harvest, citation_context_extraction |
| omlt | P1 | adopted_optional | omlt>=1.2.2,<2 | 1.2.2 | 2026-08-30 | omlt | omlt_adapter_planning | mip_surrogate_optimization, nchoosek_cardinality_bo, optional_in_repo_adapter |
| petab_libpetab | P1 | evaluate_next |  | 0.8.2 | 2026-08-30 |  | calibration_contract_candidate | mechanistic_model_contract, parameter_estimation_fixture, petab_validation |
| pixi | P1 | watch |  | 0.78.0 | 2026-08-30 |  | developer_tooling | dependency_locking |
| plotly | P1 | adopted_optional | plotly>=6.0 | 7.0.0 | 2026-08-30 | report | optional_report_visualization | bofire_html_constraint_slice, bofire_html_cost_stack, bofire_html_factor_heatmap |
| pseudobatch | P1 | evaluate_next |  |  | 2026-06-21 |  | preprocessing_candidate | fed_batch_sample_withdrawal, ledger_preprocessing, growth_rate_transform_reference |
| pydoe | P1 | watch | pydoe>=1.0.1 | 1.5.0 | 2026-08-30 |  | adapter_backed_classical_doe | screening, rsm_fit, space_filling_scout |
| pydoe3 | P1 | compatibility_only | pyDOE3>=1.0 | 1.6.2 | 2026-08-30 | pydoe3 | compatibility_adapter | extended_box_behnken, latin_hypercube_maximin, legacy_pydoe3_adapter |
| pyomo_dae | P1 | evaluate_next |  | Pyomo 6.10.1 | 2026-08-30 |  | deterministic_feasibility_sidecar | fed_batch_feasibility, dynamic_constraints |
| pypesto | P1 | evaluate_next |  | 0.6.0 | 2026-08-30 |  | calibration_sidecar_candidate | mechanistic_parameter_estimation, uncertainty_quantification_sidecar, petab_sbml_pipeline |
| pyplate | P1 | evaluate_next |  | 0.4.7 | 2026-08-30 |  | execution_recipe_sidecar | plate_arm_manifest, plate_recipe_export |
| sbml_runtime_stack | P1 | evaluate_next |  | libRoadRunner 2.10.0; Tellurium 2.2.11.2; AMICI 1.0.1 | 2026-08-30 |  | simulation_sidecar | mechanistic_model_sidecar |
| xopt | P1 | evaluate_next |  | 3.2.1 | 2026-08-30 |  | not_yet_evaluated | adaptive_backend_comparison, constrained_bo, multi_objective_bo, ... |
| atlas | P2 | watch | matter-atlas |  | 2026-08-30 |  | not_yet_evaluated | categorical_aware_bo |
| bletl | P2 | boundary_only |  | 1.7.1 | 2026-08-30 |  | external_reference | external_biolector_ingest |
| botorch_direct | P2 | watch | botorch>=0.10 | 0.18.1 | 2026-08-30 |  | not_yet_evaluated | cost_aware_acquisition, direct_surrogate_control |
| cadet | P2 | boundary_only |  | CADET-Core 5.1.1 | 2026-08-30 |  | external_reference | downstream_external_sidecar |
| cobrapy | P2 | boundary_only |  | 0.32.1 | 2026-08-30 |  | evidence_sidecar | metabolic_evidence_sidecar |
| dwsim | P2 | boundary_only |  | 9.0.5 | 2026-08-30 |  | external_reference | external_flowsheet_export |
| estim8 | P2 | boundary_only |  | 0.1.6 | 2026-08-30 |  | external_reference | fmi_modelica_parameter_estimation, external_bioprocess_model_ingest |
| europe_pmc_api | P2 | watch |  |  | 2026-06-21 |  | metadata_harvest_watch | public_life_science_search, open_fulltext_lookup, annotation_harvest |
| llambo | P2 | watch |  |  | 2026-08-30 |  | not_yet_evaluated | llm_warmstart_first_batch, optuna_sampler_pilot |
| nextflow | P2 | watch |  | 26.04.6 | 2026-08-30 |  | workflow_sidecar | large_compute_pipeline |
| obsidian_apo | P2 | boundary_only |  | 0.8.6 | 2026-08-30 |  | external_reference | dash_ui_reference, shap_explanation_reference |
| openalex_official | P2 | watch |  |  | 2026-06-21 |  | metadata_harvest_watch | public_literature_context, citation_graph_harvest |
| processoptimizer | P2 | watch |  | 1.1.2 | 2026-08-30 |  | not_yet_evaluated | scikit_optimize_migration_target |
| pymoo | P2 | evaluate_next |  | 0.6.2 | 2026-08-30 |  | candidate_table_diagnostic | pareto_report, design_tournament |
| smt | P2 | evaluate_next |  | 2.14.1 | 2026-08-30 |  | surrogate_diagnostic | scale_bridge_diagnostic |
| snakemake | P2 | watch |  | 9.26.1 | 2026-08-30 |  | workflow_sidecar | batch_benchmark_dag |
| tabicl_v2 | P2 | watch |  | 2.1.1 | 2026-08-30 |  | watch_only | foundation_model_surrogate_watch, tabpfn_comparison, larger_table_regression_watch |
| tabpfn_v2 | P2 | adopted_optional | tabpfn>=8,<9 | 8.5.0 | 2026-08-30 | tabpfn | tabpfn_adapter_planning | foundation_model_surrogate_pilot, small_data_tabular_regression, optional_in_repo_adapter |
| trieste | P2 | watch |  | 4.6.0 | 2026-08-30 |  | watch_only | complex_acquisition_reference, ask_tell_bo_watch, multi_fidelity_bo_watch |
| pysamoo | Avoid | avoid |  | 0.1.2 | 2026-08-30 |  | not_applicable |  |
| scikit_optimize | Avoid | avoid |  | 0.10.2 | 2026-08-30 |  | not_applicable |  |
