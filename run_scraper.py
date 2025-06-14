import requests
import json
import os
from urllib.parse import quote


def search_discourse(keyword="pandas", start_date="2025-01-01", end_date="2025-04-14"):
    base_url = "https://discourse.onlinedegree.iitm.ac.in"
    query = f"{keyword} after:{start_date} before:{end_date}"
    encoded_query = quote(query)
    url = f"{base_url}/search.json?q={encoded_query}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": base_url,
        "Accept": "application/json",
    }

    cookies = {
        "_t": "Zord9fCzYD7gOgIb7MM1mw%2BLPigCGax68w%2BF3NHNKClvIwEqyVC82Qqh57wQAwFnhDisI%2BDEv5x5E4EIn4SKk0MTjmlJpk68iTWHzFKVaDcEBEk8OFzI1JYi%2BIPIZITarklRlAawtOVH1JL9z4FaDrvTNyr7wuslAg8f3roIZLnfbgwbaQSnYDUvr5Z3ULTNtPq0Io6oq217eIuWrL%2Btcp%2BGCiGyNvugcyCAkA1pgJkBiu2n2x2%2FR3LivtIAu87SMxt3QnWP%2BOX29mPZOeNufOkgXxhzAtoOQjeCcQ462rbBuMWn1cw%2BxJW%2FIHk6ErLInvwAyAHtmbI%3D--w7xy0XsW3nOy0bAt--x9Sr%2FlcRhBO4t6SLxFMOXg%3D%3D"
    }

    print(f"🔍 Searching Discourse for: {query}")
    r = requests.get(url, headers=headers, cookies=cookies)

    if r.status_code != 200:
        print(f"❌ Failed with status code {r.status_code}")
        return

    try:
        data = r.json()
    except Exception as e:
        print(f"❌ Failed to parse JSON: {e}")
        return

    posts = data.get("posts", [])
    results = []

    for post in posts:
        topic_id = post.get("topic_id")
        slug = post.get("topic_slug", "unknown-topic")
        title = post.get("blurb", "").replace('\n', ' ').strip()
        created_at = post.get("created_at", "")[:10]
        results.append({
            "id": topic_id,
            "title": title,
            "created_at": created_at,
            "url": f"{base_url}/t/{slug}/{topic_id}"
        })

    os.makedirs("corpus", exist_ok=True)
    with open("corpus/topics.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved {len(results)} posts to corpus/topics.json")


if __name__ == "__main__":
    search_discourse(keyword="assignment")  # Change keyword if needed
