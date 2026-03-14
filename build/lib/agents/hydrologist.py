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
        # Placeholder: Use tree-sitter to find data calls and extract sources/sinks
        # If argument is dynamic, label as DYNAMIC_REFERENCE
        # Return list of dicts: {type, source, sink, file, dynamic}
        return []

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
        # Placeholder: Use tree-sitter to extract DAG topology from Airflow dag.py
        return []

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
