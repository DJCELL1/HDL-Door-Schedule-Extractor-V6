from __future__ import annotations
import re
from typing import List, Optional
from dataclasses import dataclass
import pdfplumber
from utils.parsing import normalize_spaces, looks_like_table
from engine import ItemRow

# ---------------------------------------------------------------------
# REGEX DEFINITIONS
# ---------------------------------------------------------------------
ARA_DOOR_RE = re.compile(
    r"""(?xi)
    \b
    (?:ED|IBF|ID|IDS|IDW|IFD|IS)   # Door families
    \d{2,6}                        # Digits e.g. ED01, ID0202
    (?:-[A-Z]|[A-Z])?              # Optional suffix like -E, -B, A
    \b
    """
)

UPPER_HEADING_RE = re.compile(r"^[A-Z0-9&/ ,.\-]{6,}$")

ARA_HEADER_ALIASES = {
    "code": {"code", "item code", "product code", "sku"},
    "description": {"description", "desc", "product", "item description"},
    "colour": {"colour", "color", "finish"},
    "quantity": {"qty", "quantity", "q’ty", "qnty"}
}

# ---------------------------------------------------------------------
# HEADER NORMALISER
# ---------------------------------------------------------------------
def _canon(col_name: str) -> Optional[str]:
    n = normalize_spaces(col_name).lower()
    for canon, opts in ARA_HEADER_ALIASES.items():
        if n in opts:
            return canon
    return None

# ---------------------------------------------------------------------
# AREA DETECTION
# ---------------------------------------------------------------------
def detect_ara_area(lines: list[str]) -> list[tuple[int, str]]:
    anchors = []
    for i, raw in enumerate(lines):
        txt = normalize_spaces(raw)
        if not txt:
            continue
        # Skip header-like lines
        if any(k in txt.lower() for k in ("code", "qty", "quantity", "description", "colour", "finish")):
            continue
        if UPPER_HEADING_RE.match(txt) and sum(ch.islower() for ch in txt) == 0:
            anchors.append((i, txt.title()))
    return anchors


def area_for_row(row_idx: int, anchors: list[tuple[int, str]]) -> str:
    last = ""
    for i, name in anchors:
        if i <= row_idx:
            last = name
        else:
            break
    return last or "General"

# ---------------------------------------------------------------------
# FIELD CLEANERS
# ---------------------------------------------------------------------
def looks_like_code(token: str) -> bool:
    t = token.strip()
    if len(t) < 2:
        return False
    if " " in t:
        return False
    if ARA_DOOR_RE.fullmatch(t):
        return False
    return any(c.isdigit() for c in t) or any(ch in t for ch in "-/._")


def maybe_swap_code_and_desc(code_val: str, desc_val: str) -> tuple[str, str]:
    code_is_code = looks_like_code(code_val or "")
    desc_is_code = looks_like_code(desc_val or "")
    if not code_is_code and desc_is_code:
        return desc_val, code_val
    return code_val, desc_val

# ---------------------------------------------------------------------
# MAIN PARSER
# ---------------------------------------------------------------------
def parse_ara_page(page) -> List[ItemRow]:
    raw = page.extract_text(x_tolerance=1, y_tolerance=1) or ""
    lines = [ln for ln in (raw.split("\n") if raw else [])]
    anchors = detect_ara_area(lines)
    rows: List[ItemRow] = []

    tables = page.extract_tables({
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
        "intersection_tolerance": 5
    }) or []

    def to_item(area, door, code, qty, product, desc=None, colour=None):
        return ItemRow(
            area=normalize_spaces(area or ""),
            door=normalize_spaces(door or ""),
            code=normalize_spaces(code or ""),
            quantity=int(qty) if str(qty).strip().isdigit() else 1,
            product=normalize_spaces(product or ""),
            description=normalize_spaces(desc or None) or None,
            colour=normalize_spaces(colour or None) or None,
        )

    # -------------------- TABLE PARSER --------------------
    def extract_door_in_row(tokens: list[str]) -> str:
        for t in tokens:
            if ARA_DOOR_RE.fullmatch(t.strip()):
                return t.strip()
        return ""

    def parse_tabular(tbl):
        if not tbl or not any(tbl):
            return
        headers = [normalize_spaces(c or "") for c in tbl[0]]
        map_idx = {}
        for idx, name in enumerate(headers):
            c = _canon(name)
            if c:
                map_idx[c] = idx

        if not map_idx:
            return

        for r_idx, row in enumerate(tbl[1:], start=1):
            tokens = [(row[i] if i < len(row) else "") for i in range(len(headers))]
            door = extract_door_in_row(tokens)
            if not door:
                continue

            area = area_for_row(r_idx, anchors)
            code_val = tokens[map_idx["code"]] if "code" in map_idx else ""
            desc_val = tokens[map_idx["description"]] if "description" in map_idx else ""
            colour_val = tokens[map_idx["colour"]] if "colour" in map_idx else ""
            qty_val = tokens[map_idx["quantity"]] if "quantity" in map_idx else "1"

            code_val, desc_val = maybe_swap_code_and_desc(code_val, desc_val)
            product_val = desc_val

            rows.append(to_item(area, door, code_val, qty_val, product_val, desc=desc_val, colour=colour_val))

    for tbl in tables:
        parse_tabular(tbl)

    # -------------------- FALLBACK PARSER --------------------
    if not rows:
        for i, ln in enumerate(lines):
            low = ln.lower()
            if any(h in low for h in ("code", "qty", "quantity", "description", "colour", "finish")):
                continue

            parts = [p for p in re.split(r"\s{2,}", ln.strip()) if p]
            if len(parts) < 2:
                parts = ln.split()

            door = ""
            for t in parts:
                if ARA_DOOR_RE.fullmatch(t.strip()):
                    door = t.strip()
                    break
            if not door:
                continue

            area = area_for_row(i, anchors)
            try:
                door_idx = parts.index(door)
            except ValueError:
                door_idx = 0

            tail = parts[door_idx+1:] if door_idx+1 < len(parts) else []
            code_val = ""
            qty_val = "1"
            colour_val = ""
            desc_tokens = []

            for t in tail:
                t = t.strip()
                if not code_val and looks_like_code(t):
                    code_val = t
                elif t.isdigit():
                    qty_val = t
                elif t.upper() in {"SC", "SS", "SSS", "BLK", "BK", "PBK", "PB", "PC"} or (len(t) <= 6 and not any(ch.isdigit() for ch in t)):
                    colour_val = (colour_val + " " + t).strip() if colour_val else t
                else:
                    desc_tokens.append(t)

            desc_val = " ".join(desc_tokens).strip()
            code_val, desc_val = maybe_swap_code_and_desc(code_val, desc_val)
            product_val = desc_val

            rows.append(to_item(area, door, code_val, qty_val, product_val, desc=desc_val, colour=colour_val))

    return rows

# ---------------------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------------------
def extract_items(pdf_bytes: bytes) -> List[ItemRow]:
    results: List[ItemRow] = []
    with pdfplumber.open(pdf_bytes) as pdf:
        for page in pdf.pages:
            if not looks_like_table(page):
                continue
            results.extend(parse_ara_page(page))
    return results
