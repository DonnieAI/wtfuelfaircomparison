import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import os
from datetime import datetime
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


def extract_latest_value_and_variations(raw_df, column_name, delays):
    """
    Extracts the latest value and % variations from a raw time series DataFrame.
    
    Parameters:
        raw_df (pd.DataFrame): Input data with at least 'Date' and one price column.
        column_name (str): Name of the column to analyze (e.g., 'Brent_Price').
        delays (list): List of day offsets to compare against latest date.
        
    Returns:
        latest_value (float)
        variations (list of float): % variations vs past values (first is always 0.0)
        latest_date (datetime): latest available date in the dataset
    """
    
    # Clean and sort the data
    df = raw_df.dropna().sort_values("Date").set_index("Date")
    
    # Get latest date and value
    latest_date = df.index.max()
    latest_value = df.loc[latest_date, column_name]

    # Extract historical values
    values = []
    for d in delays:
        target_date = latest_date - pd.Timedelta(days=d)
        valid_dates = df.index[df.index <= target_date]
        if not valid_dates.empty:
            closest_date = valid_dates.max()
            values.append(df.loc[closest_date, column_name])
        else:
            values.append(None)

    # Compute % variations from latest
    variations = [
        round((latest_value - v) / v * 100, 2) if v else None
        for v in values
    ]
    latest_date_str=latest_date.strftime("%Y-%m-%d")
    return latest_value, variations, latest_date_str



# --- Flashcard component ---
def flashcard_with_bar(label, value, unit, variations, color, latest_date,font_color="#000000"):
    import uuid
    import plotly.graph_objects as go

    # Create bar chart
    variation_labels = list(variations.keys())
    variation_values = list(variations.values())
    bar_colors = ["#E74C3C" if v < 0 else "#27AE60" for v in variation_values]

    bar_fig = go.Figure(
        data=[
            go.Bar(
                x=variation_values,
                y=variation_labels,
                orientation="h",
                marker_color=bar_colors,
                name="Δ [%]",
            )
        ]
    )

    bar_fig.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    height=150,
    xaxis=dict(
        title=dict(
            text="Δ (%)",
            font=dict(color=font_color)
        ),
        tickfont=dict(color=font_color),
        showgrid=True,
        zeroline=True
    ),
    yaxis=dict(
        tickfont=dict(color=font_color),
        showgrid=True,
        zeroline=False
    ),
    showlegend=False,
    plot_bgcolor=color,
    paper_bgcolor=color,
)

    # Generate a unique key (you can also use label as a safe key)
    chart_key = f"chart_{label}"

    with st.container():
        st.markdown(
    f"""
                <div style="
                    background-color: {color};
                    padding: 1.2rem;
                    border-radius: 10px;
                    text-align: center;
                    box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                    margin-bottom: 1.5rem;
                ">
                    <h5 style="color: {font_color}; margin-bottom: 0.3rem;">{label}</h5>
                    <div style="color: {font_color}; font-size: 0.85rem; margin-bottom: 0.5rem;">
                        Last update: <strong>{latest_date}</strong>
                    </div>
                    <h1 style="color: {font_color}; margin: 0 0 1rem 0;">
                        {value:.2f} <span style="font-size: 1.4rem;">{unit}</span>
                    </h1>
                </div>
                """,
                unsafe_allow_html=True
        )

        # ✅ Add a unique key here
        st.plotly_chart(bar_fig, use_container_width=True, key=chart_key)


st.title("🔎 Energy EU Proce Overview Dashboard")

