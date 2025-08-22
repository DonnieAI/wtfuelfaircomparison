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

st.set_page_config(page_title="Dashboard", layout="wide")
from utils import apply_style_and_logo
apply_style_and_logo()


#✅------------------------DATA EXTRACTION-----------------------------------------------------
last_month="2025-07-01"
crudes_df=pd.read_csv(f"data/{last_month}_WB_crude_oils_monthly.csv",parse_dates=["Date"])
#✅--------------------------------------------------------------------------------------------

crudes_df=crudes_df.query("Date > '2008-01-01'")

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



st.title(" Oil crudes ")
st.markdown("""
            ### 🛢️ Oil crudes view 
            
            """)
st.markdown(""" 
            source: World Bank - monthly data (from 2008 onwards)
                        """)

#------------------------------------------------------------------------------
# 📈 FIG 1 - CRUDES TRENDS
#------------------------------------------------------------------------------


pastel_blue_green = [
    "#A7D5F2", "#94CCE8", "#81C3DD", "#6FBBD3", "#5DB2C8",
    "#6DC0B8", "#7DCFA8", "#8DDC99", "#9CE98A", "#ABF67B"
]

custom_colors = {
    "Crude oil, average": "#A7D5F2",  # blue
    "Crude oil, Brent": "#7DCFA8",    # orange
    "Crude oil, Dubai": "#9CE98A",    # green
    "Crude oil, WTI": "#ABF67B"       # red
}


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


#------------------------------------------------------------------------------
# 📈 FIG 2 - BRENT
#------------------------------------------------------------------------------

st.divider()  # <--- Streamlit's built-in separator
st.markdown("""
            ### 📈 Brent YTD 
            """)
st.markdown(""" 
            source: World Bank - monthly data (from 2008 onwards)
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