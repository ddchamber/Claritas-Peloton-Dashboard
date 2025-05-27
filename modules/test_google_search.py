import requests
import os
from dotenv import load_dotenv

load_dotenv() # add you own credential to the env file
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CX")
query = "site:reddit.com/r/peloton peloton news"

def run_test():
    if not GOOGLE_API_KEY or not GOOGLE_CX:
        print("❌ API key or CX (search engine ID) is missing.")
        return

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": query,
        "num": 5
    }

    print("🔍 Sending request to Google Custom Search API...")
    print("Request URL:", url)
    print("Parameters:", params)

    response = requests.get(url, params=params)
    print("Status code:", response.status_code)

    try:
        data = response.json()
        if "items" in data:
            print(f"\n✅ {len(data['items'])} results found:\n")
            for i, item in enumerate(data["items"], 1):
                print(f"{i}. {item['title']}")
                print(item["link"])
                print(item.get("snippet", ""))
                print("-" * 40)
        else:
            print("⚠️ No results returned.")
            print("Full response:", data)
    except Exception as e:
        print("❌ Failed to parse response:", e)

if __name__ == "__main__":
    run_test()
