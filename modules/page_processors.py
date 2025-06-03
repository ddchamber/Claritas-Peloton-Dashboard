import pandas as pd
import streamlit as st

def run_forecasting_logic():
    summary = st.session_state.get("time_series_summary", "No forecast summary available.")
    historical_snippet = st.session_state.get("historical_snippet", "")
    forecast_snippet = st.session_state.get("forecast_snippet", "")
    return {
        "forecast_summary": summary,
        "historical_snippet": historical_snippet,
        "forecast_snippet": forecast_snippet
    }

def run_current_events_logic():
    news_summary = st.session_state.get("news_summary", {})
    if isinstance(news_summary, dict):
        return {
            "event_summary": news_summary.get("summary", "No news summary available."),
            "prizm_insight": news_summary.get("prizm_insight", "")
        }
    else:
        # If someone stored just a plain string instead of a dict
        return {
            "event_summary": news_summary or "No news summary available.",
            "prizm_insight": ""
        }


def run_biggest_movers_logic():
    summary = st.session_state.get("biggest_movers_summary", "No movers summary available.")
    dma_df = st.session_state.get("dma_movers")
    prizm_df = st.session_state.get("prizm_movers")
    dma_table = dma_df.to_dict("records") if isinstance(dma_df, pd.DataFrame) else []
    prizm_table = prizm_df.to_dict("records") if isinstance(prizm_df, pd.DataFrame) else []
    return {
        "movers_summary": summary,
        "dma_movers_table": dma_table,
        "prizm_movers_table": prizm_table
    }
