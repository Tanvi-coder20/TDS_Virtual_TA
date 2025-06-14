import json
import os

INPUT_PATH = "tds_virtual_ta/corpus/embeddings.json"
OUTPUT_PATH = "tds_virtual_ta/corpus/embeddings_fixed.json"

# Step 1: Load the original data
with open(INPUT_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Step 2: Fix the field names and optionally add dummy URL
fixed_data = []
for item in data:
    if "chunk" in item:
        fixed_item = {
            "text": item["chunk"],
            "embedding": item["embedding"],
            "url": "https://discourse.onlinedegree.iitm.ac.in/"  # Dummy link
        }
        fixed_data.append(fixed_item)
    else:
        print("⚠️ Skipped item without 'chunk'")

# Step 3: Save the fixed version
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(fixed_data, f, indent=2)

print(f"✅ Fixed file saved: {os.path.abspath(OUTPUT_PATH)}")
