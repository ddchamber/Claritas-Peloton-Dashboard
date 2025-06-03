import streamlit as st
from modules.google_search import google_search_snippets
from modules.reddit_search import search_reddit
from modules.twitter_search import search_twitter
from modules.youtube_search import search_youtube
from modules.chatbot import chat_with_claude
import os
import json

st.set_page_config(layout="wide")

# --- Custom Styling ---
st.markdown("""
<style>
body {
    background-color: black;
    font-family: 'Segoe UI', sans-serif;
}
h1, .css-10trblm {
    color: #F05A28 !important;
    text-shadow: 1px 1px 3px rgba(240,90,40,0.6);
}
.section-title {
    font-size: 22px;
    font-weight: 600;
    color: #F05A28;
    margin-top: 40px;
    text-shadow: 1px 1px 2px rgba(255,255,255,0.15);
}
label {
    color: #74C2E1 !important;
    font-weight: bold;
}
.divider {
    border-top: 2px solid #74C2E1;
    margin: 25px 0;
}
.filter-header {
    font-size: 20px;
    font-weight: 700;
    color: #74C2E1;
    margin-bottom: 10px;
}
.filter-label {
    font-size: 14px;
    color: #74C2E1;
    margin-top: 12px;
    margin-bottom: 4px;
    font-weight: bold;
}
.filters-title {
    font-size: 30px;
    font-weight: 800;
    color: #F05A28;
    text-shadow: 1px 1px 2px rgba(240,90,40,0.4);
    margin-bottom: 10px;
}
label[for="select_all"], label[for="toggle_map"] {
    font-size: 14px;
    color: #74C2E1 !important;
    font-weight: bold;
    margin-top: 8px;
    display: block;
}
</style>
""", unsafe_allow_html=True)

st.title("Current Events Summary")

# --- Load PRIZM segments
with open("PelotonDashboard/data/prizm_descriptions.json", "r", encoding="utf-8") as f:
    prizm_data = json.load(f)

prizm_lookup = {seg["name"]: seg for seg in prizm_data}

# --- UI: Topic and PRIZM selectors
topics = [
    "Peloton",
    "Fitness Industry",
    "Home Fitness Industry",
    "Biking Industry"
]
selected_topic = st.selectbox("Select a topic to view its summary:", topics)
segment_options = ["---"] + sorted(prizm_lookup.keys())
selected_segment_name = st.selectbox("Select a PRIZM Segment:", segment_options)
selected_segment = prizm_lookup.get(selected_segment_name)


