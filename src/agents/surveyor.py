import os
import subprocess
import networkx as nx
from typing import List, Dict, Any
from src.models.module_node import ModuleNode
from src.models.dependency_edge import DependencyEdge
from src.analyzers.tree_sitter_analyzer import LanguageRouter

class Surveyor:
    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.router = LanguageRouter()
        self.graph = nx.DiGraph()
        self.module_nodes: Dict[str, ModuleNode] = {}

    def extract_git_velocity(self, path: str, days: int = 30) -> float:
        rel_path = os.path.relpath(path, self.repo_root)
        cmd = [
            'git', 'log', f'--since={days}.days', '--pretty=format:', '--name-only', '--', rel_path
        ]
        try:
            output = subprocess.check_output(cmd, cwd=self.repo_root, text=True)
            files = [line for line in output.split('\n') if line.strip()]
            return len(files) / days if days else 0.0
        except Exception:
            return 0.0

    def analyze_file(self, file_path: str) -> ModuleNode:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        rel_path = os.path.relpath(file_path, self.repo_root)
        analysis = self.router.analyze(file_path, code)
        git_velocity = self.extract_git_velocity(file_path)
        imports = analysis.get('imports', [])
        classes = [c['name'] for c in analysis.get('classes', [])]
        functions = analysis.get('functions', [])
        node = ModuleNode(
            name=os.path.splitext(os.path.basename(file_path))[0],
            path=rel_path,
            imports=imports,
            classes=classes,
            functions=functions,
            git_velocity=git_velocity
        )
        self.module_nodes[rel_path] = node
        return node

    def build_graph(self):
        for node in self.module_nodes.values():
            self.graph.add_node(node.path, **node.dict())
            for imp in node.imports:
                # Simplified import edge logic
                target = imp.split('import')[-1].strip().split(' ')[0].replace('.', os.sep) + '.py'
                if target in self.module_nodes:
                    self.graph.add_edge(node.path, target, type='import')

    def analyze_graph(self):
        pagerank = nx.pagerank(self.graph)
        for path, pr in pagerank.items():
            if path in self.module_nodes:
                self.module_nodes[path].pagerank = pr
        circular = list(nx.strongly_connected_components(self.graph))
        return pagerank, [c for c in circular if len(c) > 1]
