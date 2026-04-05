import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import os
from datetime import datetime
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px 
from pathlib import Path
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(page_title="Dashboard", layout="wide")
from utils import apply_style_and_logo

apply_style_and_logo()

#🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄
latest_date=pd.Timestamp("2026-03-30")
latest_date_str=latest_date.strftime("%Y-%m-%d")
#🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄

#-----------------------------------------------------
#---------GRAPHICS------------------------------------
#-----------------------------------------------------

import tomllib

with open(".streamlit\palettes.toml", "rb") as f:
    palettes = tomllib.load(f)

with open(".streamlit\charts.toml", "rb") as f:
    chart_cfg = tomllib.load(f)


palette_blue = palettes["PALETTE_BLUE"]
palette_green = palettes["PALETTE_GREEN"]
palette_other = palettes["PALETTE_OTHER"]
palette_visible = palettes["PALETTE_VISIBLE"]
palette_top=palettes["PALETTE_TOP"]

line1 = chart_cfg["line"]["line1"]
line2 = chart_cfg["line"]["line2"]
line3 = chart_cfg["line"]["line3"]
line4 = chart_cfg["line"]["line4"]
layout_cfg = chart_cfg["layout"]





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
#df_ember = load_latest_ember_csv("data")  # or just "." for current folder
df_ember=pd.read_csv(f"data/{latest_date_str}_EMBER_daily_wholesale_el_prices.csv")

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
#✅--------------------------------------------------------------------
#1️⃣1️⃣1️⃣1️⃣1️⃣1️⃣1️⃣1️⃣1️⃣1️⃣1️⃣1️⃣1️⃣1️⃣1️⃣1️⃣1️⃣1️⃣1️⃣1️⃣1️⃣1️⃣1️⃣1️⃣1️⃣1️⃣1️⃣1️⃣1️⃣1️
#-----------------------------------------------------------------------------------------------------
st.title("⚡ Wholesale Electricity Prices - Trends | 🇪🇺")
#-----------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#-----------------------------------------------------
st.markdown("""
            ### 📊 Daily Wholesales Electricity Prices
            
            """)
st.caption(f"source: EMEBER - daily data - up to {latest_date_str}")
                        
country_selection = (
    df["Country"]
    .dropna()
    .sort_values()
    .unique()
    .tolist()
)

selected_country = st.selectbox(
    "Select a Country or an Aggregate (EU as default)",  # label
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
# =========================================================
# FIGURE 1 — Daily price + min/max band
# =========================================================
fig_daily = go.Figure()

# Max boundary first
fig_daily.add_trace(
    go.Scatter(
        x=df_filtered.index,
        y=df_filtered["MAX"],
        mode="lines",
        name="Max",
        line=dict(width=0),
        hoverinfo="skip",
        showlegend=False
    )
)

# Min boundary with fill to previous trace
fig_daily.add_trace(
    go.Scatter(
        x=df_filtered.index,
        y=df_filtered["MIN"],
        mode="lines",
        name="Min–Max Range",
        fill="tonexty",
        fillcolor="rgba(100, 149, 237, 0.15)",
        line=dict(width=0),
        hoverinfo="skip"
    )
)

# Main daily price
fig_daily.add_trace(
    go.Scatter(
        x=df_filtered.index,
        y=df_filtered["Price (EUR/MWhe)"],
        mode="lines",
        name=selected_country,
        line=dict(
            color=palette_blue[4],
            width=2.2,
            dash="solid"
        ),
        hovertemplate=(
            "<b>Date</b>: %{x|%d %b %Y}<br>"
            "<b>Price</b>: %{y:.2f} EUR/MWhe"
            "<extra></extra>"
        )
    )
)

fig_daily.update_layout(
    title=f"Day-Ahead Electricity Prices [EUR/MWhe] — {selected_country}",
    height=520,
    template="plotly_white",
    hovermode="x unified",
    margin=dict(l=40, r=20, t=70, b=40),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    ),
    xaxis=dict(
        title="Date",
        showgrid=False,
        tickformat="%b %Y"
    ),
    yaxis=dict(
        title="Price [EUR/MWhe]",
        showgrid=True,
        gridcolor="rgba(0,0,0,0.08)",
        zeroline=False
    )
)


# =========================================================
# FIGURE 2 — Weekly / Monthly / Yearly averages
# =========================================================
fig_avg = go.Figure()

# Weekly average
fig_avg.add_trace(
    go.Scatter(
        x=df_filtered.index,
        y=df_filtered["Weekly_Ave"],
        mode="lines",
        name="Weekly Avg",
        line=dict(
            color=palette_green[0],
            width=2,
            dash="dot"
        ),
        hovertemplate=(
            "<b>Date</b>: %{x|%d %b %Y}<br>"
            "<b>Weekly Avg</b>: %{y:.2f} EUR/MWhe"
            "<extra></extra>"
        )
    )
)

# Monthly average
fig_avg.add_trace(
    go.Scatter(
        x=df_filtered.index,
        y=df_filtered["Monthly_Ave"],
        mode="lines",
        name="Monthly Avg",
        line=dict(
            color=palette_green[1],
            width=3,
            dash="solid"
        ),
        hovertemplate=(
            "<b>Date</b>: %{x|%d %b %Y}<br>"
            "<b>Monthly Avg</b>: %{y:.2f} EUR/MWhe"
            "<extra></extra>"
        )
    )
)

