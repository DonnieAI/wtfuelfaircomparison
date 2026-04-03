"""
Electricity prices for household consumers - bi-annual data (from 2007 onwards)
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
flow_id="nrg_pc_205"
category="electricity"
sub_category="C&I"
latest_semester="2025-S1"
latest_month="2025-09-30"
#🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀

#✅------------------------DATA EXTRACTION----------------------------------------------------

df_ele=pd.read_csv(f"data/{latest_semester}_{flow_id}_{category}_{sub_category}_data.csv")
df_ele.info()

available_bands_ele = df_ele["nrg_cons"].unique()
def create_band_label_dict(df_ele, column_name):
    unique_bands_ele = df_ele[column_name].unique()
    band_labels_ele = {band: band for band in unique_bands_ele}
    return band_labels_ele
band_labels_ele = create_band_label_dict(df_ele, "nrg_cons")
print(band_labels_ele)

start_date=min(df_ele["add_formal_time"])


#🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀
FOLDER="EUROSTAT"
flow_id="nrg_pc_203"
category="gas"
sub_category="C&I"
latest_semester="2025-S1"
latest_month="2025-10-31"
#🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀

df_gas=pd.read_csv(f"data/{latest_semester}_{flow_id}_{category}_{sub_category}_data.csv")
df_gas.info()

#--Band defintion
available_bands_gas = df_gas["nrg_cons"].unique()
def create_band_label_dict(df, column_name):
    unique_bands_gas = df[column_name].unique()
    band_labels_gas = {band: band for band in unique_bands_gas}
    return band_labels_gas
band_labels_gas = create_band_label_dict(df_gas, "nrg_cons")
last_value = list(band_labels_gas.values())[-1]
print(band_labels_gas)

#✅--------------------------------------------------------------------
st.title("⚡🔥 Electricity-to-Gas Price Ratio for Industrial Consumers 🏭")

st.markdown(
    """
    ### 📊 Cross-country comparison of electricity-to-gas price ratios for industrial consumers  
    Includes both **energy-only** and **total-price** ratios
    """
)

st.markdown(
    """
    **Source:** Eurostat, bi-annual data (2007 onwards)
    """
)

#---------------------------------------------------------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#--------------------------------------------------------

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
        #### 
        
        Electricity - Commercial & Industrial (C&I)

    | Band              | Description               | Example Facility                                   |
    |-------------------|---------------------------|----------------------------------------------------|
    | MWH_LT20          | <20 MWh/year              | Small retail store or café                         |
    | MWH20-499         | 20–499 MWh/year           | Hotel, small warehouse, or office block            |
    | MWH500-1999       | 500–1,999 MWh/year        | Medium factory, school, hospital                   |
    | MWH2000-19999     | 2,000–19,999 MWh/year     | Industrial laundries, large supermarkets           |
    | MWH20000-69999    | 20,000–69,999 MWh/year    | Data centers, pharma plants, casting workshops     |
    | MWH70000-149999   | 70,000–149,999 MWh/year   | Steel rolling, chlorine plants                     |
    | MWH_GE150000      | ≥150,000 MWh/year         | Aluminum smelters, hyperscale data centers         |
    | TOT_KWH           | Total industrial electricity use | Aggregate  
        
    """)

with col2:
    st.markdown("""
          
        ####
        Gas - Commercial & Industrial (C&I)    
        

    | Band               | Description            | Example Facility                        | Est. m³/year       |
    |--------------------|------------------------|-----------------------------------------|--------------------|
    | GJ_LT1000          | <1,000 GJ/year         | Small restaurant or office              | <26,850            |
    | GJ1000-9999        | 1,000–9,999 GJ/year    | Medium hotel, school                    | 26,850–268,400     |
    | GJ10000-99999      | 10,000–99,999 GJ/year  | Large bakery, brewery                   | 268,500–2,684,900  |
    | GJ100000-999999    | 100,000–999,999 GJ/year| Chemical plants                         | 2.685M–26.85M      |
    | GJ1000000-3999999  | 1M–3.99M GJ/year       | Steel mills, fertilizer plants          | 26.85M–107.3M      |
    | GJ_GE4000000       | ≥4M GJ/year            | Petrochemical complexes                 | 107.4M+            |
    | TOT_GJ             | Total industrial gas consumption | Aggregate                     | -                  |       
            
                
                """)

#---------------------------------------------------------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#--------------------------------------------------------

available_bands_ele = sorted(df_ele["nrg_cons"].unique().tolist())



col1, col2 = st.columns(2)
with col1:
    selected_band_ele = st.selectbox(
                        "Select consumption band (total average as default) ",
                        options=available_bands_ele,
                        index=available_bands_ele.index("MWH20000-69999"),
                        key="band_selectbox_ele"  # 👈 Unique key
                    )


with col2:
        selected_band_gas = st.selectbox(
                        "Select consumption band (total average as default) ",
                        options=band_labels_gas.values(),
                        index=list(band_labels_gas.values()).index("GJ10000-99999"),
                        key="band_selectbox_gas"  # 👈 Unique key
                    )



