"""
Electricity prices for non-household consumers - bi-annual data (from 2007 onwards)

#cd C:\WT\WT_OFFICIAL_APPLICATIONS_REPOSITORY\WT_FAIR_FUEL_COMPARE
"""
import streamlit as st
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px 
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="test", layout="wide")
from utils import apply_style_and_logo

#-------------------------------------------------------------------------------------
df=pd.read_csv("nrg_pc_205_electricity_non-householders_data.csv")

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
#-------------------------------------------------------------------------------------

st.title("📊 Electricity prices for non household consumers - commercial and industrial ")
st.markdown(""" 
            source: EUROSTAT - bi-annual data (from 2007 onwards)
            
            """)

# Get unique consumption bands from the data
available_bands = df["nrg_cons"].unique()


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

custom_colors = {
    "energy": "#F4D06F",  # Soft pastel yellow
    "taxes": "#A1C6EA",   # Powder blue
    "vat": "#F7A072"      # Muted salmon/peach
}
# Multiply price by 1000 (e.g., from €/kWh to €/MWh)
df_melted["price"] = df_melted["price"]*1000
fig = px.bar(
            df_melted,
            y="geo",
            x="price",
            color="component",
            barmode="relative",
            category_orders={"geo": geo_order},
            color_discrete_map=custom_colors,
            title=f"Electricity Price Breakdown by Country || semester {time_band} || {selected_label} consumption band"
)

# Assuming df_latest is filtered for latest time and includes total prices
total_labels = df_filtered.set_index("geo").loc[geo_order]["total"]*1000

fig.add_trace(
            go.Scatter(
                x=total_labels.values,
                y=total_labels.index,
                mode="text",
                text=[f"{v:.1f}" for v in total_labels.values],  # e.g., "251.3"
                textposition="middle right",
                textfont=dict(
                            color="#00274d",   # your color
                            size=16,
                            #family="Bold"  # or any system font with bold style
                            ),
                showlegend=False
            )
)

fig.update_layout(
            height=40* len(df_filtered["geo"].unique()),  # 30px per country (adjust as needed)
            xaxis_title="Electricity Price (€/MWh)",
            yaxis_title="Country (EA20)",
            paper_bgcolor="#005680",
            plot_bgcolor="#005680",
            font=dict(size=14, color="#00274d"),
            legend_title="Component",
            xaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)")
)

# Show Plotly chart
st.plotly_chart(fig, use_container_width=True)