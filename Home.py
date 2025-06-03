import streamlit as st
from modules.page_processors import (
    run_forecasting_logic,
    run_current_events_logic,
    run_biggest_movers_logic
)
import json
import pandas as pd
from modules.chatbot import chat_with_claude

st.set_page_config(page_title="Claritas AI Dashboard", layout="wide")

# ---- Styling Block ----
st.markdown("""
<style>
body {
    background-color: black;
    font-family: 'Segoe UI', sans-serif;
}
.welcome {
    font-size: 40px;
    font-weight: 900;
    color: #F05A28;
    text-shadow: 1px 1px 3px rgba(240,90,40,0.6);
}
.header-text {
    font-size: 22px;
    color: #EDEDED;
    margin-bottom: 5px;
}
.section-title {
    font-size: 22px;
    font-weight: 600;
    color: #F05A28;
    margin-top: 40px;
    text-shadow: 1px 1px 2px rgba(255,255,255,0.15);
}
.news-summary {
    font-size: 18px;
    color: #D0E8F0;
    margin-top: 10px;
    font-weight: 500;
}
.detailed-analysis {
    font-size: 16px;
    color: #CCCCCC;
    margin-left: 20px;
    margin-top: 8px;
}
.divider {
    border-top: 2px solid #74C2E1;
    margin: 25px 0;
}
.footer {
    margin-top: 50px;
    padding-top: 20px;
    border-top: 2px solid #74C2E1;
}
.footer-header {
    font-size: 20px;
    color: #F05A28;
    font-weight: bold;
    text-shadow: 1px 1px 2px rgba(240,90,40,0.5);
}
.footer-list {
    font-size: 16px;
    color: #C9E8F2;
    margin-left: 20px;
}
            
.chat-container {
    max-height: 400px;
    overflow-y: auto;
    padding-right: 12px;
    margin-bottom: 60px;
}

.fixed-chat-input {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    padding: 16px;
    background-color: #111111;
    border-top: 2px solid #74C2E1;
    z-index: 999;
}
</style>
""", unsafe_allow_html=True)

