# RECONNAISSANCE.md

## 1. The Five FDE Day-One Questions (Manual Ground Truth)

### **Q1: What is the primary data ingestion path?**
Airflow is an orchestrator, not a specialized ETL tool, so "ingestion" is fragmented. The primary entry point for a developer is the **Scheduler**.
* **Code Path:** `airflow/jobs/scheduler_job_runner.py` manages the orchestration loop.
* **The "Work":** The actual data movement happens in the **Providers** (e.g., `airflow/providers/google/`, `airflow/providers/amazon/`).
* **Discovery:** Searching for "S3ToGCS" or "Copy" in the providers' directory reveals how data actually moves between clouds.

### **Q2: What is the "Blast Radius"?**
* **The Core:** Almost everything. Specifically, the **Models** layer (`airflow/models/`).
* **Critical Files:** `airflow/models/dag.py`, `airflow/models/taskinstance.py`, and `airflow/models/baseoperator.py`. 
* **Impact:** Any schema change requires a migration via Alembic (`airflow/migrations/`). A break here kills the Webserver, Scheduler, and Workers simultaneously because they all heartbeat to the same metadata DB.

### **Q3: Where is the "Silent Debt"? (Logic vs. Documentation)**
* **The Drift:** The official docs emphasize the modern "TaskFlow API" (decorators), but the codebase is still heavily reliant on "Classic Operators."
* **Evidence:** Deep in `airflow/utils/helpers.py` and the complex logic in `airflow/www/views.py`, there are legacy workarounds for XCom backends and timezone handling that aren't fully reflected in the "getting started" guides.
* **The "Gotcha":** The relationship between `TaskGroup` and the old `SubDAG` logic is a graveyard of deprecated-but-still-present code.

### **Q4: What is the "Hidden Architecture"? (The undocumented "True" flow)**
* **The Reality:** The `airflow/executors/` directory. While the UI shows DAGs, the true execution power (and complexity) lies in how the **CeleryExecutor** or **KubernetesExecutor** interfaces with the OS. 
* **The Secret Sauce:** The `airflow/settings.py` file. It’s the "ghost in the machine" that configures the environment, database connections, and pluggable components before any code even runs.

### **Q5: What is the "Dead Wood"? (Unused or Deprecated paths)**
* **Legacy UI:** There are still remnants of the older Flask-AppBuilder views that are being transitioned to the new REST API and future UI iterations.
* **Old Providers:** Certain internal "contrib" or older provider hooks (like legacy Hadoop/HDFS hooks) have significantly less activity and test coverage compared to the modern cloud providers, suggesting they are candidates for deprecation or "maintenance mode."

---

## 2. Difficulty Analysis: The "Manual Fatigue" Report

### **What was hardest to figure out?**
**Traceability of an Execution.** I spent 15 minutes trying to follow exactly what happens from the moment a user clicks "Trigger DAG" in the UI to the moment a Python function executes on a worker. 
* The path goes: `www/views.py` -> `models/dag.py` -> `database` -> `scheduler_job_runner.py` -> `executors/` -> `task_command.py`. 
* Manually jumping between these files across thousands of lines of code is mentally taxing and where I most frequently lost the "thread."

### **Where did I get lost?**
* **Inheritance Complexity:** `BaseOperator` is inherited by multiple other classes. Finding where a specific argument (like `retries`) is actually validated versus where it’s just passed along in `**kwargs` is a nightmare without a robust symbol-mapping tool.
* **The Provider Jungle:** The `airflow/providers` directory is so large it crashes some basic IDE search indexes