available_semester = df_ele["add_formal_time"].unique()
available_semester_sorted = sorted(available_semester)  # ensure consistent order
# Get the latest (most recent) semester
latest_time = max(available_semester_sorted)



# **************************************************************************************
df_ele_filtered = (
    df_ele
    .query("nrg_cons == @selected_band_ele and add_formal_time == @latest_time")
    .assign(
        energy=lambda x: x["energy"] * 1000,
        taxes=lambda x: x["taxes"] * 1000,
        vat=lambda x: x["vat"] * 1000,
        total=lambda x: x["total"] * 1000
    )
    .assign(Tax_Share=lambda  x: (x["vat"]+x["taxes"])/x["total"]*100)
)
# *************************************************************************************


# **************************************************************************************
df_gas_filtered = (
    df_gas
    .query("nrg_cons == @selected_band_gas and add_formal_time == @latest_time")
    .assign(
        energy=lambda x: x["energy"] * 1000,
        taxes=lambda x: x["taxes"] * 1000,
        vat=lambda x: x["vat"] * 1000,
        total=lambda x: x["total"] * 1000
    )
    .assign(Tax_Share=lambda  x: (x["vat"]+x["taxes"])/x["total"]*100)
)
# *************************************************************************************


# ============================================================
# 1. Keep only the columns needed for the comparison
# ============================================================
df_ratio = (
    df_ele_filtered[["geo", "energy", "total"]]
    .rename(columns={
        "energy": "electricity_energy",
        "total": "electricity_total"
    })
    .merge(
        df_gas_filtered[["geo", "energy", "total"]]
        .rename(columns={
            "energy": "gas_energy",
            "total": "gas_total"
        }),
        on="geo",
        how="inner"
    )
    .assign(
        ratio_energy=lambda x: x["electricity_energy"] / x["gas_energy"],
        ratio_total=lambda x: x["electricity_total"] / x["gas_total"]
    )
    .sort_values("ratio_total", ascending=True)
    .reset_index(drop=True)
)

#print(df_ratio)
df_ratio_clean = df_ratio[["geo", "ratio_energy", "ratio_total"]]
print(df_ratio_clean)

geo_order = (
    df_ratio_clean
    .sort_values("ratio_total", ascending=True)["geo"]
    .tolist()
)

df_plot = df_ratio_clean.set_index("geo").loc[geo_order].reset_index()

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=df_plot["geo"],
        y=df_plot["ratio_energy"],
        name="Electricity / Gas - Energy only",
        text=[f"{v:.2f}" for v in df_plot["ratio_energy"]],
        textposition="outside",
        marker_color=palette_blue[3],   # blue
        
    )
)

fig.add_trace(
    go.Bar(
        x=df_plot["geo"],
        y=df_plot["ratio_total"],
        name="Electricity / Gas - Total cost",
        text=[f"{v:.2f}" for v in df_plot["ratio_total"]],
        textposition="outside",
        marker_color=palette_green[2],   # blue
    )
)

fig.update_layout(
    title=f"Electricity to Gas Price Ratios by Country | {latest_time}",
    xaxis_title="Country",
    yaxis_title="Ratio",
    barmode="group",
    template="plotly_white",
    height=700,
    width=1200
)

st.plotly_chart(fig, use_container_width=True)


# ============================================================
# 1. Consumption band selectors
#    You need one band for electricity and one for gas
# ============================================================
selected_band_ele_2 = st.selectbox(
    "Select electricity consumption band",
    options=sorted(df_ele["nrg_cons"].dropna().unique().tolist()),
    key="band_ele_ratio_trend"
)

selected_band_gas_2 = st.selectbox(
    "Select gas consumption band",
    options=sorted(df_gas["nrg_cons"].dropna().unique().tolist()),
    key="band_gas_ratio_trend"
)

# ============================================================
# 2. Country selector
#    EU27_2020 shown by default + selected country
# ============================================================
available_countries = sorted(
    list(set(df_ele["geo"].dropna().unique()).intersection(set(df_gas["geo"].dropna().unique())))
)

default_country = "EU27_2020" if "EU27_2020" in available_countries else available_countries[0]

selected_country_ratio = st.selectbox(
    "Select a country (EU27_2020 is always shown as benchmark)",
    options=available_countries,
    index=available_countries.index(default_country),
    key="country_ratio_trend"
)

# ============================================================
# 3. Build ratio dataframe over time
# ============================================================
df_ele_trend = (
    df_ele
    .query("nrg_cons == @selected_band_ele_2")[["geo", "add_formal_time", "energy", "total"]]
    .rename(columns={
        "energy": "ele_energy",
        "total": "ele_total"
    })
    .assign(
        ele_energy=lambda x: x["ele_energy"] * 1000,
        ele_total=lambda x: x["ele_total"] * 1000
    )
)