# ---- Hero Section ----
st.markdown("""
<div style='display: flex; align-items: baseline; justify-content: flex-start; gap: 12px;'>
    <span style='font-size: 36px; font-weight: bold; color: #F05A28;'>Welcome</span>
    <span style='font-size: 48px; font-weight: bold; color: white;'>Peloton</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style='font-size: 18px; color: #EDEDED; margin-top: 4px;'>
    This is a powerful tool to help you combine your company's data with knowledge from the internet and AI.
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ---- Insight Summary Section and Other Data ----
forecast_output = run_forecasting_logic()
events_output = run_current_events_logic()
movers_output = run_biggest_movers_logic()
# Load PRIZM segments from JSON file
with open("PelotonDashboard/data/prizm_descriptions.json", "r", encoding="utf-8") as f:
    prizm_data = json.load(f)
# Dma demographics
dma_demographics = pd.read_csv("PelotonDashboard/data/dma_demo_region.csv")

messages = [
    {
        "role": "user",
        "content": f"""
You are an executive marketing strategist AI advising Peloton.

You have been provided with multiple AI-generated summaries and supporting data sources. Your job is to **synthesize all of it** into one clear, strategic marketing execution plan. The goal is to give a confident, executive-level recommendation that shows how Peloton is positioned in the industry, who their key audiences are, and what immediate actions they should take to grow and defend market share.

Your response should be structured using the following format:

<Required Output Structure>

### **1. Market Synopsis**  
Summarize Peloton's competitive standing and what's changing in the fitness industry.  
This should integrate insights from historical/forecast trends and current events.

- What's Peloton's momentum like?
- What major shift is happening in the market?
- Why now is a critical time to act?
- Make a note about purchases.

### **2. Audience Intelligence**  
Identify 2-3 of the most important consumer segments or regions to target right now.  
Base this on:
- PRIZM segment movers (top gainers or losses)
- DMA shifts (which cities/regions are changing most)
- Relevance to the current events summary

For each audience:
- Name the segment/region
- What behavior changed?
- How should Peloton speak to them?

### **3. Strategic Playbook**  
Lay out a full-spectrum marketing plan across three time horizons:

**Immediate Actions** (next 2-4 weeks):
Tactical moves tied to current momentum, media cycles, or segment surges.

**Quarterly Strategy** (2-3 months): 
Positioning, product offers, or cross-platform tactics to convert attention into loyalty.

**Long-Term Advantage** (6+ months):  
Bold, long-view strategies to solidify Peloton as the market leader in premium connected fitness.

### **4. Confidence Signals**  
End with 3-5 bullet points that justify why this is the *right* plan based on data.  
Each point should be based on either:  
- Forecast/historical trends  
- Segment behavior  
- Regional demand changes  
- Industry news

</Required Output Structure>

---
**Inputs to consider**:

**1. Forecast Trend Summary** - AI output analyzing the company's performance and future trends.
{forecast_output['forecast_summary']}

**2. Historical Data Snapshot**  - Where the company's trends been in the last 30 days.
{forecast_output['historical_snippet']}

**3. Forecasted Engagement Data**  - What the future trend of teh company based on an time series model.
{forecast_output['forecast_snippet']}

**4. Current Events Summary**  - What the internet is saying about Peloton and the fitness industry.
{events_output['event_summary']}

**5. PRIZM Segment Specific Insights** - How current events may impact specific PRIZM segments.
{events_output['prizm_insight']}

**5. Demographic Movers Summary** - AI output summarizing the biggest movers in Peloton's DMA regions.
{movers_output['movers_summary']}

**6. PRIZM Segment Profile JSON**  - A detailed JSON profile of Peloton's PRIZM segments.
{prizm_data}

**7. DMA Demographic Overview**  - A CSV file containing demographic data for Peloton's DMA regions.
{dma_demographics}

Do not repeat the inputs verbatim. Instead, **distill and integrate**. Prioritize clarity, confidence, and strategic depth.

Use a professional and executive tone. This is going straight to senior leadership at Peloton.
 
Use some insight from each of the inputs to create a comprehensive, actionable plan. Strait to the point.

- Make sure to include some recommendation in the Quarterly Strategy that incorporates teh news about kettlebells.

"""
    }
]


consolidated_response = chat_with_claude(messages)

st.markdown("""
<div style='font-size: 24px; font-weight: 700; color: #F05A28; margin-top: 40px;'>
    Performance Summary
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class='detailed-analysis'>
{consolidated_response}
</div>
""", unsafe_allow_html=True)

# --- Chatbot Section with Sticky Input and Memory ---
from modules.chatbot import chat_with_claude

# --- Initialize session state ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "system",
            "content": f"""
You are Claritas AI, a strategic marketing assistant for Peloton. You specialize in interpreting forecasting data, regional trends, and consumer behavior to help executives make high-impact decisions.

You have access to market forecasts, PRIZM segment insights, current events summaries, and an overall company breakdown given in the consolidated_response. Always respond with a confident, helpful tone — your goal is to translate data into action.

Your responses should be concise, professional, and focused on actionable insights.

Your task is to assist Peloton executives by providing clear, data-driven recommendations based on the latest insights, make sure they are thought out and are interesting. Give some details that are potentially too specific as idea starters.

Remember you are used as a brainstorming tool, give recommendations to spark intrigue in teh customer and ask for their input. If they sk for more information get even more specific or if they dont like it get take a step back. Get creative!

Here's the latest context:
- Forecast Summary: {forecast_output['forecast_summary']}
- Events: {events_output['event_summary']}
- Movers: {movers_output['movers_summary']}
- Main Summary and recommendations: {consolidated_response}
"""
        }
    ]
if "chatbot_input_value" not in st.session_state:
    st.session_state.chatbot_input_value = ""

# --- Message submission logic using on_change ---
def handle_user_message():
    user_msg = st.session_state.chatbot_input_value.strip()
    if user_msg:
        st.session_state.chat_history.append({"role": "user", "content": user_msg})
        with st.spinner("Thinking..."):
            assistant_reply = chat_with_claude(st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
        st.session_state.chatbot_input_value = ""  # Clears input before next rerender

# --- Section Header ---
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<div style='font-size: 24px; font-weight: 700; color: #F05A28;'>Ask Claritas AI</div>", unsafe_allow_html=True)

# --- Scrollable chat history ---
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
for msg in st.session_state.chat_history[1:]:  # Skip system prompt
    if msg["role"] == "user":
        st.markdown(f"<div style='color:#74C2E1; font-weight:bold;'>You:</div><div class='detailed-analysis'>{msg['content']}</div>", unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f"<div style='color:#F05A28; font-weight:bold;'>Claritas AI:</div><div class='detailed-analysis'>{msg['content']}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- Sticky Chat Input ---
with st.container():
    st.markdown("<div class='fixed-chat-input'>", unsafe_allow_html=True)
    st.text_input(
        "Type your question here and hit Enter...",
        key="chatbot_input_value",
        label_visibility="collapsed",
        on_change=handle_user_message,
    )
    st.markdown("</div>", unsafe_allow_html=True)


# ---- Footer Section ----
st.markdown("<div class='footer'>", unsafe_allow_html=True)

st.markdown("""
<div style='font-size: 20px; font-weight: bold; color: #F05A28;'>
    Want More? <span style='font-size: 16px; font-weight: 500; color: #C9E8F2;'>Check out these features!</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class='footer-list'>
<strong>Forecasting Dashboard</strong>: 
            Visualize historical Peloton and competitor engagement, and forecast the next 30 days using models with customizable filters.<br>
<strong>Current Events</strong>: 
            Identify and summarize key news and online discussions that may explain recent engagement patterns or shifts in DMA and PRIZM segment behavior.<br>
<strong>Biggest Movers</strong>: 
            Detect and analyze the top demographic and regional shifts influencing Peloton performance, highlighting emerging opportunities and risks.
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
