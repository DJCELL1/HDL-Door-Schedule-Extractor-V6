from __future__ import annotations

from typing import List, Optional
import pdfplumber
import io
import re

from models import ItemRow, DOOR_RE
from utils.parsing import normalize_spaces, looks_like_table, best_area_name
from utils.io_helpers import bytes_to_images
from utils.ocr import ocr_page_to_text
from suppliers import registry


def extract_text_from_pdf(data: bytes, force_ocr: bool = False) -> List[str]:
    """
    Extracts text from each page of a PDF.
    Falls back to OCR for pages with little or no text.
    """
    pages_text: List[str] = []

    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            text = normalize_spaces(text)
            use_ocr = force_ocr or len(text) < 30  # low-text pages trigger OCR

            if use_ocr:
                images = bytes_to_images(
                    data, first_page=page.page_number, last_page=page.page_number
                )
                if images:
                    ocr_text = ocr_page_to_text(images[0])
                    text = normalize_spaces(ocr_text)

            pages_text.append(text)

    return pages_text


def parse_with_supplier(text_pages: List[str], supplier_hint: Optional[str] = None) -> List[ItemRow]:
    """
    Detects or uses a supplier parser and extracts ItemRow objects.
    """
    parser = registry.get_parser(supplier_hint, text_pages)
    rows = parser.parse(text_pages)
    return rows


def detect_area(current_area: Optional[str], line: str) -> Optional[str]:
    """
    Heuristically detects when a line represents an 'Area' heading
    rather than an item line, and updates the current area.
    """
    if looks_like_table(line):
        return current_area

    if re.search(
        r"\b(Level|Ground|First|Second|Third|Basement|Mezzanine|Clubhouse|Club House|Floor|Wing|Block|Area)\b",
        line,
        re.I,
    ):
        return best_area_name(line)

    return current_area
