import streamlit as st
import pandas as pd
import plotly.express as px
import json

def render_dma_map(selected_dmas):
    dma_df = pd.read_csv("PelotonDashboard/data/dma_demo_region.csv", dtype={"dma_code": str})
    dma_df["dma_region"] = dma_df["dma_region"].str.strip()
    dma_df["geo_dma"] = dma_df["geo_dma"].str.strip()
    if selected_dmas:
        dma_df = dma_df[dma_df["dma_region"].isin(selected_dmas)]

    with open("PelotonDashboard/data/nielsen_dma.json") as f:
        dma_geojson = json.load(f)
    for feature in dma_geojson["features"]:
        feature["id"] = str(feature["properties"]["dma"])

    fig = px.choropleth_mapbox(
        dma_df,
        geojson=dma_geojson,
        locations="dma_code",
        featureidkey="properties.dma",
        color="dma_region",
        hover_name="geo_dma",
        hover_data={"dma_region": True, "dma_code": True},
        mapbox_style="carto-positron",
        center={"lat": 39.5, "lon": -98.35},
        zoom=2.3,
        opacity=0.75,
        height=500
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig
