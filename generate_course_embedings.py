import fitz  # PyMuPDF
import textwrap
import json
from sentence_transformers import SentenceTransformer
import os

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text

def chunk_text(text, max_chars=1000):
    raw_chunks = textwrap.wrap(text, width=max_chars)
    return [
        chunk.strip()
        for chunk in raw_chunks
        if len(chunk.strip().split()) > 5 and not chunk.lower().startswith("week_")
    ]

def generate_course_embeddings(pdf_path, output_path, base_url="https://course-notes.tds.iitm.ac.in/2025"):
    print(f"📘 Reading from PDF: {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text)
    print(f"✂️ Filtered to {len(chunks)} quality chunks")

    model = SentenceTransformer('all-MiniLM-L6-v2')

    results = []
    for i, chunk in enumerate(chunks):
        embedding = model.encode(chunk).tolist()
        results.append({
            "text": chunk,
            "embedding": embedding,
            "url": f"{base_url}#chunk-{i+1}",
            "source": "course"
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"✅ Saved to: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    pdf_path = "data/TDS_Notes.pdf"
    output_path = "corpus/course_notes_embeddings.json"
    generate_course_embeddings(pdf_path, output_path)
