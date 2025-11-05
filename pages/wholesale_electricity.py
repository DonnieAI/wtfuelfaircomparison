import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import os
from datetime import datetime

st.set_page_config(page_title="Dashboard", layout="wide")
from utils import apply_style_and_logo

apply_style_and_logo()


import streamlit as st
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px 
from pathlib import Path
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(page_title="Dashboard", layout="wide")
from utils import apply_style_and_logo
apply_style_and_logo()


palette_blue = [
    "#A7D5F2",  # light blue
    "#94CCE8",
    "#81C3DD",
    "#6FBBD3",
    "#5DB2C8",
    "#A9DEF9",  # baby blue
]

palette_green = [
    "#6DC0B8",  # pastel teal
    "#7DCFA8",
    "#8DDC99",
    "#9CE98A",
    "#ABF67B",
    "#C9F9D3",  # mint green
    "#C4E17F",  # lime green
]

palette_other = [
    "#FFD7BA",  # pastel orange
    "#FFE29A",  # pastel yellow
    "#FFB6C1",  # pastel pink
    "#D7BDE2",  # pastel purple
    "#F6C6EA",  # light rose
    "#F7D794",  # peach
    "#E4C1F9",  # lavender
]


#✅------------------------DATA EXTRACTION-----------------------------------------------------

def load_latest_ember_csv(directory="."):
    """
    Loads the most recent CSV file in the directory matching the pattern: *_EMBER_wholesale_el_prices.csv
    Assumes filename starts with YYYY-MM-DD.
    """
    files = [
        f for f in os.listdir(directory)
        if "EMBER_wholesale_el_prices" in f and f.endswith(".csv")
    ]

    if not files:
        raise FileNotFoundError("No EMBER_wholesale_el_prices CSV files found.")

    # Parse date prefix from filename and sort
    dated_files = []
    for f in files:
        try:
            date_str = f.split("_")[0]  # get the '2025-10-31' part
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            dated_files.append((file_date, f))
        except ValueError:
            continue  # Skip files with invalid date format

    if not dated_files:
        raise ValueError("No valid dated EMBER files found.")

    # Get the most recent file by date
    latest_file = sorted(dated_files, reverse=True)[0][1]

    print(f"Loading: {latest_file}")  # Optional for debugging
    return pd.read_csv(os.path.join(directory, latest_file))
df_ember = load_latest_ember_csv("data")  # or just "." for current folder
country_selection=(
                    df_ember["Country"]
                   .unique()
                   .tolist()
)

def compute_monthly_min_max(df, price_col):
    """
    Compute historical monthly min and max values across all years.
    
    Returns a DataFrame with:
        Month | Min | Max
    """
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.dropna(subset=[price_col])
    
    df["Month"] = df["Date"].dt.month
    monthly_stats = (
        df.groupby("Month")[price_col]
        .agg(Min="min", Max="max")
        .reset_index()
    )
    return monthly_stats

el_prices_df=df_ember[["Date", "Price (EUR/MWhe)"]]
el_prices_bands_df = compute_monthly_min_max(df=el_prices_df, price_col="Price (EUR/MWhe)")
# OPTIONAL: Exclude 'EU' if you don't want it affecting min/max
#df_prices = df_ember[df_ember["ISO3 Code"] != "EU"].copy()
# Compute min and max price per date
min_max_df = df_ember.groupby("Date")["Price (EUR/MWhe)"].agg(["min", "max"]).reset_index()
min_max_df.rename(columns={"min": "MIN", "max": "MAX"}, inplace=True)
# Merge back into original DataFrame
df = df_ember.merge(min_max_df, on="Date", how="left")

#----------------------------------------------------
st.markdown("---")  # horizontal line separator
#-----------------------------------------------------------------------------------------------------

st.title("🔎 Wholesale electricity prices")
st.markdown("""
            ### 📊 Wholesales Electricity Prices
            
            """)
st.markdown(""" 
            source: EMEBER - daily data 
                        """)


selected_country = st.selectbox(
    "Select a Country or an Aggregate (Total World as default)",  # label
    options=country_selection,
    index=country_selection.index("EU")  # 👈 set default selection by index
)

