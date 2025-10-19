from __future__ import annotations
from typing import List, Optional, Type
from suppliers.base import SupplierBase
from suppliers.allegion import AllegionParser
from suppliers.dormakaba import DormakabaParser
from suppliers.ara import ARAParser
from suppliers.jk import JKParser

PARSERS = [ARAParser, AllegionParser, DormakabaParser, JKParser]

def get_parser(hint: Optional[str], pages: List[str]) -> SupplierBase:
    if hint:
        for P in PARSERS:
            if getattr(P, "name", "").lower() == hint.lower():
                return P()
    # naive auto-detect: keyword sniffing
    joined = "\n".join(pages).lower()
    if "allegion" in joined:
        return AllegionParser()
    if "dormakaba" in joined or "dorma kaba" in joined or "dk" in joined:
        return DormakabaParser()
    if "ara" in joined:
        return ARAParser()
    if "jk" in joined:
        return JKParser()
    return SupplierBase()
