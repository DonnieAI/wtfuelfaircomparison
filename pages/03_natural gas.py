"""
🔥natural gas monthly basies extract form WorldBank 
#cd C:\WT\WT_OFFICIAL_APPLICATIONS_REPOSITORY\WT_FAIR_FUEL_COMPARE
"""
import streamlit as st
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px 
import pandas as pd
from pathlib import Path
from plotly.subplots import make_subplots
import os
import glob

st.set_page_config(page_title="Dashboard", layout="wide")
from utils import apply_style_and_logo
apply_style_and_logo()

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


def load_latest_ng_file(folder="data"):
    # Pattern to match files like 2025-08-31_WB_crude_oils_monthly.csv
    pattern = os.path.join(folder, "*_WB_natural_gas_monthly.csv")
    
    # Get list of matching files
    files = glob.glob(pattern)

    if not files:
        raise FileNotFoundError("No crude oil CSV files found in the data folder.")

    # Extract date part from each file name and find the latest
    def extract_date(file_path):
        basename = os.path.basename(file_path)
        date_part = basename.split("_")[0]
        return pd.to_datetime(date_part, format="%Y-%m-%d", errors="coerce")

    files_with_dates = [(file, extract_date(file)) for file in files]
    files_with_dates = [(file, date) for file, date in files_with_dates if pd.notnull(date)]

    if not files_with_dates:
        raise ValueError("No valid dated files found with format YYYY-MM-DD_WB_crude_oils_monthly.csv")

    # Sort and pick the latest
    latest_file, latest_date = max(files_with_dates, key=lambda x: x[1])

    # Read the file
    df = pd.read_csv(latest_file, parse_dates=["Date"])

    print(f"📄 Loaded latest crude oil file: {os.path.basename(latest_file)}")

    return df, latest_date

ng_df, last_month = load_latest_ng_file()


threshold = pd.Timestamp('2016-01-04')
threshold_str=threshold .strftime("%Y-%m-%d")
ng_df=ng_df.query("Date >=@threshold")


def compute_monthly_min_max_bands(df, price_col):
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

ttf_df=ng_df[["Date", "Natural gas, Europe"]]
ttf_bands_df = compute_monthly_min_max_bands(df=ttf_df, price_col="Natural gas, Europe")


#-------------------------------------------------------------------------------------------------
st.title("🔥Natural gas prices")
#-----------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#-----------------------------------------------------

st.markdown("### 📊 Monthly view of major gas prices indicators")
st.caption(f"Source: World Bank monthly data • Updated from {threshold_str}")


# ------------------------------------------------------------------------------
# 📈 FIG 1 - GAS PRICE TRENDS
# ------------------------------------------------------------------------------


line_styles = {
    "Natural gas, US": line1,
    "Natural gas, Europe": line2,
    "Liquefied natural gas, Japan": line3,
   
}



series_colors = {
    "Natural gas, US": palette_blue[3],                 # "#6FBBD3"
    "Natural gas, Europe": palette_top[0],            # "#6DC0B8"
    "Liquefied natural gas, Japan": palette_other[5]    # "#F7D794"
}

fig1 = go.Figure()

series_order = [
    "Natural gas, US",
    "Natural gas, Europe",
    "Liquefied natural gas, Japan",
]

series_names = {
    "Natural gas, US": "US",
    "Natural gas, Europe": "Europe",
    "Liquefied natural gas, Japan": "Japan LNG"
}

for col in series_order:
    
    style = line_styles[col]
    
    fig1.add_trace(
        go.Scatter(
            x=ng_df["Date"],
            y=ng_df[col],
            mode="lines",
            name=series_names[col],
            line=dict(
                color=series_colors[col],
                width=style["width"],
                dash=style["dash"],
                shape=style["shape"],
            ),
            hovertemplate=(
                f"<b>{series_names[col]}</b><br>"
                "Date: %{x|%b %Y}<br>"
                "Price: %{y:.2f} USD/MMBtu"
                "<extra></extra>"
            )
        )
    )

fig1.update_layout(
    title=f"Natural Gas Prices (USD/MMBtu) | up to {last_month.strftime('%b %Y')}",
    xaxis_title="Date",
    yaxis_title="Price (USD/MMBtu)",
    legend_title="Benchmark",
    template="plotly_white",
    font=dict(size=14),
    hovermode="x unified",
    margin=dict(t=60, l=40, r=20, b=40)
)

st.plotly_chart(fig1, use_container_width=True, key="gas_price_trends_chart")

