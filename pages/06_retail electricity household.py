"""
Electricity prices for household consumers - bi-annual data (from 2007 onwards)
nrg_pc_204
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
flow_id="nrg_pc_204"
category="electricity"
sub_category="householders"
latest_semester="2025-S1"
latest_month="2025-09-30"
#🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀

#✅------------------------DATA EXTRACTION----------------------------------------------------

df=pd.read_csv(f"data/{latest_semester}_{flow_id}_{category}_{sub_category}_data.csv")
df.info()

available_bands = df["nrg_cons"].unique()
def create_band_label_dict(df, column_name):
    unique_bands = df[column_name].unique()
    band_labels = {band: band for band in unique_bands}
    return band_labels
band_labels = create_band_label_dict(df, "nrg_cons")
print(band_labels)

start_date=min(df["add_formal_time"])


#✅--------------------------------------------------------------------
st.title(f" 🔌 {category} prices | {sub_category} 🏠")
st.markdown(f"""
            ### 📊 Retail {category} price for {sub_category} - cross country view 
            
            """)
st.markdown(""" 
            source: EUROSTAT - bi-annual data (from 2007 onwards)
                        """)

#---------------------------------------------------------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#---------------------------------------------------------------------------------------------------------------------------


st.markdown("""
            #### Electricity - Household

