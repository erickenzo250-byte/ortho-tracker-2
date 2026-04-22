import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path
import time

try:
    import plotly.express as px
    PLOTLY = True
except:
    PLOTLY = False

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Ortho Intelligence PRO+", layout="wide")
DATA_FILE = Path("procedures.csv")

# -----------------------------
# UI STYLING
# -----------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}
.kpi-card {
    background: linear-gradient(135deg, #1e3a8a, #2563eb);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    color: white;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.3);
    transition: 0.3s;
}
.kpi-card:hover {
    transform: scale(1.05);
}
section[data-testid="stSidebar"] {
    background: #020617;
}
.stButton>button {
    border-radius: 10px;
    background: linear-gradient(90deg, #22c55e, #16a34a);
    color: white;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

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

REPS = [
    "Kevin Ashiundu","Charity","Naomi","Carol","Josephine",
    "Geoffrey","Jacob","Faith","Erick","Spencer",
    "Evans","Miriam","Brian"
]

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
# GENERATE DATA
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
            "Rep": random.choice(REPS),
            "Duration": round(random.uniform(1, 5), 1),
            "Outcome": random.randint(65, 100),
            "Revenue": PROCEDURE_VALUE[proc]
        })
    return pd.DataFrame(rows)

# -----------------------------
# KPI FUNCTION
# -----------------------------
def kpi(title, value):
    st.markdown(f"""
    <div class="kpi-card">
        <h4>{title}</h4>
        <h2>{value}</h2>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("🦴 Ortho Intelligence PRO+")
page = st.sidebar.radio("Menu", ["Dashboard", "Add Case", "Test Data", "Reports"])

# -----------------------------
# TEST DATA
# -----------------------------
if page == "Test Data":
    st.title("🧪 Generate Test Data")

    if st.button("Generate 300 Records"):
        st.session_state.df = generate_data(300)
        save()
        st.success("✅ Data generated")

# -----------------------------
# ADD CASE
# -----------------------------
elif page == "Add Case":
    st.title("➕ Add Procedure")

    with st.form("form"):
        c1, c2 = st.columns(2)

        with c1:
            date = st.date_input("Date")
            region = st.selectbox("Region", REGIONS)
            hospital = st.selectbox("Hospital", HOSPITALS)

        with c2:
            procedure = st.selectbox("Procedure", PROCEDURES)
            surgeon = st.selectbox("Surgeon", SURGEONS)

        rep = st.selectbox("Sales Rep", REPS)
        duration = st.slider("Duration", 1.0, 10.0, 2.0)
        outcome = st.slider("Outcome", 0, 100, 80)

        if st.form_submit_button("Save"):
            new = pd.DataFrame([{
                "Date": date,
                "Region": region,
                "Hospital": hospital,
                "Procedure": procedure,
                "Category": CATEGORY_MAP[procedure],
                "Surgeon": surgeon,
                "Rep": rep,
                "Duration": duration,
                "Outcome": outcome,
                "Revenue": PROCEDURE_VALUE[procedure]
            }])

            st.session_state.df = pd.concat([st.session_state.df, new], ignore_index=True)
            save()
            st.success("✅ Saved successfully")

# -----------------------------
# DASHBOARD
# -----------------------------
elif page == "Dashboard":
    st.title("📊 Dashboard")

    df = st.session_state.df
    if df.empty:
        st.warning("Generate data first")
        st.stop()

    # FILTERS
    with st.sidebar.expander("🔍 Filters", True):
        regions = st.multiselect("Region", df["Region"].unique(), df["Region"].unique())
        reps = st.multiselect("Rep", df["Rep"].unique(), df["Rep"].unique())

    df = df[df["Region"].isin(regions) & df["Rep"].isin(reps)]

    # KPIs
    total = len(df)
    revenue = df["Revenue"].sum()
    outcome = df["Outcome"].mean()

    c1, c2, c3 = st.columns(3)
    kpi("Procedures", total)
    kpi("Revenue", f"KES {revenue:,.0f}")
    kpi("Outcome", f"{outcome:.1f}")

    # LOADING FX
    with st.spinner("Analyzing data..."):
        time.sleep(1)

    # TREND
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    st.subheader("📈 Trend")

    if PLOTLY:
        st.plotly_chart(px.line(df.groupby("Month").size()), use_container_width=True)
    else:
        st.line_chart(df.groupby("Month").size())

    # REP PERFORMANCE
    st.subheader("👥 Rep Leaderboard")

    rep_perf = df.groupby("Rep").agg({
        "Procedure": "count",
        "Revenue": "sum"
    }).rename(columns={"Procedure": "Cases"}).sort_values("Revenue", ascending=False)

    for i, (rep, row) in enumerate(rep_perf.head(5).iterrows(), 1):
        st.markdown(f"**{i}. {rep}** | 💰 {row['Revenue']:,.0f} | 📊 {row['Cases']} cases")

    # INSIGHTS
    st.subheader("🧠 Insights")

    top = rep_perf.index[0]
    worst = rep_perf.index[-1]

    st.success(f"🔥 Top Performer: {top}")
    st.error(f"⚠️ Needs Improvement: {worst}")

    if revenue > 50000000:
        st.toast("🔥 Revenue milestone hit!", icon="🔥")

    # DOWNLOAD
    st.download_button("⬇️ Download CSV", df.to_csv(index=False), "report.csv")

# -----------------------------
# REPORTS
# -----------------------------
elif page == "Reports":
    st.title("📑 Reports")

    df = st.session_state.df
    if df.empty:
        st.warning("No data")
        st.stop()

    st.subheader("Revenue by Region")
    st.bar_chart(df.groupby("Region")["Revenue"].sum())

    st.subheader("Procedure Mix")
    st.bar_chart(df["Procedure"].value_counts())
