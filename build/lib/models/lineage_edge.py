from pydantic import BaseModel
from typing import Optional

class LineageEdge(BaseModel):
    transformation_logic_file: Optional[str] = None
