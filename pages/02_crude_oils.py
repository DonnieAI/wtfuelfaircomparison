"""
Crude oil monthly basies extract form WorldBank 
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




def load_latest_crude_file(folder="data"):
    # Pattern to match files like 2025-08-31_WB_crude_oils_monthly.csv
    pattern = os.path.join(folder, "*_WB_crude_oils_monthly.csv")
    
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

crudes_df, last_month = load_latest_crude_file()

#✅------------------------DATA EXTRACTION-----------------------------------------------------
#last_month="2025-08-31"
#crudes_df=pd.read_csv(f"data/{last_month}_WB_crude_oils_monthly.csv",parse_dates=["Date"])
#✅--------------------------------------------------------------------------------------------

threshold = pd.Timestamp('2008-01-01')
threshold_str=threshold .strftime("%Y-%m-%d")
crudes_df=crudes_df.query("Date >=@threshold")

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

brent_df=crudes_df[["Date", "Crude oil, Brent"]]
brent_bands_df = compute_monthly_min_max_bands(df=brent_df, price_col="Crude oil, Brent")
#-----------------------------------------------------------------------------------------------

st.title("🛢️ Crude oil prices")
#-----------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#-----------------------------------------------------

st.markdown("### 📊 Monthly view of major crude oil indicators")
st.caption(f"Source: World Bank monthly data • Updated from {threshold_str}")

#------------------------------------------------------------------------------
# 📈 FIG 1 - CRUDES TRENDS
#------------------------------------------------------------------------------

fig1 = go.Figure()

series_colors = {
    "Crude oil, average": "#5DB2C8",  # stronger blue-teal
    "Crude oil, Brent": palette_top[0],    # teal
    "Crude oil, Dubai": "#FFD7BA",    # pastel orange
    "Crude oil, WTI": "#D7BDE2"       # pastel purple
}


line_styles = {
    "Crude oil, average": line1,
    "Crude oil, Brent": line2,
    "Crude oil, Dubai": line3,
    "Crude oil, WTI": line4,
}


for col in [
    "Crude oil, average",
    "Crude oil, Brent",
    "Crude oil, Dubai",
    "Crude oil, WTI"
]:
     
    style = line_styles[col]

    fig1.add_trace(
        go.Scatter(
            x=crudes_df["Date"],
            y=crudes_df[col],
            mode="lines",
            name=col.replace("Crude oil, ", ""),
            line=dict(
                color=series_colors[col],
                width=style["width"],
                dash=style["dash"],
                shape=style["shape"],
            ),
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "Date: %{x|%b %Y}<br>"
                "Price: %{y:.2f} USD/bbl"
                "<extra></extra>"
            )
        )
    )


fig1.update_layout(
    title=f"Crude Oil Prices (USD/bbl) |  up to {last_month.strftime('%b %Y')}",
    xaxis_title="Date",
    yaxis_title="Price (USD per barrel)",
    legend_title="Benchmark",
    template="plotly_white",
    font=dict(size=14),
    hovermode="x unified",
    margin=dict(t=60, l=40, r=20, b=40)
)

st.plotly_chart(fig1, use_container_width=True, key="price_breakdown_chart")


#-----------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#-----------------------------------------------------

# ------------------------------------------------------------------------------
# 📈 FIG 2 - SPREAD
# ------------------------------------------------------------------------------
crudes_df["SPREAD BRENT-DUBAI"] = crudes_df["Crude oil, Brent"] - crudes_df["Crude oil, Dubai"]
crudes_df["SPREAD BRENT-WTI"] = crudes_df["Crude oil, Brent"] - crudes_df["Crude oil, WTI"]
spread_colors = {
    "SPREAD BRENT-DUBAI": palette_visible[4],  # green-teal
    "SPREAD BRENT-WTI": palette_blue[3]  # medium blue
}

fig2 = go.Figure()

fig2.add_trace(
    go.Scatter(
        x=crudes_df["Date"],
        y=crudes_df["SPREAD BRENT-DUBAI"],
        mode="lines",
        name="Brent - Dubai",
        line=dict(color=spread_colors["SPREAD BRENT-DUBAI"], width=3),
        hovertemplate=(
            "<b>Brent - Dubai</b><br>"
            "Date: %{x|%b %Y}<br>"
            "Spread: %{y:.2f} USD/bbl"
            "<extra></extra>"
        )
    )
)

fig2.add_trace(
    go.Scatter(
        x=crudes_df["Date"],
        y=crudes_df["SPREAD BRENT-WTI"],
        mode="lines",
        name="Brent - WTI",
        line=dict(color=spread_colors["SPREAD BRENT-WTI"], width=3),
        hovertemplate=(
            "<b>Brent - WTI</b><br>"
            "Date: %{x|%b %Y}<br>"
            "Spread: %{y:.2f} USD/bbl"
            "<extra></extra>"
        )
    )
)

fig2.update_layout(
    title=f"Crude Oil Price Spreads - up to {last_month.strftime('%b %Y')}",
    xaxis_title="Date",
    yaxis_title="Spread (USD per barrel)",
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

st.plotly_chart(fig2, use_container_width=True, key="crude_spread_chart")

#-----------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#-----------------------------------------------------
# ------------------------------------------------------------------------------
# 📈 BOX NARRATIVE
# ------------------------------------------------------------------------------

# Latest snapshot
last_date = crudes_df["Date"].max()
latest_row = crudes_df.loc[crudes_df["Date"] == last_date].iloc[0]

# Last 3 months window including latest month
last_3m = crudes_df.loc[
    crudes_df["Date"] >= (last_date - pd.DateOffset(months=2))
].copy()

# Latest values
last_brent = latest_row["Crude oil, Brent"]
last_dubai = latest_row["Crude oil, Dubai"]
last_wti = latest_row["Crude oil, WTI"]

# 3-month averages
avg_brent = last_3m["Crude oil, Brent"].mean()
avg_dubai = last_3m["Crude oil, Dubai"].mean()
avg_wti = last_3m["Crude oil, WTI"].mean()

# Spreads
spread_brent_dubai = last_brent - last_dubai
spread_brent_wti = last_brent - last_wti

# Direction helpers
def vs_avg(latest, avg):
    diff = latest - avg
    if diff > 0:
        return f"{diff:.2f} above"
    elif diff < 0:
        return f"{abs(diff):.2f} below"
    return "in line with"

oil_narrative = f"""
<div style="border:1.5px solid {palette_blue[3]}; padding:16px 18px; border-radius:12px; background-color:rgba(255,255,255,0.04); color:white; line-height:1.6;">
    <div style="font-size:1.05rem; font-weight:700; margin-bottom:10px;">
        🛢️ Latest crude oil snapshot — {last_date.strftime('%B %Y')}
    </div>
    <div><b>Brent</b>: {last_brent:.2f} USD/bbl, {vs_avg(last_brent, avg_brent)} its 3-month average ({avg_brent:.2f})</div>
    <div><b>Dubai</b>: {last_dubai:.2f} USD/bbl, {vs_avg(last_dubai, avg_dubai)} its 3-month average ({avg_dubai:.2f})</div>
    <div><b>WTI</b>: {last_wti:.2f} USD/bbl, {vs_avg(last_wti, avg_wti)} its 3-month average ({avg_wti:.2f})</div>
    <div><b>Brent-Dubai spread</b>: {spread_brent_dubai:.2f} USD/bbl</div>
    <div><b>Brent-WTI spread</b>: {spread_brent_wti:.2f} USD/bbl</div>
