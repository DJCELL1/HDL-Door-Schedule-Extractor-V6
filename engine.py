from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
import pdfplumber
import io
import re

from utils.parsing import normalize_spaces, looks_like_table, best_area_name
from utils.io_helpers import bytes_to_images
from utils.ocr import ocr_page_to_text
from suppliers.registry import get_supplier_parser


# ---------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------
@dataclass
class ItemRow:
    area: str
    door: str
    code: str
    quantity: int
    product: str
    description: Optional[str] = None
    colour: Optional[str] = None


# ---------------------------------------------------------------------
# Door number detection regex (generic fallback)
# ---------------------------------------------------------------------
DOOR_RE = re.compile(
    r"""
    \b(
        [A-Z]{1,4}        # letters (e.g. ED, IS, D)
        \d{2,4}           # digits (e.g. 01, 0202)
        [A-Z]?            # optional suffix letter
        (?:-\d{1,2})?     # optional dash-number
        [A-Z]?            # optional trailing letter
    )\b
    """,
    re.IGNORECASE | re.VERBOSE,
)


# ---------------------------------------------------------------------
# Core extraction logic
# ---------------------------------------------------------------------
def extract_text_from_pdf(data: bytes, force_ocr: bool = False) -> str:
    """
    Extract text from a PDF file.
    Falls back to OCR (Tesseract) if no text layer is found or force_ocr=True.
    """
    text_output = []

    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            if force_ocr or not text.strip():
                # Convert the page to an image for OCR fallback
                image = bytes_to_images(data, page_numbers=[page.page_number - 1])[0]
                text = ocr_page_to_text(image)
            text_output.append(text)

    return "\n".join(text_output)


# ---------------------------------------------------------------------
# Parse with supplier
# ---------------------------------------------------------------------
def parse_with_supplier(supplier_name: str, pdf_bytes: bytes) -> List[ItemRow]:
    """
    Use the correct supplier parser from the registry to extract structured data.
    """
    parser = get_supplier_parser(supplier_name)
    try:
        items = parser(pdf_bytes)
    except Exception as e:
        raise RuntimeError(f"❌ Failed to parse supplier '{supplier_name}': {e}")

    if not isinstance(items, list):
        raise ValueError(f"Parser for '{supplier_name}' did not return a list.")

    return items


# ---------------------------------------------------------------------
# Fallback parser (if supplier not identified)
# ---------------------------------------------------------------------
def parse_generic_pdf(pdf_bytes: bytes) -> List[ItemRow]:
    """
    A generic parser for PDFs with tabular layouts or plain text when supplier is unknown.
    """
    items: List[ItemRow] = []
    current_area = "General"
    current_door = None

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            lines = [normalize_spaces(l) for l in text.splitlines() if l.strip()]

            for line in lines:
                # Try to detect area names (if your utils.best_area_name handles this)
                area_candidate = best_area_name(line)
                if area_candidate:
                    current_area = area_candidate
                    continue

                # Detect door
                door_match = DOOR_RE.search(line)
                if door_match:
                    current_door = door_match.group(1).upper()
                    continue

                # Detect code and quantity pattern (simple fallback)
                match = re.match(r"^([A-Z0-9/.-]+)\s+(.+?)\s+(\d+)\s*$", line)
                if match and current_door:
                    code, desc, qty = match.groups()
                    items.append(
                        ItemRow(
                            area=current_area,
                            door=current_door,
                            code=code.strip(),
                            description=desc.strip(),
                            colour=None,
                            quantity=int(qty),
                            product=desc.strip(),
                        )
                    )
    return items


# ---------------------------------------------------------------------
# Entry point utility
# ---------------------------------------------------------------------
def extract_items_from_pdf(pdf_bytes: bytes, supplier: Optional[str] = None, force_ocr: bool = False) -> List[ItemRow]:
    """
    Top-level function that selects the correct parser or uses a generic fallback.
    """
    if supplier:
        return parse_with_supplier(supplier, pdf_bytes)
    else:
        # fallback if supplier not specified or unknown
        return parse_generic_pdf(pdf_bytes)
