# Architecture Overview

This system is organized into the following high-level domains: Domain 0. Each domain encapsulates related functionality for modularity and maintainability.

## Critical Path (Top 5 Modules by PageRank)

- airflow-core\docs\img\diagram_auth_manager_airflow_architecture.py (PageRank: 0.0001)
- airflow-core\docs\img\diagram_dag_processor_airflow_architecture.py (PageRank: 0.0001)
- airflow-core\docs\empty_plugin\empty_plugin.py (PageRank: 0.0001)
- airflow-core\hatch_build.py (PageRank: 0.0001)
- airflow-core\src\airflow\policies.py (PageRank: 0.0001)

## Ingestion/Egress Map

**Sources:**
- test_data
- TABLE(GENERATOR(ROWCOUNT => 5))
**Sinks:**
- None

## Pain Point Registry

**Circular Dependencies:**
**High Git Velocity (Churn):**
- airflow/www/views.py
- setup.py
- airflow/models.py
- airflow/models/taskinstance.py
- airflow/models/dag.py
- dev/breeze/src/airflow_breeze/global_constants.py
- airflow/configuration.py
- airflow/www/app.py
- dev/breeze/src/airflow_breeze/commands/release_management_commands.py
- tests/core.py

## Data Lineage PageRank (Top 5 Nodes)

- user (PageRank: 0.0003)
- Edge (PageRank: 0.0140)
- webserver (PageRank: 0.0003)
- auth_manager (PageRank: 0.0006)
- scheduler (PageRank: 0.0003)

## Data Lineage Circular Dependencies

- TaskGroup
- Task
- with -> relations
- via -> provides
- TaskGroup -> task
- op -> xcomarg
- bash_op2 -> xcom_args_b
- bash_op1 -> xcom_args_a
- group2_emp3 -> Label
- w2 -> w3 -> t1 -> s2
- w2 -> w3 -> t2 -> t1 -> s2
- group1 -> Label
- Label -> op3 -> t1
- Label -> group
- Label -> group3
- Label -> t2 -> t1
- t2 -> t1
- t2 -> t1 -> s2
- t1 -> s2
- t1 -> s2 -> op2 -> op3
- t1 -> s2 -> t0
- op3 -> op2

## AI-Readiness

This documentation is structured for optimal retrieval-augmented generation (RAG) and LLM context injection.