</div>
"""

st.markdown(oil_narrative, unsafe_allow_html=True)

#-----------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#-----------------------------------------------------

# ------------------------------------------------------------------------------
# 📈 FIG 3 - FOCUS BRENT YTD
# ------------------------------------------------------------------------------
st.markdown("### 🔍 Brent YTD vs historical range")
st.caption(f"Source: World Bank monthly data • Updated from {threshold_str}")

latest_date = brent_df["Date"].max()
latest_year = latest_date.year

brent_ytd = brent_df.loc[brent_df["Date"].dt.year == latest_year].copy()
brent_ytd["MonthNum"] = brent_ytd["Date"].dt.month

hist_line_color = palette_blue[2]      # soft blue
hist_fill_color = "rgba(129, 195, 221, 0.18)"
ytd_line_color = palette_top[0]      # teal
ytd_marker_color = palette_other[0]    # peach

fig3 = go.Figure()

# Historical min
fig3.add_trace(
    go.Scatter(
        x=brent_bands_df["Month"],
        y=brent_bands_df["Min"],
        mode="lines",
        line=dict(color=hist_line_color, width=2),
        name="Historical min",
        hovertemplate=(
            "<b>Historical min</b><br>"
            "Month: %{x}<br>"
            "Price: %{y:.2f} USD/bbl"
            "<extra></extra>"
        )
    )
)

# Historical max + shaded band
fig3.add_trace(
    go.Scatter(
        x=brent_bands_df["Month"],
        y=brent_bands_df["Max"],
        mode="lines",
        line=dict(color=hist_line_color, width=2),
        fill="tonexty",
        fillcolor=hist_fill_color,
        name="Historical max",
        hovertemplate=(
            "<b>Historical max</b><br>"
            "Month: %{x}<br>"
            "Price: %{y:.2f} USD/bbl"
            "<extra></extra>"
        )
    )
)

# YTD Brent
fig3.add_trace(
    go.Scatter(
        x=brent_ytd["MonthNum"],
        y=brent_ytd["Crude oil, Brent"],
        mode="lines+markers",
        line=dict(color=ytd_line_color, width=3.5),
        marker=dict(size=8, color=ytd_marker_color),
        name=f"{latest_year} YTD Brent",
        hovertemplate=(
            f"<b>{latest_year} YTD Brent</b><br>"
            "Month: %{x}<br>"
            "Price: %{y:.2f} USD/bbl"
            "<extra></extra>"
        )
    )
)

fig3.update_layout(
    title=f"Brent YTD versus historical monthly range ({latest_year}) -up to {last_month.strftime('%b %Y')}",
    xaxis=dict(
        title="Month",
        tickmode="array",
        tickvals=list(range(1, 13)),
        ticktext=["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    ),
    yaxis_title="Price (USD per barrel)",
    legend_title="Series",
    template="plotly_white",
    font=dict(size=14),
    hovermode="x unified",
    margin=dict(t=60, l=40, r=20, b=40)
)

st.plotly_chart(fig3, use_container_width=True, key="price_band")

