import gradio as gr
import json
import numpy as np
import re
import pytesseract
from PIL import Image
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load embeddings (safely)
try:
    with open("corpus/all_embeddings.json", "r", encoding="utf-8") as f:
        db = json.load(f)[:300]
        for item in db:
            item["embedding"] = np.array(item["embedding"], dtype=np.float32)
    print("✅ Embeddings loaded successfully")
except Exception as e:
    print("❌ Failed to load embeddings:", e)
    db = []

# Semantic retrieval
def get_top_matches(question, db, top_k=3):
    q_vec = model.encode(question.strip().lower())
    doc_vectors = [item["embedding"] for item in db]
    sims = cosine_similarity([q_vec], doc_vectors)[0]
    top_indices = np.argsort(sims)[::-1][:top_k]
    return [
        {
            "text": db[i]["text"],
            "url": db[i]["url"],
            "score": float(sims[i]),
            "source": db[i].get("source", "unknown")
        }
        for i in top_indices
    ]

# Fallback logic with fixed sorting
def fallback_keyword_search(question, db):
    keywords = re.findall(r'\b\w+\b', question.lower())
    matches = []
    for item in db:
        score = sum(1 for word in keywords if word in item["text"].lower())
        if score > 0:
            matches.append((score + 0.01 * len(item["text"].split()), item))
    matches.sort(key=lambda x: x[0], reverse=True)
    return matches[:2]

# Relevance extractor
def extract_relevant_lines(text, query, num_lines=3):
    query_keywords = set(re.findall(r'\b\w+\b', query.lower()))
    lines = re.split(r"[.\n]", text)
    scored = []
    for line in lines:
        words = set(re.findall(r'\b\w+\b', line.lower()))
        score = len(words & query_keywords)
        if score > 0:
            scored.append((score, line.strip()))
    scored.sort(reverse=True)
    return "\n".join([line for _, line in scored[:num_lines]]) or text.strip()[:300]

# Main answering function
def answer_question(text, image):
    try:
        if not db:
            return "❗ Error: Embedding database not loaded.", ""

        # OCR
        if image:
            extracted = pytesseract.image_to_string(image).strip()
            question = extracted if extracted else text
        else:
            question = text

        question = question.strip()
        if not question:
            return "❗ Please enter a question or upload an image.", ""

        # Semantic results
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

# UI
iface = gr.Interface(
    fn=answer_question,
    inputs=[
        gr.Textbox(label="Ask a question 👇"),
        gr.Image(type="pil", label="Or upload a screenshot of your question")
    ],
    outputs=[
        gr.Markdown(label="🧠 Answer"),
        gr.Markdown(label="🔗 Relevant Links")
    ],
    title="TDS Virtual Teaching Assistant 🤖",
    description="Ask about TDS Jan–Apr 2025 content using semantic search. Supports screenshots and text!",
)

iface.launch()
