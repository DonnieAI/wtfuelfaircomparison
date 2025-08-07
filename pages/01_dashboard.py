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


# Step 1: Create a multi-level Y-axis by combining CATEGORY and FUELS
y_labels = [df_fuel_prices["CATEGORY"].astype(str), df_fuel_prices["FUELS"]]
# Step 2: Create the figure

fig = go.Figure()

# Step 3: Add stacked bar components
fig.add_bar(
    y=y_labels,
    x=df_fuel_prices["ENERGY_PRICE"],
    orientation='h',
    name="ENERGY PRICE EUR/MWh",
    marker=dict(color="#00274d")  # single color
)

# Step 4: Update layout for stacked bars
fig.update_layout(
    title="Energy Prices Dashboard ",
    xaxis_title="EUR/MWh",
    yaxis_title="Category / Fuel Type",
    bargap=0.25,  # default is 0.1 → increase spacing between categories
    barmode="relative",  # stacking mode
    template="plotly_dark",
    paper_bgcolor="#005680",
    plot_bgcolor="#005680",
    
    legend_title="Components",
    height=700,   # increase height
    width=1000,   # optional, or omit to use Streamlit's container width
    xaxis=dict(
                gridcolor="white",
                gridwidth=1,      # thinner, more visible
                zeroline=False,
                showgrid=True,    # explicitly enable grid
                tickcolor="white",
                linecolor="white"
                ),
    yaxis=dict(
                gridcolor="white",
                gridwidth=1,
                zeroline=False,
                showgrid=True,
                tickcolor="white",
                linecolor="white"
)
)

# Show Plotly chart
st.plotly_chart(fig, use_container_width=True)