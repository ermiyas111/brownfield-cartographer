import os

def generate_onboarding_brief(knowledge_graph, output_path):
    """
    Generate onboarding_brief.md with structured answers to the Five FDE Day-One Questions.
    """
    lines = []
    lines.append("# Onboarding Brief: FDE Day-One Answers\n")
    lines.append("This document provides immediate answers to the five most critical questions for new Forward-Deployed Engineers (FDEs).\n")

    # 1. What is the primary data ingestion path?
    sources = knowledge_graph.get('sources', [])
    primary_ingestion = sources[0] if sources else 'N/A'
    lines.append("## 1. What is the primary data ingestion path?\n")
    lines.append(f"**A:** {primary_ingestion}\n")
    lines.append(f"**Evidence:** All sources: {', '.join(sources)}\n")

    # 2. What are the 3-5 most critical output datasets/endpoints?
    sinks = knowledge_graph.get('sinks', [])
    critical_outputs = sinks[:5] if sinks else []
    lines.append("## 2. What are the 3-5 most critical output datasets/endpoints?\n")
    lines.append(f"**A:** {', '.join(critical_outputs) if critical_outputs else 'N/A'}\n")
    lines.append(f"**Evidence:** All sinks: {', '.join(sinks)}\n")

    # 3. What is the blast radius if the most critical module fails?
    pagerank = knowledge_graph.get('pagerank', [])
    most_critical = max(pagerank, key=lambda x: x['score'], default=None)
    blast_radius = []
    if most_critical and 'path' in most_critical:
        # Find all direct downstream nodes (out-edges)
        lineage_graph = knowledge_graph.get('lineage_graph', None)
        if lineage_graph:
            blast_radius = lineage_graph.get(most_critical['path'], [])
    lines.append("## 3. What is the blast radius if the most critical module fails?\n")
    if most_critical:
        lines.append(f"**A:** {most_critical['path']} (PageRank: {most_critical['score']:.4f})\n")
        if blast_radius:
            lines.append(f"**Blast Radius:** {', '.join(blast_radius)}\n")
        else:
            lines.append("**Blast Radius:** (See lineage_graph.json for downstream impact.)\n")
    else:
        lines.append("**A:** N/A\n")

    # 4. Where is the business logic concentrated vs. distributed?
    clusters = knowledge_graph.get('clusters', [])
    cluster_sizes = [(c['name'], len(c.get('modules', []))) for c in clusters]
    if cluster_sizes:
        concentrated = max(cluster_sizes, key=lambda x: x[1])
        distributed = min(cluster_sizes, key=lambda x: x[1])
        lines.append("## 4. Where is the business logic concentrated vs. distributed?\n")
        lines.append(f"**A:** Most concentrated in {concentrated[0]} ({concentrated[1]} modules); most distributed in {distributed[0]} ({distributed[1]} modules).\n")
        lines.append(f"**Evidence:** Cluster sizes: {', '.join([f'{n}: {s}' for n, s in cluster_sizes])}\n")
    else:
        lines.append("## 4. Where is the business logic concentrated vs. distributed?\n")
        lines.append("**A:** N/A\n")

    # 5. What has changed most frequently in the last 90 days (git velocity map)?
    high_velocity = knowledge_graph.get('high_velocity', [])
    lines.append("## 5. What has changed most frequently in the last 90 days (git velocity map)?\n")
    lines.append(f"**A:** {', '.join(high_velocity) if high_velocity else 'N/A'}\n")
    lines.append(f"**Evidence:** Top changed files: {', '.join(high_velocity)}\n")

    # Evidence and references
    lines.append("\n---\n")
    lines.append("For further evidence, see CODEBASE.md, lineage_graph.json, and module_graph.json.\n")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    return output_path
