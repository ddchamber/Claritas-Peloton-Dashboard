import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from modules.biggest_mover_functions import dma_change, prizm_change

# --- Page Setup ---
st.set_page_config(layout="wide")
st.markdown("""
<style>
/* Base */
body {
    background-color: black;
    font-family: 'Segoe UI', sans-serif;
}
h1, h2, h3, .css-10trblm {
    color: #F05A28 !important;
    text-shadow: 1px 1px 3px rgba(240,90,40,0.6);
}
.section-title {
    font-size: 22px;
    font-weight: 600;
    color: #F05A28;
    margin-bottom: 10px;
}
/* Sidebar and inputs */
label, .stSelectbox label, .stDateInput label, .stButton>button {
    color: #74C2E1 !important;
    font-weight: bold;
}
/* DataFrame Container */
.css-1d391kg, .css-1r6slb0, .css-1v0mbdj {
    background-color: #1e1e1e;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("Biggest Movers")

# --- Load data ---
@st.cache_data
def load_data():
    df_peloton_grouped = pd.read_csv('PelotonDashboard/data/peloton_dma_grouped.csv')
    df_peloton_grouped['date'] = pd.to_datetime(df_peloton_grouped['date'])

    df_peloton = pd.read_csv('PelotonDashboard/data/peloton_dma.csv')
    df_peloton['date'] = pd.to_datetime(df_peloton['date'])

    df_prizm = pd.read_excel("PelotonDashboard/data/PRIZM2DMA.xlsx")
    cols_to_pct = [col for col in df_prizm.columns if col != 'DMA_GCODE']
    row_sums = df_prizm[cols_to_pct].sum(axis=1)
    df_prizm[cols_to_pct] = df_prizm[cols_to_pct].div(row_sums, axis=0) * 100

    return df_peloton_grouped, df_peloton, df_prizm

df_peloton_grouped, df_peloton, df_prizm = load_data()

START_LIMIT = pd.to_datetime("2024-01-01")
END_LIMIT = pd.to_datetime("2025-04-07")

# --- Layout: 4/5 content, 1/5 filters ---
content_col, filter_col = st.columns([4, 1])

with filter_col:
    st.markdown("### Filters")
    start_date = st.date_input("Select Start Date", value=START_LIMIT, min_value=START_LIMIT, max_value=END_LIMIT)

    action = st.selectbox(
        "Select Action Type",
        options=["Total Activity", "View", "Click", "Purchase"],
        index=0
    )

    run_analysis = st.button("Run Analysis")
    show_map = st.checkbox("Show DMA Map", value=False, key="toggle_map")

with content_col:
    if run_analysis:
        with st.spinner("Calculating..."):
            dma_results = dma_change(
                df=df_peloton_grouped,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=None,
                action=None if action == "Total Activity" else action or None
            ).head(8)  

            prizm_results = prizm_change(
                df_peloton=df_peloton,
                df_prizm=df_prizm,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=None,
                action=None if action == "Total Activity" else action or None
            ).head(8) 


        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<div style='color:#D93A32; font-size:22px; font-weight:600; margin-bottom:10px;'>DMA Movers</div>", unsafe_allow_html=True)
            dma_display = dma_results[["dma", "start_count", "end_count", "weighted_pct_change"]].rename(columns={
                "dma": "Region",
                "start_count": "Start Count",
                "end_count": "End Count",
                "weighted_pct_change": "Percent Change"
            })
            st.dataframe(
                dma_display[["Region" ,"Percent Change", "Start Count", "End Count"]]
                    .style.format({"Percent Change": "{:.1f}%"})
                    .set_properties(**{
                        'background-color': '#1e1e1e',
                        'color': 'white',
                        'border-color': 'white'
                    }),
                use_container_width=True
            )


            top_dma = dma_results.head(8)
            labels = top_dma["dma"]
            x = range(len(labels))

            fig, ax = plt.subplots(figsize=(7, 4))
            ax.bar([i - 0.2 for i in x], top_dma['start_count'], width=0.4, label='Start', color='#74C2E1')
            ax.bar([i + 0.2 for i in x], top_dma['end_count'], width=0.4, label='End', color='#D93A32')

            # Add % change labels above bar pairs
            for i, pct in enumerate(top_dma['weighted_pct_change']):
                y = max(top_dma['start_count'].iloc[i], top_dma['end_count'].iloc[i])
                ax.text(i, y + 0.01 * y, f"{pct:.1f}%", ha='center', color='white', fontsize=9)

            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=45, ha='right', color='white')
            ax.set_ylabel("Value", color='white')
            ax.set_title("Top 8 DMA Start vs End", color='white')
            ax.tick_params(colors='white')
            ax.legend(facecolor='#1e1e1e', edgecolor='white', labelcolor='white')
            fig.patch.set_facecolor('#1e1e1e')
            ax.set_facecolor('#1e1e1e')

            st.pyplot(fig)


        with col2:
            st.markdown("<div style='color:#D93A32; font-size:22px; font-weight:600; margin-bottom:10px;'>PRIZM Segment Movers</div>", unsafe_allow_html=True)
            prizm_display = prizm_results[["segment", "start_count", "end_count", "weighted_pct_change"]].rename(columns={
                "segment": "Segment",
                "start_count": "Start Count",
                "end_count": "End Count",
                "weighted_pct_change": "Percent Change"
            })
            st.dataframe(
                prizm_display[["Segment","Percent Change", "Start Count", "End Count"]]
                    .style.format({"Percent Change": "{:.1f}%"})
                    .set_properties(**{
                        'background-color': '#1e1e1e',
                        'color': 'white',
                        'border-color': 'white'
                    }),
                use_container_width=True
            )



            top_prizm = prizm_results.head(8)
            labels = top_prizm["segment"]
            x = range(len(labels))

            fig2, ax2 = plt.subplots(figsize=(7, 4))
            ax2.bar([i - 0.2 for i in x], top_prizm['start_count'], width=0.4, label='Start', color='#74C2E1')
            ax2.bar([i + 0.2 for i in x], top_prizm['end_count'], width=0.4, label='End', color='#D93A32')

            # Add % change labels
            for i, pct in enumerate(top_prizm['weighted_pct_change']):
                y = max(top_prizm['start_count'].iloc[i], top_prizm['end_count'].iloc[i])
                ax2.text(i, y + 0.01 * y, f"{pct:.1f}%", ha='center', color='white', fontsize=9)

            ax2.set_xticks(x)
            ax2.set_xticklabels(labels, rotation=45, ha='right', color='white')
            ax2.set_ylabel("Value", color='white')
            ax2.set_title("Top 8 PRIZM Segments Start vs End", color='white')
            ax2.tick_params(colors='white')
            ax2.legend(facecolor='#1e1e1e', edgecolor='white', labelcolor='white')
            fig2.patch.set_facecolor('#1e1e1e')
            ax2.set_facecolor('#1e1e1e')

            st.pyplot(fig2)


        if show_map:
            st.markdown("<div class='section-title'>DMA Map</div>", unsafe_allow_html=True)

            # Call your existing map function
            from modules.map import render_dma_map

            fig_map = render_dma_map(top_dma["dma"].tolist())
            st.plotly_chart(fig_map, use_container_width=True)


# --- AI Insight
# Claritas-style blue divider
st.markdown("<div style='border-top: 2px solid #74C2E1; margin: 10px 0 20px 0;'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>AI Insight</div>", unsafe_allow_html=True)

def summarize_movers(start_date, action_type, dma_df, prizm_df):
    return [
        {
            "role": "user",
            "content": f"""
You are an expert marketing and business intelligence analyst.

The following data reflects a comparison between activity levels starting from {start_date} for the action type "{action_type}". Metrics represent percent changes in engagement across DMA regions and PRIZM consumer segments.

Top DMA Movers:
{dma_df.to_markdown(index=False)}

Top PRIZM Segment Movers:
{prizm_df.to_markdown(index=False)}

Please write an executive summary that includes:
- The regions and segments with the largest gains and losses
- Any geographic or demographic trends
- Suggestions on how Peloton should respond to these shifts
"""
        }
    ]

import boto3
import json
from dotenv import load_dotenv
import os

# Format the top 5 rows of each mover DataFrame (you can adjust this number)
dma_summary_df = dma_results[["dma", "start_count", "end_count", "weighted_pct_change"]].rename(columns={
    "dma": "Region",
    "start_count": "Start Count",
    "end_count": "End Count",
    "weighted_pct_change": "Adjusted Percent Change"
}).head(5)

prizm_summary_df = prizm_results[["segment", "start_count", "end_count", "weighted_pct_change"]].rename(columns={
    "segment": "Segment",
    "start_count": "Start Count",
    "end_count": "End Count",
    "weighted_pct_change": "Adjusted Percent Change"
}).head(5)

# Build the Claude message prompt
message = summarize_movers(
    start_date=start_date.strftime("%Y-%m-%d"),
    action_type=action,
    dma_df=dma_summary_df,
    prizm_df=prizm_summary_df
)

client = boto3.client(
    "bedrock-runtime",
    region_name="us-west-2",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN")
)

# Claude API call
response = client.invoke_model(
    modelId="anthropic.claude-3-haiku-20240307-v1:0",
    contentType="application/json",
    accept="application/json",
    body=json.dumps({
        "messages": message,  # <-- Now a list of { role, content } objects
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2048,
        "temperature": 0.5
    })
)

result = json.loads(response["body"].read().decode("utf-8"))

st.write(result["content"][0]["text"])

st.session_state["biggest_movers_summary"] = result["content"][0]["text"]
st.session_state["dma_movers"] = dma_summary_df
st.session_state["prizm_movers"] = prizm_summary_df
