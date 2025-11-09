import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Dashboard", layout="wide")
from utils import apply_style_and_logo

apply_style_and_logo()

st.title("🔎 Fuels Price Energy Based Comparison Overview")
st.markdown("""
            ### 📊 Fuels and Commodity enrgy based comparison
            #### ⚠️ Prices are adjusted for energy content, but data for different fuels come from varying dates. Values are not strictly simultaneous.
            
            """)
st.markdown(""" 
            source: Wavetransition - (data sources available in methodology page)
                        """)

# Example DataFrame (replace with your df_fuel_prices)
df_fuel_prices=pd.read_csv("data/table_summary.csv", parse_dates=["DATE"])
df_fuel_prices["CATEGORY"] = df_fuel_prices["CATEGORY"].astype("category")


# Your color palette
pastel_blue_green = [
    "#A7D5F2", "#94CCE8", "#81C3DD", "#6FBBD3", "#5DB2C8",
    "#6DC0B8", "#7DCFA8", "#8DDC99", "#9CE98A", "#ABF67B"
]

fig = go.Figure()

# Group by CATEGORY
categories = df_fuel_prices["CATEGORY"].unique()

# Map CATEGORY to a color
color_map = {cat: pastel_blue_green[i % len(pastel_blue_green)] for i, cat in enumerate(categories)}

# Add one bar trace per CATEGORY
for cat in categories:
    subset = df_fuel_prices[df_fuel_prices["CATEGORY"] == cat]
    y_labels = [subset["CATEGORY"].astype(str), subset["FUELS"]]
    
    fig.add_bar(
        y=y_labels,
        x=subset["ENERGY_PRICE"],
        orientation='h',
        name=cat,
        marker=dict(color=color_map[cat])
    )

# Layout styling (same as yours)
fig.update_layout(
    title="Energy Prices Dashboard",
    xaxis_title="EUR/MWh",
    yaxis_title="Category / Fuel Type",
    bargap=0.50,
    barmode="relative",
    template="plotly_dark",
    paper_bgcolor="#005680",
    plot_bgcolor="#005680",
    legend_title="CATEGORY",
    height=1000,
    width=1000,
    xaxis=dict(
        gridcolor="grey",
        gridwidth=1,
        zeroline=False,
        showgrid=True,
        tickcolor="grey",
        linecolor="grey",
        tickfont=dict(size=12),
        title=dict(
            text="EUR/MWh",
            font=dict(size=20)
        )
    ),
    yaxis=dict(
        gridcolor="grey",
        gridwidth=1,
        zeroline=False,
        showgrid=True,
        tickcolor="grey",
        linecolor="grey",
        tickfont=dict(size=12),
        title=dict(
            text="Category / Fuel Type",
            font=dict(size=14)
        )
    ),
)

# Show Plotly chart
st.plotly_chart(fig, use_container_width=True)