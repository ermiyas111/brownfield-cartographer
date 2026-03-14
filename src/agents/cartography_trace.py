import os
import json
import uuid
from datetime import datetime

def log_event(event_type, details, log_path):
    event = {
        'uuid': str(uuid.uuid4()),
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'event_type': event_type,
        'details': details
    }
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(event) + '\n')
    return event['uuid']

def save_knowledge_graph(knowledge_graph, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(knowledge_graph, f, indent=2)

def load_knowledge_graph(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
