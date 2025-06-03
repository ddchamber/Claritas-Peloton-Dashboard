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

    st.markdown("<p class='filter-label'>Historical Viewing Period (Months)</p>", unsafe_allow_html=True)
    months_to_show = st.number_input("Months", min_value=1, max_value=12, value=3, step=1, label_visibility="collapsed")
    days_to_show = months_to_show * 28

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
    recent_train = train.last(f"{days_to_show}D")
    ax.plot(recent_train.index, recent_train, label='Peloton HitCount')
    ax.plot(forecast_index_peloton, forecast_peloton, label='Forecast', color='green')
    all_selected = set(selected_dmas) == set(dma_options)
    dma_label = "All Regions" if all_selected else ", ".join(selected_dmas)
    action_label = selected_action if selected_action != 'All' else "All Actions"
    ax.set_title(f"Peloton |{action_label} | {dma_label}")
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
        recent_comp = comp_series.last(f"{days_to_show}D")
        ax2.plot(recent_comp.index, recent_comp, label='Competitor HitCount')
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

peloton_last_30 = train.tail(30)
if not comp_series.empty:
    comp_last_30 = comp_series.tail(30)
else:
    # If no competitor data, create dummy data with zeros
    comp_last_30 = pd.Series([0] * 30, index=peloton_last_30.index)

# Create comprehensive summary with both historical and forecast data
historical_df = pd.DataFrame({
    "Date": peloton_last_30.index,
    "Historical HitCount for Peloton": peloton_last_30.values,
    "Historical HitCount for Competitor": comp_last_30.values
})

forecast_df = pd.DataFrame({
    "Date": forecast_index_peloton,
    "Forecasted HitCount for Peloton": forecast_peloton,
    "Forecasted HitCount for Competitor": forecast_comp
})

# Combine historical and forecast data
combined_summary = pd.concat([
    historical_df.add_suffix('_Historical'),
    forecast_df.add_suffix('_Forecast')
], axis=0).reset_index(drop=True)

# Create a more readable format for the AI
historical_snippet = historical_df.to_string(index=False)
forecast_snippet = forecast_df.to_string(index=False)

messages = [
    {
        "role": "user",
        "content": f"""
<Role>
You are a senior fitness industry analyst. Your task is to identify the biggest industry trend from Peloton vs. competitor engagement data and explain what it means for the market's future.
</Role>

<Core Focus>
Look for the one major trend that tells the story of how the fitness industry is evolving right now.
</Core Focus>

 <Analysis Focus> 
 **TREND IDENTIFICATION**: What's the dominant pattern? - Momentum shifts, competitive dynamics, market evolution signals
INDUSTRY IMPACT: What does this mean for the broader fitness market?
Market maturation, consumer behavior changes, competitive positioning shifts
STRATEGIC IMPLICATIONS: What should Peloton do about it?
Immediate opportunities, defensive moves, positioning adjustments
 </Analysis Focus>

<Required Output Structure>
### **Industry Trend**:
2-3 concise sentences identifying the dominant trend for:

1. **Peloton's Competitive Position**: Comment on market share shifts, recent momentum, or performance relative to expectations.
2. **Broader Fitness Industry Evolution**: Describe high-level consumer behavior trends, technological adoption patterns, or signs of market maturation.

### **Evidence**:
3-4 bullet points with specific proof from the data:
- Use percentage changes, growth/decline rates, or comparative metrics between Peloton and its competitor.
- Highlight timeline-based patterns (e.g., week-over-week or month-over-month changes).
- Call out any inflection points, convergence/divergence, or trajectory mismatches in forecasts.

### **Market Implications**:
Analyze what the trend means for the fitness landscape:
- **Consumer Behavior**: What are users expecting or prioritizing now?
- **Competitive Dynamics**: How is market power shifting and why?
- **Industry Stage**: Does this signal disruption, consolidation, or maturity?
- **Strategic Inflection Point**: What's the next major decision the industry must make?

</Required Output Structure>

Use the Historical Data representing the previous 30 days hit counts and the Forecasted Data representing the next 30 days hit counts to generate a comprehensive analysis of Peloton's market position and future strategy using the required output structure.
Take note of the detail in the Example and use that to guide your output for using the data given on the Peloton and Competitor engagement data below.

Historical Engagement Data (Last 30 Days) {historical_snippet}
Forecasted Engagement Data (Next 30 Days) {forecast_snippet}

Focus more on the trends than the numbers because they are not to scale. and get strait to the point of the analysis.
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
        "max_tokens": 2048,
        "temperature": 0.0
    })
)

result = json.loads(response["body"].read().decode("utf-8"))
st.markdown("**AI Recommendation:**")
st.write(result["content"][0]["text"])

st.session_state["time_series_summary"] = result["content"][0]["text"]
st.session_state["historical_snippet"] = historical_snippet
st.session_state["forecast_snippet"] = forecast_snippet