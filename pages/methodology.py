import streamlit as st
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Data", layout="wide")
from utils import apply_style_and_logo

apply_style_and_logo()
# Load your CSV data
df = pd.read_csv("data/table_summary.csv")  # adjust the path to your CSV file

st.set_page_config(page_title="Dashboard", layout="wide")
from utils import apply_style_and_logo
st.markdown("## 📊 Methodology – Data Snapshot")
st.markdown("""
Below is the dataset used to generate the current price comparison visualizations.  
You can explore the values directly or download the file for local analysis.
""")

# Display the DataFrame in a nice table
st.dataframe(df, use_container_width=True)

# Prepare CSV for download
csv = df.to_csv(index=False).encode("utf-8")

# Download button
st.download_button(
    label="⬇️ Download CSV",
    data=csv,
    file_name="energy_prices_snapshot.csv",
    mime="text/csv",
)