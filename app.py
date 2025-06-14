import gradio as gr
import json
import numpy as np
import re
import pytesseract
from PIL import Image
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load model once
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load and slice corpus
try:
    with open("corpus/all_embeddings.json", "r", encoding="utf-8") as f:
        db = json.load(f)[:300]  # Limit size for Hugging Face RAM
        for item in db:
            item["embedding"] = np.array(item["embedding"], dtype=np.float32)
except FileNotFoundError:
    db = []
    print("❗ Warning: embeddings file not found. App will not work until 'corpus/all_embeddings.json' is uploaded.")

# Semantic search
def get_top_matches(question, db, top_k=3):
    query_vec = model.encode(question.strip().lower())
    doc_vecs = [item["embedding"] for item in db]
    sims = cosine_similarity([query_vec], doc_vecs)[0]
    top_indices = np.argsort(sims)[::-1][:top_k]
    return [
        {
            "text": db[i]["text"],
            "url": db[i]["url"],
            "score": float(sims[i]),
            "source": db[i].get("source", "unknown"),
        }
        for i in top_indices
    ]

# Keyword fallback
def fallback_keyword_search(question, db):
    keywords = re.findall(r"\b\w+\b", question.lower())
    matches = []
    for item in db:
        score = sum(1 for w in keywords if w in item["text"].lower())
        if score > 0:
            quality = len(item["text"].split())
            matches.append((score + 0.01 * quality, item))
    matches.sort(reverse=True)
    return matches[:2]

# Extract most relevant lines
def extract_relevant_lines(text, query, n=3):
    query_keywords = set(re.findall(r"\b\w+\b", query.lower()))
    lines = re.split(r"[.\n]", text)
    scored = []
    for line in lines:
        if not line.strip(): continue
        words = set(re.findall(r"\b\w+\b", line.lower()))
        score = len(words & query_keywords)
        if score > 0:
            scored.append((score, line.strip()))
    scored.sort(reverse=True)
    top = [line for _, line in scored[:n]]
    return "\n".join(top) if top else text[:300]

# Main QA logic
def answer_question(text, image):
    try:
        if not db:
            return "❗ Error: No embeddings loaded. Please upload the required JSON file.", ""

        if image:
            extracted = pytesseract.image_to_string(image).strip()
            question = extracted if extracted else text
        else:
            question = text.strip()

        if not question:
            return "❗ Please enter a valid question or upload an image.", ""

        results = get_top_matches(question, db)

        if not results or results[0]["score"] < 0.45:
            fallback = fallback_keyword_search(question, db)
            if fallback:
                best = fallback[0][1]
                answer = extract_relevant_lines(best["text"], question)
                return f"(Fallback from {best.get('source', 'unknown')}):\n\n{answer}", best["url"]
            else:
                return "❌ No relevant content found.", ""

        top = results[0]
        answer = extract_relevant_lines(top["text"], question)

        # Format links (avoid \n issues)
        link_lines = []
        for i, res in enumerate(results):
            snippet = res["text"][:80].replace("\n", " ")
            line = f"{i+1}. [{snippet}...]({res['url']}) — {res['source']} ({res['score']:.2f})"
            link_lines.append(line)
        links = "\n".join(link_lines)

        return answer, links

    except Exception as e:
        print("❌ Internal error:", e)
        return f"An error occurred: {str(e)}", ""

# Gradio UI
iface = gr.Interface(
    fn=answer_question,
    inputs=[
        gr.Textbox(label="Ask your question 👇 (or leave blank if using image)"),
        gr.Image(type="pil", label="Upload a screenshot of your question"),
    ],
    outputs=[
        gr.Markdown(label="🧠 Answer"),
        gr.Markdown(label="🔗 Relevant Links"),
    ],
    title="TDS Virtual Teaching Assistant 🤖",
    description="Ask anything from the TDS Jan–Apr 2025 course using text or image. Powered by semantic search, fallback, and OCR.",
)

iface.launch()
