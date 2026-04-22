import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path

st.set_page_config(page_title="Ortho Command V5 FIXED", layout="wide")
DATA_FILE = Path("procedures.csv")

# -----------------------------
# LOGIN
# -----------------------------
USERS = {"admin": "admin123", "erick": "1234"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if USERS.get(u) == p:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid login")
    st.stop()

# -----------------------------
# MASTER DATA
# -----------------------------
PROCEDURES = ["Fracture Fixation","Spinal Surgery","Knee Replacement","Hip Replacement","Arthroscopy","ACL Reconstruction"]

CATEGORY_MAP = {
    "Fracture Fixation":"Trauma","Spinal Surgery":"Trauma",
    "Knee Replacement":"Arthroplasty","Hip Replacement":"Arthroplasty",
    "Arthroscopy":"Sports","ACL Reconstruction":"Sports"
}

VALUE = {
    "Fracture Fixation":120000,"Spinal Surgery":200000,
    "Knee Replacement":320000,"Hip Replacement":350000,
    "Arthroscopy":150000,"ACL Reconstruction":180000
}

COST = {
    "Fracture Fixation":80000,"Spinal Surgery":120000,
    "Knee Replacement":200000,"Hip Replacement":220000,
    "Arthroscopy":90000,"ACL Reconstruction":110000
}

REPS = ["Kevin Ashiundu","Charity","Naomi","Carol","Josephine","Geoffrey","Jacob","Faith","Erick","Spencer","Evans","Miriam","Brian"]

REGIONS = ["Eldoret","Nairobi","Mombasa","Meru"]
HOSPITALS = ["MTRH","Kijabe","Nairobi Hosp","Mombasa Hosp","Meru Hosp"]

# -----------------------------
# LOAD DATA
# -----------------------------
def load_data():
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        return df
    return pd.DataFrame()

if "df" not in st.session_state:
    st.session_state.df = load_data()

def save():
    st.session_state.df.to_csv(DATA_FILE, index=False)

# -----------------------------
# CLEAN DATA (IMPORTANT FIX)
# -----------------------------
def clean(df):
    if df.empty:
        return df

    df["Category"] = df["Procedure"].map(CATEGORY_MAP)
    df["Revenue"] = df["Procedure"].map(VALUE)
    df["Cost"] = df["Procedure"].map(COST)
    df["Profit"] = df["Revenue"] - df["Cost"]

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    return df

# -----------------------------
# GENERATE DATA
# -----------------------------
def generate(n=300):
    rows=[]
    for _ in range(n):
        p=random.choice(PROCEDURES)
        rows.append({
            "Date": datetime.today()-timedelta(days=random.randint(0,365)),
            "Region": random.choice(REGIONS),
            "Hospital": random.choice(HOSPITALS),
            "Procedure": p,
            "Rep": random.choice(REPS),
            "Outcome": random.randint(65,100)
        })
    df=pd.DataFrame(rows)
    return clean(df)

# -----------------------------
# TABS
# -----------------------------
tab1,tab2,tab3,tab4,tab5 = st.tabs([
    "📊 Executive","👥 Reps","🏥 Hospitals","📈 Forecast","📑 Reports"
])

df = clean(st.session_state.df)

# -----------------------------
# EXECUTIVE
# -----------------------------
with tab1:
    st.title("📊 Executive Dashboard")

    if df.empty:
        if st.button("Generate Demo Data"):
            st.session_state.df = generate(300)
            save()
            st.rerun()
        st.warning("No data available")
        st.stop()

    st.metric("Procedures", len(df))
    st.metric("Revenue", f"KES {df['Revenue'].sum():,.0f}")
    st.metric("Profit", f"KES {df['Profit'].sum():,.0f}")
    st.metric("Outcome", f"{df['Outcome'].mean():.1f}")

# -----------------------------
# REPS
# -----------------------------
with tab2:
    st.title("👥 Rep Command Center")

    rep = df.groupby("Rep").agg({
        "Procedure":"count",
        "Revenue":"sum",
        "Profit":"sum"
    }).rename(columns={"Procedure":"Cases"})

    TARGET = 50
    rep["Target"] = TARGET
    rep["Achievement %"] = (rep["Cases"]/TARGET*100).round(1)
    rep["Commission"] = rep["Profit"] * 0.05

    st.dataframe(rep.sort_values("Revenue",ascending=False))

# -----------------------------
# HOSPITALS
# -----------------------------
with tab3:
    st.title("🏥 Hospital Intelligence")

    hosp = df.groupby("Hospital").agg({
        "Procedure":"count",
        "Revenue":"sum"
    }).rename(columns={"Procedure":"Cases"})

    st.dataframe(hosp.sort_values("Revenue",ascending=False))

# -----------------------------
# FORECAST
# -----------------------------
with tab4:
    st.title("📈 Forecast")

    if df["Date"].isna().all():
        st.warning("No valid dates for forecasting")
    else:
        days = (datetime.today() - df["Date"].min()).days
        avg = len(df) / max(days,1)
        proj = int(avg * 90)

        st.metric("Projected Quarter", proj)

# -----------------------------
# INSIGHTS
# -----------------------------
st.sidebar.subheader("🧠 Insights")

if not df.empty:
    if df["Outcome"].mean() < 75:
        st.sidebar.warning("⚠️ Outcomes dropping")

    trauma = len(df[df["Category"]=="Trauma"])
    arthro = len(df[df["Category"]=="Arthroplasty"])

    if trauma > arthro * 2:
        st.sidebar.warning("⚠️ Too much Trauma vs Arthroplasty")

# -----------------------------
# REPORTS
# -----------------------------
with tab5:
    st.title("📑 Reports")

    st.download_button("Download CSV", df.to_csv(index=False), "report.csv")

# -----------------------------
# UPLOAD
# -----------------------------
upload = st.sidebar.file_uploader("Upload CSV")

if upload:
    new = pd.read_csv(upload)
    st.session_state.df = pd.concat([df, new], ignore_index=True)
    save()
    st.success("Uploaded successfully")
