from __future__ import annotations
from typing import List
from models import ItemRow, DOOR_RE
import re

ARA_DOOR_RE = re.compile(
    r"""(?xi)
    \b
    (?:ED|IBF|ID|IDS|IDW|IFD|IS)   # ARA door families
    \d{2,6}                        # numbers: ED01, ED0202, ID11, etc.
    (?:-[A-Z]|[A-Z])?              # optional -E / -B or trailing A/B
    \b
    """
)


class ARAParser:
    name = "ara"

    def parse(self, pages: List[str]) -> List[ItemRow]:
        rows: List[ItemRow] = []
        current_area = None
        for page in pages:
            for raw in page.split("\n"):
                line = raw.strip()
                if not line:
                    continue
                if re.search(r"\b(CLUBHOUSE|LEVEL|GROUND|FLOOR|AREA|STAGE)\b", line, re.I):
                    current_area = line.title()
                m = ARA_DOOR_RE.search(line) or DOOR_RE.search(line)
                if not m:
                    continue
                door = m.group(1)
                # ARA format sample: Area  Door  Code  Description  Colour  Qty
                # Strategy: split by 2+ spaces; assume last token is qty if int
                parts = re.split(r"\s{2,}", line)
                qty = 1
                if parts and re.fullmatch(r"\d+", parts[-1]):
                    qty = int(parts[-1])
                    parts = parts[:-1]
                code = ""
                description = ""
                colour = ""
                # Attempt mapping by positions if we have >=4 parts
                if len(parts) >= 4:
                    # [maybe Area], Door/Code may be merged; be defensive
                    # Find the first token that looks like a code: letters+digits
                    for p in parts:
                        if re.search(r"[A-Z]{2,}\d", p, re.I):
                            code = p.strip()
                            break
                    # Description and Colour from remaining tail
                    tail = " ".join(x for x in parts if x != code).strip()
                    # Try to split colour from description if colour is a short all-caps token
                    mcol = re.search(r"\b([A-Z]{2,6})\b\s*$", tail)
                    if mcol:
                        colour = mcol.group(1)
                        description = tail[:mcol.start()].strip()
                    else:
                        description = tail
                else:
                    # fallback
                    tail = line[m.end():].strip()
                    code_m = re.search(r"([A-Z0-9/\-]{3,})", tail)
                    if code_m:
                        code = code_m.group(1)
                    description = tail
                product = description if description else tail if 'tail' in locals() else ""
                rows.append(ItemRow(area=current_area or "Unspecified", door=door, code=code, quantity=qty, product=product, description=description, colour=colour))
        return rows
