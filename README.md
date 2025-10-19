# HDL Door Schedule Extractor — V6

Streamlit app + parsing engine for extracting *Area, Door, Code, Qty, Product (and optional Description/Colour)* from multi‑supplier PDFs into a clean Excel file. Includes OCR fallback, supplier heuristics, and a devcontainer for Codespaces.

## Quick start (local)
```bash
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Cloud
- Push this folder to GitHub
- On Streamlit Cloud: **New app** → Select repo → Main file: `app.py`
- (Optional) Add environment variables or Tesseract path in **Secrets**

## Features
- Supplier profiles: Allegion, Dormakaba, ARA, JK, (generic)
- Fast text extraction via `pdfplumber`
- OCR fallback (per‑page) via `pytesseract` + `pdf2image`
- Door number detection with flexible regex (e.g., `ED0202`, `ID11A`, `IS03-B` etc.)
- Output to Excel with frozen header row, widths, and minimal styling
- CSV and JSONL exports
- Pluggable rule system — add more suppliers in `suppliers/`
- Large message size support for Streamlit (`.streamlit/config.toml`)

## Folder layout
```
app.py
engine.py
exporters.py
suppliers/
  __init__.py
  base.py
  allegion.py
  dormakaba.py
  ara.py
  jk.py
utils/
  ocr.py
  io_helpers.py
  parsing.py
  excel.py
requirements.txt
.devcontainer/devcontainer.json
.streamlit/config.toml
Procfile
sample_data/
tests/
```

## Notes
- If pdf text is clean, OCR is skipped. If a page has low text extraction, OCR is attempted for that page only.
- You can force OCR with the sidebar toggle.
- Excel sheet is named **Doors with Hardware** to match legacy outputs.
- *CIN7 product HTML templates* are **not** produced by default in V6, but there is a stub exporter you can extend in `exporters.py`.
