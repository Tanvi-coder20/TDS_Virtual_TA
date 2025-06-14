import json
with open("corpus/all_embeddings.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

matches = [c for c in chunks if "kumu" in c["text"].lower()]
print(f"🔍 Chunks about Kumu: {len(matches)}")
for m in matches:
    print("\n---\n", m["text"])
