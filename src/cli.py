
import typer
import os
import tempfile
import shutil
import re
import subprocess
import json
import networkx as nx
from src.orchestrator import main
from src.agents.navigator import Navigator

def is_github_url(path: str) -> bool:
    return bool(re.match(r"https://github.com/.+/.+", path))


app = typer.Typer()

@app.command()
def analyze(
    reference: str = typer.Argument(..., help="Path to local repo or GitHub URL")
):
    """Analyze a codebase (local path or GitHub URL) and build the module graph."""
    repo_path = reference
    temp_dir = None
    if is_github_url(reference):
        temp_dir = tempfile.mkdtemp(prefix="meltano_repo_")
        print(f"Cloning {reference} to {temp_dir}...")
        subprocess.run(["git", "clone", reference, temp_dir], check=True)
        repo_path = temp_dir
    try:
        main(repo_path)
        # If using a temp_dir (GitHub clone), copy .cartography outputs to CWD
        if temp_dir:
            src_cartography = os.path.join(temp_dir, '.cartography')
            if os.path.exists(src_cartography):
                dest_cartography = os.path.join(os.getcwd(), '.cartography')
                if os.path.exists(dest_cartography):
                    shutil.rmtree(dest_cartography, ignore_errors=True)
                shutil.copytree(src_cartography, dest_cartography)
                print(f"Copied .cartography results to {dest_cartography}")
    finally:
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)

@app.command()
def query(
    command: str = typer.Argument(..., help="Query type: trace_lineage or blast_radius"),
    node: str = typer.Argument(..., help="Node name (dataset, table, or module)")
):
    """Query the lineage graph for trace_lineage or blast_radius."""
    lineage_path = os.path.join('.cartography', 'lineage_graph.json')
    knowledge_path = os.path.join('.cartography', 'module_graph.json')
    if not os.path.exists(lineage_path):
        print(f"Lineage graph not found at {lineage_path}")
        raise typer.Exit(1)
    with open(lineage_path, 'r', encoding='utf-8') as f:
        lineage_graph = json.load(f)
    # Load knowledge_graph if needed for file:line evidence (future)
    # with open(knowledge_path, 'r', encoding='utf-8') as f:
    #     knowledge_graph = json.load(f)
    # Use Navigator for queries
    nav = Navigator({'lineage_graph': lineage_graph})
    if command == 'trace_lineage':
        # Upstream traversal (BFS)
        G = build_nx_graph(lineage_graph)
        if node not in G:
            print(f"Node '{node}' not found in lineage graph.")
            raise typer.Exit(1)
        upstream = list(nx.ancestors(G, node))
        print(f"Upstream sources for {node}:")
        for src in upstream:
            print(f"- {src}")
    elif command == 'blast_radius':
        # Downstream traversal (BFS)
        G = build_nx_graph(lineage_graph)
        if node not in G:
            print(f"Node '{node}' not found in lineage graph.")
            raise typer.Exit(1)
        downstream = list(nx.descendants(G, node))
        print(f"Blast radius for {node} (downstream dependents):")
        for tgt in downstream:
            print(f"- {tgt}")
    else:
        print(f"Unknown query command: {command}")
        raise typer.Exit(1)

def build_nx_graph(lineage_graph):
    import networkx as nx
    G = nx.DiGraph()
    for node in lineage_graph.get('nodes', []):
        G.add_node(node['id'])
    for edge in lineage_graph.get('edges', []):
        G.add_edge(edge['source'], edge['target'])
    return G


if __name__ == "__main__":
    app()