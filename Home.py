import streamlit as st
from modules.page_processors import (
    run_forecasting_logic,
    run_current_events_logic,
    run_biggest_movers_logic
)
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
    This is a powerful tool to help you combine your company’s data with knowledge from the internet and AI.
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ---- Insight Summary Section ----
forecast_output = run_forecasting_logic()
events_output = run_current_events_logic()
movers_output = run_biggest_movers_logic()

combined_prompt = f"""
You are a senior business strategist. Based on the following data, generate a detailed, specific marketing recommendation.

Forecast Trends:
{forecast_output['forecast_summary']}
{forecast_output['trend_snippet']}

Current Events:
{events_output['event_summary']}

PRIZM Insight:
{events_output['prizm_insight']}

Biggest Movers:
{movers_output['movers_summary']}
{movers_output['dma_movers_table']}
{movers_output['prizm_movers_table']}
"""

consolidated_response = chat_with_claude(combined_prompt)

st.markdown("""
<div style='font-size: 24px; font-weight: 700; color: #F05A28; margin-top: 40px;'>
    Performance Summary
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style='font-size: 18px; color: #FFFFFF; font-weight: 600;'>
    {events_output['event_summary']}
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class='detailed-analysis'>
{consolidated_response}
</div>
""", unsafe_allow_html=True)

# ---- Footer Section ----
st.markdown("<div class='footer'>", unsafe_allow_html=True)

st.markdown("""
<div style='font-size: 20px; font-weight: bold; color: #F05A28;'>
    Want More? <span style='font-size: 16px; font-weight: 500; color: #C9E8F2;'>Check out these features!</span>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='border-top: 2px solid #74C2E1; margin: 10px 0 20px 0;'></div>", unsafe_allow_html=True)

st.markdown("""
<div class='footer-list'>
- <strong>Time Series Predictions</strong>: Forecast future demand, traffic, and sales using advanced AI models.<br>
- <strong>Internet Search</strong>: Discover real-time insights from news, social media, and videos that impact your KPIs.<br>
- <strong>In-Depth Trends</strong>: Uncover behavioral shifts across regions, demographics, and competitive segments.
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
