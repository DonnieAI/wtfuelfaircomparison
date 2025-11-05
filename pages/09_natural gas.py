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


#✅------------------------DATA EXTRACTION-----------------------------------------------------
#ng_df=pd.read_csv("data/WB_natural_gas_selection.csv",parse_dates=["Date"])
ttf_bands_df=pd.read_csv("data/WB_ttf_min_max_bands.csv")
#✅--------------------------------------------------------------------------------------------

#✅------------------------DATA EXTRACTION-----------------------------------------------------
last_month="2025-08-31"
ng_df=pd.read_csv(f"data/{last_month}_WB_natural_gas_monthly.csv",parse_dates=["Date"])
#✅--------------------------------------------------------------------------------------------

ng_df=ng_df.query("Date > '2008-01-01'")

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
    title="Natural Gas Prices (Monthly , source Worldbank)",
    xaxis_title="Date",
    yaxis_title="Price (USD per mmbtu)",
    legend_title="Gas" ,
    template="plotly_white",
    font=dict(size=14)
)

st.plotly_chart(fig1, use_container_width=True, key="price_breakdown_chart")


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
<li><span style="color:{palette_green[3]}; font-weight:bold;">European Natural Gas (TTF):</span> {last_eu:.2f} EUR/MWh (3-month avg: {avg_eu:.2f})</li>
<li><span style="color:{palette_green[3]}; font-weight:bold;">LNG Japan :</span> {last_japan:.2f} USD/MMBtu (3-month avg: {avg_japan:.2f})</li>
<li><span style="color:{palette_green[3]}; font-weight:bold;">EU–US Gas Spread:</span> {spread_eu_us:.2f} (Note: cross-currency/unit)</li>
<li><span style="color:{palette_green[3]}; font-weight:bold;">EU–Japan LNG Spread:</span> {spread_eu_japan:.2f} (Note: cross-currency/unit)</li>
</ul>
</div>
"""

st.markdown(gas_narrative, unsafe_allow_html=True)



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
# 📈 FIG 2 - TTF
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
    name="TTF"
))


fig2.update_layout(
    title="TTF YTD on historical monthly Min/Max",
    xaxis=dict(title="Month", tickmode="array", tickvals=list(range(1, 13))),
    yaxis_title="Price (USD permmbtu)",
    template="plotly_white"
)

st.plotly_chart(fig2, use_container_width=True, key="price_band")