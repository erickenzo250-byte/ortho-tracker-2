import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Ortho Intelligence", layout="wide")

DATA_FILE = Path("procedures.csv")

# -----------------------------
# MASTER DATA
# -----------------------------
PROCEDURES = [
    "Fracture Fixation", "Spinal Surgery",
    "Knee Replacement", "Hip Replacement",
    "Arthroscopy", "ACL Reconstruction"
]

CATEGORY_MAP = {
    "Fracture Fixation": "Trauma",
    "Spinal Surgery": "Trauma",
    "Knee Replacement": "Arthroplasty",
    "Hip Replacement": "Arthroplasty",
    "Arthroscopy": "Sports",
    "ACL Reconstruction": "Sports"
}

PROCEDURE_VALUE = {
    "Fracture Fixation": 120000,
    "Spinal Surgery": 200000,
    "Knee Replacement": 320000,
    "Hip Replacement": 350000,
    "Arthroscopy": 150000,
    "ACL Reconstruction": 180000
}

REGIONS = ["Eldoret", "Nairobi/Kijabe", "Mombasa", "Meru"]
HOSPITALS = ["MTRH Eldoret", "Kijabe", "Nairobi Hosp", "Mombasa Hosp", "Meru Hosp"]
SURGEONS = ["Dr. Achieng", "Dr. Patel", "Dr. Kamau", "Dr. Smith"]

TARGETS = {
    "Eldoret": {"Trauma": 140, "Arthroplasty": 140},
    "Nairobi/Kijabe": {"Trauma": 135, "Arthroplasty": 45},
    "Mombasa": {"Trauma": 120, "Arthroplasty": 20},
    "Meru": {"Trauma": 60, "Arthroplasty": 10},
}

# -----------------------------
# LOAD DATA
# -----------------------------
if "df" not in st.session_state:
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
        df["Date"] = pd.to_datetime(df["Date"])
    else:
        df = pd.DataFrame()
    st.session_state.df = df

def save():
    st.session_state.df.to_csv(DATA_FILE, index=False)

# -----------------------------
# GENERATE TEST DATA (300)
# -----------------------------
def generate_data(n=300):
    rows = []
    for _ in range(n):
        proc = random.choice(PROCEDURES)
        rows.append({
            "Date": datetime.today() - timedelta(days=random.randint(0, 365)),
            "Region": random.choice(REGIONS),
            "Hospital": random.choice(HOSPITALS),
            "Procedure": proc,
            "Category": CATEGORY_MAP[proc],
            "Surgeon": random.choice(SURGEONS),
            "Duration": round(random.uniform(1, 5), 1),
            "Outcome": random.randint(65, 100),
            "Revenue": PROCEDURE_VALUE[proc]
        })
    return pd.DataFrame(rows)

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("🦴 Ortho Intelligence")
page = st.sidebar.radio("Menu", ["Dashboard", "Add Case", "Test Data"])

# -----------------------------
# TEST DATA
# -----------------------------
if page == "Test Data":
    st.title("🧪 Generate Test Data")

    if st.button("Generate 300 Records"):
        st.session_state.df = generate_data(300)
        save()
        st.success("✅ 300 records generated")

# -----------------------------
# ADD CASE
# -----------------------------
elif page == "Add Case":
    st.title("➕ Add Procedure")

    with st.form("form"):
        col1, col2 = st.columns(2)

        with col1:
            date = st.date_input("Date")
            region = st.selectbox("Region", REGIONS)
            hospital = st.selectbox("Hospital", HOSPITALS)

        with col2:
            procedure = st.selectbox("Procedure", PROCEDURES)
            surgeon = st.selectbox("Surgeon", SURGEONS)

        duration = st.slider("Duration (hrs)", 1.0, 10.0, 2.0)
        outcome = st.slider("Outcome (0–100)", 0, 100, 80)

        submit = st.form_submit_button("Save")

        if submit:
            new_row = {
                "Date": date,
                "Region": region,
                "Hospital": hospital,
                "Procedure": procedure,
                "Category": CATEGORY_MAP[procedure],
                "Surgeon": surgeon,
                "Duration": duration,
                "Outcome": outcome,
                "Revenue": PROCEDURE_VALUE[procedure]
            }

            st.session_state.df = pd.concat(
                [st.session_state.df, pd.DataFrame([new_row])],
                ignore_index=True
            )
            save()
            st.success("✅ Procedure saved")

# -----------------------------
# DASHBOARD
# -----------------------------
elif page == "Dashboard":
    st.title("📊 Orthopedic Intelligence Dashboard")

    df = st.session_state.df

    if df.empty:
        st.warning("No data available. Generate test data first.")
        st.stop()

    # KPIs
    total = len(df)
    revenue = df["Revenue"].sum()
    avg_outcome = df["Outcome"].mean()

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Procedures", total)
    c2.metric("Total Revenue", f"KES {revenue:,.0f}")
    c3.metric("Avg Outcome", f"{avg_outcome:.1f}")

    st.divider()

    # CATEGORY PERFORMANCE
    st.subheader("📌 Category Performance")
    st.bar_chart(df["Category"].value_counts())

    # REGION VS TARGET
    st.subheader("🎯 Region vs Target")

    perf = df.groupby(["Region", "Category"]).size().unstack(fill_value=0)

    results = []
    for region in TARGETS:
        for cat in ["Trauma", "Arthroplasty"]:
            actual = perf.loc[region][cat] if region in perf.index and cat in perf.columns else 0
            target = TARGETS[region][cat]
            achievement = (actual / target * 100) if target > 0 else 0

            results.append({
                "Region": region,
                "Category": cat,
                "Actual": actual,
                "Target": target,
                "Achievement %": round(achievement, 1)
            })

    st.dataframe(pd.DataFrame(results), use_container_width=True)

    # EXEC SUMMARY
    st.subheader("🧠 Executive Summary")

    top_region = df["Region"].value_counts().idxmax()
    top_surgeon = df["Surgeon"].value_counts().idxmax()

    st.info(f"""
    • Total Procedures: {total}  
    • Revenue: KES {revenue:,.0f}  
    • Top Region: {top_region}  
    • Top Surgeon: {top_surgeon}  
    • Avg Outcome: {avg_outcome:.1f}  
    """)

    # REVENUE
    st.subheader("💰 Revenue by Region")
    st.bar_chart(df.groupby("Region")["Revenue"].sum())

    # SURGEON PERFORMANCE
    st.subheader("👨‍⚕️ Surgeon Performance")

    surg = df.groupby("Surgeon").agg({
        "Procedure": "count",
        "Outcome": "mean",
        "Revenue": "sum"
    }).rename(columns={"Procedure": "Cases"})

    st.dataframe(surg, use_container_width=True)
