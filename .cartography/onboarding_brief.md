# Onboarding Brief: FDE Day-One Answers

This document provides immediate answers to the five most critical questions for new Forward-Deployed Engineers (FDEs).

## 1. What is the primary data ingestion path?

**A:** test_data

**Evidence:** All sources: test_data, TABLE(GENERATOR(ROWCOUNT => 5))

## 2. What are the 3-5 most critical output datasets/endpoints?

**A:** None

**Evidence:** All sinks: None

## 3. What is the blast radius if the most critical module fails?

**A:** airflow-core\docs\img\diagram_auth_manager_airflow_architecture.py (PageRank: 0.0001)

**Blast Radius:** (See lineage_graph.json for downstream impact.)

## 4. Where is the business logic concentrated vs. distributed?

**A:** Most concentrated in Domain 0 (6863 modules); most distributed in Domain 0 (6863 modules).

**Evidence:** Cluster sizes: Domain 0: 6863

## 5. What has changed most frequently in the last 90 days (git velocity map)?

**A:** airflow/www/views.py, setup.py, airflow/models.py, airflow/models/taskinstance.py, airflow/models/dag.py, dev/breeze/src/airflow_breeze/global_constants.py, airflow/configuration.py, airflow/www/app.py, dev/breeze/src/airflow_breeze/commands/release_management_commands.py, tests/core.py

**Evidence:** Top changed files: airflow/www/views.py, setup.py, airflow/models.py, airflow/models/taskinstance.py, airflow/models/dag.py, dev/breeze/src/airflow_breeze/global_constants.py, airflow/configuration.py, airflow/www/app.py, dev/breeze/src/airflow_breeze/commands/release_management_commands.py, tests/core.py


---

For further evidence, see CODEBASE.md, lineage_graph.json, and module_graph.json.
