import json
import numpy as np
from sentence_transformers import SentenceTransformer

# Paths
course_path = "corpus/course_notes_embeddings.json"
discourse_path = "corpus/embeddings_with_urls.json"
output_path = "corpus/all_embeddings.json"

# Load files
with open(course_path, "r", encoding="utf-8") as f:
    course = json.load(f)

with open(discourse_path, "r", encoding="utf-8") as f:
    discourse = json.load(f)

# Tag if missing
for item in discourse:
    item["source"] = "discourse"

# Merge and format
combined = course + discourse
for item in combined:
    item["embedding"] = np.array(item["embedding"]).tolist()

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(combined, f, indent=2)

print(f"✅ Merged {len(combined)} items saved to: {output_path}")
