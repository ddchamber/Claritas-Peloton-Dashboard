import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pmdarima import auto_arima
import numpy as np
from dotenv import load_dotenv
import os
import json
from modules.map import render_dma_map
import boto3

# Custom styling
st.markdown("""
<style>
/* Background and font */
body {
    background-color: black;
    font-family: 'Segoe UI', sans-serif;
}

/* Title */
h1, .css-10trblm {  /* Streamlit title default */
    color: #F05A28 !important;
    text-shadow: 1px 1px 3px rgba(240,90,40,0.6);
}

/* Section headers */
.section-title {
    font-size: 22px;
    font-weight: 600;
    color: #F05A28;
    margin-top: 40px;
    text-shadow: 1px 1px 2px rgba(255,255,255,0.15);
}

/* Blue filter labels */
label {
    color: #74C2E1 !important;
    font-weight: bold;
}

/* Divider */
.divider {
    border-top: 2px solid #74C2E1;
    margin: 25px 0;
}
            
/* Custom Filters Styling */
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
            
/* Filters section title in orange */
.filters-title {
    font-size: 30px;
    font-weight: 800;
    color: #F05A28;
    text-shadow: 1px 1px 2px rgba(240,90,40,0.4);
    margin-bottom: 10px;
}

/* Blue labels for toggles and dropdown labels */
.filter-label, label[for="select_all"], label[for="toggle_map"] {
    font-size: 14px;
    color: #74C2E1 !important;
    font-weight: bold;
    margin-top: 8px;
    display: block;
}

/* Make "Show DMA Map" checkbox label blue */
label[for="toggle_map"] {
    color: #74C2E1 !important;
    font-weight: bold;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)

# Page title
st.markdown(
    "<h1 style='font-size: 42px; font-weight: 900;'>"
    "<span style='color: white;'>Peloton </span>"
    "<span style='color: #F05A28; text-shadow: 1px 1px 3px rgba(240,90,40,0.6);'>Forecasting Dashboard</span>"
    "</h1>",
    unsafe_allow_html=True
)


# Load and preprocess data
df = pd.read_csv("PelotonDashboard/data/new_peloton_data_with_region.csv", parse_dates=['date'])

# --- Filters
action_options = df['action'].unique().tolist()
dma_options = df['dma_region'].unique().tolist()

col1, col2 = st.columns([4, 1])

# -- Filters (Right side)
with col2:
    st.markdown("<p class='filters-title'>Filters</p>", unsafe_allow_html=True)

    st.markdown("<p class='filter-label'>Action</p>", unsafe_allow_html=True)
    selected_action = st.selectbox("", ['All'] + action_options, label_visibility="collapsed")
    
    st.markdown("<p class='filter-label'>DMA Region</p>", unsafe_allow_html=True)
    select_all_dmas = st.checkbox("Select All", value=True)

    selected_dmas = st.multiselect(
    "Choose DMAs",
    options=dma_options,
    default=dma_options if select_all_dmas else [],
    key="dma_multiselect",
    disabled=select_all_dmas,
    label_visibility="collapsed"
    )

    show_map = st.checkbox("Show DMA Map", value=False, key="toggle_map")

# -- ARIMA Forecasting (Main left panel)
with col1:
    st.markdown("<div class='section-title'>Forecast</div>", unsafe_allow_html=True)

    filtered_df = df.copy()
    if selected_action != 'All':
        filtered_df = filtered_df[filtered_df['action'] == selected_action]
    if selected_dmas:
        filtered_df = filtered_df[filtered_df['dma_region'].isin(selected_dmas)]

    daily_df = filtered_df.groupby('date')['hitCount'].sum().reset_index()
    daily_df.set_index('date', inplace=True)
    daily_df = daily_df.asfreq('D', fill_value=0)
    train = daily_df['hitCount']
    train_log = np.log1p(train)

    if train_log.empty:
        st.error("No data available to train. Adjust filters.")
        st.stop()

    with st.spinner("Training Auto ARIMA..."):
        model = auto_arima(
            train_log,
            seasonal=True,
            m=7,
            d=1,
            D=1,
            trace=False,
            error_action='ignore',
            suppress_warnings=True,
            stepwise=True
        )

    forecast_log = model.predict(n_periods=30)
    forecast_peloton = np.expm1(forecast_log)
    forecast_index_peloton = pd.date_range(
        start=train.index[-1] + pd.Timedelta(days=1),
        periods=30,
        freq='D'
    )

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(train.index, train, label='Training')
    ax.plot(forecast_index_peloton, forecast_peloton, label='Forecast', color='green')
    all_selected = set(selected_dmas) == set(dma_options)
    dma_label = "All Regions" if all_selected else ", ".join(selected_dmas)
    action_label = selected_action if selected_action != 'All' else "All Actions"
    ax.set_title(f"{action_label} | {dma_label}")
    ax.set_xlabel("Date")
    ax.set_ylabel("HitCount")
    ax.legend()
    st.pyplot(fig)

# --- Competitor Data
competitor_df = pd.read_csv("PelotonDashboard/data/new_competitor_data_with_region.csv")

with col1:
    st.markdown("<div class='section-title'>Competitor Time Series Overview</div>", unsafe_allow_html=True)

    competitor_filtered = competitor_df.copy()
    if selected_action != 'All':
        competitor_filtered = competitor_filtered[competitor_filtered['action'] == selected_action]
    if selected_dmas:
        competitor_filtered = competitor_filtered[competitor_filtered['dma_region'].isin(selected_dmas)]

    competitor_daily = competitor_filtered.groupby('date')['hitcount'].sum().reset_index()
    competitor_daily.set_index('date', inplace=True)
    competitor_daily.index = pd.to_datetime(competitor_daily.index)
    competitor_daily = competitor_daily.asfreq('D', fill_value=0)

    comp_series = competitor_daily['hitcount']
    comp_series_log = np.log1p(comp_series)

    if comp_series_log.empty:
        st.warning("No competitor data available for selected filters.")
        forecast_comp = [0] * 30
        forecast_index_comp = pd.date_range(start=forecast_index_peloton[0], periods=30, freq='D')
    else:
        with st.spinner("Training Auto ARIMA on Competitor Data..."):
            comp_model = auto_arima(
                comp_series_log,
                seasonal=True,
                m=7,
                d=1,
                D=1,
                trace=False,
                error_action='ignore',
                suppress_warnings=True,
                stepwise=True
            )
        forecast_log_comp = comp_model.predict(n_periods=30)
        forecast_comp = np.expm1(forecast_log_comp)
        forecast_index_comp = pd.date_range(start=comp_series.index[-1] + pd.Timedelta(days=1), periods=30, freq='D')

        fig2, ax2 = plt.subplots(figsize=(14, 5))
        ax2.plot(comp_series.index, comp_series, label='Competitor HitCount', color='red')
        ax2.plot(forecast_index_comp, forecast_comp, label='Forecast', color='green')
        ax2.set_title(f"Competitor | {action_label} | {dma_label}")
        ax2.set_xlabel("Date")
        ax2.set_ylabel("HitCount")
        ax2.legend()
        st.pyplot(fig2)

        if show_map:
            st.markdown("<div class='section-title'>DMA Coverage Map</div>", unsafe_allow_html=True)
            st.plotly_chart(render_dma_map(selected_dmas), use_container_width=True)

# --- AI Insight
# Claritas-style blue divider
st.markdown("<div style='border-top: 2px solid #74C2E1; margin: 10px 0 20px 0;'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>AI Insight</div>", unsafe_allow_html=True)

load_dotenv("PelotonDashboard/.env")
client = boto3.client(
    "bedrock-runtime",
    region_name="us-west-2",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN")
)

summary_df = pd.DataFrame({
    "Date": forecast_index_peloton,
    "Forecasted HitCount for Peloton": forecast_peloton,
    "Forecasted HitCount for Competitor": forecast_comp
})
trend_snippet = summary_df.tail(30).to_string(index=False)

messages = [
    {
        "role": "user",
        "content": f"""
You are a senior business analyst. Based on the following 30-day forecast of user hitcount activity, describe the current trend and suggest one action a marketing team could take.

Forecast:
{trend_snippet}
"""
    }
]

response = client.invoke_model(
    modelId="anthropic.claude-3-haiku-20240307-v1:0",
    contentType="application/json",
    accept="application/json",
    body=json.dumps({
        "messages": messages,
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 400,
        "temperature": 0.5
    })
)

result = json.loads(response["body"].read().decode("utf-8"))
st.markdown("**AI Recommendation:**")
st.write(result["content"][0]["text"])

st.session_state["time_series_summary"] = result["content"][0]["text"]
st.session_state["trend_snippet"] = trend_snippet  