"""
Registry of all supplier parsers used by the HDL Door Schedule Extractor.
Each supplier parser must expose a .extract_items(pdf_bytes: bytes) -> List[ItemRow] function.
"""

from suppliers.allegion import AllegionParser
from suppliers.dormakaba import DormakabaParser
from suppliers.ARA import ARAParser
from suppliers.jk import JKParser

# Optional base class if your parsers inherit from SupplierBase
# (you can safely remove this import if not used)
from suppliers.base import SupplierBase


# ---------------------------------------------------------------------
# Supplier registry dictionary
# ---------------------------------------------------------------------
registry = {
    "Allegion": AllegionParser.extract_items,
    "Dormakaba": DormakabaParser.extract_items,
    "ARA": ARAParser.extract_items,
    "JK": JKParser.extract_items,
}


# ---------------------------------------------------------------------
# Helper function to get the correct parser dynamically
# ---------------------------------------------------------------------
def get_supplier_parser(name: str):
    """
    Retrieve the extract_items function for a given supplier name.
    Example:
        parser = get_supplier_parser("ARA")
        items = parser(pdf_bytes)
    """
    key = name.strip().title()
    if key not in registry:
        raise ValueError(f"❌ Unknown supplier: {name}. Available: {', '.join(registry.keys())}")
    return registry[key]


# ---------------------------------------------------------------------
# Optional: function to list all available suppliers
# ---------------------------------------------------------------------
def list_suppliers() -> list[str]:
    """Return a list of registered supplier names."""
    return list(registry.keys())