#-----------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#-----------------------------------------------------

# ------------------------------------------------------------------------------
# 📈 FIG 2 - GAS SPREADS
# ------------------------------------------------------------------------------
ng_df["SPREAD EU-US"] = ng_df["Natural gas, Europe"] - ng_df["Natural gas, US"]
ng_df["SPREAD JP-EU"] = ng_df["Liquefied natural gas, Japan"] - ng_df["Natural gas, Europe"]
spread_colors = {
    "SPREAD EU-US": palette_visible[4],   # "#9CE98A"
    "SPREAD JP-EU": palette_blue[3]     # "#6FBBD3"
}

fig2 = go.Figure()

fig2.add_trace(
    go.Scatter(
        x=ng_df["Date"],
        y=ng_df["SPREAD EU-US"],
        mode="lines",
        name="Europe - US",
        line=dict(color=spread_colors["SPREAD EU-US"], width=3),
        hovertemplate=(
            "<b>Europe - US</b><br>"
            "Date: %{x|%b %Y}<br>"
            "Spread: %{y:.2f} USD/MMBtu"
            "<extra></extra>"
        )
    )
)

# ------------------------------------------------------------------------------
# 📈 FIG 2 - GAS SPREADS
# ------------------------------------------------------------------------------
ng_df["SPREAD EU-US"] = ng_df["Natural gas, Europe"] - ng_df["Natural gas, US"]
ng_df["SPREAD JP-EU"] = ng_df["Liquefied natural gas, Japan"] - ng_df["Natural gas, Europe"]
ng_df["SPREAD EU-JP"] = -ng_df["Liquefied natural gas, Japan"] + ng_df["Natural gas, Europe"]
spread_colors = {
    "SPREAD EU-US": palette_green[3],   # "#9CE98A"
    "SPREAD EU-JP": palette_blue[3]     # "#6FBBD3"
}

fig2 = go.Figure()

fig2.add_trace(
    go.Scatter(
        x=ng_df["Date"],
        y=ng_df["SPREAD EU-US"],
        mode="lines",
        name="Europe - US",
        line=dict(color=spread_colors["SPREAD EU-US"], width=3),
        hovertemplate=(
            "<b>Europe - US</b><br>"
            "Date: %{x|%b %Y}<br>"
            "Spread: %{y:.2f} USD/MMBtu"
            "<extra></extra>"
        )
    )
)

fig2.add_trace(
    go.Scatter(
        x=ng_df["Date"],
        y=ng_df["SPREAD EU-JP"],
        mode="lines",
        name="Japan LNG - Europe",
        line=dict(color=spread_colors["SPREAD EU-JP"], width=3),
        hovertemplate=(
            "<b>Japan LNG - Europe</b><br>"
            "Date: %{x|%b %Y}<br>"
            "Spread: %{y:.2f} USD/MMBtu"
            "<extra></extra>"
        )
    )
)

fig2.update_layout(
    title=f"Natural Gas Price Spreads (USD/MMBtu) | up to {last_month.strftime('%b %Y')}",
    xaxis_title="Date",
    yaxis_title="Spread (USD/MMBtu)",
    legend_title="Spread",
    template="plotly_white",
    font=dict(size=14),
    hovermode="x unified",
    margin=dict(t=60, l=40, r=20, b=40)
)

fig2.add_hline(
    y=0,
    line_width=1.2,
    line_dash="dash",
    line_color="gray"
)

st.plotly_chart(fig2, use_container_width=True, key="gas_spread_chart")


#-----------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#-----------------------------------------------------

# ------------------------------------------------------------------------------
# 📈 BOX NARRATIVE
# ------------------------------------------------------------------------------
import pandas as pd

# Latest snapshot
last_date = ng_df["Date"].max()
latest_row = ng_df.loc[ng_df["Date"] == last_date].iloc[0]

# Last 3 months including latest month
last_3m = ng_df.loc[
    ng_df["Date"] >= (last_date - pd.DateOffset(months=2))
].copy()

# Latest values
last_us = latest_row["Natural gas, US"]
last_eu = latest_row["Natural gas, Europe"]
last_japan = latest_row["Liquefied natural gas, Japan"]

# 3-month averages
avg_us = last_3m["Natural gas, US"].mean()
avg_eu = last_3m["Natural gas, Europe"].mean()
avg_japan = last_3m["Liquefied natural gas, Japan"].mean()

# Spreads
spread_eu_us = last_eu - last_us
spread_japan_eu = last_japan - last_eu

