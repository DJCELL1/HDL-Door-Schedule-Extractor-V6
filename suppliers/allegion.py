from __future__ import annotations
from typing import List
from models import ItemRow, DOOR_RE
import re

class AllegionParser:
    name = "allegion"

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
                # Allegion lines often "CODE  Qty  Product ..."
                # Try to capture "CODE" followed by qty near end
                code = ""
                qty = 1
                # code pattern like "L9D11S" or "6649RH/30SSS"
                cm = re.search(r"([A-Z0-9]{3,}(?:/[A-Z0-9]+)?)", line[m.end():])
                if cm:
                    code = cm.group(1)
                qms = re.findall(r"(\d+)\s*$", line)
                if qms:
                    qty = int(qms[-1])
                product = re.sub(rf".*?{re.escape(code)}", "", line).strip(" -:")
                rows.append(ItemRow(area=current_area or "Unspecified", door=door, code=code, quantity=qty, product=product))
        return rows
