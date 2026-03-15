import os
import re
import logging
import networkx as nx
from typing import List, Dict, Any, Optional
from src.models.lineage_node import LineageNode
from src.models.lineage_edge import LineageEdge
import sqlglot

logger = logging.getLogger("hydrologist")

class PythonDataFlowAnalyzer:
    DATA_CALLS = [
        ("pandas", "read_csv"),
        ("pandas", "read_sql"),
        ("sqlalchemy", "execute"),
        ("pyspark", "read"),
        ("pyspark", "write"),
    ]

    def __init__(self, tree_sitter_router):
        self.router = tree_sitter_router

    def analyze(self, code: str) -> List[Dict[str, Any]]:
        results = []
        # Try to use tree-sitter if available, else fallback to regex for demo
        try:
            if self.router:
                tree = self.router.parse(code)
                # TODO: Implement real tree-sitter logic for pandas/sqlalchemy/pyspark
                # For now, fallback to regex below
        except Exception as e:
            logger.warning(f"Tree-sitter parse failed: {e}")

        # Regex fallback for demo: pandas.read_csv, pandas.read_sql, sqlalchemy.execute, pyspark.read/write
        patterns = [
            (r"pandas\.read_csv\(([^)]+)\)", 'read_csv'),
            (r"pandas\.read_sql\(([^)]+)\)", 'read_sql'),
            (r"sqlalchemy\.[\w_]+\.execute\(([^)]+)\)", 'execute'),
            (r"pyspark\.[\w_]+\.read\(([^)]+)\)", 'read'),
            (r"pyspark\.[\w_]+\.write\(([^)]+)\)", 'write'),
        ]
        for pat, call_type in patterns:
            for m in re.finditer(pat, code):
                arg = m.group(1).strip()
                # Try to extract string literal, else mark as dynamic
                if arg.startswith("f\"") or arg.startswith("f'" ):
                    dataset = 'DYNAMIC_REFERENCE'
                    dynamic = True
                elif arg.startswith('"') or arg.startswith("'"):
                    dataset = arg.strip('"\' ')
                    dynamic = False
                else:
                    dataset = 'DYNAMIC_REFERENCE'
                    dynamic = True
                results.append({
                    'type': call_type,
                    'source': dataset if call_type in ['read_csv', 'read_sql', 'read'] else None,
                    'sink': dataset if call_type in ['write', 'execute'] else None,
                    'dynamic': dynamic
                })
        # Real extraction: try to pair reads and writes in the same file
        reads = []
        writes = []
        for pat, call_type in patterns:
            for m in re.finditer(pat, code):
                arg = m.group(1).strip()
                if arg.startswith("f\"") or arg.startswith("f'"):
                    dataset = 'DYNAMIC_REFERENCE'
                    dynamic = True
                elif arg.startswith('"') or arg.startswith("'"):
                    dataset = arg.strip('"\' ')
                    dynamic = False
                else:
                    dataset = 'DYNAMIC_REFERENCE'
                    dynamic = True
                if call_type in ['read_csv', 'read_sql', 'read']:
                    reads.append({'type': call_type, 'dataset': dataset, 'dynamic': dynamic})
                elif call_type in ['write', 'execute']:
                    writes.append({'type': call_type, 'dataset': dataset, 'dynamic': dynamic})
        # Pair reads and writes for edges, else emit as sources/sinks
        for r in reads:
            results.append({'type': r['type'], 'source': r['dataset'], 'sink': None, 'dynamic': r['dynamic']})
        for w in writes:
            results.append({'type': w['type'], 'source': None, 'sink': w['dataset'], 'dynamic': w['dynamic']})
        # Add edges between all reads and writes in the same file (simple heuristic)
        for r in reads:
            for w in writes:
                if r['dataset'] != 'DYNAMIC_REFERENCE' and w['dataset'] != 'DYNAMIC_REFERENCE':
                    results.append({'type': 'edge', 'source': r['dataset'], 'sink': w['dataset'], 'dynamic': False})
        return results

class SQLLineageAnalyzer:
    def __init__(self):
        pass

    def parse_sql(self, sql: str, dialect: Optional[str] = None) -> List[Dict[str, Any]]:
        try:
            parsed = sqlglot.parse_one(sql, read=dialect)
            tables = set()
            sinks = set()
            for node in parsed.walk():
                if node.key == "from" or node.key == "join":
                    tables.add(str(node.args.get("this")))
                if node.key == "select":
                    sinks.add(str(node.args.get("this")))
            return [{"sources": list(tables), "sinks": list(sinks)}]
        except Exception as e:
            logger.warning(f"SQL parse failed: {e}")
            return [{"sources": ["unresolved"], "sinks": ["unresolved"]}]

    def analyze(self, sql: str, file_path: str) -> List[Dict[str, Any]]:
        dialect = None
        if "bigquery" in file_path.lower():
            dialect = "bigquery"
        elif "postgres" in file_path.lower() or "pg_" in file_path.lower():
            dialect = "postgres"
        return self.parse_sql(sql, dialect)

class DAGConfigAnalyzer:
    def __init__(self, tree_sitter_router):
        self.router = tree_sitter_router

    def analyze(self, code: str) -> List[Dict[str, Any]]:
        # Simple regex-based Airflow DAG and task extraction
        results = []
        # Find DAG definitions
        dag_matches = re.findall(r'DAG\s*\(.*?\)', code, re.DOTALL)
        for dag_def in dag_matches:
            results.append({'type': 'dag', 'definition': dag_def})
        # Find operator/task instantiations (e.g., PythonOperator, BashOperator, etc.)
        op_matches = re.findall(r'(\w+Operator)\s*\(', code)
        for op in op_matches:
            results.append({'type': 'operator', 'operator': op})
        # Find task dependencies (>> or <<)
        dep_matches = re.findall(r'(\w+)\s*(>>|<<)\s*(\w+)', code)
        for left, op, right in dep_matches:
            results.append({'type': 'dependency', 'from': left, 'to': right, 'direction': op})
        return results

class DataLineageGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_node(self, node_id: str, node_data: dict):
        self.graph.add_node(node_id, **node_data)

    def add_edge(self, source: str, target: str, edge_data: dict):
        self.graph.add_edge(source, target, **edge_data)

    def blast_radius(self, node: str) -> List[str]:
        return list(nx.descendants(self.graph, node))

    def find_sources(self) -> List[str]:
        return [n for n in self.graph.nodes if self.graph.in_degree(n) == 0]

    def find_sinks(self) -> List[str]:
        return [n for n in self.graph.nodes if self.graph.out_degree(n) == 0]