def vs_avg(latest, avg):
    diff = latest - avg
    if diff > 0:
        return f"{diff:.2f} above"
    elif diff < 0:
        return f"{abs(diff):.2f} below"
    return "in line with"

gas_narrative = f"""
<div style="border:1.5px solid {palette_blue[3]}; padding:16px 18px; border-radius:12px; background-color:rgba(255,255,255,0.04); color:white; line-height:1.6;">
    <div style="font-size:1.05rem; font-weight:700; margin-bottom:10px;">
        🔥 Latest natural gas snapshot — {last_date.strftime('%B %Y')}
    </div>
    <div><b>US (Henry Hub)</b>: {last_us:.2f} USD/MMBtu, {vs_avg(last_us, avg_us)} its 3-month average ({avg_us:.2f})</div>
    <div><b>Europe (TTF)</b>: {last_eu:.2f} USD/MMBtu, {vs_avg(last_eu, avg_eu)} its 3-month average ({avg_eu:.2f})</div>
    <div><b>Japan LNG</b>: {last_japan:.2f} USD/MMBtu, {vs_avg(last_japan, avg_japan)} its 3-month average ({avg_japan:.2f})</div>
    <div><b>Europe - US spread</b>: {spread_eu_us:.2f} USD/MMBtu</div>
    <div><b>Japan LNG - Europe spread</b>: {spread_japan_eu:.2f} USD/MMBtu</div>
</div>
"""

st.markdown(gas_narrative, unsafe_allow_html=True)

#-----------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#-----------------------------------------------------

#------------------------------------------------------------------------------
# 📈 FIG 3 - FOCUS TTF YTD
#------------------------------------------------------------------------------


st.markdown("### 🔍 TTF YTD vs historical range")
st.caption(f"Source: World Bank monthly data • Updated from {threshold_str}")

latest_date = ttf_df["Date"].max()
latest_year = latest_date.year

ttf_ytd = ttf_df.loc[ttf_df["Date"].dt.year == latest_year].copy()
ttf_ytd["MonthNum"] = ttf_ytd["Date"].dt.month

hist_line_color = palette_blue[2]      # soft blue
hist_fill_color = "rgba(129, 195, 221, 0.18)"
ytd_line_color = palette_top[0]      # teal
ytd_marker_color = palette_other[0]    # peach

fig3 = go.Figure()

# Historical min
fig3.add_trace(
    go.Scatter(
        x=ttf_bands_df["Month"],
        y=ttf_bands_df["Min"],
        mode="lines",
        line=dict(color=hist_line_color, width=2),
        name="Historical min",
        hovertemplate=(
            "<b>Historical min</b><br>"
            "Month: %{x}<br>"
            "Price: %{y:.2f} USD/MMBtu"
            "<extra></extra>"
        )
    )
)

# Historical max + shaded band
fig3.add_trace(
    go.Scatter(
        x=ttf_bands_df["Month"],
        y=ttf_bands_df["Max"],
        mode="lines",
        line=dict(color=hist_line_color, width=2),
        fill="tonexty",
        fillcolor=hist_fill_color,
        name="Historical max",
        hovertemplate=(
            "<b>Historical max</b><br>"
            "Month: %{x}<br>"
            "Price: %{y:.2f} USD/MMBtu"
            "<extra></extra>"
        )
    )
)

# YTD TTF
fig3.add_trace(
    go.Scatter(
        x=ttf_ytd["MonthNum"],
        y=ttf_ytd["Natural gas, Europe"],
        mode="lines+markers",
        line=dict(color=ytd_line_color, width=3.5),
        marker=dict(size=8, color=ytd_marker_color),
        name=f"{latest_year} YTD TTF",
        hovertemplate=(
            f"<b>{latest_year} YTD TTF</b><br>"
            "Month: %{x}<br>"
            "Price: %{y:.2f} USD/MMBtu"
            "<extra></extra>"
        )
    )
)

fig3.update_layout(
    title=f"TTF YTD versus historical monthly range ({latest_year}) - up to {last_month.strftime('%b %Y')}",
    xaxis=dict(
        title="Month",
        tickmode="array",
        tickvals=list(range(1, 13)),
        ticktext=["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    ),
    yaxis_title="Price (USD/MMBtu)",
    legend_title="Series",
    template="plotly_white",
    font=dict(size=14),
    hovermode="x unified",
    margin=dict(t=60, l=40, r=20, b=40)
)

st.plotly_chart(fig3, use_container_width=True, key="ttf_price_band")