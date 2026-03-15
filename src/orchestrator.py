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
                src = result.get('source')
                sink = result.get('sink')
                # Only add valid nodes/edges (not None or empty)
                if src and src != 'None':
                    lineage_graph.add_node(src, {'type': 'source'})
                if sink and sink != 'None':
                    lineage_graph.add_node(sink, {'type': 'sink'})
                if src and sink and src != 'None' and sink != 'None':
                    lineage_graph.add_edge(src, sink, {'file': file_path})
            # DAG config: add Airflow DAGs, operators, and dependencies to lineage graph
            for dag_result in dag_analyzer.analyze(code):
                if dag_result['type'] == 'dag':
                    dag_id = dag_result['definition'][:40]  # Use first 40 chars as ID (improve as needed)
                    lineage_graph.add_node(dag_id, {'type': 'dag'})
                elif dag_result['type'] == 'operator':
                    op_id = dag_result['operator']
                    lineage_graph.add_node(op_id, {'type': 'operator'})
                elif dag_result['type'] == 'dependency':
                    left = dag_result['from']
                    right = dag_result['to']
                    direction = dag_result['direction']
                    # Add nodes if not present
                    lineage_graph.add_node(left, {'type': 'task'})
                    lineage_graph.add_node(right, {'type': 'task'})
                    # Add edge in correct direction
                    if direction == '>>':
                        lineage_graph.add_edge(left, right, {'type': 'dependency'})
                    elif direction == '<<':
                        lineage_graph.add_edge(right, left, {'type': 'dependency'})
        except Exception as e:
            print(f"[WARN] Could not analyze {file_path}: {e}")

    for file_path in find_files(repo_path, (".sql",)):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sql = f.read()
            for result in sql_analyzer.analyze(sql, file_path):
                sources = result.get('sources', [])
                sinks = result.get('sinks', [])
                for src in sources:
                    if src and src != 'unresolved':
                        lineage_graph.add_node(src, {'type': 'source'})
                for sink in sinks:
                    if sink and sink != 'unresolved':
                        lineage_graph.add_node(sink, {'type': 'sink'})
                for src in sources:
                    for sink in sinks:
                        if src and sink and src != 'unresolved' and sink != 'unresolved':
                            lineage_graph.add_edge(src, sink, {'file': file_path, 'type': 'sql_lineage'})
        except Exception as e:
            print(f"[WARN] Could not analyze {file_path}: {e}")

    lineage_out = os.path.join(repo_path, '.cartography', 'lineage_graph.json')
    with open(lineage_out, 'w', encoding='utf-8') as f:
        json.dump(json_graph.node_link_data(lineage_graph.graph), f, indent=2)

    print(f"Lineage graph written to {lineage_out}")

    # Phase 3: Semanticist enrichment and CODEBASE.md
    try:
        from src.agents.archivist import generate_CODEBASE_md
        from src.agents.semanticist import Semanticist
        import asyncio
        import subprocess
        # Collect module nodes (Python files)
        module_nodes = []
        for file_path in find_files(repo_path, (".py",)):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                docstring = ''
                if code.strip().startswith('"""') or code.strip().startswith("'''"):
                    docstring = code.strip().split('\n')[0].strip('"\' ')
                module_nodes.append({'path': file_path, 'code': code, 'docstring': docstring})
            except Exception as e:
                print(f"[WARN] Could not read {file_path}: {e}")
        # Run Semanticist to generate purpose statements and clusters
        semanticist = Semanticist(None)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        module_nodes = loop.run_until_complete(semanticist.bulk_generate_purpose_statements(module_nodes))
        module_nodes = semanticist.cluster_into_domains(module_nodes)
        # Compute PageRank and cycles for both module graph and lineage graph
        pr = nx.pagerank(surveyor.graph)
        pagerank = [{'path': n, 'score': s} for n, s in pr.items()]
        try:
            circular = list(nx.simple_cycles(surveyor.graph))
        except Exception:
            circular = []

        # PageRank and cycles for lineage graph
        try:
            lineage_pagerank = nx.pagerank(lineage_graph.graph)
        except Exception:
            lineage_pagerank = {}
        try:
            lineage_circular = list(nx.simple_cycles(lineage_graph.graph))
        except Exception:
            lineage_circular = []
        # Git velocity (churn): top 10 most changed files
        high_velocity = []
        try:
            git_cmd = ["git", "-C", repo_path, "log", "--pretty=format:", "--name-only"]
            output = subprocess.check_output(git_cmd, encoding="utf-8", errors="ignore")
            file_counts = {}
            for line in output.splitlines():
                line = line.strip()
                if line and line.endswith('.py'):
                    file_counts[line] = file_counts.get(line, 0) + 1
            high_velocity = sorted(file_counts, key=file_counts.get, reverse=True)[:10]
        except Exception as e:
            print(f"[WARN] Could not compute git velocity: {e}")
        # Improved sources/sinks extraction from lineage_graph
        sources = [n for n, d in lineage_graph.graph.nodes(data=True) if d.get('type') == 'source']
        sinks = [n for n, d in lineage_graph.graph.nodes(data=True) if d.get('type') == 'sink']
        # Build knowledge_graph
        clusters = []
        for cluster_id in set(n['domain_cluster'] for n in module_nodes):
            clusters.append({
                'name': f"Domain {cluster_id}",
                'modules': [n['path'] for n in module_nodes if n['domain_cluster'] == cluster_id]
            })
        knowledge_graph = {
            'clusters': clusters,
            'pagerank': pagerank,
            'sources': sources,
            'sinks': sinks,
            'circular': circular,
            'high_velocity': high_velocity,
            'modules': module_nodes,
            'lineage_pagerank': [{'node': n, 'score': s} for n, s in lineage_pagerank.items()],
            'lineage_circular': lineage_circular,
        }
        codebase_md_path = os.path.join(repo_path, '.cartography', 'CODEBASE.md')
        generate_CODEBASE_md(knowledge_graph, codebase_md_path)
        print(f"CODEBASE.md written to {codebase_md_path}")
    except Exception as e:
        import traceback
        print(f"[ERROR] Could not generate CODEBASE.md: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    import sys
    main(sys.argv[1])
