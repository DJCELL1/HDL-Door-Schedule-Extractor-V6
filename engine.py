from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Optional, Iterable, Tuple
import pdfplumber
import re
import io
from utils.parsing import normalize_spaces, looks_like_table, best_area_name
from utils.io_helpers import bytes_to_images
from utils.ocr import ocr_page_to_text
from suppliers import registry

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
        [A-Z]{1,4}    # letters
        (?:\d{2,4})  # digits
        (?:[A-Z])?    # optional letter suffix
        (?:-\d{1,2})? # optional -number (e.g., IS10-B or IFD01-E already covered by letter; keep optional)
        (?:[A-Z])?    # optional extra suffix
    )\b
""")

def extract_text_from_pdf(data: bytes, force_ocr: bool = False) -> List[str]:
    pages_text: List[str] = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            txt = page.extract_text() or ""
            txt = normalize_spaces(txt)
            use_ocr = force_ocr or len(txt) < 30  # very low-confidence page: OCR
            if use_ocr:
                img = bytes_to_images(data, first_page=page.page_number, last_page=page.page_number)[0]
                txt = ocr_page_to_text(img)
                txt = normalize_spaces(txt)
            pages_text.append(txt)
    return pages_text

def parse_with_supplier(text_pages: List[str], supplier_hint: Optional[str] = None) -> List[ItemRow]:
    parser = registry.get_parser(supplier_hint, text_pages)
    rows = parser.parse(text_pages)
    return rows

def detect_area(current_area: Optional[str], line: str) -> Optional[str]:
    # heuristic: lines that look like headings (Title Case / ALL CAPS) and not items
    if looks_like_table(line):
        return current_area
    # capture area-like phrases
    if re.search(r"\b(Level|Ground|First|Second|Third|Basement|Mezzanine|Clubhouse|Club House|Floor|Wing|Block|Area)\b", line, re.I):
        return best_area_name(line)
    return current_area
