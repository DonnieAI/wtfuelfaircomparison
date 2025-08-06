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
crudes_df=pd.read_csv("data/WB_crude_oil_selection.csv",parse_dates=["Date"])
brent_bands_df=pd.read_csv("data/WB_brent_min_max_bands.csv")
#✅--------------------------------------------------------------------------------------------

brent_df=crudes_df[["Date", "Crude oil, Brent"]]

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
custom_colors = {
    "Crude oil, average": "#7FDBFF",  # blue
    "Crude oil, Brent": "#77DD77",    # orange
    "Crude oil, Dubai": "#8EE5EE",    # green
    "Crude oil, WTI": "#d62728"       # red
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
    title="Crude Oil Prices (Monthly , source Worldbank",
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