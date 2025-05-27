import json
from modules.chatbot import chat_with_claude  # uses your Claude wrapper
import streamlit as st  # required to use st.code()
def expand_search_queries(user_question):
    prompt = (
    "You are a search assistant. Given a user's question, generate up to 4 Google search queries targeting different platforms. "
    "You are an employee of Peloton, so words, like our, we, us and our should, be treated as Peloton."
    "One for Reddit, one for Twitter, one for YouTube, and one for News. "
    "Use appropriate site filters (e.g., site:reddit.com, site:twitter.com, site:youtube.com, "
    "or site:cnn.com OR site:nytimes.com OR site:techcrunch.com). "
    "Output ONLY a valid JSON array of strings like this: [\"query1\", \"query2\", \"query3\", \"query4\"] "
    "— no explanation, no bullets, no text outside the array. "
    f"User question: '{user_question}'"
    )


    raw_response = chat_with_claude(prompt).strip()

    st.markdown("### 🧪 Claude's Raw Output")
    st.code(raw_response, language="json")


    try:
        queries = json.loads(raw_response)
        assert isinstance(queries, list)
        return queries
    except Exception:
        return [f"peloton site:reddit.com", f"peloton site:twitter.com", f"peloton site:youtube.com", f"peloton site:cnn.com"]

