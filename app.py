import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Ortho Command System", layout="wide")
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

VALUE = {
    "Fracture Fixation": 120000,
    "Spinal Surgery": 200000,
    "Knee Replacement": 320000,
    "Hip Replacement": 350000,
    "Arthroscopy": 150000,
    "ACL Reconstruction": 180000
}

COST = {
    "Fracture Fixation": 80000,
    "Spinal Surgery": 120000,
    "Knee Replacement": 200000,
    "Hip Replacement": 220000,
    "Arthroscopy": 90000,
    "ACL Reconstruction": 110000
}

REPS = [
    "Kevin Ashiundu","Charity","Naomi","Carol","Josephine",
    "Geoffrey","Jacob","Faith","Erick","Spencer",
    "Evans","Miriam","Brian"
]

REGIONS = ["Eldoret", "Nairobi", "Mombasa", "Meru"]
HOSPITALS = ["MTRH", "Kijabe", "Nairobi Hosp", "Mombasa Hosp", "Meru Hosp"]

# -----------------------------
# LOAD DATA
# -----------------------------
def load_data():
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        return df
    return pd.DataFrame()

if "df" not in st.session_state:
    st.session_state.df = load_data()

def save_data():
    st.session_state.df.to_csv(DATA_FILE, index=False)

# -----------------------------
# CLEAN DATA (CRITICAL FIX)
# -----------------------------
def clean(df):
    if df.empty:
        return df

    df["Category"] = df["Procedure"].map(CATEGORY_MAP)
    df["Revenue"] = df["Procedure"].map(VALUE)
    df["Cost"] = df["Procedure"].map(COST)
    df["Profit"] = df["Revenue"] - df["Cost"]
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    return df

# -----------------------------
# GENERATE DEMO DATA
# -----------------------------
def generate_data(n=300):
    rows = []
    for _ in range(n):
        p = random.choice(PROCEDURES)
        rows.append({
            "Date": datetime.today() - timedelta(days=random.randint(0, 365)),
            "Region": random.choice(REGIONS),
            "Hospital": random.choice(HOSPITALS),
            "Procedure": p,
            "Rep": random.choice(REPS),
            "Outcome": random.randint(65, 100)
        })

    return clean(pd.DataFrame(rows))

# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------
page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "➕ Add Procedure", "🧪 Data Tools"]
)

df = clean(st.session_state.df)

# =============================
# ➕ ADD PROCEDURE (FIXED)
# =============================
if page == "➕ Add Procedure":
    st.title("➕ Add New Procedure")

    with st.form("add_form"):
        col1, col2 = st.columns(2)

        with col1:
            date = st.date_input("Date", value=datetime.today())
            region = st.selectbox("Region", REGIONS)
            hospital = st.selectbox("Hospital", HOSPITALS)
            procedure = st.selectbox("Procedure", PROCEDURES)

        with col2:
            rep = st.selectbox("Sales Rep", REPS)
            outcome = st.slider("Outcome (0–100)", 0, 100, 80)

        submitted = st.form_submit_button("💾 Save Procedure")

    if submitted:
        new_row = pd.DataFrame([{
            "Date": date,
            "Region": region,
            "Hospital": hospital,
            "Procedure": procedure,
            "Rep": rep,
            "Outcome": outcome
        }])

        updated_df = pd.concat([df, new_row], ignore_index=True)
        updated_df = clean(updated_df)

        st.session_state.df = updated_df
        save_data()

        st.success("✅ Procedure added successfully")
        st.rerun()

# =============================
# 🧪 DATA TOOLS
# =============================
elif page == "🧪 Data Tools":
    st.title("🧪 Data Tools")

    if st.button("Generate 300 Demo Records"):
        st.session_state.df = generate_data(300)
        save_data()
        st.success("Demo data generated")
        st.rerun()

    upload = st.file_uploader("Upload CSV")

    if upload:
        new_df = pd.read_csv(upload)
        st.session_state.df = pd.concat([df, new_df], ignore_index=True)
        st.session_state.df = clean(st.session_state.df)
        save_data()
        st.success("File uploaded successfully")
        st.rerun()

# =============================
# 📊 DASHBOARD
# =============================
elif page == "📊 Dashboard":
    st.title("📊 Executive Dashboard")

    if df.empty:
        st.warning("No data available. Add or generate data.")
        st.stop()

    # -------------------------
    # FILTERS
    # -------------------------
    st.sidebar.subheader("Filters")

    region_f = st.sidebar.multiselect("Region", df["Region"].unique(), df["Region"].unique())
    rep_f = st.sidebar.multiselect("Rep", df["Rep"].unique(), df["Rep"].unique())
    hosp_f = st.sidebar.multiselect("Hospital", df["Hospital"].unique(), df["Hospital"].unique())

    df = df[
        df["Region"].isin(region_f) &
        df["Rep"].isin(rep_f) &
        df["Hospital"].isin(hosp_f)
    ]

    # -------------------------
    # KPIs
    # -------------------------
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Procedures", len(df))
    c2.metric("Revenue", f"KES {df['Revenue'].sum():,.0f}")
    c3.metric("Profit", f"KES {df['Profit'].sum():,.0f}")
    c4.metric("Outcome", f"{df['Outcome'].mean():.1f}")

    st.divider()

    # -------------------------
    # TREND
    # -------------------------
    st.subheader("📈 Monthly Trend")

    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    trend = df.groupby("Month").size()

    st.line_chart(trend)

    # -------------------------
    # TOP PERFORMERS
    # -------------------------
    st.subheader("🏆 Top Performers")

    rep_perf = df.groupby("Rep").agg({
        "Procedure": "count",
        "Revenue": "sum"
    }).rename(columns={"Procedure": "Cases"}).sort_values("Revenue", ascending=False)

    hosp_perf = df.groupby("Hospital").agg({
        "Procedure": "count",
        "Revenue": "sum"
    }).rename(columns={"Procedure": "Cases"}).sort_values("Revenue", ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        st.write("👥 Top Reps")
        st.dataframe(rep_perf.head(5))

    with col2:
        st.write("🏥 Top Hospitals")
        st.dataframe(hosp_perf.head(5))

    # -------------------------
    # INSIGHTS
    # -------------------------
    st.subheader("🧠 Executive Insights")

    insights = []

    if df["Outcome"].mean() < 75:
        insights.append("⚠️ Clinical outcomes are below target.")

    if len(df[df["Category"] == "Trauma"]) > len(df[df["Category"] == "Arthroplasty"]) * 2:
        insights.append("⚠️ Over-reliance on trauma procedures.")

    if insights:
        for i in insights:
            st.warning(i)
    else:
        st.success("All key indicators are within expected range.")

    # -------------------------
    # DOWNLOAD
    # -------------------------
    st.download_button(
        "⬇️ Download Executive Report",
        df.to_csv(index=False),
        "executive_report.csv"
    )
