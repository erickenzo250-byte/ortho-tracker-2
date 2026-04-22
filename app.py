import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="Enterprise Sales AI", layout="wide")

# =========================================================
# SESSION DATA INIT
# =========================================================
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame()

df = st.session_state.df

# =========================================================
# MASTER DATA
# =========================================================
REPS = [
    "Kevin Ashiundu","Charity","Naomi","Carol","Josephine",
    "Geoffrey","Jacob","Faith","Erick","Spencer",
    "Evans","Miriam","Brian"
]

HOSPITALS = ["MTRH", "Kijabe", "Nairobi Hospital", "Mombasa Hospital", "Meru Hospital"]

REGIONS = ["Eldoret", "Nairobi/Kijabe", "Mombasa", "Meru"]

PROCEDURES = ["Trauma Case", "Arthroplasty Case", "Sports Injury", "Spinal Case"]

# =========================================================
# GENERATE 300 TEST RECORDS (IMPORTANT FIX)
# =========================================================
def generate_test_data(n=300):
    data = []

    for _ in range(n):
        rep = random.choice(REPS)

        revenue = random.randint(80000, 400000)
        cost = int(revenue * random.uniform(0.5, 0.8))
        profit = revenue - cost

        row = {
            "Date": datetime.today() - timedelta(days=random.randint(0, 365)),
            "Rep": rep,
            "Hospital": random.choice(HOSPITALS),
            "Region": random.choice(REGIONS),
            "Procedure": random.choice(PROCEDURES),
            "Revenue": revenue,
            "Cost": cost,
            "Profit": profit,
            "Outcome": random.randint(60, 100)
        }

        data.append(row)

    return pd.DataFrame(data)

# =========================================================
# PROCESS DATA
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
    "Enterprise System",
    ["📊 Dashboard","➕ Add Procedure","🧪 Generate Test Data","🤖 AI","💰 Commission"]
)

# =========================================================
# 🧪 TEST DATA (FIXED BUTTON)
# =========================================================
if page == "🧪 Generate Test Data":
    st.title("🧪 Generate 300 Test Records")

    if st.button("Generate Dataset"):
        st.session_state.df = generate_test_data(300)
        st.success("300 test records created successfully")
        st.dataframe(st.session_state.df.head())

# =========================================================
# ➕ ADD PROCEDURE (FIXED WORKING FORM)
# =========================================================
elif page == "➕ Add Procedure":
    st.title("➕ Add Procedure (Live Input)")

    with st.form("add_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            rep = st.selectbox("Rep", REPS)
            hospital = st.selectbox("Hospital", HOSPITALS)

        with col2:
            region = st.selectbox("Region", REGIONS)
            procedure = st.selectbox("Procedure", PROCEDURES)

        with col3:
            revenue = st.number_input("Revenue", 50000, 1000000, 150000)
            outcome = st.slider("Outcome", 0, 100, 80)

        submitted = st.form_submit_button("Save Procedure")

        if submitted:
            cost = int(revenue * 0.65)

            new_row = {
                "Date": datetime.today(),
                "Rep": rep,
                "Hospital": hospital,
                "Region": region,
                "Procedure": procedure,
                "Revenue": revenue,
                "Cost": cost,
                "Profit": revenue - cost,
                "Outcome": outcome
            }

            st.session_state.df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            st.session_state.df = process(st.session_state.df)

            st.success("Procedure added successfully")

# =========================================================
# 📊 DASHBOARD (INTERACTIVE)
# =========================================================
elif page == "📊 Dashboard":
    st.title("📊 Executive Command Dashboard")

    if df.empty:
        st.warning("No data available. Generate test data first.")
        st.stop()

    # FILTERS
    col1, col2, col3 = st.columns(3)

    with col1:
        rep_filter = st.multiselect("Rep", df["Rep"].unique(), df["Rep"].unique())

    with col2:
        region_filter = st.multiselect("Region", df["Region"].unique(), df["Region"].unique())

    with col3:
        hospital_filter = st.multiselect("Hospital", df["Hospital"].unique(), df["Hospital"].unique())

    df_f = df[
        df["Rep"].isin(rep_filter) &
        df["Region"].isin(region_filter) &
        df["Hospital"].isin(hospital_filter)
    ]

    # KPIs
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Records", len(df_f))
    c2.metric("Revenue", f"{df_f['Revenue'].sum():,.0f}")
    c3.metric("Profit", f"{df_f['Profit'].sum():,.0f}")
    c4.metric("Avg Outcome", f"{df_f['Outcome'].mean():.1f}")

    st.divider()

    # REP PERFORMANCE
    st.subheader("👥 Rep Performance")

    rep = df_f.groupby("Rep").agg({
        "Revenue":"sum",
        "Profit":"sum",
        "Outcome":"mean",
        "Score":"sum"
    }).sort_values("Score", ascending=False)

    selected_rep = st.selectbox("Drill into Rep", rep.index)

    st.dataframe(rep)

    st.write("📋 Rep Details")
    st.dataframe(df_f[df_f["Rep"] == selected_rep])

# =========================================================
# 🤖 AI (SIMPLE BUT WORKING)
# =========================================================
elif page == "🤖 AI":
    st.title("🤖 Sales AI Assistant")

    q = st.text_input("Ask AI")

    if st.button("Run"):
        if df.empty:
            st.warning("No data available")
        else:
            top_rep = df.groupby("Rep")["Score"].sum().idxmax()
            low_rep = df.groupby("Rep")["Score"].sum().idxmin()
            top_region = df.groupby("Region")["Revenue"].sum().idxmax()

            st.success(f"Top Rep: {top_rep}")
            st.warning(f"Low Rep: {low_rep}")
            st.info(f"Best Region: {top_region}")

# =========================================================
# 💰 COMMISSION ENGINE
# =========================================================
elif page == "💰 Commission":
    st.title("💰 Commission Report")

    if df.empty:
        st.warning("No data")
        st.stop()

    rate = st.slider("Commission %", 1, 20, 8) / 100

    comm = df.groupby("Rep").agg({
        "Revenue":"sum",
        "Profit":"sum"
    })

    comm["Commission"] = comm["Profit"] * rate

    st.dataframe(comm.sort_values("Commission", ascending=False))