# **************************************************************************************
#selection for the different energy in EJ
df['Date'] = pd.to_datetime(df['Date'])  # ✅ Ensure it's datetime
df_filtered = (
    df
    .query("Country == @selected_country")
    .set_index("Date")
    .sort_index()
    .assign(Weekly_Ave=lambda x:x["Price (EUR/MWhe)"].resample("W").transform("mean"))
    .assign(Monthly_Ave=lambda x:x["Price (EUR/MWhe)"].resample("ME").transform("mean"))
    .assign(Yearly_Ave=lambda x:x["Price (EUR/MWhe)"].resample("Y").transform("mean"))
   
)
# **************************************************************************************

# Create subplot: 2 rows, shared x-axis
fig = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.12,
    row_heights=[0.7, 0.3],
    subplot_titles=(
        f" Day-Ahead Prices Electricity[EUR/MWhe] - {selected_country}",
        "Weekly - Monthly - Yearly average  [EUR/MWhe]"
    )
)

# Trace 1: Selected Country
fig.add_trace(
    go.Scatter(
        x=df_filtered.index,
        y=df_filtered["Price (EUR/MWhe)"],
        mode="lines+markers",
        name=f"{selected_country}",
        line=dict(
            color=palette_blue[4],
            width=1,
            dash="solid"
        ),
        marker=dict(
            color=palette_blue[4],
            size=3,
            symbol="circle",
            line=dict(width=1, color="white")
        )
    ),
    row=1,
    col=1
)

# Area between MAX and MIN (shaded range)
fig.add_trace(
    go.Scatter(
        x=df_filtered.index,
        y=df_filtered["MAX"],
        mode="lines",
        name="Max Price",
        line=dict(color="rgba(255, 0, 0, 0.3)", width=0),  # transparent line
        showlegend=False
    ),
    row=1,
    col=1
)

fig.add_trace(
    go.Scatter(
        x=df_filtered.index,
        y=df_filtered["MIN"],
        mode="lines",
        name="Price Range (MIN–MAX)",
        fill='tonexty',  # ← key!
        fillcolor='rgba(255, 255, 0, 0.2)',  # yellowish fill
        line=dict(color="rgba(0,0,0,0)"),  # hide line
        showlegend=True
    ),
    row=1,
    col=1
)


# Weekly Average: fine-grained, thin line with small markers
fig.add_trace(
    go.Scatter(
        x=df_filtered.index,
        y=df_filtered["Weekly_Ave"],
        mode="lines+markers",
        name=f"{selected_country} | Weekly Avg",
        line=dict(
            color=palette_green[0],
            width=1.5,
            dash="dot"  # dotted to imply granularity
        ),
        marker=dict(
            color=palette_green[0],
            size=4,
            symbol="diamond",
            line=dict(width=1, color="white")
        ),
        opacity=0.8
    ),
    row=2,
    col=1
)

# Monthly Average: thicker line, semi-transparent
fig.add_trace(
    go.Scatter(
        x=df_filtered.index,
        y=df_filtered["Monthly_Ave"],
        mode="lines+markers",
        name=f"{selected_country} | Monthly Avg",
        line=dict(
            color=palette_green[1],
            width=3,
            dash="solid"
        ),
        marker=dict(
            color=palette_green[1],
            size=5,
            symbol="circle",
            line=dict(width=1, color="white")
        ),
        opacity=0.6
    ),
    row=2,
    col=1
)

# Yearly Average: bold line, low opacity (background trend)
fig.add_trace(
    go.Scatter(
        x=df_filtered.index,
        y=df_filtered["Yearly_Ave"],
        mode="lines",
        name=f"{selected_country} | Yearly Avg",
        line=dict(
            color=palette_other[3],
            width=4,
            dash="dash"
        ),
        opacity=0.4
    ),
    row=2,
    col=1
)

fig.update_layout(height=1000) 
# Show Plotly chart
st.plotly_chart(fig, use_container_width=True, key="Twholesalre")


