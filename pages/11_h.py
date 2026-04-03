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

file_path = Path("data/2026-04-02_EMBER_hourly_wholesale_el_prices.parquet")

df = pd.read_parquet(file_path)

# ==========================================================
# Title
# ==========================================================
st.title("⚡ Wholesale Electricity Price Distribution")

st.markdown("### 📊 Histogram of hourly wholesale electricity prices by country")


# ==========================================================
# Country selector
# ==========================================================
# ---------------------------------------------------
# Set your real column names here
# ---------------------------------------------------
# ---------------------------------------------------
# Example column names
# ---------------------------------------------------
geo_col = "Country"
datetime_col = "Datetime (Local)"
price_col = "Price (EUR/MWhe)"

df[datetime_col] = pd.to_datetime(df[datetime_col])

selected_country = st.selectbox(
    "Select a country",
    options=sorted(df[geo_col].dropna().unique()),
    key="hist_country_compare"
)

selected_year = st.selectbox(
    "Select a year to compare against full history",
    options=sorted(df[datetime_col].dt.year.dropna().unique()),
    key="hist_year_compare"
)

df_country = df.loc[df[geo_col] == selected_country, [datetime_col, price_col]].dropna().copy()
df_country["year"] = df_country[datetime_col].dt.year

df_all = df_country.copy()
df_year = df_country.loc[df_country["year"] == selected_year].copy()

# ---------------------------------------------------
# Common bins
# ---------------------------------------------------
n_bins = 70

xmin = df_all[price_col].min()
xmax = df_all[price_col].max()
bin_size = (xmax - xmin) / n_bins

fig = go.Figure()

fig.add_trace(
    go.Histogram(
        x=df_all[price_col],
        xbins=dict(start=xmin, end=xmax, size=bin_size),
        name="All years",
        opacity=0.55,
        marker=dict(color="#4C78A8"),
        histnorm="percent"
    )
)

fig.add_trace(
    go.Histogram(
        x=df_year[price_col],
        xbins=dict(start=xmin, end=xmax, size=bin_size),
        name=str(selected_year),
        opacity=0.55,
        marker=dict(color="#F58518"),
        histnorm="percent"
    )
)

fig.update_layout(
    title=f"Wholesale electricity price distribution | {selected_country}",
    xaxis_title="Price",
    yaxis_title="Number of hours",
    barmode="overlay",
    template="plotly_white",
    height=600
)

st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------
# Adjust these to your real column names
# ---------------------------------------------------
geo_col = "Country"
datetime_col = "Datetime (Local)"
price_col = "Price (EUR/MWhe)"

# Make sure datetime is datetime
df[datetime_col] = pd.to_datetime(df[datetime_col])

available_countries = sorted(df[geo_col].dropna().unique().tolist())

selected_country = st.selectbox(
    "Select a country",
    options=available_countries,
    key="heatmap_country"
)

view_mode = st.selectbox(
    "Heatmap view",
    options=["Average by month and hour", "Daily pattern by date and hour"],
    key="heatmap_view"
)

df_country = df.loc[df[geo_col] == selected_country, [datetime_col, price_col]].dropna().copy()

df_country["hour"] = df_country[datetime_col].dt.hour
df_country["month"] = df_country[datetime_col].dt.month
df_country["date"] = df_country[datetime_col].dt.date

# =========================================================
# 1. Average by month and hour
# =========================================================
if view_mode == "Average by month and hour":
    heatmap_data = (
        df_country
        .groupby(["month", "hour"], as_index=False)[price_col]
        .mean()
        .pivot(index="month", columns="hour", values=price_col)
    )

    y_vals = heatmap_data.index.tolist()
    y_labels = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]
    y_labels = [y_labels[m - 1] for m in y_vals]

    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns.tolist(),
            y=y_labels,
            colorscale="RdYlBu_r",
            colorbar=dict(title="Price")
        )
    )

    fig.update_layout(
        title=f"Average hourly wholesale electricity prices | {selected_country}",
        xaxis_title="Hour of day",
        yaxis_title="Month",
        height=600
    )

# =========================================================
# 2. Daily pattern by date and hour
# =========================================================
else:
    heatmap_data = (
        df_country
        .groupby(["date", "hour"], as_index=False)[price_col]
        .mean()
        .pivot(index="date", columns="hour", values=price_col)
    )

    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns.tolist(),
            y=heatmap_data.index.astype(str).tolist(),
            colorscale="RdYlBu_r",
            colorbar=dict(title="Price")
        )
    )

    fig.update_layout(
        title=f"Daily hourly wholesale electricity prices | {selected_country}",
        xaxis_title="Hour of day",
        yaxis_title="Date",
        height=800
    )

st.plotly_chart(fig, use_container_width=True)