import os
import json

def generate_semantic_index(module_nodes, output_dir):
    """
    Save all module purpose statements as a vector store (JSONL) for semantic search.
    """
    os.makedirs(output_dir, exist_ok=True)
    index_path = os.path.join(output_dir, 'semantic_index.jsonl')
    with open(index_path, 'w', encoding='utf-8') as f:
        for node in module_nodes:
            entry = {
                'path': node.get('path'),
                'semantic_purpose': node.get('semantic_purpose', ''),
                'domain_cluster': node.get('domain_cluster', None),
                # Add embedding/vector here if available
            }
            f.write(json.dumps(entry) + '\n')
    return index_path
