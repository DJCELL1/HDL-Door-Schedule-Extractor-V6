from __future__ import annotations
import pandas as pd
from typing import List
from engine import ItemRow
from utils.excel import df_to_excel_bytes

COLUMNS_DEFAULT = ["Area","Door","Code","Quantity","Product"]
COLUMNS_EXTENDED = ["Area","Door","Code","Description","Colour","Quantity","Product"]

def rows_to_dataframe(rows: List[ItemRow], extended: bool=False) -> pd.DataFrame:
    if extended:
        data = [ [r.area, r.door, r.code, r.description or "", r.colour or "", r.quantity, r.product] for r in rows ]
        cols = COLUMNS_EXTENDED
    else:
        data = [ [r.area, r.door, r.code, r.quantity, r.product] for r in rows ]
        cols = COLUMNS_DEFAULT
    df = pd.DataFrame(data, columns=cols)
    return df

def export_excel(rows: List[ItemRow], extended: bool=False, sheet_name: str="Doors with Hardware") -> bytes:
    df = rows_to_dataframe(rows, extended=extended)
    return df_to_excel_bytes(df, sheet_name=sheet_name)

def export_csv(rows: List[ItemRow], extended: bool=False) -> str:
    df = rows_to_dataframe(rows, extended=extended)
    return df.to_csv(index=False)

def export_jsonl(rows: List[ItemRow]) -> str:
    import json
    return "\n".join([ json.dumps(r.__dict__, ensure_ascii=False) for r in rows ])

# Stub for CIN7 HTML product templates (per-product separated). Extend as needed.
def export_cin7_html_templates(rows: List[ItemRow]) -> List[str]:
    templates = []
    for r in rows:
        html = f"""<div class='product-template'>
  <h3>{r.code} — {r.product}</h3>
  <ul>
    <li>Area: {r.area}</li>
    <li>Door: {r.door}</li>
    <li>Qty: {r.quantity}</li>
  </ul>
</div>"""
        templates.append(html)
    return templates
