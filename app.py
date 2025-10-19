import io
import time
from pathlib import Path
import streamlit as st
from engine import extract_text_from_pdf, parse_with_supplier
from exporters import export_excel, export_csv, export_jsonl, export_cin7_html_templates

st.set_page_config(page_title="HDL Door Schedule Extractor V6", page_icon="🚪", layout="wide")
st.title("HDL Door Schedule Extractor — V6")

with st.sidebar:
    st.header("Options")
    supplier = st.selectbox("Supplier profile", ["auto","allegion","dormakaba","ara","jk"])
    force_ocr = st.toggle("Force OCR (slower)", value=False)
    extended = st.toggle("Extended columns (Description/Colour)", value=True)
    st.caption("Tip: Extended columns help ARA-style schedules.")

uploaded = st.file_uploader("Drop one or more PDF schedules", type=["pdf"], accept_multiple_files=True)
if not uploaded:
    st.info("Upload PDFs to begin.")
    st.stop()

all_rows = []
extract_log = []

start = time.time()
for f in uploaded:
    data = f.read()
    text_pages = extract_text_from_pdf(data, force_ocr=force_ocr)
    rows = parse_with_supplier(text_pages, None if supplier == "auto" else supplier)
    all_rows.extend(rows)
    extract_log.append((f.name, len(text_pages), len(rows)))

elapsed = time.time() - start
st.success(f"Parsed {len(uploaded)} files in {elapsed:.2f}s — {sum(r for _,_,r in extract_log)} rows.")

# PREVIEW
from exporters import rows_to_dataframe
preview = rows_to_dataframe(all_rows, extended=extended)
st.dataframe(preview, use_container_width=True)

# DOWNLOADS
col1, col2, col3, col4 = st.columns(4)
with col1:
    xlsx = export_excel(all_rows, extended=extended)
    st.download_button("⬇️ Excel (.xlsx)", data=xlsx, file_name="door_schedule_v6.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
with col2:
    csv = export_csv(all_rows, extended=extended)
    st.download_button("⬇️ CSV (.csv)", data=csv, file_name="door_schedule_v6.csv", mime="text/csv")
with col3:
    jsonl = export_jsonl(all_rows)
    st.download_button("⬇️ JSONL (.jsonl)", data=jsonl, file_name="door_schedule_v6.jsonl", mime="application/jsonl")
with col4:
    htmls = export_cin7_html_templates(all_rows)
    zipped = io.BytesIO()
    import zipfile
    with zipfile.ZipFile(zipped, "w", zipfile.ZIP_DEFLATED) as z:
        for i, h in enumerate(htmls, start=1):
            z.writestr(f"product_{i:03d}.html", h)
    st.download_button("⬇️ CIN7 HTML (zip)", data=zipped.getvalue(), file_name="cin7_templates.zip", mime="application/zip")

with st.expander("Extraction details"):
    for name, pages, rows in extract_log:
        st.write(f"**{name}** — {pages} pages → {rows} rows")

st.caption("V6 — pdfplumber primary, per‑page OCR fallback. Extend supplier rules in `suppliers/`.")
