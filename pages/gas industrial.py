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
import pandas as pd
from pathlib import Path
from plotly.subplots import make_subplots

st.set_page_config(page_title="Dashboard", layout="wide")
from utils import apply_style_and_logo
apply_style_and_logo()

#-------------------------------------------------------------------------------------
df=pd.read_csv("data/nrg_pc_202_gas_non_householders_data.csv")
category="gas"
subcategory="industrial"
#1 GJ = 0.2778 MWh (approx.)
available_bands = df["nrg_cons"].unique()
band_labels = {
    "GJ_LT20": "< 5.6 MWh",
    "GJ20-199": "5.6–55.3 MWh",
    "GJ_GE200": "55.6+ MWh",
    "TOT_GJ": "Total Average"
}
#-------------------------------------------------------------------------------------
ttf_df = pd.read_csv("data/Dutch_TTF.csv", parse_dates=['Date'])


st.title(" Retail Gas Prices for no-household consumers - commercial and industrial ")
st.markdown("""
            ### 📊 Gas Price cross country view 
            
            """)
st.markdown(""" 
            source: EUROSTAT - bi-annual data (from 2007 onwards)
                        """)

# Reverse mapping for lookup
label_to_code = {v: k for k, v in band_labels.items()}
selected_label = st.selectbox(
    "Select consumption band (total average as default) ",
    options=band_labels.values(),
    index=list(band_labels.values()).index("55.6+ MWh")  # 👈 default index
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
    index=len(available_semester_sorted) - 2
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
    "energy": "#7FDBFF",  # Soft pastel yellow
    "taxes": "#77DD77",   # Powder blue
    "vat": "#8EE5EE"      # Muted salmon/peach  #66CDAA  #8EE5EE
}

df_melted["price"] = df_melted["price"]*1000  # Multiply price by 1000 (e.g., from €/kWh to €/MWh)
fig1 = px.bar(
            df_melted,
            y="geo",
            x="price",
            color="component",
            barmode="relative",
            category_orders={"geo": geo_order},
            color_discrete_map=custom_colors,
            title=f"Retail Gas Price Breakdown by Country || semester {time_band} || {selected_label} consumption band"
)

# Assuming df_latest is filtered for latest time and includes total prices
total_labels = df_filtered.set_index("geo").loc[geo_order]["total"]*1000

fig1.add_trace(
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

fig1.update_layout(
            height=40* len(df_filtered["geo"].unique()),  # 30px per country (adjust as needed)
            xaxis_title=f"Retail {category} Price (€/MWh)",
            yaxis_title="Country (EA20)",
            paper_bgcolor="#005680",
            plot_bgcolor="#005680",
            font=dict(size=14, color="#00274d"),
            legend_title="Component",
            xaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)")
)

# Show Plotly chart
st.plotly_chart(fig1, use_container_width=True, key="price_breakdown_chart")
#--------------------fg1b data preparation---------------------------------------------------------

# 1. Filter for the selected time band
df_selected_time = df[df["add_formal_time"] == time_band].copy()

# 2. Compute fiscal impact
df_selected_time["fiscal_impact"] = 100 * (df_selected_time["taxes"] + df_selected_time["vat"]) / df_selected_time["total"]
df_selected_time["fiscal_impact"] = df_selected_time["fiscal_impact"].round(1)
df_fiscal=df_selected_time[["geo","nrg_cons","fiscal_impact"]]
#df_fiscal["nrg_cons_label"] = df_fiscal["nrg_cons"].map(band_labels)


band_order = ["GJ_LT20", "GJ20-199", "GJ_GE200", "TOT_GJ"]
df_fiscal["nrg_cons"] = pd.Categorical(df_fiscal["nrg_cons"], categories=band_order, ordered=True)

# Create a single-subplot figure
# Create subplot with 1 row and 2 columns
fig1b = make_subplots(rows=1, cols=2, subplot_titles=(f"Fiscal Impact by Consumption Band  {time_band}", "Plot B"))

