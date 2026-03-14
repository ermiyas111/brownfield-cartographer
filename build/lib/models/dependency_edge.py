from pydantic import BaseModel

class DependencyEdge(BaseModel):
    source: str
    target: str
    type: str  # e.g., 'import', 'inheritance', etc.
