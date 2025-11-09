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
    "Crude oil, average": "#A7D5F2",  # blue
    "Crude oil, Brent": "#7DCFA8",    # orange
    "Crude oil, Dubai": "#9CE98A",    # green
    "Crude oil, WTI": "#ABF67B"       # red
}


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

threshold = pd.Timestamp('2016-01-04')
threshold_str=threshold .strftime("%Y-%m-%d")
crudes_df=crudes_df.query("Date >@threshold")

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

brent_df=crudes_df[["Date", "Crude oil, Brent"]]
brent_bands_df = compute_monthly_min_max(df=brent_df, price_col="Crude oil, Brent")
#-----------------------------------------------------------------------------------------------

st.title(" Oil crudes ")
st.markdown("""
            ### 🛢️ Oil crudes view 
            
            """)
st.markdown(f""" 
            source: World Bank - monthly data (from {threshold_str})
                        """)

#------------------------------------------------------------------------------
# 📈 FIG 1 - CRUDES TRENDS
#------------------------------------------------------------------------------


fig1 = px.line(
    crudes_df,
    x="Date",
    y=[
        "Crude oil, average",
        "Crude oil, Brent",
        "Crude oil, Dubai",
        "Crude oil, WTI"
    ],
    title="Crude Oil Prices Over Time",
    color_discrete_map=custom_colors
)

# Update figure layout
fig1.update_layout(
    title="Crude Oil Prices (Monthly , source Worldbank)",
    xaxis_title="Date",
    yaxis_title="Price (USD per barrel)",
    legend_title="Oil Type",
    template="plotly_white",
    font=dict(size=14)
)

st.plotly_chart(fig1, use_container_width=True, key="price_breakdown_chart")


#-----------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#-----------------------------------------------------
# Get last date
last_date = crudes_df["Date"].max()
latest_row = crudes_df[crudes_df["Date"] == last_date].iloc[0]
last_3m = crudes_df[crudes_df["Date"] > last_date - pd.DateOffset(months=3)]

# Latest values
last_Brent = latest_row["Crude oil, Brent"]
last_Dubai = latest_row["Crude oil, Dubai"]
last_WTI = latest_row["Crude oil, WTI"]

# 3-month averages
avg_Brent = last_3m["Crude oil, Brent"].mean()
avg_Dubai = last_3m["Crude oil, Dubai"].mean()
avg_WTI = last_3m["Crude oil, WTI"].mean()

# Spreads
spread_Brent_Dubai = last_Brent - last_Dubai  # Note: currency/unit mismatch may apply
spread_Brent_WTI = last_Brent-last_WTI
# Narrative
gas_narrative = f"""
<div style="
    border: 2px solid {palette_green[3]};
    padding: 15px;
    border-radius: 10px;
    background-color: rgba(255, 255, 255, 0.05);
    color: white;
">

<b>🌍 Latest Natural Gas Price Overview - {last_date.strftime('%B %Y')}</b><br><br>
<ul>
<li><span style="color:{palette_green[3]}; font-weight:bold;">Brent:</span> {last_Brent:.2f} USD/bbl(3-month avg: {avg_Brent:.2f})</li>
<li><span style="color:{palette_green[3]}; font-weight:bold;">Dubai:</span> {last_Dubai:.2f} USD/bbl (3-month avg: {avg_Dubai:.2f})</li>
<li><span style="color:{palette_green[3]}; font-weight:bold;">WTI :</span> {last_WTI:.2f} USD/bbl (3-month avg: {avg_WTI:.2f})</li>
<li><span style="color:{palette_green[3]}; font-weight:bold;">Brent-Dubai Gas Spread:</span> {spread_Brent_Dubai:.2f} (Note: cross-currency/unit)</li>
<li><span style="color:{palette_green[3]}; font-weight:bold;">Brent-WTI Spread:</span> {spread_Brent_WTI:.2f} (Note: cross-currency/unit)</li>
</ul>
</div>
"""

st.markdown(gas_narrative, unsafe_allow_html=True)

#-----------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#-----------------------------------------------------


#-----------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#-----------------------------------------------------

#------------------------------------------------------------------------------
# 📈 FIG 2 - SPREAD
#------------------------------------------------------------------------------
crudes_df["SPREAD BRENT-DUBAI"]=crudes_df["Crude oil, Brent"] - crudes_df["Crude oil, Dubai"]
crudes_df["SPREAD BRENT-WTI"]=crudes_df["Crude oil, Brent"]-crudes_df["Crude oil, WTI"] 

spread_colors={
    "SPREAD BRENT-DUBAI" : palette_green[3],
    "SPREAD BRENT-WTI" : palette_blue[3]
    
}

fig3 = px.line(
    crudes_df,
    x="Date",
    y=[
        "SPREAD BRENT-DUBAI",
        "SPREAD BRENT-WTI",
     
    ],
    title="SPREAD",
    color_discrete_map=spread_colors
)

# Update figure layout
fig3.update_layout(
    title="Crudes Oils (Monthly , source Worldbank)",
    xaxis_title="Date",
    yaxis_title="Price (USD per barrel)",
    legend_title="Crude Spreads" ,
    template="plotly_white",
    font=dict(size=14)
)

st.plotly_chart(fig3, use_container_width=True, key="price_breakdown_chartdfdfs")


#------------------------------------------------------------------------------
# 📈 FIG 2 - BRENT
#------------------------------------------------------------------------------

st.divider()  # <--- Streamlit's built-in separator
st.markdown("""
            ### 📈 Brent YTD 
            """)
st.markdown(""" 
            source: World Bank - monthly data
                        """)

fig2 = go.Figure()

# Min line
fig2.add_trace(go.Scatter(
    x=brent_bands_df["Month"], 
    y=brent_bands_df["Min"],
    mode="lines",
    line=dict(color="lightgrey"),
    name="Historical Min"
))

# Max line with shading
fig2.add_trace(go.Scatter(
    x=brent_bands_df["Month"], 
    y=brent_bands_df["Max"],
    mode="lines",
    line=dict(color="lightgrey"),
    fill="tonexty",  # Fill area between this and previous trace
    fillcolor="rgba(200,200,200,0.3)",
    name="Historical Max"
))

fig2.add_trace(go.Scatter(
    x=brent_df.query("Date >= '2025-01-01'")["Date"].dt.month,
    y=brent_df.query("Date >= '2025-01-01'")["Crude oil, Brent"],
    mode="lines",
    line=dict(color="#77DD77", width=2),
    name="YTD Brent"
))


fig2.update_layout(
    title="Brent YTD on historical monthly Min/Max",
    xaxis=dict(title="Month", tickmode="array", tickvals=list(range(1, 13))),
    yaxis_title="Price (USD per barrel)",
    template="plotly_white"
)

st.plotly_chart(fig2, use_container_width=True, key="price_band")