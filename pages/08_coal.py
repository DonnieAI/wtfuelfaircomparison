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

st.set_page_config(page_title="Dashboard", layout="wide")
from utils import apply_style_and_logo
apply_style_and_logo()


#✅------------------------DATA EXTRACTION-----------------------------------------------------
coal_df=pd.read_csv("data/WB_coal_selection.csv",parse_dates=["Date"])
sa_coal_bands_df=pd.read_csv("data/WB_sa_coal_min_max_bands.csv")
#✅--------------------------------------------------------------------------------------------

sa_coal_df=coal_df[["Date", "Coal, South African **"]]

st.title(" Coal prices ")
st.markdown("""
            ### ⚫ Oil crudes view 
            
            """)
st.markdown(""" 
            source: World Bank - monthly data (from 2008 onwards)
                        """)

#------------------------------------------------------------------------------
# 📈 FIG 1 - COAL TRENDS
#------------------------------------------------------------------------------
custom_colors = {
    "Coal, Australian": "#7FDBFF",  # blue
    "Coal, South African **": "#77DD77",    # orange
   # "Crude oil, Dubai": "#8EE5EE",    # green
   # "Crude oil, WTI": "#d62728"       # red
}


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


#------------------------------------------------------------------------------
# 📈 FIG 2 - South Africa Coal
#------------------------------------------------------------------------------

st.divider()  # <--- Streamlit's built-in separator
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