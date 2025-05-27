import json
import re
from modules.chatbot import chat_with_claude


def fallback_keyword_queries(user_question):
    # Base Peloton-related keywords
    base_terms = '"Peloton" OR "Peloton App" OR "pelotoncycle" OR "Peloton Bike" OR "Peloton Rower"'

    # Extract year/month/quarter references
    time_matches = re.findall(
        r"(Q[1-4]\s?\d{4}|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s?\d{4}|\b\d{4})",
        user_question,
        flags=re.I
    )

    # Extract product/sentiment keywords
    topic_matches = re.findall(
        r"(review|feedback|cancel|signup|update|issue|bug|launch|announcement|price|feature|comparison|reaction)",
        user_question,
        flags=re.I
    )

    # Build combined keyword string
    keyword_fragments = time_matches + topic_matches
    keyword_string = " ".join(keyword_fragments).strip()

    if not keyword_string:
        keyword_string = "Peloton"  # default fallback if no keywords detected

    platforms = {
        "Reddit": f'({base_terms}) {keyword_string} site:reddit.com',
        "Twitter": f'({base_terms}) {keyword_string} site:twitter.com',
        "YouTube": f'({base_terms}) {keyword_string} site:youtube.com',
        "News": f'({base_terms}) {keyword_string} (site:cnn.com OR site:nytimes.com OR site:techcrunch.com)'
    }

    return list(platforms.values())


def expand_search_queries(user_question):
    prompt = (
        "You are a search query generator. Given a user's question, extract the essential keywords and generate up to 4 concise Google search queries "
        "targeted to different platforms: Reddit, Twitter, YouTube, and News. "
        "Avoid repeating the full question. Use keywords like dates (e.g., 'Q1 2025'), products (e.g., 'Peloton App'), and event names. "
        "Use site filters: site:reddit.com, site:twitter.com, site:youtube.com, or "
        "site:cnn.com OR site:nytimes.com OR site:techcrunch.com. "
        "Output ONLY a valid JSON list like: "
        "[\"query1\", \"query2\", \"query3\", \"query4\"] — no commentary, no formatting."
        f"\n\nUser question: \"{user_question}\""
    )

    raw_response = chat_with_claude(prompt).strip()

    try:
        queries = json.loads(raw_response)
        assert isinstance(queries, list)
        return queries
    except Exception as e:
        print("⚠️ Claude failed to return valid JSON. Falling back to regex extraction:", e)
        return fallback_keyword_queries(user_question)
