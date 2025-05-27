from modules.google_search import google_search_snippets  # reused for fallback

def search_youtube(query, num_results=5, recency=None):
    youtube_query = f"{query} site:youtube.com"
    results = google_search_snippets(youtube_query, num_results=num_results, recency=recency)
    return [{"source": "YouTube", **r} for r in results]
