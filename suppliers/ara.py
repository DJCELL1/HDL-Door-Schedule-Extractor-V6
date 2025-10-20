from __future__ import annotations
import re
from typing import List
import pdfplumber
from engine import ItemRow
from utils.parsing import normalize_spaces

# ------------------------------------------------------------
# REGEX DEFINITIONS
# ------------------------------------------------------------
DOOR_RE = re.compile(
    r"\b(?:ED|IBF|ID|IDS|IDW|IFD|IS)\d{2,4}(?:[A-Z]|-[A-Z])?\b", re.IGNORECASE
)
AREA_RE = re.compile(r"\b(CLUBHOUSE|RECEPTION|VILLAGE|COMMUNITY CENTRE)\b", re.IGNORECASE)
CODE_LINE_RE = re.compile(r"^([A-Z0-9/.-]+)\s+(.+?)\s+(\d+)\s*$")

# ------------------------------------------------------------
# CORE PARSER
# ------------------------------------------------------------
def extract_items(pdf_bytes: bytes) -> List[ItemRow]:
    items: List[ItemRow] = []
    current_area = ""
    current_door = ""

    with pdfplumber.open(pdf_bytes) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            lines = [normalize_spaces(l) for l in text.splitlines() if l.strip()]

            for line in lines:
                # Detect Area (e.g., CLUBHOUSE, RECEPTION)
                if AREA_RE.search(line) and len(line.split()) == 1:
                    current_area = AREA_RE.search(line).group(1).title()
                    continue

                # Detect Door headings (e.g., ED01 CLUBHOUSE STAFF ENTRY)
                door_match = DOOR_RE.search(line)
                if door_match:
                    current_door = door_match.group(0).upper()
                    continue

                # Detect "Code Description Product" lines
                code_match = CODE_LINE_RE.match(line)
                if code_match and current_door:
                    code = code_match.group(1).strip()
                    desc = code_match.group(2).strip()
                    qty = code_match.group(3).strip()

                    # Remove "ARA", "LW", etc. from beginning of desc if redundant
                    desc = re.sub(r"^(ARA|LW|MN|CL|FT|TS)\s+", "", desc, flags=re.IGNORECASE)

                    items.append(
                        ItemRow(
                            area=current_area or "General",
                            door=current_door,
                            code=code,
                            description=desc,
                            colour=None,
                            quantity=int(qty) if qty.isdigit() else 1,
                            product=desc,
                        )
                    )

    return items
