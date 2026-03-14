import os
import subprocess
import json
from src.agents.surveyor import Surveyor
from src.agents.semanticist import Semanticist
from src.agents.cartography_trace import save_knowledge_graph, load_knowledge_graph

def get_git_head_hash(repo_path):
    return subprocess.check_output(['git', '-C', repo_path, 'rev-parse', 'HEAD'], encoding='utf-8').strip()

def get_changed_files(repo_path, old_hash, new_hash):
    diff = subprocess.check_output(['git', '-C', repo_path, 'diff', '--name-only', old_hash, new_hash], encoding='utf-8')
    return [line.strip() for line in diff.splitlines() if line.strip()]

def checkpoint_update(repo_path, knowledge_graph_path, meta_path):
    # Load previous meta
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
    else:
        meta = {}
    old_hash = meta.get('git_head')
    new_hash = get_git_head_hash(repo_path)
    if old_hash == new_hash:
        return 'No changes.'
    changed_files = get_changed_files(repo_path, old_hash, new_hash) if old_hash else []
    # Load knowledge graph
    knowledge_graph = load_knowledge_graph(knowledge_graph_path)
    # Re-run Surveyor and Semanticist only on changed files (mocked)
    for file in changed_files:
        Surveyor(repo_path).analyze_file(file)
        # Update knowledge_graph as needed (mocked)
    # Save updated knowledge graph
    save_knowledge_graph(knowledge_graph, knowledge_graph_path)
    # Update meta
    meta['git_head'] = new_hash
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2)
    return f'Updated {len(changed_files)} files.'
