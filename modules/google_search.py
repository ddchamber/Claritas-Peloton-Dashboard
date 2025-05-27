import requests
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CX")

# Map custom ranges to Google's 'tbs' values
RECENCY_MAP = {
    "7d": "qdr:w",     # last week
    "30d": "qdr:m",    # last month
    "90d": "qdr:m",    # approximate using month
    "180d": "qdr:m",   # approximate using month
    "365d": "qdr:y"    # last year
}

def google_search_snippets(query, num_results=5, recency=None):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CX,
        "q": query,
        "num": num_results
    }

    if recency in RECENCY_MAP:
        params["tbs"] = RECENCY_MAP[recency]

    response = requests.get(url, params=params)
    data = response.json()

    results = []
    for item in data.get("items", []):
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        link = item.get("link", "")
        results.append({
            "title": title,
            "snippet": snippet,
            "link": link
        })

    return results
