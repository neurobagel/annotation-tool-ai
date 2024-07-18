from typing import Dict, Optional
from pydantic import BaseModel
from app.products.annotations import Annotations


class TSVAnnotations(BaseModel):  # type: ignore
    Description: str
    Levels: Optional[Dict[str, str]] = None
    Annotations: Annotations
