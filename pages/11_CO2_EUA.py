import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px 
from pathlib import Path
from plotly.subplots import make_subplots
from datetime import datetime

#https://docs.streamlit.io/develop/api-reference/charts/st.pydeck_chart
#https://docs.mapbox.com/api/maps/styles/
#    cd C:\WT\WT_OFFICIAL_APPLICATIONS_REPOSITORY\WT_CARBON_SCOPE_COMPASS
#https://energy.instrat.pl/en/prices/eu-ets/

st.set_page_config(page_title="projects", layout="wide")
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

#-----------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------
co2_price_df=pd.read_csv("data/prices_eu_ets_all.csv")
co2_price_df["date"] = pd.to_datetime(co2_price_df["date"], dayfirst=True)
# Extract the year from the date
co2_price_df["year"] = co2_price_df["date"].dt.year

# Calculate yearly average EUA prices from 2005 to 2024 (based on available data)
yearly_avg_prices = co2_price_df.groupby("year")["price"].mean().round(2)
yearly_avg_prices = yearly_avg_prices[(yearly_avg_prices.index >= 2005) & (yearly_avg_prices.index <= 2025)]

# Calculate YTD average for the current year (e.g., 2025)
current_year = datetime.now().year
ytd_avg_price = co2_price_df[co2_price_df["year"] == current_year].groupby("year")["price"].mean().round(2)

# Update or append the YTD value to the main series
yearly_avg_prices.update(ytd_avg_price)
yearly_avg_prices = yearly_avg_prices.sort_index()

# Convert to DataFrame for export or further analysis
yearly_avg_df = yearly_avg_prices.reset_index()
yearly_avg_df.columns = ["year", "price"]

#yearly_avg_df["year"]=pd.to_datetime(yearly_avg_df["year"])
# Optional: Save to CSV
# yearly_avg_df.to_csv("data/yearly_avg_eua_prices.csv", index=False)

print(yearly_avg_df)

# Make sure df is sorted
co2_price_df = co2_price_df.sort_values("date").reset_index(drop=True)

# Get last available value
last_row = co2_price_df.iloc[-1]
last_date = last_row["date"]
last_price = last_row["price"]

# Get previous week's value (7 days before last_date)
prev_week_df = co2_price_df[co2_price_df["date"] <= (last_date - pd.Timedelta(days=7))]

if not prev_week_df.empty:
    prev_row = prev_week_df.iloc[-1]
    prev_date = prev_row["date"]
    prev_price = prev_row["price"]
    
    # Calculate variation
    abs_change = last_price - prev_price
    pct_change = (abs_change / prev_price) * 100
else:
    prev_date = None
    prev_price = None
    abs_change = None
    pct_change = None


#--------------------------------------------------------------------------------------------
st.title("EU Allowance (EUA)")
st.markdown("""
            ### 📈 EU Allowance (EUA) price trend (EUR/tCO2)
            
            """)
st.markdown(""" 
            source: energy.instrat.pl
            """)

#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------

fig_price=px.line(
                    co2_price_df,
                    x="date",
                    y="price"
)
        
        # Add vertical dashed lines

# Step 3: Optional layout tweaks
fig_price.update_layout(
                    legend_title_text='Legend',
                    xaxis_title='Date',
                    yaxis_title='€/t CO₂',
                    hovermode='x unified'
        )

fig_price.add_vrect(
                x0=pd.Timestamp("2021-01-01"), 
                x1=co2_price_df["date"].max(),  # also a Timestamp
                fillcolor="blue", opacity=0.1, line_width=0,
                annotation_text="Phase 4", annotation_position="top left"
)

fig_price.add_vrect(
                x0=pd.Timestamp("2013-01-01"), 
                x1=pd.Timestamp("2020-12-31"),
                fillcolor="red", opacity=0.1, line_width=0,
                annotation_text="Phase 3", annotation_position="top left"
)


fig_price.update_xaxes(
                dtick="M12",         # one tick every 12 months
                tickformat="%Y",     # show only the year
                ticklabelmode="period"  # align ticks at year start
)
 

st.plotly_chart(fig_price, use_container_width=True)

# Build narrative
if prev_price is not None:
    price_comment_narrative = f"""
    <div style="
        border: 2px solid {palette_green[3]};
        padding: 15px;
        border-radius: 10px;
        background-color: rgba(255, 255, 255, 0.05);
        color: white;
        font-family: Arial, sans-serif;
        line-height: 1.6;
    ">
        <b>📊 Key Insights</b><br><br>
        📈 As of <b>{last_date.strftime('%Y-%m-%d')}</b>, the CO₂ price is 
        <b>{last_price:.2f} €/t</b>.<br>
        Compared to <b>{prev_date.strftime('%Y-%m-%d')}</b> 
        (<i>{prev_price:.2f} €/t</i>),<br>
        this represents a change of 
        <b>{abs_change:+.2f} €/t</b> 
        (<b>{pct_change:+.2f}%</b>).
    </div>
    """
else:
    price_comment_narrative = f"""
    <div style="
        border: 2px solid {palette_green[3]};
        padding: 15px;
        border-radius: 10px;
        background-color: rgba(255, 255, 255, 0.05);
        color: white;
        font-family: Arial, sans-serif;
        line-height: 1.6;
    ">
        <b>📊 Key Insights</b><br><br>
        📈 As of <b>{last_date.strftime('%Y-%m-%d')}</b>, 
        the CO₂ price is <b>{last_price:.2f} €/t</b>.<br>
        (Not enough data for week-on-week comparison.)
    </div>
"""

st.markdown(price_comment_narrative, unsafe_allow_html=True)

#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------
