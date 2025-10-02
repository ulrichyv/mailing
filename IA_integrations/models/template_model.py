from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class TemplateData:
    name: str
    html: str
    text: str
    preview: str
    model: str
    variables: List[str]
    debug_info: Optional[List[str]] = None

@dataclass 
class VariableCategory:
    name: str
    variables: List[str]
    description: str
    icon: str