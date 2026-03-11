from pydantic import BaseModel
from typing import Optional

class LineageNode(BaseModel):
    type: str  # e.g., 'table', 'file', 'task', 'unresolved'
    table_name: Optional[str] = None
    schema: Optional[str] = None
