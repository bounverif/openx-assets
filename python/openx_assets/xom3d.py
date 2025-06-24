from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple


@dataclass
class Context:
    asset_schema: Optional[Dict] = None
    asset: Optional[Dict] = None
    material_schema: Optional[Dict] = None
    materials: Optional[Dict] = None
