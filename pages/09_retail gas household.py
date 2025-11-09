"""
Gas prices for household consumers - bi-annual data (from 2007 onwards)
nrg_pc_202
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


custom_colors = {
    "energy": "#A7D5F2",  
    "taxes": "#6DC0B8",   # Powder blue
    "vat": "#8DDC99"      # Muted salmon/peach  #66CDAA  #8EE5EE
}


#🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀
FOLDER="EUROSTAT"
flow_id="nrg_pc_202"
category="gas"
sub_category="householders"
latest_semester="2025-S1"
latest_month="2025-09-30"
#🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀


#✅------------------------DATA EXTRACTION-----------------------------------------------------
df=pd.read_csv(f"data/{latest_semester}_{flow_id}_{category}_{sub_category}_data.csv")
df.info()
#1 GJ = 0.2778 MWh (approx.)
#--Band defintion
available_bands = df["nrg_cons"].unique()
def create_band_label_dict(df, column_name):
    unique_bands = df[column_name].unique()
    band_labels = {band: band for band in unique_bands}
    return band_labels
band_labels = create_band_label_dict(df, "nrg_cons")
last_value = list(band_labels.values())[-1]
print(band_labels)


start_date=min(df["add_formal_time"])

ttf_df = pd.read_csv(f"data/{latest_month}_ttf.csv", parse_dates=['Date'])
ttf_df=ttf_df.query("Date >=@start_date")

#✅--------------------------------------------------------------------
st.title(f" 🔥 {category} prices for {sub_category} 🏠")
st.markdown(f"""
            ### 📊 Retail {category} price for {sub_category} - cross country view 
            
            """)
st.markdown(""" 
            source: EUROSTAT - bi-annual data (from 2007 onwards)
                        """)

#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
st.markdown("""#### Gas - Household Conversion: 1 GJ ≈ 26.85 m³ of natural gas (based on EU average HHV)

