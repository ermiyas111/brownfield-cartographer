from pydantic import BaseModel, Field
from typing import List, Optional

class ModuleNode(BaseModel):
    name: str
    path: str
    imports: List[str]
    classes: List[str]
    functions: List[str]
    git_velocity: Optional[float] = None
    pagerank: Optional[float] = None