| Band             | Description            | Example Household                                    |Band
|------------------|------------------------|------------------------------------------------------|---|
| KWH_LT1000       | <1,000 kWh/year        | Very small or unoccupied home, vacation property     |DA|
| KWH1000-2499     | 1,000–2,499 kWh/year   | Small apartment, no electric heating                 |DB|
| KWH2500-4999     | 2,500–4,999 kWh/year   | Average household, moderate appliance usage          |DC|
| KWH5000-14999    | 5,000–14,999 kWh/year  | Home with electric heating or EV charging            |DD|
| KWH_GE15000      | ≥15,000 kWh/year       | Large household with high-end appliances, PV system  |DE|
| TOT_KWH          | Total household electricity use | Aggregate                                   |ALL|
                      
            
           """ )
#---------------------------------------------------------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#---------------------------------------------------------------------------------------------------------------------------
# 1️⃣ FIG----------------
available_bands = sorted(df["nrg_cons"].unique().tolist())
selected_band = st.selectbox(
                    "Select consumption band (total average as default) ",
                    options=available_bands,
                    index=available_bands.index("TOT_KWH"),
                    key="band_selectbox_1"  # 👈 Unique key
                )
#selected_band = label_to_code[selected_label]

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
df_filtered = (
    df
    .query("nrg_cons == @selected_band and add_formal_time == @time_band")
    .assign(
        energy=lambda x: x["energy"] * 1000,
        taxes=lambda x: x["taxes"] * 1000,
        vat=lambda x: x["vat"] * 1000,
        total=lambda x: x["total"] * 1000
    )
    .assign(Tax_Share=lambda  x: (x["vat"]+x["taxes"])/x["total"]*100)
)
# **************************************************************************************

geo_order = (
    df_filtered
    .sort_values("total", ascending=True)["geo"]
    .tolist()
)

# Assuming df_latest is filtered for latest time and includes total prices
total_labels = df_filtered.set_index("geo").loc[geo_order]["total"]

# Step 5: Create subplots
fig1 = make_subplots(
    rows=1,
    cols=2,
    shared_xaxes=False,
    horizontal_spacing=0.05,
    column_widths=[0.9, 0.1],
    subplot_titles=(
        f"{category} Price Breakdown by Country [EUR/MWh] | semester {time_band} | consumption band {selected_band}",
        "Tax Share [%]"
    )
)

components = ["energy", "taxes", "vat"]
for comp in components:
    fig1.add_trace(
        go.Bar(
            x=df_filtered.set_index("geo").loc[geo_order][comp],
            y=geo_order,
            name=comp.capitalize(),
            orientation="h",
            marker=dict(color=custom_colors.get(comp, "#cccccc"))
        ),
        row=1,
        col=1
    )

fig1.add_trace(
    go.Scatter(
        x=total_labels.values,
        y=total_labels.index,
        mode="text",
        text=[f"{v:.1f}" for v in total_labels.values],
        textposition="middle right",
        textfont=dict(color="white", size=16),
        showlegend=False
    ),
    row=1,
    col=1
)

# Step 8: Add Tax Share scatter markers (right subplot)
fig1.add_trace(
                go.Scatter(
                            x=df_filtered.set_index("geo").loc[geo_order]["Tax_Share"],
                            y=geo_order,
                            mode="markers",
                            name="Tax Share",
                            marker=dict(
                                color=palette_other[2],
                                size=8,
                                symbol="diamond"
                            )
                        ),
                        row=1,
                        col=2
)

# Step 9: Set layout and styling
fig1.update_layout(
                    barmode="relative",  # ✅ stacked bars
                    height=40 * len(geo_order),
                    xaxis_title="Electricity Price (€/MWh)",
                    yaxis_title="Country (EA20)",
                    paper_bgcolor="#005680",
                    plot_bgcolor="#005680",
                    font=dict(size=14, color="white"),
                    legend_title="Component",
                    margin=dict(t=80, b=40, l=100, r=40),
                    xaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)"),
                    xaxis2=dict(color="white", gridcolor="rgba(255,255,255,0.1)"),
)

# Step 10: Sync y-axis order between both subplots
fig1.update_yaxes(
                    categoryorder="array",
                    categoryarray=geo_order,
                    row=1,
                    col=1
)
fig1.update_yaxes(
                    categoryorder="array",
                    categoryarray=geo_order,
                    row=1,
                    col=2
)

# Step 11: Show chart in Streamlit
st.plotly_chart(fig1, use_container_width=True)


#--------------------------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#---------------------------------------------------------------------------------------------

# 2️⃣ FIG----------------
st.markdown(f"""
            ### 📊 Retail {category} price for {sub_category} - Fiscal impact  
            
            """)
st.markdown(""" 
            source: EUROSTAT - bi-annual data (from 2007 onwards 
                        """)

df_selected_time = df[df["add_formal_time"] == time_band].copy()
# 2. Compute fiscal impact
df_selected_time["fiscal_impact"] = 100 * (df_selected_time["taxes"] + df_selected_time["vat"]) / df_selected_time["total"]
df_selected_time["fiscal_impact"] = df_selected_time["fiscal_impact"].round(1)
df_fiscal=df_selected_time[["geo","nrg_cons","fiscal_impact"]]
#df_fiscal["nrg_cons_label"] = df_fiscal["nrg_cons"].map(band_labels)

df_fiscal["nrg_cons"] = pd.Categorical(df_fiscal["nrg_cons"], categories=band_labels, ordered=True)
df_energy=df_selected_time[["geo","nrg_cons","energy"]]
df_energy["nrg_cons"] = pd.Categorical(df_energy["nrg_cons"], categories=band_labels, ordered=True)


# --------------------------------------
# Titles
# --------------------------------------
#main_title = "Fiscal Impact vs Energy Price by Consumption Band"
subplot_title_left = f"Fiscal Impact || {time_band}"
subplot_title_right = f"Energy Price || {time_band}"

# --------------------------------------
# Setup subplot
# --------------------------------------
fig2 = make_subplots(
    rows=1,
    cols=2,
    subplot_titles=(
        subplot_title_left, 
        subplot_title_right),
    horizontal_spacing=0.1,
    column_widths=[0.5, 0.5]
)

# --------------------------------------
# First subplot – Fiscal Impact
# --------------------------------------
for band_code, band_label in band_labels.items():
    df_band = df_fiscal[df_fiscal["nrg_cons"] == band_code]
    if not df_band.empty:
        fig2.add_trace(
            go.Box(
                y=df_band["fiscal_impact"],
                name=band_label,
                boxpoints="outliers",
                marker=dict(color="#94CCE8"),
                line=dict(width=1),
                customdata=df_band[["geo"]].values,
                hovertemplate="Country: %{customdata[0]}<br>Fiscal Impact: %{y:.1f}%<extra></extra>",
                showlegend=False
            ),
            row=1,
            col=1
        )

# --------------------------------------
# Second subplot – Energy Price (€/MWh)
# --------------------------------------
for band_code, band_label in band_labels.items():
    df_band = df_energy[df_energy["nrg_cons"] == band_code]
    if not df_band.empty:
        fig2.add_trace(
            go.Box(
                y=df_band["energy"] * 1000,  # scale to €/MWh
                name=band_label,
                boxpoints="outliers",
                marker=dict(color="#94CCE8"),
                line=dict(width=1),
                customdata=df_band[["geo"]].values,
                hovertemplate="Country: %{customdata[0]}<br>Energy Price: %{y:.1f} €/MWh<extra></extra>",
                showlegend=False
            ),
            row=1,
            col=2
        )

# --------------------------------------
# Layout and styling
# --------------------------------------
fig2.update_layout(
    height=500,
    #title_x=0.5,
    font=dict(size=14, color="white"),
    paper_bgcolor="#005680",
    plot_bgcolor="#005680",
    margin=dict(t=80, b=60, l=60, r=60)
)

# Axis titles
fig2.update_xaxes(title_text="Consumption Band", row=1, col=1)
fig2.update_yaxes(title_text="Fiscal Impact (%)", row=1, col=1)

fig2.update_xaxes(title_text="Consumption Band", row=1, col=2)
fig2.update_yaxes(title_text="Energy Price (EUR/MWh)", row=1, col=2)

# --------------------------------------
# Display in Streamlit
# --------------------------------------
st.plotly_chart(fig2, use_container_width=True, key="subplot_breakdown_chart")
#--------------------------------------------------------------------------------

# 💹FIG2💹---------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#---------------------------------------------------------------------------------------------------------------------------
#3️⃣ FIG-----------


st.markdown(f"""
            ### 📈 Retail {category} price {sub_category} - single country historical trend
            """)
st.markdown(""" 
            source: EUROSTAT - bi-annual data (from 2007 onwards) 
                        """)

selected_band_2 = st.selectbox(
                    "Select consumption band (total average as default) ",
                    options=available_bands,
                    index=available_bands.index("TOT_KWH"),
                     key="band_selectbox_2"
                )

available_countries=(
                    df["geo"]
                   .unique()
                   .tolist()
)

selected_country = st.selectbox(
                    "Select a Country or an Aggregate (EU27_2020 as default)",  # label
                    options=available_countries,
                    index=available_countries.index("EU27_2020")  # 👈 set default selection by index
                )

# **************************************************************************************
df_filtered_2 = (
    df
    .query("nrg_cons == @selected_band_2  and geo == @selected_country")
    .set_index("add_formal_time")
    .sort_index()
    .assign(
        energy=lambda x: x["energy"] * 1000,
        taxes=lambda x: x["taxes"] * 1000,
        vat=lambda x: x["vat"] * 1000,
        total=lambda x: x["total"] * 1000
    )
    .assign(Tax_Share=lambda  x: (x["vat"]+x["taxes"])/x["total"]*100)
    .assign(variation =lambda x: x["total"].pct_change()*100)
)
df_filtered_2.index = pd.to_datetime(df_filtered_2.index)
# **************************************************************************************
ave_EU=(
   df
   .query("nrg_cons == @selected_band_2  and geo == 'EU27_2020'")
    .set_index("add_formal_time")
    .sort_index()
    .assign(total=lambda x: x["total"] * 1000)  # scale to €/MWh
 
)
ave_EU.index = pd.to_datetime(ave_EU.index) 

# 💹FIG2💹---------------------------------------------------------------------

# -------------------------------
# Subplot Titles Setup (fallback to blank if missing info)
# -------------------------------

if not category or not sub_category:
    title_price = ""

# -------------------------------
# Create Subplots Layout
# -------------------------------
fig3 = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.12,
    row_heights=[0.7, 0.3],
    subplot_titles=(
        f"Retail {category} | price {sub_category} | {selected_country} | {selected_band_2}", 
       "Semester-over-Semester Change [%]")
)

# -------------------------------
# FIG2 Top Plot: Total Price Trend (Lines + Markers)
# -------------------------------
fig3.add_trace(
                go.Scatter(
                    x=df_filtered_2.index,
                    y=df_filtered_2["total"],
                    mode="lines+markers",
                    fill='tozeroy',
                    name=f"Retail {category} price {sub_category}",
                    line=dict(color=palette_blue[1], width=4, dash="dash"),
                    marker=dict(
                        color=palette_blue[1],
                        size=8,
                        symbol="diamond",
                        line=dict(width=1, color='white')
                    )
                ),
                row=1,
                col=1
)
fig3.add_trace(
                go.Scatter(
                    x=ave_EU.index,
                    y=ave_EU["total"],
                    mode="lines+markers",
                    #fill='tozeroy',
                    name=f"Retail {category} price {sub_category} average EU",
                    line=dict(
                        color=palette_other[1], width=2, dash="dash"),
                    marker=dict(
                        color=palette_other[1],
                        size=1,
                        symbol="diamond",
                        line=dict(width=3, color='white')
                    )
                ),
                row=1,
                col=1
)
# -------------------------------
# Bottom Plot: Semester Variation (Bars)
# -------------------------------
fig3.add_trace(
    go.Bar(
        x=df_filtered_2.index,
        y=df_filtered_2["variation"],
        name="Variation (%)",
        marker_color=[
            "#F5B7B1" if v < 0 else "#A9DFBF"
            for v in df_filtered_2["variation"]
        ]
    ),
    row=2,
    col=1
)

# -------------------------------
# Axis Formatting
# -------------------------------
fig3.update_yaxes(
    title_text=f"{category} {sub_category} Price (€/MWh)",
    row=1,
    col=1,
    title_font=dict(color='white'),
    tickfont=dict(color='white'),
    gridcolor="rgba(255,255,255,0.1)"
)

fig3.update_yaxes(
    title_text="Variation (%)",
    row=2,
    col=1,
    title_font=dict(color='white'),
    tickfont=dict(color='white'),
    gridcolor="rgba(255,255,255,0.1)"
)

fig3.update_xaxes(
    title_text="Semester",
    row=2,
    col=1,
    title_font=dict(color='white'),
    tickfont=dict(color='white'),
    gridcolor="rgba(255,255,255,0.1)"
)

# -------------------------------
# Layout Styling
# -------------------------------
fig3.update_layout(
    height=800,
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
st.plotly_chart(fig3, use_container_width=True,key="historical_chart")


#----------------------------------------------------------------------
st.markdown("---")  # horizontal line separator
#----------------------------------------------------------------------
# Prepare CSV for download
csv = df.to_csv(index=True).encode("utf-8")
# Download button
st.download_button(
    label=f"⬇️ Download data for {category} | {sub_category} ",
    data=csv,
    file_name=f"Data_{category}_{sub_category}.csv",
    mime="text/csv",
)

#--------------------------------------------------------------------------------------------
st.divider()  # <--- Streamlit's built-in separator
#---------------------------------------------------------------------------------------------

st.markdown("""
📊 **Understanding Household Electricity Prices Across Consumption Bands**

Electricity prices for households are not uniform — they vary based on how much electricity is consumed annually. This dataset includes price comparisons across different consumption bands to help illustrate these differences.

🔍 **Why do low-consumption households often face higher €/kWh rates?**

Retail electricity prices typically include two main cost components:

1. **Variable (energy-based) charges** – billed per kWh consumed  
2. **Fixed charges** – billed per year or per kW of contracted capacity

These fixed components cover services like:

- ⚡ Grid access and maintenance  
- 🧾 Metering and billing services  
- 🌱 Environmental levies and policy costs (e.g., support for renewables)

When a household uses **very little electricity** (e.g., < 1 000 kWh/year), those fixed costs are spread over a small number of kWh, causing the **average price per kWh to rise** significantly — sometimes exceeding €600/MWh. In contrast, households consuming **2 500–5 000 kWh/year** spread those costs over more usage, leading to lower average €/kWh.

💡 **What does 2 700 kWh/year really mean?**

Most residential users have a contracted power level of 3 kW. If a home uses 2 700 kWh annually, that's equivalent to:

\[
\frac{2\,700 \text{ kWh}}{3 \text{ kW}} = 900 \text{ full-load hours/year}
\]

📉 This translates to a **load factor of ~10%**, meaning the home uses electricity intermittently — lights, appliances, etc., are only active a small fraction of the time. The grid, however, must always be ready to supply the full 3 kW, even if rarely used.

📎 **Key takeaway**:  
- High €/MWh values in low-use households don't necessarily reflect expensive energy, but rather **how fixed costs dominate when consumption is low**.  
- When comparing countries or consumer groups, always consider both **energy use levels** and **tariff structure** to interpret price signals accurately.

📥 Below is the dataset used to generate the current price comparison visualizations.  
You can explore the values directly or download the file for local analysis.
""")