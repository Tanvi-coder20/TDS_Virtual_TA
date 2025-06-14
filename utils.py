import torch
import json
import os
from sentence_transformers import SentenceTransformer, util

# Load corpus
CORPUS_PATH = "tds_virtual_ta/corpus/full_posts.json"
EMBEDDINGS_PATH = "tds_virtual_ta/corpus/post_embeddings.pt"

with open(CORPUS_PATH, "r", encoding="utf-8") as f:
    posts = json.load(f)

post_embeddings = torch.load(EMBEDDINGS_PATH)
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_virtual_ta_response(question: str):
    query_embedding = model.encode(question, convert_to_tensor=True)
    scores = util.pytorch_cos_sim(query_embedding, post_embeddings)[0]
    top_results = torch.topk(scores, k=2)

    answer_post = posts[top_results.indices[0]]
    related_links = [
        {
            "url": post["url"],
            "text": post["title"][:100]
        }
        for idx in top_results.indices
        for post in [posts[idx]]
    ]

    return {
        "answer": answer_post["content"],
        "links": related_links
    }
