from modules.google_search import google_search_snippets

def search_reddit(query, num_results=5, recency=None):
    keywords = '"Peloton" OR "Peloton App" OR "pelotoncycle" OR "Peloton Bike" OR "Peloton Rower"'
    reddit_query = f'({keywords}) {query} site:reddit.com'
    results = google_search_snippets(reddit_query, num_results=num_results, recency=recency)
    return [{"source": "Reddit", **r} for r in results]


