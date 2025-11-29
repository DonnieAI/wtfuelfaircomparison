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
st.title("Natural Gas")
st.markdown("""
            ### 🔥 Natural Gas price view 
            
            """)
st.markdown(f""" 
            source: World Bank - monthly data (from {threshold_str} onwards)
                        """)

#------------------------------------------------------------------------------
# 📈 FIG 1 - GAS PRICE  TRENDS
#------------------------------------------------------------------------------
custom_colors = {
    "Natural gas, US": "#7FDBFF",  # blue
    "Natural gas, Europe": "#77DD77",    # orange
    "Liquefied natural gas, Japan": "#8EE5EE",    # green
    #"Crude oil, WTI": "#d62728"       # red
}

fig1 = px.line(
    ng_df,
    x="Date",
    y=[
        "Natural gas, US",
        "Natural gas, Europe",
        "Liquefied natural gas, Japan",
      
    ],
    title="Natural Gas Prices Over Time",
    color_discrete_map=custom_colors
)

# Update figure layout
fig1.update_layout(
    title="Natural Gas Prices (Monthly , source Worldbank)",
    xaxis_title="Date",
    yaxis_title="Price (USD per mmbtu)",
    legend_title="Gas" ,
    template="plotly_white",
    font=dict(size=14)
)

st.plotly_chart(fig1, use_container_width=True, key="price_breakdown_chart")

#-----------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#-----------------------------------------------------
# Get last date
last_date = ng_df["Date"].max()
latest_row = ng_df[ng_df["Date"] == last_date].iloc[0]
last_3m = ng_df[ng_df["Date"] > last_date - pd.DateOffset(months=3)]

# Latest values
last_us = latest_row["Natural gas, US"]
last_eu = latest_row["Natural gas, Europe"]
last_japan = latest_row["Liquefied natural gas, Japan"]

# 3-month averages
avg_us = last_3m["Natural gas, US"].mean()
avg_eu = last_3m["Natural gas, Europe"].mean()
avg_japan = last_3m["Liquefied natural gas, Japan"].mean()

# Spreads
spread_eu_us = last_eu - last_us  # Note: currency/unit mismatch may apply
spread_eu_japan = last_eu - last_japan  # Note: currency/unit mismatch may apply

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
<li><span style="color:{palette_green[3]}; font-weight:bold;">US Natural Gas (Henry Hub):</span> {last_us:.2f} USD/MMBtu (3-month avg: {avg_us:.2f})</li>
<li><span style="color:{palette_green[3]}; font-weight:bold;">European Natural Gas (TTF):</span> {last_eu:.2f} USD/MMBtu (3-month avg: {avg_eu:.2f})</li>
<li><span style="color:{palette_green[3]}; font-weight:bold;">LNG Japan :</span> {last_japan:.2f} USD/MMBtu (3-month avg: {avg_japan:.2f})</li>
<li><span style="color:{palette_green[3]}; font-weight:bold;">EU–US Gas Spread:</span> {spread_eu_us:.2f} (Note: cross-currency/unit)</li>
<li><span style="color:{palette_green[3]}; font-weight:bold;">EU–Japan LNG Spread:</span> {spread_eu_japan:.2f} (Note: cross-currency/unit)</li>
</ul>
</div>
"""

st.markdown(gas_narrative, unsafe_allow_html=True)

#-----------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#-----------------------------------------------------

#------------------------------------------------------------------------------
# 📈 FIG 2 - SPREAD
#------------------------------------------------------------------------------
ng_df["SPREAD EU-US"]=ng_df["Natural gas, Europe"] - ng_df["Natural gas, US"]
ng_df["SPREAD JP-EU"]=ng_df["Liquefied natural gas, Japan"]-ng_df["Natural gas, Europe"] 

spread_colors={
    "SPREAD EU-US" : palette_green[3],
    "SPREAD JP-EU" : palette_blue[3]
    
}

fig3 = px.line(
    ng_df,
    x="Date",
    y=[
        "SPREAD EU-US",
        "SPREAD JP-EU",
     
    ],
    title="SPREAD",
    color_discrete_map=spread_colors
)

# Update figure layout
fig3.update_layout(
    title="Natural Gas Prices (Monthly , source Worldbank)",
    xaxis_title="Date",
    yaxis_title="Price (USD per mmbtu)",
    legend_title="Gas" ,
    template="plotly_white",
    font=dict(size=14)
)

st.plotly_chart(fig3, use_container_width=True, key="price_breakdown_chartdfdfs")

#------------------------------------------------------------------------------
# 📈 FIG 3 - TTF
#------------------------------------------------------------------------------

#-----------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#-----------------------------------------------------

st.markdown("""
            ### 📈 TTF YTD 
            """)
st.markdown(""" 
            source: World Bank - monthly data (from 2008 onwards)
                        """)

fig2 = go.Figure()

# Min line
fig2.add_trace(go.Scatter(
            x=ttf_bands_df["Month"], 
            y=ttf_bands_df["Min"],
            mode="lines",
            line=dict(color="lightgrey"),
            name="Historical Min"
        ))

# Max line with shading
fig2.add_trace(go.Scatter(
    x=ttf_bands_df["Month"], 
    y=ttf_bands_df["Max"],
    mode="lines",
    line=dict(color="lightgrey"),
    fill="tonexty",  # Fill area between this and previous trace
    fillcolor="rgba(200,200,200,0.3)",
    name="Historical Max"
))

fig2.add_trace(go.Scatter(
    x=ttf_df.query("Date >= '2025-01-01'")["Date"].dt.month,
    y=ttf_df.query("Date >= '2025-01-01'")["Natural gas, Europe"],
    mode="lines",
    line=dict(color="#77DD77", width=2),
    name="TTF"
))


fig2.update_layout(
    title="TTF YTD on historical monthly Min/Max",
    xaxis=dict(title="Month", tickmode="array", tickvals=list(range(1, 13))),
    yaxis_title="Price (USD/MMBtu)",
    template="plotly_white"
)

st.plotly_chart(fig2, use_container_width=True, key="price_band")