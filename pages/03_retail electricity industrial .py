"""
Electricity prices for non-household consumers - bi-annual data (from 2007 onwards)
nrg_pc_205
#cd C:\WT\WT_OFFICIAL_APPLICATIONS_REPOSITORY\WT_FAIR_FUEL_COMPARE
"""
import streamlit as st
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px 
from pathlib import Path
from plotly.subplots import make_subplots

st.set_page_config(page_title="test", layout="wide")
from utils import apply_style_and_logo
apply_style_and_logo()

#✅------------------------DATA EXTRACTION----------------------------------------------------

df=pd.read_csv("nrg_pc_205_electricity_non-householders_data.csv")
category="Electricity"
subcategory="C&I"
available_bands = df["nrg_cons"].unique()
band_labels = {
    "MWH_LT20": "< 20 MWh",
    "MWH20-499": "20–499 MWh",
    "MWH500-1999": "500–1,999 MWh",
    "MWH2000-19999": "2,000–19,999 MWh",
    "MWH20000-69999": "20,000–69,999 MWh",
    "MWH70000-149999": "70,000–149,999 MWh",
    "MWH_GE150000": "150,000+ MWh",
    "TOT_KWH": "Total Average"
}
#✅--------------------------------------------------------------------
st.title(f"{category} Prices for {subcategory}")
st.markdown("""
            ### 📊 Retail Electricity Price no-household - cross country view 
            
            """)
st.markdown(""" 
            source: EUROSTAT - bi-annual data (from 2007 onwards)
                        """)


# Reverse mapping for lookup
label_to_code = {v: k for k, v in band_labels.items()}
selected_label = st.selectbox(
    "Select consumption band (total average as default) ",
    options=band_labels.values(),
    index=list(band_labels.values()).index("Total Average")  # 👈 default index
)
selected_band = label_to_code[selected_label]

available_semester = df["add_formal_time"].unique()
available_semester_sorted = sorted(available_semester)  # ensure consistent order

# Get the latest (most recent) semester
latest_time = max(available_semester_sorted)

# Set selectbox with default at latest_time
time_band = st.selectbox(
    "Select start semester",
    options=available_semester_sorted,
    index=available_semester_sorted.index(latest_time)
)

# **************************************************************************************
df_filtered = df.query("nrg_cons == @selected_band and add_formal_time == @time_band")
# **************************************************************************************

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

pastel_blue_green = [
    "#A7D5F2", "#94CCE8", "#81C3DD", "#6FBBD3", "#5DB2C8",
    "#6DC0B8", "#7DCFA8", "#8DDC99", "#9CE98A", "#ABF67B"
]


custom_colors = {
    "energy": "#A7D5F2",  
    "taxes": "#6DC0B8",   # Powder blue
    "vat": "#8DDC99"      # Muted salmon/peach  #66CDAA  #8EE5EE
}
# Multiply price by 1000 (e.g., from €/kWh to €/MWh)
df_melted["price"] = df_melted["price"]*1000
# Assuming df_latest is filtered for latest time and includes total prices
total_labels = df_filtered.set_index("geo").loc[geo_order]["total"]*1000

# 💹FIG1A💹---------------------------------------------------------------------
fig1a = px.bar(
            df_melted,
            y="geo",
            x="price",
            color="component",
            barmode="relative",
            category_orders={"geo": geo_order},
            color_discrete_map=custom_colors,
            title=f"{category} Price Breakdown by Country || semester {time_band} || {selected_label} consumption band"
)

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
            xaxis_title="Electricity Price (€/MWh)",
            yaxis_title="Country (EA20)",
            paper_bgcolor="#005680",
            plot_bgcolor="#005680",
            font=dict(size=14, color="white"),
            legend_title="Component",
            xaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)")
)

# Show Plotly chart
st.plotly_chart(fig1a, use_container_width=True)
#-------------------------------------------------------------------------------
df_selected_time = df[df["add_formal_time"] == time_band].copy()

# 2. Compute fiscal impact
df_selected_time["fiscal_impact"] = 100 * (df_selected_time["taxes"] + df_selected_time["vat"]) / df_selected_time["total"]
df_selected_time["fiscal_impact"] = df_selected_time["fiscal_impact"].round(1)
df_fiscal=df_selected_time[["geo","nrg_cons","fiscal_impact"]]
#df_fiscal["nrg_cons_label"] = df_fiscal["nrg_cons"].map(band_labels)

band_order = ["GJ_LT20", "GJ20-199", "GJ_GE200", "TOT_GJ"]
band_order = [
    "MWH_LT20","MWH20-499", "MWH500-1999",  "MWH2000-19999",
    "MWH20000-69999", "MWH70000-149999", "MWH_GE150000", "TOT_KWH"
    ]

df_fiscal["nrg_cons"] = pd.Categorical(df_fiscal["nrg_cons"], categories=band_order, ordered=True)
df_energy=df_selected_time[["geo","nrg_cons","energy"]]
df_energy["nrg_cons"] = pd.Categorical(df_energy["nrg_cons"], categories=band_order, ordered=True)


# 💹FIG1B💹---------------------------------------------------------------------
fig1b = make_subplots(
    rows=1, cols=2,
    subplot_titles=(f"{category}-{subcategory} || Fiscal Impact by Consumption Band || {time_band}",
                    f"{category}-{subcategory} ||Energy Price Component by Consumption Band || {time_band}")
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
#--------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#---------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
st.markdown("""
            ### 📈 Retail Electricity Price no-household - single country historical trend
            """)
st.markdown(""" 
            source: EUROSTAT - bi-annual data (from 2007 onwards)
                        """)

available_countries = df["geo"].unique()
df["total"]=df["total"]*1000 # EUR/MWH
selected_country = st.selectbox("Select country", sorted(available_countries))
selected_bands = [
    "MWH_LT20","MWH20-499", "MWH500-1999",  "MWH2000-19999",
    "MWH20000-69999", "MWH70000-149999", "MWH_GE150000", "TOT_KWH"
    ]

df_filtered = df[
    (df["geo"] == selected_country) &
    (df["nrg_cons"].isin(selected_bands))
]



# 💹FIG2A💹---------------------------------------------------------------------
fig2a = go.Figure()

trendcolors = [
    "#A7D5F2", "#94CCE8", "#81C3DD", "#6FBBD3", "#5DB2C8",
    "#6DC0B8", "#7DCFA8", "#8DDC99", "#9CE98A", "#ABF67B"
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



# Final layout
fig2a.update_layout(
    title=f"Retail {category} Prices historical trend in {selected_country} with TTF Gas Reference",
    xaxis_title="Time",
    yaxis_title="Price (€/MWh)",
    legend_title="Legend"
)

fig2a.update_layout(
            #height=40* len(df_filtered["geo"].unique()),  # 30px per country (adjust as needed)
            yaxis_title=f"{category} {subcategory} Price (€/MWh)",
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