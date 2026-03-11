# Brownfield Cartographer

**Mission:** Transform a massive, unmapped codebase into a living, queryable map—empowering engineers to orient themselves and drive change within 72 hours.

## Project Overview
Brownfield Cartographer is a static analysis and knowledge graph tool for Python/SQL codebases (with a focus on Apache Airflow). It rapidly maps both the structural skeleton (modules, imports, classes) and the data lineage (tables, configs, DAGs) of a codebase, outputting results as queryable JSON graphs.

## Prerequisites
1. **Python 3.12+** (tree-sitter-languages does not support Python 3.13+)
2. **uv** for dependency management ([Install uv](https://github.com/astral-sh/uv))
3. Access to a local **Git repository** (the codebase you want to map)

## Installation
1. Clone this repository and `cd` into it.
2. Create a virtual environment and install dependencies:
	```sh
	uv venv
	uv pip install .
	```
	_Alternatively, use:_
	```sh
	pip install -r requirements.txt
	```
3. **Note:** The tool uses [tree-sitter-languages](https://github.com/grantjenks/python-tree-sitter-languages) for parsing Python, SQL, YAML, and TypeScript. No manual grammar setup is required.

## Usage
### 1. Run the Analyzer
```sh
python src/cli.py analyze <repo_path>
```
- `<repo_path>`: Path to the root of the codebase you want to analyze (must be a local Git repo).
- This command triggers the orchestrator, which runs the **Surveyor** (structural mapping) and **Hydrologist** (data lineage) agents sequentially.

### 2. Output Artifacts
After execution, results are written to the `.cartography/` directory inside your target repo:
- `module_graph.json`: Structural graph of modules, imports, classes, and functions. Includes PageRank scores and circular dependency detection.
- `lineage_graph.json`: Data lineage graph showing table-level and config-level data flows (partial, SQL-based extraction).

#### Interpreting Results
- **module_graph.json**: Nodes represent code modules; edges represent imports/inheritance. High PageRank nodes are architectural hubs. Cycles indicate spaghetti/circular dependencies.
- **lineage_graph.json**: Nodes represent tables, files, or tasks; edges represent data movement or config dependencies. Use this to trace data flow and blast radius.

## System Map: Agentic Architecture
- **Surveyor Agent:** Crawls the codebase, parses files with tree-sitter, builds the structural graph, and computes analytics (PageRank, cycles, git velocity).
- **Hydrologist Agent:** Extracts data lineage by parsing SQL (via sqlglot), YAML configs, and Airflow DAGs, then builds a unified data flow graph.

## Configuration
- **SQL Dialect:** The SQLLineageAnalyzer auto-detects dialects (Postgres, BigQuery) based on file path. To force a dialect, edit the analyzer or pass the `dialect` argument in your own scripts.
- **Extensibility:** The system is modular—add new analyzers or extend the KnowledgeGraph for custom needs.

## Day-One Orientation
This tool is designed for the "Day-One" problem: helping Forward Deployed Engineers rapidly understand and navigate unfamiliar, legacy codebases. Within minutes, you'll have a living map of both code structure and data flow.

## Current Capabilities
- **Structural Mapping:** Module graph, PageRank hubs, and circular dependency detection.
- **Partial Data Lineage:** SQL lineage extraction via sqlglot (YAML and Airflow DAG parsing in progress).

---
For questions or contributions, please open an issue or pull request.
# brownfield-cartographer
