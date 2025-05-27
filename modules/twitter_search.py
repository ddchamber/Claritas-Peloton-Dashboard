from modules.google_search import google_search_snippets  # temporarily reused for Twitter search

def search_twitter(query, num_results=5, recency=None):
    keywords = '"Peloton" OR "Peloton App" OR "pelotoncycle" OR "Peloton Bike" OR "Peloton Rower"'
    twitter_query = f'({keywords}) {query} site:twitter.com'
    results = google_search_snippets(twitter_query, num_results=num_results, recency=recency)
    return [{"source": "Twitter", **r} for r in results]


