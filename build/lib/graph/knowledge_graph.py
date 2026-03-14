import networkx as nx
from networkx.readwrite import json_graph
import json
import logging
from typing import Any, Dict, Optional, List, Tuple

logger = logging.getLogger("knowledge_graph")

class KnowledgeGraph:
    def __init__(self) -> None:
        self.graph = nx.DiGraph()
        self.node_types = {}

    def add_node(self, node_id: str, node_type: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        if node_id not in self.graph:
            self.graph.add_node(node_id, type=node_type, **(metadata or {}))
            self.node_types[node_id] = node_type
        else:
            # Update metadata if node exists
            self.graph.nodes[node_id].update(metadata or {})
            self.graph.nodes[node_id]['type'] = node_type
            self.node_types[node_id] = node_type

    def add_edge(self, source: str, target: str, edge_type: str, weight: float = 1.0) -> None:
        if source not in self.graph:
            logger.warning(f"[KnowledgeGraph] Source node '{source}' missing, creating stub.")
            self.add_node(source, node_type="Stub", metadata={})
        if target not in self.graph:
            logger.warning(f"[KnowledgeGraph] Target node '{target}' missing, creating stub.")
            self.add_node(target, node_type="Stub", metadata={})
        self.graph.add_edge(source, target, type=edge_type, weight=weight)

    def get_hub_nodes(self, top_n: int = 5) -> List[Tuple[str, float]]:
        pr = nx.pagerank(self.graph)
        return sorted(pr.items(), key=lambda x: -x[1])[:top_n]

    def detect_cycles(self) -> List[List[str]]:
        return [cycle for cycle in nx.simple_cycles(self.graph)]

    def get_downstream_path(self, start_node: str) -> List[str]:
        return list(nx.descendants(self.graph, start_node))

    def save_to_json(self, path: str) -> None:
        data = json_graph.node_link_data(self.graph)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def load_from_json(self, path: str) -> None:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.graph = json_graph.node_link_graph(data, directed=True)
        # Rebuild node_types registry
        self.node_types = {n: d.get('type', 'Unknown') for n, d in self.graph.nodes(data=True)}

    def export_summary(self) -> str:
        n_nodes = self.graph.number_of_nodes()
        n_edges = self.graph.number_of_edges()
        n_cycles = len(self.detect_cycles())
        return f"Graph contains {n_nodes} nodes and {n_edges} edges, with {n_cycles} circular dependencies found."