st.markdown("""
### 📊 Fuels and Commodity Energy-Based Comparison

This dashboard provides a snapshot of key energy market indicators, including **oil (Brent)**, **natural gas (TTF)**, **coal**, and refined products across Europe. Prices are normalized based on **energy content** to enable meaningful cross-fuel comparisons.

#### ⚠️ Please Note:
- Data sources vary by fuel type and may not align to the same reference date.
- Figures reflect the **latest available values**, with **weekly**, **monthly**, and **year-to-date (YTD)** changes to highlight market trends.
- All prices are presented in their relevant units (€/MWh, $/bbl, etc.).

Use this page for a quick visual reference of market conditions. Detailed trends and time series charts are available in the following sections.
""")
st.markdown(""" 
            source: Wavetransition - (data sources available in methodology page)
                        """)


# Row 1: Commodities

#----------------------------------------------------------------------
st.markdown("---")  # horizontal line separator
#----------------------------------------------------------------------
st.markdown("""### Commodities
            
            """)

#🛢️🛢️🛢️🛢️🛢️🛢️🛢️🛢️🛢️--BRENT DATA EXTRACTION-🛢️🛢️🛢️🛢️🛢️🛢️🛢️🛢️🛢️🛢️🛢️🛢️🛢️🛢️🛢️🛢️-
brent_raw_df = pd.read_csv("data/2025-10-31_EIA_brent_weekly.csv", parse_dates=["Date"])

brent_latest_value, brent_variations, brent_latest_date = extract_latest_value_and_variations(
            brent_raw_df,
            column_name="Brent_Price",
            delays=[0, 7, 30, 90, 180, 360]
)

brent_card = {
    "label": "🛢️ Brent Price",
    "value": brent_latest_value,
    "unit": "$/bbl",
    "variations": {
        "Weekly": brent_variations[1],
        "Monthly": brent_variations[2],
        "3 Months" :brent_variations[3],
        "6-months": brent_variations[4],
        "YoY": brent_variations[5]
    },
    "color": palette_blue[0],  # baby blue
    "latest_date": brent_latest_date
}


#🔥🔥🔥🔥🔥🔥🔥🔥🔥 TTF 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥
ttf_raw_df=pd.read_csv("data/2025-11-06_TTF_weekly.csv", parse_dates=["Date"])

ttf_latest_value, ttf_variations, ttf_latest_date = extract_latest_value_and_variations(
    ttf_raw_df,
    column_name="Close",
    delays=[0, 7, 30, 90, 180, 360]
)


ttf_card = {
    "label": "🔥 Dutch TTF",
    "value": ttf_latest_value,
    "unit": "EUR/MWh",
    "variations": {
        "Weekly": ttf_variations[1],
        "Monthly": ttf_variations[2],
        "3 Months" :ttf_variations[3],
        "6-months": ttf_variations[4],
        "YoY": ttf_variations[5]
    },
    "color": palette_blue[0],  # baby blue
    "latest_date": ttf_latest_date
}

coal_card = {
    "label": "🪨 Coal Price",
    "value":  100,
    "unit": "EUR/t",
   "variations": {
        "Weekly": ttf_variations[1],
        "Monthly": ttf_variations[2],
        "3 Months" :ttf_variations[3],
        "6-months": ttf_variations[4],
        "YoY": ttf_variations[5]
    },
    "color": "#A9DEF9",  # baby blue
    "latest_date": "DUMMY"
}
#flashcard_with_bar(**brent_card)


commodities = [brent_card, ttf_card, coal_card]

cols = st.columns(len(commodities))
for col, card in zip(cols, commodities):
    with col:
        flashcard_with_bar(**card)

#---------------------------------------------------------------
#----------------------------------------------------------------------
st.markdown("---")  # horizontal line separator
#----------------------------------------------------------------------
#✅------------------------DATA EXTRACTION-----------------------------------------------------
# Extraction of oil product with tax
files = list(Path("data").glob("*.parquet"))
# latest "withtaxes"
withtaxes_files = [f for f in files if "withtaxes" in f.stem]
latest_withtaxes = max(withtaxes_files, key=lambda f: pd.to_datetime(f.stem.split("_")[0]))
print("Latest withtaxes:", latest_withtaxes.name)

