import json
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import numpy as np
import os

# Load posts
with open("corpus/full_posts.json", "r", encoding="utf-8") as f:
    posts = json.load(f)

# Option 1: Use Sentence Transformers (local, free)
model = SentenceTransformer("all-MiniLM-L6-v2")  # Fast and good enough for testing

# Chunk and embed
embeddings = []
for post in posts:
    content = post.get("content", "")
    if not content.strip():
        continue
    chunks = [content[i:i + 500] for i in range(0, len(content), 500)]  # Chunking
    for chunk in chunks:
        vector = model.encode(chunk)
        embeddings.append({
            "chunk": chunk,
            "embedding": vector.tolist(),
            "meta": {"url": post["url"], "title": post["title"]}
        })

# Save
os.makedirs("corpus", exist_ok=True)
with open("corpus/embeddings.json", "w", encoding="utf-8") as f:
    json.dump(embeddings, f, indent=2, ensure_ascii=False)

print(f"✅ Saved {len(embeddings)} embeddings to corpus/embeddings.json")
