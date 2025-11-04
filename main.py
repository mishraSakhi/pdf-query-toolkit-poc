import io
import re
import os
import requests
import pdfplumber
from fuzzywuzzy import fuzz
from fastapi import FastAPI, Query
from pyngrok import ngrok


PORT = 8000
PDF_URLS = [
    "https://github.com/mishraSakhi/support-tickets-pdf/raw/main/.github/workflows/pdfs/TS015475137_analysis_20250924_135140.pdf",
    "https://github.com/mishraSakhi/support-tickets-pdf/raw/main/.github/workflows/pdfs/TS011853282_analysis_20250923_130509.pdf",
    "https://github.com/mishraSakhi/support-tickets-pdf/raw/main/.github/workflows/pdfs/TS016804688_analysis_20250923_135233.pdf",
    "https://github.com/mishraSakhi/support-tickets-pdf/raw/main/.github/workflows/pdfs/TS020010126_analysis_20250923_141206.pdf",
    "https://github.com/mishraSakhi/support-tickets-pdf/raw/main/.github/workflows/pdfs/TS020228920_analysis_20250923_140851.pdf"
]

app = FastAPI(title="PDF Query API", description="Search PDFs with regex, fuzzy, and boolean logic.", version="1.2.0")

pdf_texts = []


@app.on_event("startup")
def load_pdfs():
    global pdf_texts
    print("🔄 Loading PDFs from GitHub...")
    for url in PDF_URLS:
        try:
            response = requests.get(url)
            with pdfplumber.open(io.BytesIO(response.content)) as pdf:
                text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
                pdf_texts.append({"url": url, "text": text})
            print(f"✅ Loaded: {url}")
        except Exception as e:
            print(f"⚠️ Failed to load {url}: {e}")
    print("✅ All PDFs loaded successfully!")


@app.get("/")
def home():
    return {
        "message": "PDF Query API is running!",
        "endpoints": {
            "/query?q=authentication error": "Search PDFs for text, regex, or boolean query.",
            "/health": "Check if PDFs are loaded and service is live."
        }
    }


@app.get("/health")
def health():
    return {"status": "ok", "pdfs_loaded": len(pdf_texts)}


@app.get("/query")
def query_pdf(
    q: str = Query(..., description="Keyword, regex, or boolean query (AND, OR, NOT)"),
    use_regex: bool = Query(False, description="Interpret query as regex"),
    case_sensitive: bool = Query(False, description="Case-sensitive search")
):
    results = []
    q_clean = q.strip()
    query_lower = q_clean if case_sensitive else q_clean.lower()

    def interpret_query(q):
        if re.search(r"\bNOT\b", q, re.IGNORECASE):
            term = re.split(r"\bNOT\b", q, flags=re.IGNORECASE)[1].strip()
            return {"type": "NOT", "term": term}
        elif re.search(r"\bAND\b", q, re.IGNORECASE):
            parts = [p.strip() for p in re.split(r"\bAND\b", q, flags=re.IGNORECASE)]
            return {"type": "AND", "terms": parts}
        elif re.search(r"\bOR\b", q, re.IGNORECASE):
            parts = [p.strip() for p in re.split(r"\bOR\b", q, flags=re.IGNORECASE)]
            return {"type": "OR", "terms": parts}
        else:
            return {"type": "SIMPLE", "term": q}

    query_logic = interpret_query(q_clean)

    for pdf in pdf_texts:
        text = pdf["text"]
        text_to_search = text if case_sensitive else text.lower()
        lines = text_to_search.splitlines()
        matched = False
        confidence = 0.0

        try:
            if use_regex:
                try:
                    pattern = re.compile(query_lower, 0 if case_sensitive else re.IGNORECASE)
                    if pattern.search(text_to_search):
                        matched = True
                        confidence = 1.0
                except re.error as e:
                    return {"error": f"Invalid regular expression syntax: {e}"}

            elif query_logic["type"] == "NOT":
                term = query_logic["term"]
                term_check = term if case_sensitive else term.lower()
                if term_check not in text_to_search:
                    matched = True
                    confidence = 1.0

            elif query_logic["type"] == "AND":
                terms = query_logic["terms"]
                term_check = [t if case_sensitive else t.lower() for t in terms]
                if all(t in text_to_search for t in term_check):
                    matched = True
                    confidence = 1.0

            elif query_logic["type"] == "OR":
                terms = query_logic["terms"]
                term_check = [t if case_sensitive else t.lower() for t in terms]
                if any(t in text_to_search for t in term_check):
                    matched = True
                    confidence = 1.0

            else:
                for line in lines:
                    line_to_compare = line if case_sensitive else line.lower()
                    score = fuzz.partial_ratio(query_lower, line_to_compare)
                    if score > 70:
                        matched = True
                        confidence = score / 100.0
                        break

            if matched:
                snippet = "\n".join(lines[:10])[:1000]
                results.append({
                    "snippet": snippet,
                    "page_number": 1,
                    "confidence": round(confidence, 2)
                })

        except Exception as e:
            print(f"⚠️ Error processing PDF: {e}")
            continue

    return {
        "query": q,
        "regex_enabled": use_regex,
        "match_count": len(results),
        "results": results,
        "message": f"{len(results)} matches found across {len(results)} PDFs."
    }


# NGROK TUNNEL

if __name__ == "__main__":
    print("🚀 Starting FastAPI with Ngrok tunnel...")
    public_url = ngrok.connect(PORT).public_url
    print(f"🌐 Public URL: {public_url}")
    os.system(f"uvicorn main:app --host 0.0.0.0 --port 8000")
