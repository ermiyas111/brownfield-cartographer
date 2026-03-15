import os
import json
from typing import List, Dict, Any
from datetime import datetime

def generate_CODEBASE_md(knowledge_graph, output_path):
    """
    Generate CODEBASE.md documentation from the KnowledgeGraph.
    """
    lines = []
    # Architecture Overview
    clusters = knowledge_graph.get('clusters', [])
    overview = f"This system is organized into the following high-level domains: {', '.join(set(c['name'] for c in clusters))}. Each domain encapsulates related functionality for modularity and maintainability."
    lines.append("# Architecture Overview\n")
    lines.append(overview + "\n")
    # Critical Path
    pagerank = knowledge_graph.get('pagerank', [])
    lines.append("## Critical Path (Top 5 Modules by PageRank)\n")
    for node in pagerank[:5]:
        lines.append(f"- {node['path']} (PageRank: {node['score']:.4f})")
    lines.append("")
    # Ingestion/Egress Map
    sources = knowledge_graph.get('sources', [])
    sinks = knowledge_graph.get('sinks', [])
    lines.append("## Ingestion/Egress Map\n")
    lines.append("**Sources:**")
    for src in sources:
        lines.append(f"- {src}")
    lines.append("**Sinks:**")
    for sink in sinks:
        lines.append(f"- {sink}")
    lines.append("")
    # Pain Point Registry
    circular = knowledge_graph.get('circular', [])
    high_velocity = knowledge_graph.get('high_velocity', [])
    lines.append("## Pain Point Registry\n")
    lines.append("**Circular Dependencies:**")
    for c in circular:
        lines.append(f"- {c}")
    lines.append("**High Git Velocity (Churn):**")
    for hv in high_velocity:
        lines.append(f"- {hv}")
    lines.append("")
    # Lineage Graph Insights
    lineage_pagerank = knowledge_graph.get('lineage_pagerank', [])
    lineage_circular = knowledge_graph.get('lineage_circular', [])
    if lineage_pagerank:
        lines.append("## Data Lineage PageRank (Top 5 Nodes)\n")
        for node in lineage_pagerank[:5]:
            lines.append(f"- {node['node']} (PageRank: {node['score']:.4f})")
        lines.append("")
    if lineage_circular:
        lines.append("## Data Lineage Circular Dependencies\n")
        for cycle in lineage_circular:
            lines.append(f"- {' -> '.join(cycle)}")
        lines.append("")
    # AI-Readiness
    lines.append("## AI-Readiness\n")
    lines.append("This documentation is structured for optimal retrieval-augmented generation (RAG) and LLM context injection.\n")
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    return output_path
