"""
⚫Coal monthly basies extract form WorldBank 
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


custom_colors = {
    "Coal, Australian": "#7FDBFF",  # blue
    "Coal, South African **": "#77DD77",    # orange
   # "Crude oil, Dubai": "#8EE5EE",    # green
   # "Crude oil, WTI": "#d62728"       # red
}


def load_latest_coal_file(folder="data"):
    # Pattern to match files like 2025-08-31_WB_crude_oils_monthly.csv
    pattern = os.path.join(folder, "*_WB_coal_monthly.csv")
    
    # Get list of matching files
    files = glob.glob(pattern)

    if not files:
        raise FileNotFoundError("No coal CSV files found in the data folder.")

    # Extract date part from each file name and find the latest
    def extract_date(file_path):
        basename = os.path.basename(file_path)
        date_part = basename.split("_")[0]
        return pd.to_datetime(date_part, format="%Y-%m-%d", errors="coerce")

    files_with_dates = [(file, extract_date(file)) for file in files]
    files_with_dates = [(file, date) for file, date in files_with_dates if pd.notnull(date)]

    if not files_with_dates:
        raise ValueError("No valid dated files found with format YYYY-MM-DD_WB_coal_monthly.csv")

    # Sort and pick the latest
    latest_file, latest_date = max(files_with_dates, key=lambda x: x[1])

    # Read the file
    df = pd.read_csv(latest_file, parse_dates=["Date"])

    print(f"📄 Loaded latest crude oil file: {os.path.basename(latest_file)}")

    return df, latest_date


coal_df, last_month = load_latest_coal_file()

threshold = pd.Timestamp('2016-01-04')
threshold_str=threshold .strftime("%Y-%m-%d")
coal_df=coal_df.query("Date >=@threshold")

#✅------------------------DATA EXTRACTION-----------------------------------------------------
#coal_df=pd.read_csv("data/WB_coal_selection.csv",parse_dates=["Date"])
#sa_coal_bands_df=pd.read_csv("data/WB_au_coal_min_max_bands.csv")
#✅--------------------------------------------------------------------------------------------


sa_coal_df=coal_df[["Date", "Coal, South African **"]]

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


sa_coal_bands_df = compute_monthly_min_max_bands(df=sa_coal_df, price_col="Coal, South African **")

st.title(" Coal prices ")
st.markdown("""
            ### ⚫ Coals view 
            
            """)
st.markdown(f""" 
            source: World Bank - monthly data (from {threshold_str} onwards)
                        """)

#------------------------------------------------------------------------------
# 📈 FIG 1 - COAL TRENDS
#------------------------------------------------------------------------------


fig1 = px.line(
    coal_df,
    x="Date",
    y=[
        "Coal, Australian",
        "Coal, South African **",
       # "Crude oil, Dubai",
       # "Crude oil, WTI"
    ],
    title="Coal Prices Over Time",
    color_discrete_map=custom_colors
)

# Update figure layout
fig1.update_layout(
    title="Coal Prices (Monthly , source Worldbank",
    xaxis_title="Date",
    yaxis_title="Price (USD per mt)",
    legend_title="Coal Type",
    template="plotly_white",
    font=dict(size=14)
)

st.plotly_chart(fig1, use_container_width=True, key="price_breakdown_chart")

#-----------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#-----------------------------------------------------

last_date = coal_df["Date"].max()
latest_row = coal_df[coal_df["Date"] == last_date].iloc[0]
last_3m = coal_df[coal_df["Date"] > last_date - pd.DateOffset(months=3)]

# Latest values
last_au = latest_row["Coal, Australian"]
last_sa = latest_row["Coal, South African **"]

# 3-month averages
avg_au = last_3m["Coal, Australian"].mean()
avg_sa = last_3m["Coal, South African **"].mean()

# Spreads
spread_au_sa = last_au - last_sa  # Note: currency/unit mismatch may apply



# Narrative
coal_narrative = f"""
<div style="
    border: 2px solid {palette_green[3]};
    padding: 15px;
    border-radius: 10px;
    background-color: rgba(255, 255, 255, 0.05);
    color: white;
">

<b>🌍 Latest Natural Gas Price Overview - {last_date.strftime('%B %Y')}</b><br><br>
<ul>
<li><span style="color:{palette_green[3]}; font-weight:bold;">Coal, Australian:</span> {last_au:.2f} USD/t (3-month avg: {avg_au:.2f})</li>
<li><span style="color:{palette_green[3]}; font-weight:bold;">Coal, South African:</span> {last_sa:.2f} USD/t (3-month avg: {avg_sa:.2f})</li>

<li><span style="color:{palette_green[3]}; font-weight:bold;">Australian - South African Spread:</span> {spread_au_sa:.2f} USD/t </li>
</ul>
</div>
"""

st.markdown(coal_narrative, unsafe_allow_html=True)


#------------------------------------------------------------------------------
# 📈 FIG 2 - South Africa Coal
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#------------------------------------------------------------------------------
st.markdown("""
            ### 📈 South Africa Coal YTD 
            """)
st.markdown(""" 
            source: World Bank - monthly data (from 2008 onwards)
                        """)

fig2 = go.Figure()

# Min line
fig2.add_trace(go.Scatter(
    x=sa_coal_bands_df["Month"], 
    y=sa_coal_bands_df["Min"],
    mode="lines",
    line=dict(color="lightgrey"),
    name="Historical Min"
))

# Max line with shading
fig2.add_trace(go.Scatter(
    x=sa_coal_bands_df["Month"], 
    y=sa_coal_bands_df["Max"],
    mode="lines",
    line=dict(color="lightgrey"),
    fill="tonexty",  # Fill area between this and previous trace
    fillcolor="rgba(200,200,200,0.3)",
    name="Historical Max"
))

fig2.add_trace(go.Scatter(
    x=sa_coal_df.query("Date >= '2025-01-01'")["Date"].dt.month,
    y=sa_coal_df.query("Date >= '2025-01-01'")["Coal, South African **"],
    mode="lines",
    line=dict(color="#77DD77", width=2),
    name="YTD Brent"
))


fig2.update_layout(
    title="South Africa Coal YTD on historical monthly Min/Max",
    xaxis=dict(title="Month", tickmode="array", tickvals=list(range(1, 13))),
    yaxis_title="Price (USD per mt)",
    template="plotly_white"
)

st.plotly_chart(fig2, use_container_width=True, key="price_band")