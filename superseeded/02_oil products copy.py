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
import numpy as np

st.set_page_config(page_title="Dashboard", layout="wide")
from utils import apply_style_and_logo
apply_style_and_logo()

#GRAPHICS----------------------------------------------
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

units_selection = [
    "€/1000L",   # Super_95
    "€/1000L",   # Diesel
    "€/1000L",   # Heating_Oil
    "€/ton", # Heavy_Fuel_Oil
    "€/ton", # Heavy_Fuel_Oil_Type_III
    "€/1000L"    # GPL
]


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

#df is the final merged dataframe
df=df_withtaxes
df["Price_wotax"] = df_wotaxes["Price"]
P_t = df["Price"].values
P_next = np.roll(P_t, -1)
price_delta = (P_t - P_next) / P_next
price_delta[-1] = np.nan
df["Price_delta"] = price_delta*100 #in %
#df["Price_delta"] = df["Price"].pct_change(fill_method=None).fillna(0)
df["Price_delta_forward"] = df["Price"].pct_change(periods=-1)
#df["Price_delta"] = df["Price"].pct_change(periods=-1)
df["Tax_impact"]=(df["Price"]-df["Price_wotax"])/df["Price"]*100


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
    id_vars=["Country", "Date", "Fuel_Type","Tax_impact"],
    value_vars=["Price", "Price_wotax","Tax_impact"],
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


# Define the figure with better spacing and widths
fig1 = make_subplots(
    rows=1,
    cols=2,
    shared_xaxes=True,
    horizontal_spacing=0.05,
    column_widths=[0.9, 0.1],
    subplot_titles=(
        f"{selected_product} || Price Breakdown by Country || Week {selected_week}",
        "Tax Burden [%]"
    )
)

# Bar chart for price breakdown (grouped bars, one per component)
for component, comp_df in df_melted.groupby("component"):
    fig1.add_trace(
        go.Bar(
            y=comp_df["Country"],
            x=comp_df["price"],
            name=component,
            orientation='h',
            marker_color=custom_colors.get(component, None)
        ),
        row=1,
        col=1
    )

# Add total price labels as a Scatter text overlay
total_labels = df_filtered.set_index("Country").loc[geo_order]["Price"]
fig1.add_trace(
    go.Scatter(
        x=total_labels.values,
        y=total_labels.index,
        mode="text",
        text=[f"{v:.0f}" for v in total_labels.values],
        textposition="middle right",
        textfont=dict(color="white", size=16),
        showlegend=False
    ),
    row=1,
    col=1  # Make sure it's added to the correct subplot
)

# Add tax burden as a line plot in second subplot
fig1.add_trace(
    go.Scatter(
        y=df_melted["Country"],
        x=df_melted["Tax_impact"],
        mode="markers",
        name="Tax Burden [%]",
        #line=dict(color="red", width=4, dash="dash"),
        marker=dict(
            color=palette_other[2],
            size=8,
            symbol="diamond",
            #line=dict(width=1, color='white')
        )
    ),
    row=1,
    col=2
)

# Get the unit for the selected product
unit_measure = dict(zip(products_selection, units_selection)).get(selected_product, "")

# Configure layout and styling
fig1.update_layout(
    height=40 * len(df_filtered["Country"].unique()),
    xaxis_title=f"{category} Price {unit_measure}",
    yaxis_title="Country",
    paper_bgcolor="#005680",
    plot_bgcolor="#005680",
    font=dict(size=14, color="#ffffff"),
    legend_title="Component",
    barmode='group',
)

# Apply consistent axis formatting
fig1.update_xaxes(color="white", gridcolor="rgba(255,255,255,0.1)", row=1, col=1)
fig1.update_yaxes(color="white", gridcolor="rgba(255,255,255,0.1)", categoryorder="array", categoryarray=geo_order)

fig1.update_layout(
    height=1000,
    showlegend=True,
    paper_bgcolor="#005680",
    plot_bgcolor="#005680",
    font=dict(size=14, color="#ffffff"),
    legend_title="Price Type",
)

# Show in Streamlit
st.plotly_chart(fig1, use_container_width=True, key="price_breakdown_chart")

#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
st.markdown("""
            ### 📈 Oil Products Price - single country historical trend
            """)
st.markdown(""" 
            source: EU DG Energy - weekly data - nominals terms
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

# --- Step 1: Melt dataframe ---
df_melted_fig2 = df_filtered_fig2.melt(
    id_vars=["Date", "Price_delta_forward"],  # keep delta for later
    value_vars=["Price", "Price_wotax"],
    var_name="Price_Type",
    value_name="Price_Value"
)

# Optional: map price type labels
df_melted_fig2["Price_Type"] = df_melted_fig2["Price_Type"].map({
    "Price": "Price with Tax",
    "Price_wotax": "Price without Tax"
})

# --- Step 2: Create subplot ---
fig2 = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.1,
    subplot_titles=(
        f"{selected_product} || Historical Prices || Week {selected_week}",
        "Weekly Variation [%]"
    )
)

# --- Step 3: Add filled lines (Price and Price_wotax) to row=1 ---
for price_type, subdf in df_melted_fig2.groupby("Price_Type"):
    fig2.add_trace(
        go.Scatter(
            x=subdf["Date"],
            y=subdf["Price_Value"],
            name=price_type,
            fill="tozeroy",
            mode="lines",
            line=dict(
                color=custom_colors.get(price_type, None),
                shape="linear"
            )
        ),
        row=1,
        col=1
    )

# --- Step 4: Add Price_delta_forward to row=2 ---
fig2.add_trace(
    go.Bar(
        x=df_filtered_fig2["Date"],
        y=df_filtered_fig2["Price_delta_forward"] * 100,  # Convert to percentage
        name="Weekly % Change",
        marker_color=palette_other[4]
    ),
    row=2,
    col=1
)

# --- Step 5: Update layout ---
fig2.update_layout(
    height=600,
    showlegend=True,
    paper_bgcolor="#005680",
    plot_bgcolor="#005680",
    font=dict(size=14, color="#ffffff"),
    legend_title="Price Type",
)

# Format axes
#fig2.update_xaxes(title_text="Date", color="white", gridcolor="rgba(255,255,255,0.1)")
fig2.update_yaxes(title_text=f"Price [{unit_measure}]", color="white", row=1, col=1)
fig2.update_yaxes(title_text="Δ [%]", color="white", row=2, col=1)

# Optional: reverse x-axis if you want most recent on left
# fig2.update_xaxes(autorange="reversed")

# In Streamlit
st.plotly_chart(fig2, use_container_width=True, key="historical_price_chart")