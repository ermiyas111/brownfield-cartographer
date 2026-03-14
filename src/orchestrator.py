import os
import json
from concurrent.futures import ThreadPoolExecutor
from src.agents.surveyor import Surveyor
from src.agents.hydrologist import PythonDataFlowAnalyzer, SQLLineageAnalyzer, DAGConfigAnalyzer, DataLineageGraph
import networkx as nx
from networkx.readwrite import json_graph

def find_files(root: str, exts=(".py", ".sql", ".yaml", ".yml")):
    ignore_dirs = {'.git', '.venv', 'venv', '__pycache__'}
    for dirpath, dirnames, filenames in os.walk(root):
        # Remove ignored directories in-place
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
        for f in filenames:
            if f.endswith(exts):
                yield os.path.join(dirpath, f)

def main(repo_path: str):
    # Phase 1: Surveyor
    surveyor = Surveyor(repo_path)
    py_files = list(find_files(repo_path, (".py",)))
    with ThreadPoolExecutor() as executor:
        list(executor.map(surveyor.analyze_file, py_files))
    surveyor.build_graph()
    pagerank, circular = surveyor.analyze_graph()
    os.makedirs(os.path.join(repo_path, '.cartography'), exist_ok=True)
    out_path = os.path.join(repo_path, '.cartography', 'module_graph.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(json_graph.node_link_data(surveyor.graph), f, indent=2)
    print(f"Module graph written to {out_path}")

    # Phase 2: Hydrologist
    lineage_graph = DataLineageGraph()
    tree_sitter_router = getattr(surveyor, 'router', None)
    py_analyzer = PythonDataFlowAnalyzer(tree_sitter_router)
    sql_analyzer = SQLLineageAnalyzer()
    dag_analyzer = DAGConfigAnalyzer(tree_sitter_router)

    for file_path in find_files(repo_path, (".py",)):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            # Python data flow
            for result in py_analyzer.analyze(code):
                src = result.get('source', 'unresolved')
                sink = result.get('sink', 'unresolved')
                lineage_graph.add_node(src, {'type': 'source'})
                lineage_graph.add_node(sink, {'type': 'sink'})
                lineage_graph.add_edge(src, sink, {'file': file_path})
            # DAG config
            for dag in dag_analyzer.analyze(code):
                # Placeholder for DAG topology
                pass
        except Exception as e:
            print(f"[WARN] Could not analyze {file_path}: {e}")

    for file_path in find_files(repo_path, (".sql",)):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sql = f.read()
            for result in sql_analyzer.analyze(sql, file_path):
                for src in result.get('sources', []):
                    for sink in result.get('sinks', []):
                        lineage_graph.add_node(src, {'type': 'source'})
                        lineage_graph.add_node(sink, {'type': 'sink'})
                        lineage_graph.add_edge(src, sink, {'file': file_path})
        except Exception as e:
            print(f"[WARN] Could not analyze {file_path}: {e}")

    lineage_out = os.path.join(repo_path, '.cartography', 'lineage_graph.json')
    with open(lineage_out, 'w', encoding='utf-8') as f:
        json.dump(json_graph.node_link_data(lineage_graph.graph), f, indent=2)

    print(f"Lineage graph written to {lineage_out}")

    # Phase 3: Generate CODEBASE.md
    try:
        from src.agents.archivist import generate_CODEBASE_md
        # Build a mock knowledge_graph from available data (for now)
        knowledge_graph = {
            'clusters': [],  # TODO: Fill with real clusters from Semanticist
            'pagerank': [{'path': n, 'score': s} for n, s in getattr(surveyor, 'pagerank', {}).items()] if hasattr(surveyor, 'pagerank') else [],
            'sources': list(lineage_graph.graph.nodes),
            'sinks': list(lineage_graph.graph.nodes),
            'circular': circular if 'circular' in locals() else [],
            'high_velocity': [],  # TODO: Fill with real git velocity data
        }
        codebase_md_path = os.path.join(repo_path, '.cartography', 'CODEBASE.md')
        generate_CODEBASE_md(knowledge_graph, codebase_md_path)
        print(f"CODEBASE.md written to {codebase_md_path}")
    except Exception as e:
        print(f"[WARN] Could not generate CODEBASE.md: {e}")

if __name__ == '__main__':
    import sys
    main(sys.argv[1])
