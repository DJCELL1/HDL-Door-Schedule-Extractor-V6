from __future__ import annotations
from typing import List
from engine import ItemRow, DOOR_RE
import re

class DormakabaParser:
    name = "dormakaba"

    def parse(self, pages: List[str]) -> List[ItemRow]:
        rows: List[ItemRow] = []
        current_area = None
        for page in pages:
            for line in page.split("\n"):
                line = line.strip()
                if not line:
                    continue
                if re.search(r"\b(Ground|Level|Floor|Basement)\b", line, re.I):
                    current_area = line.title()
                m = DOOR_RE.search(line)
                if not m:
                    continue
                door = m.group(1)
                # DK codes like "MS2604PT", "OC SSS", "TS93 G N AB EN1-5 SIL"
                # Heuristic: quantity is the last integer; code is the first token group after door
                qty = 1
                qms = re.findall(r"(\d+)\s*$", line)
                if qms:
                    qty = int(qms[-1])
                tail = line[m.end():].strip(" -:")
                code = tail.split()[0] if tail else ""
                product = tail
                rows.append(ItemRow(area=current_area or "Unspecified", door=door, code=code, quantity=qty, product=product))
        return rows
