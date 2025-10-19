from __future__ import annotations
from typing import List
from engine import ItemRow, DOOR_RE
import re

class SupplierBase:
    name = "base"

    def parse(self, pages: List[str]) -> List[ItemRow]:
        # default generic parser: find rows with door code + qty + product/code tokens
        rows: List[ItemRow] = []
        current_area = None
        for page in pages:
            for line in page.split("\n"):
                line = line.strip()
                if not line:
                    continue
                # area detection (weak)
                if re.search(r"\b(Ground|First|Second|Third|Basement|Level|Clubhouse|Floor)\b", line, re.I):
                    current_area = line.title()
                # door
                m = DOOR_RE.search(line)
                if not m:
                    continue
                door = m.group(1)
                # quantity (last integer on line if present)
                q = 1
                qm = re.findall(r"(\d+)", line)
                if qm:
                    try:
                        q = int(qm[-1])
                    except:
                        q = 1
                # product code token heuristic: first ALLCAPS+digits chunk after door
                tail = line[m.end():].strip(" -:")
                code = ""
                cm = re.search(r"([A-Z0-9]{3,}[A-Z0-9/\-]*)", tail)
                if cm:
                    code = cm.group(1)
                product = tail
                rows.append(ItemRow(area=current_area or "Unspecified", door=door, code=code, quantity=q, product=product))
        return rows
