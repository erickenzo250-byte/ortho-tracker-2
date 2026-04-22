import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="Ortho Intelligence AI System", layout="wide")

DATA_FILE = Path("ortho_data.csv")

# =========================================================
# MASTER DATA (FALLBACK FOR DEMO / CLEANING)
# =========================================================
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
    "Geoffrey","Jacob","Faith","Erick","Spencer","Evans","Miriam","Brian"
]

# =========================================================
# LOAD DATA
# =========================================================
def load_data():
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        return df
    return pd.DataFrame()

if "df" not in st.session_state:
    st.session_state.df = load_data()

def save():
    st.session_state.df.to_csv(DATA_FILE, index=False)

# =========================================================
# CLEAN + ENGINEERING
# =========================================================
def process(df):
    if df.empty:
        return df

    df["Category"] = df["Procedure"].map(CATEGORY_MAP)
    df["Revenue"] = df["Procedure"].map(VALUE)
    df["Cost"] = df["Procedure"].map(COST)
    df["Profit"] = df["Revenue"] - df["Cost"]

    # Doctor performance score
    df["Doctor_Score"] = (
        df["Outcome"] * 0.4 +
        (df["Revenue"] / 100000) * 0.3 +
        (df["Profit"] / 100000) * 0.3
    )

    return df

df = process(st.session_state.df)

# =========================================================
# AI ENGINE
# =========================================================
def ai_assistant(df, query):
    query = query.lower()

    if df.empty:
        return "No data available."

    # TOP DOCTOR
    if "best doctor" in query or "top doctor" in query:
        doc = df.groupby("Doctor")["Doctor_Score"].mean().sort_values(ascending=False).head(1)
        return f"Top doctor: {doc.index[0]} (Score: {doc.values[0]:.2f})"

    # REVENUE
    if "revenue" in query:
        return f"Total revenue: KES {df['Revenue'].sum():,.0f}"

    # PROFIT
    if "profit" in query:
        return f"Total profit: KES {df['Profit'].sum():,.0f}"

    # REGION
    if "region" in query:
        r = df.groupby("Region")["Revenue"].sum().sort_values(ascending=False)
        return f"Best region: {r.index[0]} (KES {r.iloc[0]:,.0f})"

    # DOCTORS LOW
    if "worst" in query or "low" in query:
        doc = df.groupby("Doctor")["Doctor_Score"].mean().sort_values().head(1)
        return f"Lowest doctor: {doc.index[0]} (Score: {doc.values[0]:.2f})"

    # CASE MIX
    if "trauma" in query or "arthroplasty" in query:
        t = len(df[df["Category"]=="Trauma"])
        a = len(df[df["Category"]=="Arthroplasty"])
        return f"Trauma: {t}, Arthroplasty: {a}"

    return "Ask about: doctors, revenue, profit, regions, performance."

# =========================================================
# NAVIGATION
# =========================================================
page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard","👨‍⚕️ Doctors","📁 Upload Data","🤖 AI Assistant","📑 Reports"]
)

# =========================================================
# 📁 UPLOAD DATA
# =========================================================
if page == "📁 Upload Data":
    st.title("📁 Upload Real Hospital Data")

    file = st.file_uploader("Upload CSV or Excel")

    if file:
        if file.name.endswith(".csv"):
            new_df = pd.read_csv(file)
        else:
            new_df = pd.read_excel(file)

        st.session_state.df = pd.concat([df, new_df], ignore_index=True)
        st.session_state.df = process(st.session_state.df)
        save()

        st.success("Data uploaded successfully")
        st.dataframe(st.session_state.df.head())

# =========================================================
# 📊 DASHBOARD
# =========================================================
elif page == "📊 Dashboard":
    st.title("📊 Executive Dashboard")

    if df.empty:
        st.warning("No data available")
        st.stop()

    # FILTERS
    st.sidebar.subheader("Filters")

    region_f = st.sidebar.multiselect("Region", df["Region"].dropna().unique(), df["Region"].dropna().unique())
    rep_f = st.sidebar.multiselect("Doctor", df["Doctor"].dropna().unique(), df["Doctor"].dropna().unique())

    df_f = df[df["Region"].isin(region_f) & df["Doctor"].isin(rep_f)]

    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Cases", len(df_f))
    c2.metric("Revenue", f"KES {df_f['Revenue'].sum():,.0f}")
    c3.metric("Profit", f"KES {df_f['Profit'].sum():,.0f}")
    c4.metric("Avg Outcome", f"{df_f['Outcome'].mean():.1f}")

    st.divider()

    # TREND
    st.subheader("📈 Trend")
    df_f["Month"] = df_f["Date"].dt.to_period("M").astype(str)
    st.line_chart(df_f.groupby("Month").size())

    # TOP DOCTORS
    st.subheader("👨‍⚕️ Top Doctors")

    doc = df_f.groupby("Doctor").agg({
        "Revenue":"sum",
        "Profit":"sum",
        "Doctor_Score":"mean",
        "Outcome":"mean"
    }).sort_values("Doctor_Score", ascending=False)

    st.dataframe(doc)

    # INSIGHTS
    st.subheader("🧠 Insights")

    if df_f["Outcome"].mean() < 75:
        st.warning("Clinical outcomes below target")

    top = doc.index[0]
    st.success(f"Top performer: {top}")

# =========================================================
# 👨‍⚕️ DOCTOR MODULE
# =========================================================
elif page == "👨‍⚕️ Doctors":
    st.title("👨‍⚕️ Doctor Performance System")

    doc = df.groupby("Doctor").agg({
        "Revenue":"sum",
        "Profit":"sum",
        "Outcome":"mean",
        "Doctor_Score":"mean",
        "Hospital":"count"
    }).rename(columns={"Hospital":"Cases"}).sort_values("Doctor_Score", ascending=False)

    st.dataframe(doc)

    st.subheader("🏆 Top 5 Doctors")
    st.dataframe(doc.head(5))

    st.subheader("⚠️ Bottom 5 Doctors")
    st.dataframe(doc.tail(5))

# =========================================================
# 🤖 AI ASSISTANT
# =========================================================
elif page == "🤖 AI Assistant":
    st.title("🤖 AI Decision Assistant")

    st.info("Ask questions like: best doctor, revenue, profit, region performance, etc.")

    q = st.text_input("Ask something")

    if st.button("Analyze"):
        answer = ai_assistant(df, q)
        st.success(answer)

# =========================================================
# 📑 REPORTS
# =========================================================
elif page == "📑 Reports":
    st.title("📑 Executive Reports")

    report = df.groupby(["Region","Doctor"]).agg({
        "Revenue":"sum",
        "Profit":"sum",
        "Outcome":"mean"
    })

    st.dataframe(report)

    st.download_button(
        "⬇️ Download Report",
        report.to_csv().encode("utf-8"),
        "executive_report.csv"
    )
