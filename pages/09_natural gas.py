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

st.set_page_config(page_title="Dashboard", layout="wide")
from utils import apply_style_and_logo
apply_style_and_logo()


#✅------------------------DATA EXTRACTION-----------------------------------------------------
ng_df=pd.read_csv("data/WB_natural_gas_selection.csv",parse_dates=["Date"])
ttf_bands_df=pd.read_csv("data/WB_ttf_min_max_bands.csv")
#✅--------------------------------------------------------------------------------------------

ttf_df=ng_df[["Date", "Natural gas, Europe"]]

st.title("Natural Gas")
st.markdown("""
            ### 🔥 Natural Gas price view 
            
            """)
st.markdown(""" 
            source: World Bank - monthly data (from 2008 onwards)
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
    title="Natural Gas Prices (Monthly , source Worldbank",
    xaxis_title="Date",
    yaxis_title="Price (USD per mmbtu)",
    legend_title="Gas" ,
    template="plotly_white",
    font=dict(size=14)
)

st.plotly_chart(fig1, use_container_width=True, key="price_breakdown_chart")


#------------------------------------------------------------------------------
# 📈 FIG 2 - BRENT
#------------------------------------------------------------------------------

st.divider()  # <--- Streamlit's built-in separator
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
    name="YTD Brent"
))


fig2.update_layout(
    title="TTF YTD on historical monthly Min/Max",
    xaxis=dict(title="Month", tickmode="array", tickvals=list(range(1, 13))),
    yaxis_title="Price (USD permmbtu)",
    template="plotly_white"
)

st.plotly_chart(fig2, use_container_width=True, key="price_band")