# Yearly average
fig_avg.add_trace(
    go.Scatter(
        x=df_filtered.index,
        y=df_filtered["Yearly_Ave"],
        mode="lines",
        name="Yearly Avg",
        line=dict(
            color=palette_other[3],
            width=3.5,
            dash="dash"
        ),
        hovertemplate=(
            "<b>Date</b>: %{x|%d %b %Y}<br>"
            "<b>Yearly Avg</b>: %{y:.2f} EUR/MWhe"
            "<extra></extra>"
        )
    )
)

fig_avg.update_layout(
    title=f"Averages Comparison — {selected_country}",
    height=520,
    template="plotly_white",
    hovermode="x unified",
    margin=dict(l=40, r=20, t=70, b=40),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0
    ),
    xaxis=dict(
        title="Date",
        showgrid=False,
        tickformat="%b %Y"
    ),
    yaxis=dict(
        title="Average Price [EUR/MWhe]",
        showgrid=True,
        gridcolor="rgba(0,0,0,0.08)",
        zeroline=False
    )
)


# =========================================================
# STREAMLIT OUTPUT
# =========================================================
st.plotly_chart(fig_daily, use_container_width=True, key="wholesale_daily_chart")
st.plotly_chart(fig_avg, use_container_width=True, key="wholesale_avg_chart")

#-------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#-------------------------------------------------------------------------
#2️⃣2️⃣2️⃣2️⃣2️⃣2️⃣2️⃣2️⃣2️⃣2️⃣2️⃣2️⃣2️⃣2️⃣2️⃣2️⃣2️⃣2️⃣2️⃣2️⃣2️⃣2️⃣2️⃣2️⃣2️⃣2️⃣2️⃣2️⃣2️⃣
st.markdown("""
            ### 📈 Wholesale prices | 🇪🇺 - single country historical trend
            """)
st.caption(f"source: EMEBER - daily data - up to {latest_date_str}")
                        

country_selection = (
    df["Country"]
    .dropna()
    .sort_values()
    .unique()
    .tolist()
)

selected_country_fig2 = st.selectbox(
    "Select a Country or an Aggregate (EU as default)",
    options=country_selection,
    index=country_selection.index("EU"),
    key="weekly_country_compare_selectbox"
)

# --- Safety check ---
if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
    df["Date"] = pd.to_datetime(df["Date"])

# --- Keep needed columns only ---
df_base = (
    df.loc[:, ["Date", "Country", "Price (EUR/MWhe)"]]
    .dropna(subset=["Date", "Country", "Price (EUR/MWhe)"])
    .copy()
)

# --- Weekly average by country ---
df_weekly = (
    df_base
    .sort_values("Date")
    .set_index("Date")
    .groupby("Country")["Price (EUR/MWhe)"]
    .resample("W")
    .mean()
    .reset_index()
    .rename(columns={"Price (EUR/MWhe)": "Weekly_Ave"})
)

# --- Selected country ---
selected_weekly = (
    df_weekly
    .query("Country == @selected_country_fig2")
    .sort_values("Date")
    .copy()
)

# --- EU benchmark ---
eu_weekly = (
    df_weekly
    .query("Country == 'EU'")
    .sort_values("Date")
    .copy()
)

# --- Normalize to first value = 1 ---
selected_weekly["Weekly_Ave_norm"] = (
    selected_weekly["Weekly_Ave"] / selected_weekly["Weekly_Ave"].iloc[0]
)

eu_weekly["Weekly_Ave_norm"] = (
    eu_weekly["Weekly_Ave"] / eu_weekly["Weekly_Ave"].iloc[0]
)

# --- Plot ---
fig_weekly_norm = go.Figure()

fig_weekly_norm.add_trace(
    go.Scatter(
        x=eu_weekly["Date"],
        y=eu_weekly["Weekly_Ave_norm"],
        mode="lines",
        name="EU | Normalized",
        line=dict(
            color=palette_top[0],
            width=line1["width"],
            dash=line1["dash"],
            shape=line1["shape"],
        ),
    )
)

if selected_country_fig2 != "EU":
    fig_weekly_norm.add_trace(
        go.Scatter(
            x=selected_weekly["Date"],
            y=selected_weekly["Weekly_Ave_norm"],
            mode="lines",
            name=f"{selected_country_fig2} | Normalized",
            line=dict(
                color=palette_visible[0],
                width=line2["width"],
                dash=line2["dash"],
                shape=line2["shape"],
            ),
        )
    )

fig_weekly_norm.update_layout(
    title=f"Normalized weekly average electricity prices | EU vs {selected_country_fig2}",
    height=600,
    showlegend=True,
    paper_bgcolor="#005680",
    plot_bgcolor="#005680",
    font=dict(size=14, color="#ffffff"),
    legend_title="Series",
)

fig_weekly_norm.update_xaxes(
    title_text="Date",
    color="white",
    gridcolor="rgba(255,255,255,0.1)"
)

fig_weekly_norm.update_yaxes(
    title_text="Index (first week = 1)",
    color="white",
    gridcolor="rgba(255,255,255,0.1)"
)

st.plotly_chart(fig_weekly_norm, use_container_width=True, key="weekly_comparison_chart_norm")
