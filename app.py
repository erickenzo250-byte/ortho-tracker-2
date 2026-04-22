import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="Sales Intelligence OS", layout="wide")

# =========================================================
# SAFE DATA INIT (CRITICAL FIX)
# =========================================================
if "df" not in st.session_state or st.session_state.df is None:
    st.session_state.df = pd.DataFrame()

df = st.session_state.df

# =========================================================
# MASTER DATA
# =========================================================
REPS = ["Kevin","Charity","Naomi","Carol","Josephine","Geoffrey","Jacob","Faith","Erick","Spencer","Evans","Miriam","Brian"]
DOCTORS = ["Dr Achieng","Dr Patel","Dr Kamau","Dr Smith","Dr Njoroge","Dr Otieno"]
HOSPITALS = ["MTRH","Kijabe","Nairobi Hospital","Mombasa Hospital","Meru Hospital"]

# =========================================================
# GUARANTEED TEST DATA (STABLE)
# =========================================================
def generate_data(n=300):
    rows = []

    for _ in range(n):
        revenue = random.randint(80000, 500000)
        cost = int(revenue * random.uniform(0.5, 0.75))

        rows.append({
            "Date": datetime.today() - timedelta(days=random.randint(0, 365)),
            "Rep": random.choice(REPS),
            "Doctor": random.choice(DOCTORS),
            "Hospital": random.choice(HOSPITALS),
            "Revenue": revenue,
            "Cost": cost,
            "Profit": revenue - cost,
            "Outcome": random.randint(60, 100)
        })

    return pd.DataFrame(rows)

# =========================================================
# SAFE PROCESSING (NO CRASHES)
# =========================================================
def process(df):
    if df.empty:
        return df

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    df["Score"] = (
        df["Revenue"] * 0.4 +
        df["Profit"] * 0.4 +
        df["Outcome"] * 1000 * 0.2
    )

    return df

df = process(df)

# =========================================================
# NAVIGATION
# =========================================================
page = st.sidebar.radio(
    "Sales OS",
    ["📊 Dashboard","🧪 Data Setup","👥 Rep View"]
)

# =========================================================
# 🧪 DATA SETUP (FIXED + RELIABLE)
# =========================================================
if page == "🧪 Data Setup":
    st.title("🧪 Dataset Engine")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Generate 300 Test Records"):
            st.session_state.df = generate_data(300)
            st.success("Dataset generated successfully")

    with col2:
        if st.button("Clear Data"):
            st.session_state.df = pd.DataFrame()
            st.warning("Data cleared")

    if not df.empty:
        st.dataframe(df.head())

# =========================================================
# 📊 DASHBOARD (STABLE + INTERACTIVE)
# =========================================================
elif page == "📊 Dashboard":
    st.title("📊 Executive Dashboard")

    if df.empty:
        st.warning("No data found. Go to Data Setup → Generate 300 records.")
        st.stop()

    # FILTERS (FIXED)
    col1, col2, col3 = st.columns(3)

    with col1:
        rep_f = st.multiselect("Rep", df["Rep"].unique(), df["Rep"].unique())

    with col2:
        hosp_f = st.multiselect("Hospital", df["Hospital"].unique(), df["Hospital"].unique())

    with col3:
        doc_f = st.multiselect("Doctor", df["Doctor"].unique(), df["Doctor"].unique())

    df_f = df[
        df["Rep"].isin(rep_f) &
        df["Hospital"].isin(hosp_f) &
        df["Doctor"].isin(doc_f)
    ]

    # KPIs
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Records", len(df_f))
    c2.metric("Revenue", f"{df_f['Revenue'].sum():,.0f}")
    c3.metric("Profit", f"{df_f['Profit'].sum():,.0f}")
    c4.metric("Avg Score", f"{df_f['Score'].mean():.1f}")

    st.divider()

    # REP TABLE
    st.subheader("👥 Rep Performance")

    rep_table = df_f.groupby("Rep").agg({
        "Revenue":"sum",
        "Profit":"sum",
        "Score":"sum"
    }).sort_values("Score", ascending=False)

    st.dataframe(rep_table, use_container_width=True)

# =========================================================
# 👥 REP VIEW (DRILL DOWN)
# =========================================================
elif page == "👥 Rep View":
    st.title("👥 Rep Drilldown View")

    if df.empty:
        st.warning("No data available")
        st.stop()

    rep = st.selectbox("Select Rep", df["Rep"].unique())

    st.subheader(f"Performance: {rep}")

    data = df[df["Rep"] == rep]

    c1,c2,c3 = st.columns(3)
    c1.metric("Revenue", f"{data['Revenue'].sum():,.0f}")
    c2.metric("Profit", f"{data['Profit'].sum():,.0f}")
    c3.metric("Cases", len(data))

    st.dataframe(data)