df_gas_trend = (
    df_gas
    .query("nrg_cons == @selected_band_gas_2")[["geo", "add_formal_time", "energy", "total"]]
    .rename(columns={
        "energy": "gas_energy",
        "total": "gas_total"
    })
    .assign(
        gas_energy=lambda x: x["gas_energy"] * 1000,
        gas_total=lambda x: x["gas_total"] * 1000
    )
)

df_ratio_trend = (
    df_ele_trend
    .merge(
        df_gas_trend,
        on=["geo", "add_formal_time"],
        how="inner"
    )
    .assign(
        ratio_energy=lambda x: x["ele_energy"] / x["gas_energy"],
        ratio_total=lambda x: x["ele_total"] / x["gas_total"]
    )
)

df_ratio_trend["add_formal_time"] = pd.to_datetime(df_ratio_trend["add_formal_time"])

# ============================================================
# 4. Filter selected country and EU27 benchmark
# ============================================================
df_country_ratio = (
    df_ratio_trend
    .query("geo == @selected_country_ratio")
    .sort_values("add_formal_time")
    .set_index("add_formal_time")
    .assign(
        variation_total=lambda x: x["ratio_total"].pct_change() * 100
    )
)

df_eu_ratio = (
    df_ratio_trend
    .query("geo == 'EU27_2020'")
    .sort_values("add_formal_time")
    .set_index("add_formal_time")
)

# ============================================================
# 5. Plot
# ============================================================
fig_ratio = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.12,
    row_heights=[0.7, 0.3],
    subplot_titles=(
        f"Electricity-to-Gas Price Ratio | {selected_country_ratio} vs EU27_2020",
        "Semester-over-Semester Change of Total Ratio [%]"
    )
)

# ------------------------------------------------------------
# Top chart: selected country ratios
# ------------------------------------------------------------
fig_ratio.add_trace(
    go.Scatter(
        x=df_country_ratio.index,
        y=df_country_ratio["ratio_energy"],
        mode="lines+markers",
        name=f"{selected_country_ratio} - Energy only ratio",
        line=dict(color="#4C78A8", width=3),
        marker=dict(size=8)
    ),
    row=1,
    col=1
)

fig_ratio.add_trace(
    go.Scatter(
        x=df_country_ratio.index,
        y=df_country_ratio["ratio_total"],
        mode="lines+markers",
        name=f"{selected_country_ratio} - Total price ratio",
        line=dict(color="#F58518", width=3),
        marker=dict(size=8)
    ),
    row=1,
    col=1
)

# ------------------------------------------------------------
# Top chart: EU27 benchmark
# ------------------------------------------------------------
fig_ratio.add_trace(
    go.Scatter(
        x=df_eu_ratio.index,
        y=df_eu_ratio["ratio_energy"],
        mode="lines+markers",
        name="EU27_2020 - Energy only ratio",
        line=dict(color="#72B7B2", width=2, dash="dot"),
        marker=dict(size=6)
    ),
    row=1,
    col=1
)

fig_ratio.add_trace(
    go.Scatter(
        x=df_eu_ratio.index,
        y=df_eu_ratio["ratio_total"],
        mode="lines+markers",
        name="EU27_2020 - Total price ratio",
        line=dict(color="#E45756", width=2, dash="dot"),
        marker=dict(size=6)
    ),
    row=1,
    col=1
)

# ------------------------------------------------------------
# Bottom chart: variation of selected country's total ratio
# ------------------------------------------------------------
fig_ratio.add_trace(
    go.Bar(
        x=df_country_ratio.index,
        y=df_country_ratio["variation_total"],
        name="Δ Total ratio [%]",
        marker_color=[
            "#F5B7B1" if pd.notnull(v) and v < 0 else "#A9DFBF"
            for v in df_country_ratio["variation_total"]
        ]
    ),
    row=2,
    col=1
)

# ============================================================
# 6. Axis formatting
# ============================================================
fig_ratio.update_yaxes(
    title_text="Ratio",
    row=1,
    col=1,
    title_font=dict(color="white"),
    tickfont=dict(color="white"),
    gridcolor="rgba(255,255,255,0.1)"
)

fig_ratio.update_yaxes(
    title_text="Variation (%)",
    row=2,
    col=1,
    title_font=dict(color="white"),
    tickfont=dict(color="white"),
    gridcolor="rgba(255,255,255,0.1)"
)

fig_ratio.update_xaxes(
    title_text="Semester",
    row=2,
    col=1,
    title_font=dict(color="white"),
    tickfont=dict(color="white"),
    gridcolor="rgba(255,255,255,0.1)"
)

# ============================================================
# 7. Layout
# ============================================================
fig_ratio.update_layout(
    height=850,
    paper_bgcolor="#005680",
    plot_bgcolor="#005680",
    font=dict(size=14, color="white"),
    margin=dict(t=100, l=80, r=50, b=60),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
        font=dict(color="white")
    )
)

st.plotly_chart(fig_ratio, use_container_width=True, key="ratio_trend_chart")