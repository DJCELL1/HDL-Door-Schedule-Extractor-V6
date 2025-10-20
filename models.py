from dataclasses import dataclass
from typing import Optional
import re

@dataclass
class ItemRow:
    area: str
    door: str
    code: str
    quantity: int
    product: str
    description: Optional[str] = None
    colour: Optional[str] = None

DOOR_RE = re.compile(r"""(?xi)
    \b(
        [A-Z]{1,4}      # letters
        (?:\d{2,4})     # digits
        (?:[A-Z])?      # optional letter suffix
        (?:-\d{1,2})?   # optional -number
        (?:[A-Z])?      # optional extra suffix
    )\b
""")

