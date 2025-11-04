# preprocess.py
import re, json, io, requests
import pdfplumber
from pathlib import Path

PDF_URLS = [
    "https://github.com/mishraSakhi/support-tickets-pdf/raw/main/.github/workflows/pdfs/TS015475137_analysis_20250924_135140.pdf",
    "https://github.com/mishraSakhi/support-tickets-pdf/raw/main/.github/workflows/pdfs/TS011853282_analysis_20250923_130509.pdf",
    "https://github.com/mishraSakhi/support-tickets-pdf/raw/main/.github/workflows/pdfs/TS016804688_analysis_20250923_135233.pdf",
    "https://github.com/mishraSakhi/support-tickets-pdf/raw/main/.github/workflows/pdfs/TS020010126_analysis_20250923_141206.pdf",
    "https://github.com/mishraSakhi/support-tickets-pdf/raw/main/.github/workflows/pdfs/TS020228920_analysis_20250923_140851.pdf"
]

CASE_ID_RE = re.compile(r"\b(?:TS|SCTS)\d{5,10}\b", re.IGNORECASE)
TITLE_RE = re.compile(r"(?:Case Title|Case title|Title):\s*(.+)", re.IGNORECASE)
REPORTED_BY_RE = re.compile(r"(?:Reported by|Reporter|Reported):\s*(.+)", re.IGNORECASE)
# Generic name capture (e.g., in case feed lines)
NAME_RE = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b")

def extract_text_from_pdf_bytes(b):
    pages = []
    with pdfplumber.open(io.BytesIO(b)) as pdf:
        for p in pdf.pages:
            t = p.extract_text()
            if t:
                pages.append(t)
    return "\n".join(pages)

records = []
for url in PDF_URLS:
    print("Fetching:", url)
    r = requests.get(url, timeout=30)
    txt = extract_text_from_pdf_bytes(r.content)
    case_ids = list({m.group(0).upper() for m in CASE_ID_RE.finditer(txt)})
    title = None
    m = TITLE_RE.search(txt)
    if m:
        title = m.group(1).splitlines()[0].strip()
    reporters = set()
    for m in REPORTED_BY_RE.finditer(txt):
        reporters.add(m.group(1).strip())
    # fallback: look for likely names in the "Case Feed" area
    if not reporters:
        for m in re.finditer(r"\n([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b", txt):
            name = m.group(1).strip()
            # simple heuristic: name length > 4
            if len(name) > 4:
                reporters.add(name)
    records.append({
        "case_ids": case_ids or ["Unknown"],
        "title": title or "Unknown",
        "reporters": list(reporters),
        "all_text": txt,
        "source": url
    })

Path("data").mkdir(exist_ok=True)
with open("data/records.json", "w", encoding="utf8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

print("Saved data/records.json with", len(records), "records")
