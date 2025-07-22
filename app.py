"""
FAIR FUEL COMPARE
app dedicated to STREAMLIT APPLICATION

"""

# ───────────────────────────────────────────────────────────────
#bash
#cd ~/Documents/PYTHON_STREAMLIT/NEWSRANKER_CLOUD
# py -m streamlit run app.py

#(projenv) C:\Users\donat\Documents\PYTHON_STREAMLIT>
#cd FUELPRICES
#streamlit run app.py

# ───────────────────────────────────────────────────────────────
import streamlit as st
import pandas as pd

# ── Load user credentials and profiles ────────────────────────
CREDENTIALS = dict(st.secrets["auth"])
PROFILES = st.secrets.get("profile", {})

# ── Login form ────────────────────────────────────────────────
def login():
    st.title("🔐 Login Required")

    user = st.text_input("Username", key="username_input")
    password = st.text_input("Password", type="password", key="password_input")

    if st.button("Login", key="login_button"):
        if user in CREDENTIALS and password == CREDENTIALS[user]:
            st.session_state["authenticated"] = True
            st.session_state["username"] = user
            st.session_state["first_name"] = PROFILES.get(user, {}).get("first_name", user)
        else:
            st.error("❌ Invalid username or password")

# ── Auth state setup ──────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# ── Login gate ────────────────────────────────────────────────
if not st.session_state["authenticated"]:
    login()
    st.stop()

# ── App begins after login ────────────────────────────────────

# ---------------Sidebar
from utils import apply_style_and_logo

st.sidebar.success(f"Welcome {st.session_state['first_name']}!")
st.sidebar.button("Logout", on_click=lambda: st.session_state.update(authenticated=False))

# Spacer to push the link to the bottom (optional tweak for better placement)
st.sidebar.markdown("<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)

# Company website link
st.sidebar.markdown(
    '<p style="text-align:center;">'
    '<a href="https://www.wavetransition.com" target="_blank">🌐 Visit WaveTransition</a>'
    '</p>',
    unsafe_allow_html=True
)
# ---------Main content
st.set_page_config(page_title="Fuel Dashboard", layout="wide")
st.title("WAVETRANSITION FAIR FUEL COMPARE APPLICATION")
st.markdown("""
## Welcome to **FAIR FUEL COMPARE APPLICATION**


This web app provides a unified view of major energy fuels — such as **electricity, natural gas, diesel, CNG**, and **LNG** — expressed in **euro per megawatt-hour (€/MWh)**. By converting all fuel prices to a standard energy unit, you can directly compare their relative costs, regardless of fuel type.

---

### 🌍 Coverage: EU20 Snapshot

The data shown in this app refers to the **EU20 countries**, offering a European-scale perspective on energy prices. While the app provides a harmonized energy basis (€/MWh), it is important to note that:

- **Each country** applies its own **fuel pricing structures**, influenced by **local markets**, **regulations**, and **taxation schemes** (such as **VAT** and **excise duties**).
- Some countries may report prices **with or without fiscal components**, depending on national practices or data availability.
- Update frequencies and methodologies can vary by fuel type and country.

This makes the app a valuable tool for observing both **relative differences** and **structural variations** across Europe.

---

### 🎯 Purpose

This app offers a **frozen snapshot** of current energy prices, enabling high-level comparisons on a consistent energy basis. While data may come from asynchronous or source-specific reports, the harmonized format supports clearer interpretation and decision-making.

---

### 📌 Key Features

- Energy-based comparison in **€/MWh**
- Covers **electricity, gas, CNG, LNG, diesel**, and more
- Displays **VAT and excise components** when available
- Clear visualizations to easily identify price differences across Europe

---

### ⚠️ Note

This app focuses on **cross-sectional comparisons** across fuel types and EU20 countries. **Time series analysis** and dynamic market trends are addressed in other specialized tools.

---

### 🧭 Start exploring!

Use the filters and charts below to compare fuel prices across **energy types, countries**, and **market segments**.
""")