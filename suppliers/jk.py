from __future__ import annotations
from typing import List
from engine import ItemRow, DOOR_RE
import re

class JKParser:
    name = "jk"

    def parse(self, pages: List[str]) -> List[ItemRow]:
        rows = []
        current_area = None
        for page in pages:
            for line in page.split("\n"):
                line = line.strip()
                if not line:
                    continue
                if re.search(r"\b(Ground|First|Second|Level|Floor)\b", line, re.I):
                    current_area = line.title()
                m = DOOR_RE.search(line)
                if not m:
                    continue
                door = m.group(1)
                qty = 1
                qms = re.findall(r"(\d+)\s*$", line)
                if qms: qty = int(qms[-1])
                tail = line[m.end():].strip(" -:")
                code = ""
                cm = re.search(r"([A-Z0-9]{3,}(?:/[A-Z0-9]+)?)", tail)
                if cm: code = cm.group(1)
                product = tail
                rows.append(ItemRow(area=current_area or "Unspecified", door=door, code=code, quantity=qty, product=product))
        return rows