# Loop through each band and add box
for band in band_order:
    values = df_fiscal[df_fiscal["nrg_cons"] == band]["fiscal_impact"]
    if not values.empty:
        fig1b.add_trace(
            go.Box(
        y=values,
        name=band_labels.get(band, band),
        boxpoints="outliers",
        marker=dict(color="#FFA07A"),
        line=dict(width=1),
        # 👇 Add custom hover data
        customdata=df_fiscal[df_fiscal["nrg_cons"] == band][["geo"]].values,
        hovertemplate="Country: %{customdata[0]}<br>Fiscal Impact: %{y:.1f}%<extra></extra>"
    ),
            row=1, col=1
        )

fig1b.update_layout(
    xaxis1=dict(title="Consumption Band", color="white"),
    yaxis1=dict(title="Fiscal Impact (%)", color="white")
)



fig1b.add_trace(
    go.Scatter(
        x=[1, 2, 3],
        y=[2, 1, 4],
        mode="lines+markers",
        name="Line Example",
        marker=dict(color="lightblue")
    ),
    row=1, col=2
)



# Update layout if needed
fig1b.update_layout(title_text="Subplot in One Row", height=400)

# Display in Streamlit
st.plotly_chart(fig1b, use_container_width=True, key="subplot_breakdown_chart")









st.divider()  # <--- Streamlit's built-in separator
st.markdown("""
            ### 📈 Gas Price single country historical trend
            """)
st.markdown(""" 
            source: EUROSTAT - bi-annual data (from 2007 onwards)
                        """)


available_countries = df["geo"].unique()
df["total"]=df["total"]*1000 # EUR/MWH
selected_country = st.selectbox("Select country", sorted(available_countries))
selected_bands = ["GJ_LT20", "GJ20-199", "GJ_GE200"]
df_filtered = df[
    (df["geo"] == selected_country) &
    (df["nrg_cons"].isin(selected_bands))
]


fig2 = go.Figure()

# Line for semestral retail prices (from df_filtered)
for band in df_filtered['nrg_cons'].unique():
    df_band = df_filtered[df_filtered['nrg_cons'] == band]
    fig2.add_trace(go.Scatter(
        x=df_band['add_formal_time'],
        y=df_band['total'],
        mode='lines+markers',
        name=f'Retail ({band})'
    ))

# Daily TTF line (optionally filter for same time range)
fig2.add_trace(go.Scatter(
    x=ttf_df['Date'],
    y=ttf_df['Price'],  # replace 'Price' with your actual column name
    mode='lines',
    name='TTF Gas Price (Daily)',
    line=dict(dash='dot', color='gray')
))

# Final layout
fig2.update_layout(
    title=f"Retail {category} Prices historical trend in {selected_country} with TTF Gas Reference",
    xaxis_title="Time",
    yaxis_title="Price (€/MWh)",
    legend_title="Legend"
)



fig2.update_layout(
            #height=40* len(df_filtered["geo"].unique()),  # 30px per country (adjust as needed)
            yaxis_title=f"Retail {category} Price {subcategory} (€/MWh)",
            xaxis_title="Semester",
            paper_bgcolor="#005680",
            plot_bgcolor="#005680",
            font=dict(size=14, color="#00274d"),
            #legend_title="Component",
            xaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(color="white", gridcolor="rgba(255,255,255,0.1)")
)


# Show Plotly chart
st.plotly_chart(fig2, use_container_width=True,key="historical_chart")

# Create subplot with 1 row and 2 columns
fig2b = make_subplots(rows=1, cols=2, subplot_titles=("Plot A", "Plot B"))

# Add traces to each subplot
fig2b.add_trace(go.Scatter(y=[1, 3, 2], name='Line A'), row=1, col=1)
fig2b.add_trace(go.Bar(y=[2, 1, 3], name='Bar B'), row=1, col=2)

# Update layout if needed
fig2b.update_layout(title_text="Subplot in One Row", height=400)

# Display in Streamlit
st.plotly_chart(fig2b, use_container_width=True,key="second_subplot")