import logging
from typing import List, Dict, Any
import os

def extract_dag_topology(filepath: str) -> List[Dict[str, Any]]:
    """
    Extract task-level topology from YAML or Airflow Python config.
    Returns a flat list of edges: {source, target, type}
    """
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext in (".yaml", ".yml"):
            import yaml
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return _extract_yaml_edges(data)
        elif ext == ".py":
            return _extract_airflow_edges(filepath)
        else:
            logging.warning(f"[dag_config_parser] Unsupported file type: {filepath}")
            return []
    except Exception as e:
        logging.warning(f"[dag_config_parser] Could not parse {filepath}: {e}")
        return []

def _extract_yaml_edges(data: Any) -> List[Dict[str, Any]]:
    edges = []
    if isinstance(data, dict):
        for task, props in data.items():
            depends = props.get('depends_on') or []
            if isinstance(depends, str):
                depends = [depends]
            for dep in depends:
                edges.append({"source": dep, "target": task, "type": "config_flow"})
    return edges

def _extract_airflow_edges(filepath: str) -> List[Dict[str, Any]]:
    import ast
    edges = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=filepath)
        # Find task_id assignments and >> operator usage
        task_ids = {}
        class TaskVisitor(ast.NodeVisitor):
            def visit_Assign(self, node):
                if isinstance(node.value, ast.Call):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            # Heuristic: look for task_id in kwargs
                            for kw in node.value.keywords:
                                if kw.arg == 'task_id' and isinstance(kw.value, ast.Constant):
                                    task_ids[target.id] = kw.value.value
                self.generic_visit(node)
            def visit_BinOp(self, node):
                if isinstance(node.op, ast.RShift):
                    left = getattr(node.left, 'id', None)
                    right = getattr(node.right, 'id', None)
                    if left and right:
                        edges.append({"source": task_ids.get(left, left), "target": task_ids.get(right, right), "type": "config_flow"})
                self.generic_visit(node)
        TaskVisitor().visit(tree)
    except Exception as e:
        logging.warning(f"[dag_config_parser] Airflow parse error in {filepath}: {e}")
    return edges