# Load them
df_withtaxes = pd.read_parquet(latest_withtaxes)
latest_date_oil_products=max(df_withtaxes["Date"])

Super_95_df = (
    df_withtaxes
    .query("Fuel_Type == 'Super_95' and Country == 'EU'")
    .loc[:, ["Date", "Price"]]
    .dropna()
    .assign(Date=lambda df: pd.to_datetime(df["Date"]))
    .sort_values("Date")
    .drop_duplicates(subset="Date", keep="last")  # just in case
    .reset_index(drop=True)
)
Super_95_latest_value, Super_95_variations, Super_95_latest_date = extract_latest_value_and_variations(
            Super_95_df,
            column_name="Price",
            delays=[0, 1, 4, 12, 24, 52]
)

Diesel_df = (
    df_withtaxes
    .query("Fuel_Type == 'Diesel' and Country == 'EU'")
    .loc[:, ["Date", "Price"]]
    .dropna()
    .assign(Date=lambda df: pd.to_datetime(df["Date"]))
    .sort_values("Date")
    .drop_duplicates(subset="Date", keep="last")  # just in case
    .reset_index(drop=True)
)
Diesel_latest_value, Diesel_variations, Diesel_latest_date = extract_latest_value_and_variations(
            Diesel_df,
            column_name="Price",
            delays=[0, 1, 4, 12, 24, 52]
)

GPL_df = (
    df_withtaxes
    .query("Fuel_Type == 'GPL' and Country == 'EU'")
    .loc[:, ["Date", "Price"]]
    .dropna()
    .assign(Date=lambda df: pd.to_datetime(df["Date"]))
    .sort_values("Date")
    .drop_duplicates(subset="Date", keep="last")  # just in case
    .reset_index(drop=True)
)
GPL_latest_value, GPL_variations, GPL_latest_date = extract_latest_value_and_variations(
            GPL_df,
            column_name="Price",
            delays=[0, 1, 4, 12, 24, 52]
)
st.markdown("""### Oil products
            
            """)

Super_95_card = {
    "label": "⛽ Super 95",
    "value": Super_95_latest_value/1000,
    "unit": "EUR/liter",
    "variations": {
        "Weekly": Super_95_variations[1],
        "Monthly": Super_95_variations[2],
        "3 Months" :Super_95_variations[3],
        "6-months": Super_95_variations[4],
        "YoY": Super_95_variations[5]
    },
    "color": palette_blue[1],  # baby blue
    "latest_date": Super_95_latest_date
}

Diesel_card = {
    "label": "🛢️ Diesel",
    "value": Diesel_latest_value/1000,
    "unit": "EUR/liter",
    "variations": {
        "Weekly": Diesel_variations[1],
        "Monthly": Diesel_variations[2],
        "3 Months" :Diesel_variations[3],
        "6-months": Diesel_variations[4],
        "YoY": Diesel_variations[5]
    },
    "color": palette_blue[1],  # baby blue
    "latest_date":  Diesel_latest_date
}


GPL_card = {
    "label": "🧯 GPL",
    "value": GPL_latest_value/1000,
    "unit": "EUR/liter",
    "variations": {
        "Weekly": GPL_variations[1],
        "Monthly": GPL_variations[2],
        "3 Months" :GPL_variations[3],
        "6-months": GPL_variations[4],
        "YoY": GPL_variations[5]
    },
    "color": palette_blue[1],  # baby blue
    "latest_date": GPL_latest_date
}

oil_products = [Super_95_card, Diesel_card, GPL_card]

cols2 = st.columns(len(oil_products))
for col2, card in zip(cols2, oil_products):
    with col2:
        flashcard_with_bar(**card)
#---

#----------------------------------------------------------------------
st.markdown("---")  # horizontal line separator
#----------------------------------------------------------------------



