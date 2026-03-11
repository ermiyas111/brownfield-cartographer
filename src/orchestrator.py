import os
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from src.agents.surveyor import Surveyor
import networkx as nx
from networkx.readwrite import json_graph

def find_py_files(root: str):
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if f.endswith('.py'):
                yield os.path.join(dirpath, f)

def analyze_file(args):
    surveyor, file_path = args
    return surveyor.analyze_file(file_path)

def main(repo_path: str):
    surveyor = Surveyor(repo_path)
    files = list(find_py_files(repo_path))
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(surveyor.analyze_file, files))
    surveyor.build_graph()
    pagerank, circular = surveyor.analyze_graph()
    os.makedirs(os.path.join(repo_path, '.cartography'), exist_ok=True)
    out_path = os.path.join(repo_path, '.cartography', 'module_graph.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(json_graph.node_link_data(surveyor.graph), f, indent=2)
    print(f"Graph written to {out_path}\nHubs: {sorted(pagerank.items(), key=lambda x: -x[1])[:5]}\nCircular: {circular}")

if __name__ == '__main__':
    import sys
    main(sys.argv[1])
