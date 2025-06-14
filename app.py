import gradio as gr
import json
import numpy as np
import re
import pytesseract
from PIL import Image
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Windows users: Uncomment this if needed
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load embeddings
with open("corpus/all_embeddings.json", "r", encoding="utf-8") as f:
    db = json.load(f)[:300]

for item in db:
    if "embedding" in item:
        item["embedding"] = np.array(item["embedding"])

# --- Semantic similarity ---
def get_top_matches(question, db, top_k=3):
    q_vec = model.encode(question.strip().lower())
    doc_vectors = [item["embedding"] for item in db]
    sims = cosine_similarity([q_vec], doc_vectors)[0]
    top_indices = np.argsort(sims)[::-1][:top_k]
    return [{
        "text": db[i]["text"],
        "url": db[i]["url"],
        "score": sims[i],
        "source": db[i].get("source", "unknown")
    } for i in top_indices]

# --- Keyword fallback ---
def fallback_keyword_search(question, db):
    keywords = re.findall(r'\b\w+\b', question.lower())
    matches = []
    for item in db:
        score = sum(1 for word in keywords if word in item["text"].lower())
        if score > 0:
            chunk_quality = len(item["text"].split())
            matches.append((score + 0.01 * chunk_quality, item))
    matches.sort(reverse=True, key=lambda x: x[0])
    return matches[:2]

# --- Extract only relevant lines from the matched chunk ---
def extract_relevant_lines(text, query, num_lines=3):
    query_keywords = set(re.findall(r'\b\w+\b', query.lower()))
    lines = re.split(r"[.\n]", text)  # sentence/line split
    scored = []
    for line in lines:
        words = set(re.findall(r'\b\w+\b', line.lower()))
        score = len(words & query_keywords)
        if score > 0:
            scored.append((score, line.strip()))
    scored.sort(reverse=True, key=lambda x: x[0])
    top = [line for _, line in scored[:num_lines]]
    return "\n".join(top) if top else text.strip()[:300]

# --- Main QA logic ---
def answer_question(text, image):
    try:
        # OCR
        if image is not None:
            extracted = pytesseract.image_to_string(image).strip()
            question = extracted if extracted else text
        else:
            question = text

        if not question.strip():
            return "❗ Please enter a question or upload a readable image.", ""

        results = get_top_matches(question, db)

        if not results or results[0]["score"] < 0.45:
            fallback = fallback_keyword_search(question, db)
            if fallback:
                best = fallback[0][1]
                answer = extract_relevant_lines(best["text"], question)
                return f"(Fallback from {best.get('source', 'unknown')}):\n\n" + answer, best["url"]
            else:
                return "❌ No relevant answer found.", ""

        top = results[0]
        answer = extract_relevant_lines(top["text"], question)
        links = "\n".join([
            f"{i+1}. [{res['text'][:80].replace('\n', ' ')}...]({res['url']}) — {res['source']} ({res['score']:.2f})"
            for i, res in enumerate(results)
        ])
        return answer, links

    except Exception as e:
        print("❌ ERROR:", e)
        return f"An error occurred: {str(e)}", ""

# --- Gradio UI ---
iface = gr.Interface(
    fn=answer_question,
    inputs=[
        gr.Textbox(label="Ask your question 👇 (or leave blank if using image)"),
        gr.Image(type="pil", label="Upload a screenshot of your question")
    ],
    outputs=[
        gr.Markdown(label="🧠 Answer"),
        gr.Markdown(label="🔗 Relevant Links")
    ],
    title="TDS Virtual Teaching Assistant 🤖",
    description="Ask anything from the TDS Jan–Apr 2025 course using text or image. Powered by semantic search, fallback, and OCR.",
    theme="default"
)

iface.launch(server_name="0.0.0.0", server_port=8080)

