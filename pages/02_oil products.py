"""
⛽Oil products  - weekly data 
data from DG Energy
#cd C:\WT\WT_OFFICIAL_APPLICATIONS_REPOSITORY\WT_FAIR_FUEL_COMPARE
"""
import streamlit as st
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px 
from pathlib import Path
from plotly.subplots import make_subplots

st.set_page_config(page_title="Dashboard", layout="wide")
from utils import apply_style_and_logo
apply_style_and_logo()

#✅------------------------DATA EXTRACTION-----------------------------------------------------
df=pd.read_parquet("data/DG_Energy_oil_products_weekly.parquet")
df.dropna()
category="Oil Products"
subcategory="Oil Products"


#✅--------------------------------------------------------------------
st.title(f" ⛽ {category} Prices")
st.markdown("""
            ### 📊 Oil Products Price - cross country view (data from March 2005)
            
            """)
st.markdown(""" 
            source: EU DG Energy - weekly data 
                        """)

products_selection=(
                    df["Fuel_Type"]
                   .unique()
                   .tolist()
)
selected_product = st.selectbox(
    "Select a oil product product",  # label
    options=products_selection
)


weeks_selection = (
    df["Date"]
    .dropna()
    .unique()
    .tolist()
)

selected_week = st.selectbox(
    "Select a week (by default the last available)",
    options=[d.strftime("%Y-%m-%d") for d in weeks_selection],
    index=0
)

# **************************************************************************************
df_filtered = df.query("Fuel_Type == @selected_product and Date == @selected_week")
# **************************************************************************************

df_melted = df_filtered.melt(
    id_vars=["Country", "Date", "Fuel_Type"],
    value_vars=["Price"],
    var_name="component",
    value_name="price"
)

geo_order = (
    df_filtered
    .sort_values("Price", ascending=False)["Country"]
    .tolist()
)

pastel_blue_green = [
    "#A7D5F2", "#94CCE8", "#81C3DD", "#6FBBD3", "#5DB2C8",
    "#6DC0B8", "#7DCFA8", "#8DDC99", "#9CE98A", "#ABF67B"
]

custom_colors = {
    "Price": "#A7D5F2",  
   # "taxes": "#6DC0B8",   # Powder blue
   # "vat": "#8DDC99"      # Muted salmon/peach  #66CDAA  #8EE5EE
}

# 💹FIG1A💹---------------------------------------------------------------------
fig1a = px.bar(
            df_melted,
            y="Country",
            x="price",
            color="component",
            barmode="relative",
            category_orders={"Country": geo_order},
            color_discrete_map=custom_colors,
            title=f"{selected_product}|| Price Breakdown by Country || week  {selected_week}"
)

# Assuming df_latest is filtered for latest time and includes total prices
total_labels = df_filtered.set_index("Country").loc[geo_order]["Price"]

fig1a.add_trace(
            go.Scatter(
                x=total_labels.values,
                y=total_labels.index,
                mode="text",
                text=[f"{v:.0f}" for v in total_labels.values],  # e.g., "251.3"
                textposition="middle right",
                textfont=dict(
                            color="white",   # your color
                            size=16,
                            #family="Bold"  # or any system font with bold style
                            ),
                showlegend=False
            )
)

units_selection = [
    "€/1000L",   # Super_95
    "€/1000L",   # Diesel
    "€/1000L",   # Heating_Oil
    "€/ton", # Heavy_Fuel_Oil
    "€/ton", # Heavy_Fuel_Oil_Type_III
    "€/1000L"    # GPL
]

# Create a dictionary using index mapping
unit_map = dict(zip(products_selection, units_selection))

# Get the right unit for the selected product
unit_measure = unit_map.get(selected_product , "")


fig1a.update_layout(
            height=40* len(df_filtered["Country"].unique()),  # 30px per country (adjust as needed)
            xaxis_title=f"{category} Price {unit_measure}",
            yaxis_title="Country",
            paper_bgcolor="#005680",
            plot_bgcolor="#005680",
            font=dict(size=14, color="#00274d"),
            legend_title="Component",
            xaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)")
)

# Show Plotly chart
st.plotly_chart(fig1a, use_container_width=True, key="price_breakdown_chart")


#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
st.markdown("""
            ### 📈 Oil Products Price - single country historical trend
            """)
st.markdown(""" 
            source: EU DG Energy - weekly data
                        """)

countries_selection=(
                    df["Country"]
                   .unique()
                   .dropna()
                   .tolist()
)
selected_country = st.selectbox(
    "Select a country (EU - European Union | EUR - Eurozone )",  # label
    options=countries_selection
)

# **************************************************************************************
df_filtered_fig2 = df.query("Country == @selected_country and Fuel_Type==@selected_product")
# **************************************************************************************

fig2=px.line(
    df_filtered_fig2,
    x="Date",
    y="Price"
)


fig2.update_layout(
            #height=40* len(df_filtered["geo"].unique()),  # 30px per country (adjust as needed)
            title=f" {selected_product} || Prices historical trend in || {selected_country}",
            yaxis_title=f"{selected_product} Price {unit_measure}",
            xaxis_title="Weeks",
            paper_bgcolor="#005680",
            plot_bgcolor="#005680",
            font=dict(size=14, color="#00274d"),
            #legend_title="Component",
            xaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)")
)


st.plotly_chart(fig2, use_container_width=True,key="historical_chart")