def load_latest_ember_csv(directory="."):
    """
    Loads the most recent CSV file in the directory matching the pattern: *_EMBER_wholesale_el_prices.csv
    Assumes filename starts with YYYY-MM-DD.
    """
    files = [
        f for f in os.listdir(directory)
        if "EMBER_wholesale_el_prices" in f and f.endswith(".csv")
    ]

    if not files:
        raise FileNotFoundError("No EMBER_wholesale_el_prices CSV files found.")

    # Parse date prefix from filename and sort
    dated_files = []
    for f in files:
        try:
            date_str = f.split("_")[0]  # get the '2025-10-31' part
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            dated_files.append((file_date, f))
        except ValueError:
            continue  # Skip files with invalid date format

    if not dated_files:
        raise ValueError("No valid dated EMBER files found.")

    # Get the most recent file by date
    latest_file = sorted(dated_files, reverse=True)[0][1]

    print(f"Loading: {latest_file}")  # Optional for debugging
    return pd.read_csv(os.path.join(directory, latest_file))
df_ember = load_latest_ember_csv("data")  # or just "." for current folder


eu_wholesale_el_price = (
    df_ember
    .query("Country == 'EU'")
    .assign(Date=lambda df: pd.to_datetime(df["Date"]))  # ensure Date is datetime
    .set_index("Date")  # required for resample to work
    .resample("W")  # weekly average
    .agg(Weekly_Ave=("Price (EUR/MWhe)", "mean"))
    .dropna()
    .reset_index()  # restore Date as column
    .sort_values("Date")
)
eu_wholesale_el_price_latest_value, eu_wholesale_el_price_variations, eu_wholesale_el_price_latest_date = extract_latest_value_and_variations(
            eu_wholesale_el_price,
            column_name="Weekly_Ave",
            delays=[0, 1, 4, 12, 24, 52]
)

st.markdown("""### EU data
            
            """)

eu_el_eprice_card = {
    "label": "⚡ Wholesale electricity",
    "value": eu_wholesale_el_price_latest_value,
    "unit": "EUR/MWh",
    "variations": {
        "Weekly": eu_wholesale_el_price_variations[1],
        "Monthly": eu_wholesale_el_price_variations[2],
        "3 Months" :eu_wholesale_el_price_variations[3],
        "6-months": eu_wholesale_el_price_variations[4],
        "YoY": eu_wholesale_el_price_variations[5]
    },
    "color": palette_blue[2],  # baby blue
    "latest_date": eu_wholesale_el_price_latest_date
}






#---

co2_price_df=pd.read_csv("data/prices_eu_ets_all.csv")  #daily
#co2_price_df["date"] = pd.to_datetime(co2_price_df["date"], dayfirst=True)
eua_price = (
    co2_price_df
    .assign(Date=lambda df: pd.to_datetime(df["date"],dayfirst=True))  # ensure Date is datetime
    .set_index("Date")  # required for resample to work
    .dropna()
    .reset_index()  # restore Date as column
    .sort_values("Date")
     .loc[:, ["Date", "price"]]
)


eua_price_latest_value, eua_price_price_variations, eua_price_price_latest_date = extract_latest_value_and_variations(
            eua_price,
            column_name="price",
            delays=[0, 7, 30, 90, 180, 360]
)


co2_price_card = {
    "label": "💨 CO2 price",
    "value": eua_price_latest_value,
    "unit": "EUR/tCO2",
    "variations": {
        "Weekly": eua_price_price_variations[1],
        "Monthly": eua_price_price_variations[2],
        "3 Months" :eua_price_price_variations[3],
        "6-months": eua_price_price_variations[4],
        "YoY": eua_price_price_variations[5]
    },
    "color": palette_blue[3],  # baby blue
    "latest_date": eua_price_price_latest_date
}



eu_data=[eu_el_eprice_card,co2_price_card]

cols3 = st.columns(len(eu_data))
for col3, card in zip(cols3, eu_data):
    with col3:
        flashcard_with_bar(**card)