# --- Generate content
if st.button("Generate Summaries for All Topics"):
    if "summaries" not in st.session_state:
        st.session_state["summaries"] = {}

    for topic in topics:
        with st.spinner(f"Fetching and analyzing content for: {topic}"):
            # --- Check if this topic already has a summary
            if topic in st.session_state["summaries"]:
                topic_summary = st.session_state["summaries"][topic]["summary"]
                all_results = st.session_state["summaries"][topic]["sources"]
            else:
                # --- Run searches
                google_results = google_search_snippets(topic, num_results=5, recency="qdr:y")
                reddit_results = search_reddit(topic, num_results=5, recency="qdr:y")
                twitter_results = search_twitter(topic, num_results=5, recency="qdr:y")
                youtube_results = search_youtube(topic, num_results=5, recency="qdr:y")

                # --- Combine results
                all_results = []
                for group, results in [
                    ("Google", google_results),
                    ("Reddit", reddit_results),
                    ("Twitter", twitter_results),
                    ("YouTube", youtube_results)
                ]:
                    for r in results:
                        all_results.append({
                            "source": group,
                            "title": r.get("title", "Untitled"),
                            "snippet": r.get("snippet", r.get("text", "")),
                            "link": r.get("link", "")
                        })

                combined_text = "\n\n".join(
                    f"[{r['source']}] {r['title']}\n{r['snippet']}\n{r['link']}" for r in all_results
                )

                # --- Main summary prompt
                topic_prompt = f"""
You are a professional market intelligence analyst. Your job is to analyze recent content from social media, forums, and the web to extract key insights that would be useful for a business leader.

Below is content related to "{topic}". Your output must follow these rules:

1. Identify the **5 most relevant current events or trends** that appear across the sources.
2. For each, create a short **title** (like a headline), followed by **1-2 sentences** explaining the event in plain language.
3. Use clear, concise, and professional language.
4. Avoid speculation. Only summarize what can reasonably be inferred from the sources.
5. Reference the list of sources directly and supply a date to see recency.
6. Order news from most recent to oldest.
7. Use **bold** for the titles of each event.
8. Use *italics* for the source names.
9. Use **bullet points** for each event.
10. Do not add anything else to output besides the summaries.

Make the result visually scannable and useful for brainstorming decisions or strategies. Example format:

**1. Peloton Loses 3 Five-Star Instructors**

Peloton recently parted ways with several top instructors, sparking concern among its loyal user base and raising questions about company culture and retention.
(Google 2023-10-01 with link to url used)

**Sources:**

- Remember to include the source name, title, and link for each event.
{combined_text}
"""
                topic_summary = chat_with_claude(topic_prompt)

            # --- PRIZM analysis (always rerun with selected segment)
            if selected_segment_name != "---" and selected_segment:
                prizm_profile_json = json.dumps(selected_segment, indent=2, ensure_ascii=False)
                prizm_prompt = f"""
You are a marketing strategist AI. Below is a summary of current events related to "{topic}" and a profile of a specific PRIZM segment.

Your job is to briefly explain **how these events may impact or be perceived by people in the {selected_segment_name} segment.** Mention possible reactions, behaviors, or marketing implications.

Respond in 3-4 concise, professional sentences with clear relevance.

--- Segment Profile (JSON) ---
{prizm_profile_json}

--- Current Events Summary ---
{topic_summary}
"""
                prizm_insight = chat_with_claude(prizm_prompt)
            else:
                prizm_insight = "No specific PRIZM segment selected. This is a general overview based on public trends and behaviors."

            # --- Always update PRIZM insight to reflect current selection
            st.session_state["summaries"][topic] = {
                "summary": topic_summary,
                "sources": all_results,
                "prizm_insight": prizm_insight
            }



# --- Output Display for Current Topic ---
if "summaries" in st.session_state and selected_topic in st.session_state["summaries"]:
    current_summary = st.session_state["summaries"][selected_topic]["summary"]
    current_sources = st.session_state["summaries"][selected_topic]["sources"]

    # --- Always recalculate PRIZM insight if a segment is selected
    if selected_segment_name != "---" and selected_segment:
        prizm_profile_json = json.dumps(selected_segment, indent=2, ensure_ascii=False)
        updated_prizm_prompt = f"""
You are a marketing strategist AI. Below is a summary of current events related to "{selected_topic}" and a profile of a specific PRIZM segment.

Your job is to briefly explain **how these events may impact or be perceived by people in the {selected_segment_name} segment.** Mention possible reactions, behaviors, or marketing implications.

Respond in 4-5 concise, professional sentences with clear relevance.

--- Segment Profile (JSON) ---
{prizm_profile_json}

--- Current Events Summary ---
{current_summary}
"""
        updated_prizm_insight = chat_with_claude(updated_prizm_prompt)
    else:
        updated_prizm_insight = "No specific PRIZM segment selected. This is a general overview based on public trends and behaviors."

    # --- Display Section
    st.markdown(f"""
    <h2 style='margin-bottom: 0;'>
        <span style='color: #F05A28;'>AI Websearch Summary for:</span>
        <span style='color: white;'>{selected_topic}</span>
    </h2>
    """, unsafe_allow_html=True)

    st.markdown(current_summary)

    with st.expander("Sources Used"):
        for r in current_sources:
            if r['link']:
                st.markdown(f"- [{r['source']}] [{r['title']}]({r['link']})")

    st.markdown("<div style='border-top: 2px solid #74C2E1; margin: 10px 0 20px 0;'></div>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:#F05A28;'>How This Affects <span style='color:white'>{selected_segment_name}</span></h3>", unsafe_allow_html=True)
    st.markdown(updated_prizm_insight)

st.session_state["news_summary"] = current_summary
st.session_state["prizm_insight"] = updated_prizm_insight
