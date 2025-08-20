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
# Extraction of oil product with tax
files = list(Path("data").glob("*.parquet"))

# latest "withtaxes"
withtaxes_files = [f for f in files if "withtaxes" in f.stem]
latest_withtaxes = max(withtaxes_files, key=lambda f: pd.to_datetime(f.stem.split("_")[0]))

# latest "wotaxes"
wotaxes_files = [f for f in files if "wotaxes" in f.stem]
latest_wotaxes = max(wotaxes_files, key=lambda f: pd.to_datetime(f.stem.split("_")[0]))

print("Latest withtaxes:", latest_withtaxes.name)
print("Latest wotaxes:", latest_wotaxes.name)

# Load them
df_withtaxes = pd.read_parquet(latest_withtaxes)
df_wotaxes   = pd.read_parquet(latest_wotaxes)

df=df_withtaxes
df["Price_wotax"] = df_wotaxes["Price"]


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
    value_vars=["Price", "Price_wotax"],
    var_name="component",
    value_name="price"
)

component_labels = {
    "Price": "Price with Tax",
    "Price_wotax": "Price without Tax"
}

df_melted["component"] = df_melted["component"].map(component_labels)
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
    "Price with Tax": "#A7D5F2",  
    "Price without Tax": "#6DC0B8",   # Powder blue
   # "vat": "#8DDC99"      # Muted salmon/peach  #66CDAA  #8EE5EE
}


# 💹FIG1A💹---------------------------------------------------------------------
fig1a = px.bar(
            df_melted,
            y="Country",
            x="price",
            color="component",
            barmode="group",
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

# --------------------------------------------
# 2. Melt 'Price' and 'Price_wotax' for tidy format
# --------------------------------------------
df_melted_fig2 = df_filtered_fig2.melt(
    id_vars=["Date"],
    value_vars=["Price", "Price_wotax"],
    var_name="Price_Type",
    value_name="Price_Value"
)

df_melted_fig2["Price_Type"] = df_melted_fig2["Price_Type"].map({
    "Price": "Price with Tax",
    "Price_wotax": "Price without Tax"
})



# Use px.line with fill='tozeroy'
fig2 = px.line(
    df_melted_fig2,
    x="Date",
    y="Price_Value",
    color="Price_Type",  # 👈 This tells Plotly to draw separate lines
    color_discrete_map=custom_colors,  # Optional: your custom color map
    line_shape='linear'
)
# Apply fill to area under the line
for trace in fig2.data:
    trace.update(fill='tozeroy')  # turns line into filled area

# Layout
fig2.update_layout(
    title=f"{selected_product} || Historical Price Trend in {selected_country}",
    yaxis_title=f"{selected_product} Price {unit_measure}",
    xaxis_title="Weeks",
    paper_bgcolor="#005680",
    plot_bgcolor="#005680",
    font=dict(size=14, color="#00274d"),
    xaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)"),
    yaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)"),
    legend_title=""
)


st.plotly_chart(fig2, use_container_width=True,key="historical_chart")