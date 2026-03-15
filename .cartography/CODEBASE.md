# Architecture Overview

This system is organized into the following high-level domains: Domain 0. Each domain encapsulates related functionality for modularity and maintainability.

## Critical Path (Top 5 Modules by PageRank)

- airflow-core\docs\img\diagram_auth_manager_airflow_architecture.py (PageRank: 0.0001)
- airflow-core\docs\img\diagram_basic_airflow_architecture.py (PageRank: 0.0001)
- airflow-core\hatch_build.py (PageRank: 0.0001)
- airflow-core\src\airflow\providers_manager.py (PageRank: 0.0001)
- airflow-core\docs\img\diagram_dag_processor_airflow_architecture.py (PageRank: 0.0001)

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
- provides -> via
- TaskGroup -> task
- op -> xcomarg
- xcom_args_b -> bash_op2
- xcom_args_a -> bash_op1
- w2 -> w3 -> t1 -> s2
- w2 -> w3 -> t2 -> t1 -> s2
- op2 -> op3 -> t1 -> s2
- op2 -> op3
- t2 -> t1
- t2 -> t1 -> s2
- t2 -> t1 -> Label
- group3 -> Label
- Label -> op3 -> t1
- Label -> group
- Label -> group1
- Label -> group2_emp3
- t1 -> s2
- t1 -> s2 -> t0

## AI-Readiness

This documentation is structured for optimal retrieval-augmented generation (RAG) and LLM context injection.
