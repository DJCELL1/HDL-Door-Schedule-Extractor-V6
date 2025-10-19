import pytesseract
from PIL import Image

def ocr_page_to_text(img: Image.Image) -> str:
    return pytesseract.image_to_string(img)
