from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json

app = FastAPI()

# Allow React frontend to talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:3000"] for security
    allow_methods=["*"],
    allow_headers=["*"],
)

model = SentenceTransformer('all-MiniLM-L6-v2')
with open("tds_virtual_ta/corpus/embeddings.json", "r", encoding="utf-8") as f:
    db = json.load(f)

class Query(BaseModel):
    question: str

@app.post("/api/")
def get_answer(query: Query):
    q_vec = model.encode(query.question)
    similarities = cosine_similarity([q_vec], [item["embedding"] for item in db])[0]
    top_k = sorted(range(len(similarities)), key=lambda i: -similarities[i])[:2]
    return {
        "answer": db[top_k[0]]["text"][:300],
        "links": [
            {"url": db[i]["url"], "text": db[i]["text"][:100]} for i in top_k
        ]
    }
