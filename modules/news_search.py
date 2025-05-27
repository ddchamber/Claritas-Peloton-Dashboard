from modules.google_search import google_search_snippets  # reuse your existing CSE-based search

def search_news(query, num_results=5):
    news_sites = "site:cnn.com OR site:techcrunch.com OR site:nytimes.com"
    news_query = f"{query} {news_sites}"
    results = google_search_snippets(news_query, num_results=num_results)
    return [{"source": "News", **r} for r in results]
