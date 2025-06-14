import json
import os
import time
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://discourse.onlinedegree.iitm.ac.in"
INPUT_FILE = "corpus/topics.json"
OUTPUT_FILE = "corpus/full_posts.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": BASE_URL,
    "Accept": "text/html",
}

# 🧁 Your session cookie (you may need to update this periodically)
COOKIES = {
    "_forum_session": "CWR55K%2FXAtymoiYNJMHBsgg89VwZ3gozsvRjIs2V%2BbxexQW2GVNMtsTZP7Ztd2%2BDaNPm2WpLvsmItnVgybI1HXQq4x3rYZH4wAACB0%2FcUnS1LNJxUJ3ts4ZaD0EQyqEdRCbvW7FAZogZ6%2BQtwJPfB55FpsacQ1tTpNoBOefamNfYqZxsoPSl%2F8dXSOFPibicrx8V0DpQU%2BBI%2BrOWPzJ4rJLPj1ldVJaFoGRNOAPa6pLWdemYDvAthsASnVPXj4%2Fao0M6B12OA61Wh9JcBW7dGux4wh2v4Q%3D%3D--1dvT6y6VPLNZ8yO%2F--CTnqiQQVIsciOPAdO3V60Q%3D%3D",
    "_t": "Zord9fCzYD7gOgIb7MM1mw%2BLPigCGax68w%2BF3NHNKClvIwEqyVC82Qqh57wQAwFnhDisI%2BDEv5x5E4EIn4SKk0MTjmlJpk68iTWHzFKVaDcEBEk8OFzI1JYi%2BIPIZITarklRlAawtOVH1JL9z4FaDrvTNyr7wuslAg8f3roIZLnfbgwbaQSnYDUvr5Z3ULTNtPq0Io6oq217eIuWrL%2Btcp%2BGCiGyNvugcyCAkA1pgJkBiu2n2x2%2FR3LivtIAu87SMxt3QnWP%2BOX29mPZOeNufOkgXxhzAtoOQjeCcQ462rbBuMWn1cw%2BxJW%2FIHk6ErLInvwAyAHtmbI%3D--w7xy0XsW3nOy0bAt--x9Sr%2FlcRhBO4t6SLxFMOXg%3D%3D"
}


def fetch_full_post(url):
    print(f"📄 Fetching {url}")
    response = requests.get(url + ".json", headers=HEADERS, cookies=COOKIES)

    if response.status_code != 200:
        print(f"❌ Failed to fetch {url}: {response.status_code}")
        return None

    try:
        data = response.json()
        post_stream = data["post_stream"]["posts"]
        first_post = post_stream[0]
        return {
            "url": url,
            "title": data["title"],
            "content": first_post["cooked"],  # HTML content
            "created_at": first_post["created_at"]
        }
    except Exception as e:
        print(f"⚠️ Error parsing post JSON: {e}")
        return None


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        topics = json.load(f)

    results = []

    for topic in topics:
        post = fetch_full_post(topic["url"])
        if post:
            results.append(post)
        time.sleep(1)  # be polite to the server

    os.makedirs("corpus", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved {len(results)} full posts to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