| Band       | Description              | Example Usage                             | Est. m³/year   |
|------------|--------------------------|--------------------------------------------|----------------|
| GJ_LT20    | <20 GJ/year              | Small apartment or single-person home      | <537           |
| GJ20-199   | 20–199 GJ/year           | Average single-family home                 | 537–5,345      |
| GJ_GE200   | 200+ GJ/year             | Large home or villa                        | 5,370+         |
| TOT_GJ     | Total household gas consumption | Aggregate                            | -              |
""")

#---------------------------------------------------------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#--------------------------------------------------------------------------------------------

# Reverse mapping for lookup
label_to_code = {v: k for k, v in band_labels.items()}
selected_label = st.selectbox(
    "Select consumption band (GJ_GE200 as default) ",
    options=band_labels.values(),
    index=list(band_labels.values()).index("GJ_LT20")  # 👈 default index
)
selected_band = label_to_code[selected_label]
available_semester = df["add_formal_time"].unique()
available_semester_sorted = sorted(available_semester)  # ensure consistent order

# Get the latest (most recent) semester
latest_time = max(available_semester_sorted)

# Set selectbox with default at latest_time
time_band = st.selectbox(
    "Select start semester (the latest available as default)",
    options=available_semester_sorted,
    index=len(available_semester_sorted) - 1
)

# **************************************************************************************
df_filtered = df.query("nrg_cons == @selected_band and add_formal_time == @time_band")
# **************************************************************************************

# FIG1a------------------------------------------------------------------------------------------

df_melted = df_filtered.melt(
    id_vars=["geo", "add_formal_time", "nrg_cons"],
    value_vars=["energy", "taxes", "vat"],
    var_name="component",
    value_name="price"
)

geo_order = (
    df_filtered
    .sort_values("total", ascending=False)["geo"]
    .tolist()
)

df_melted["price"] = df_melted["price"]*1000  # Multiply price by 1000 (e.g., from €/kWh to €/MWh)
# 💹FIG1A💹---------------------------------------------------------------------
fig1a = px.bar(
            df_melted,
            y="geo",
            x="price",
            color="component",
            barmode="relative",
            category_orders={"geo": geo_order},
            color_discrete_map=custom_colors,
            title=f"{category} price breakdown by country || semester {time_band} || {selected_label} consumption band"
)

# Assuming df_latest is filtered for latest time and includes total prices
total_labels = df_filtered.set_index("geo").loc[geo_order]["total"]*1000

fig1a.add_trace(
            go.Scatter(
                x=total_labels.values,
                y=total_labels.index,
                mode="text",
                text=[f"{v:.1f}" for v in total_labels.values],  # e.g., "251.3"
                textposition="middle right",
                textfont=dict(
                            color="white",   # your color
                            size=16,
                            #family="Bold"  # or any system font with bold style
                            ),
                showlegend=False
            )
)

fig1a.update_layout(
            height=40* len(df_filtered["geo"].unique()),  # 30px per country (adjust as needed)
            xaxis_title=f"{category} Price (€/MWh)",
            yaxis_title="Country (EA20)",
            paper_bgcolor="#005680",
            plot_bgcolor="#005680",
            font=dict(size=14, color="#00274d"),
            legend_title="Component",
            xaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)")
)

# Show Plotly chart
st.plotly_chart(fig1a, use_container_width=True, key="price_breakdown_chart")

#-------------------------------------------------------------------------------

# 1. Filter for the selected time band
df_selected_time = df[df["add_formal_time"] == time_band].copy()

# 2. Compute fiscal impact
df_selected_time["fiscal_impact"] = 100 * (df_selected_time["taxes"] + df_selected_time["vat"]) / df_selected_time["total"]
df_selected_time["fiscal_impact"] = df_selected_time["fiscal_impact"].round(1)
df_fiscal=df_selected_time[["geo","nrg_cons","fiscal_impact"]]
#df_fiscal["nrg_cons_label"] = df_fiscal["nrg_cons"].map(band_labels)

band_order = ["GJ_LT20", "GJ20-199", "GJ_GE200", "TOT_GJ"]
df_fiscal["nrg_cons"] = pd.Categorical(df_fiscal["nrg_cons"], categories=band_order, ordered=True)
df_energy=df_selected_time[["geo","nrg_cons","energy"]]
df_energy["nrg_cons"] = pd.Categorical(df_energy["nrg_cons"], categories=band_order, ordered=True)


# 💹FIG1B💹---------------------------------------------------------------------
fig1b = make_subplots(
    rows=1, cols=2,
    subplot_titles=(f"{category}-{sub_category} || Fiscal Impact by Consumption Band || {time_band}",
                    f"{category}-{sub_category} ||Energy Price Component by Consumption Band || {time_band}")
)

# First subplot - Fiscal Impact
for band in band_order:
    values = df_fiscal[df_fiscal["nrg_cons"] == band]["fiscal_impact"]
    if not values.empty:
        fig1b.add_trace(
            go.Box(
                y=values,
                name=band_labels.get(band, band),
                boxpoints="outliers",
                marker=dict(color="#94CCE8"),
                line=dict(width=1),
                customdata=df_fiscal[df_fiscal["nrg_cons"] == band][["geo"]].values,
                hovertemplate="Country: %{customdata[0]}<br>Fiscal Impact: %{y:.1f}%<extra></extra>",
                showlegend=False# ✅ legend visible
            ),
            row=1, col=1
        )

# Second subplot - Energy Price (same categories as first)
for band in band_order:
    values = df_energy[df_energy["nrg_cons"] == band]["energy"] * 1000
    if not values.empty:
        fig1b.add_trace(
            go.Box(
                y=values,
                name=band_labels.get(band, band),  # same x-category label
                boxpoints="outliers",
                marker=dict(color="#94CCE8"),  # different color if needed
                line=dict(width=1),
                customdata=df_energy[df_energy["nrg_cons"] == band][["geo"]].values,
                hovertemplate="Country: %{customdata[0]}<br>Energy Price: %{y:.1f}<extra></extra>",
                showlegend=False  # ✅ legend no visible
            ),
            row=1, col=2
        )


# Layout
fig1b.update_layout(
    xaxis1=dict(title="Consumption Band"),
    yaxis1=dict(title="Fiscal Impact (%)"),
    xaxis2=dict(title="Consumption Band"),
    yaxis2=dict(title="Energy Price (EUR/MWh)"),
    title_text="Fiscal Impact vs Energy Price by Consumption Band",
    height=400,
    showlegend=True
)


# Display in Streamlit
st.plotly_chart(fig1b, use_container_width=True, key="subplot_breakdown_chart")

#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
st.markdown(f"""
            ### 📈 Retail {category} price {sub_category} - single country historical trend
            """)
st.markdown(""" 
            source: EUROSTAT - bi-annual data (from 2007 onwards) || TTF prices : Word Bank || Exchage rate USD EUR : ECB
                        """)


available_countries = df["geo"].unique()
df["total"]=df["total"]*1000 # EUR/MWH
selected_country = st.selectbox("Select country", sorted(available_countries))
selected_bands = ["GJ_LT20", "GJ20-199", "GJ_GE200"]
df_filtered = df[
    (df["geo"] == selected_country) &
    (df["nrg_cons"].isin(selected_bands))
]


# 💹FIG2A💹---------------------------------------------------------------------
fig2a = go.Figure()

trendcolors = [
    "#A7D5F2",   "#5DB2C8",
    "#6DC0B8",   "#9CE98A", "#ABF67B"
]

# Loop with index so you can assign colors
for i, band in enumerate(df_filtered['nrg_cons'].unique()):
    df_band = df_filtered[df_filtered['nrg_cons'] == band]
    fig2a.add_trace(go.Scatter(
        x=df_band['add_formal_time'],
        y=df_band['total'],
        mode='lines+markers',
        name=f'Retail ({band})',
        line=dict(color=trendcolors[i % len(trendcolors)])  # ✅ assign color
    ))

# Daily TTF line (optionally filter for same time range)
fig2a.add_trace(go.Scatter(
    x=ttf_df['Date'],
    y=ttf_df['price_eur/mwh'],  # replace 'Price' with your actual column name
    mode='lines',
    name='TTF Gas Price (Daily)',
    line=dict(dash='dot', color="#ABF67B")
))

# Final layout
fig2a.update_layout(
    title=f"Retail {category} prices historical trend in {selected_country} with TTF monthly price",
    xaxis_title="Time",
    yaxis_title="Price (€/MWh)",
    legend_title="Legend"
)

fig2a.update_layout(
            #height=40* len(df_filtered["geo"].unique()),  # 30px per country (adjust as needed)
            yaxis_title=f"{category} {sub_category} Price (€/MWh)",
            xaxis_title="Semester",
            paper_bgcolor="#005680",
            plot_bgcolor="#005680",
            font=dict(size=14, color="#00274d"),
            #legend_title="Component",
            xaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)")
)

# Show Plotly chart
st.plotly_chart(fig2a, use_container_width=True,key="historical_chart")




