from typing import List
from pdf2image import convert_from_bytes

def bytes_to_images(data: bytes, first_page: int = 1, last_page: int = None) -> List["PIL.Image.Image"]:
    return convert_from_bytes(data, first_page=first_page, last_page=last_page or first_page, dpi=300)
