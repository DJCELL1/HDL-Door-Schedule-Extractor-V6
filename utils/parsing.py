import re

def normalize_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()

def looks_like_table(line: str) -> bool:
    # crude heuristic: many spaces or tab separators
    return bool(re.search(r"\s{2,}|\t", line))

def best_area_name(line: str) -> str:
    # Clean to a "title" style name
    line = re.sub(r"[^A-Za-z0-9 \-]", "", line).strip()
    return line.title()
