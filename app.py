import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

st.set_page_config(page_title="Ortho AI Intelligence System", layout="wide")

DATA_FILE = Path("ortho_ai_data.csv")

# =========================================================
# LOAD DATA
# =========================================================
def load():
    if DATA_FILE.exists():
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame()

if "df" not in st.session_state:
    st.session_state.df = load()

def save():
    st.session_state.df.to_csv(DATA_FILE, index=False)

# =========================================================
# INTELLIGENT DATA PROCESSING
# =========================================================
def process(df):
    if df.empty:
        return df

    required = ["Doctor","Rep","Hospital","Region","Outcome"]

    for c in required:
        if c not in df.columns:
            df[c] = "Unknown"

    df["Revenue"] = df.get("Revenue", 100000)
    df["Cost"] = df.get("Cost", 60000)
    df["Profit"] = df["Revenue"] - df["Cost"]

    df["Outcome"] = pd.to_numeric(df["Outcome"], errors="coerce").fillna(70)

    # AI Score (multi-factor intelligence)
    df["AI_Score"] = (
        df["Outcome"] * 0.45 +
        (df["Revenue"] / 100000) * 0.25 +
        (df["Profit"] / 100000) * 0.30
    )

    return df

df = process(st.session_state.df)

# =========================================================
# AI ENGINE (DECISION MAKER)
# =========================================================
def ai_engine(df):
    insights = []

    if df.empty:
        return ["No data available"]

    # TOP DOCTOR
    top_doc = df.groupby("Doctor")["AI_Score"].mean().sort_values(ascending=False).head(1)
    insights.append(f"🟢 Top Doctor: {top_doc.index[0]}")

    # WEAK DOCTOR
    weak_doc = df.groupby("Doctor")["AI_Score"].mean().sort_values().head(1)
    insights.append(f"🔴 Needs Support: {weak_doc.index[0]}")

    # REGION RISK
    region = df.groupby("Region")["Revenue"].sum()
    insights.append(f"⚠️ Weak Region: {region.idxmin()}")

    # REP PERFORMANCE
    rep = df.groupby("Rep")["Revenue"].sum()
    insights.append(f"📊 Best Rep: {rep.idxmax()}")

    return insights

# =========================================================
# FORECAST ENGINE (TREND-BASED)
# =========================================================
def forecast(df):
    if df.empty or "Date" not in df.columns:
        return None

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    monthly = df.groupby("Month")["Revenue"].sum().reset_index()

    if len(monthly) < 2:
        return None

    x = np.arange(len(monthly))
    y = monthly["Revenue"].values

    slope = np.polyfit(x, y, 1)[0]

    next_month = y[-1] + slope

    return max(next_month, 0)

# =========================================================
# REPORT ENGINE
# =========================================================
def report(df):
    if df.empty:
        return "No data"

    return f"""
ORTHO EXECUTIVE AI REPORT

Total Cases: {len(df)}
Revenue: {df['Revenue'].sum():,.0f}
Profit: {df['Profit'].sum():,.0f}
Average Outcome: {df['Outcome'].mean():.1f}

Top Region: {df.groupby('Region')['Revenue'].sum().idxmax()}
Top Doctor: {df.groupby('Doctor')['AI_Score'].mean().idxmax()}

AI Insight:
- Optimize low performing doctors
- Increase support in weak regions
- Balance rep distribution
"""

# =========================================================
# NAVIGATION
# =========================================================
page = st.sidebar.radio(
    "AI Intelligence System",
    ["📊 Dashboard","🤖 AI Engine","📈 Forecast","⚠️ Alerts","📑 Report","📁 Upload"]
)

# =========================================================
# 📁 UPLOAD
# =========================================================
if page == "📁 Upload":
    st.title("📁 Upload Hospital Data")

    file = st.file_uploader("Upload CSV / Excel")

    if file:
        if file.name.endswith(".csv"):
            new = pd.read_csv(file)
        else:
            new = pd.read_excel(file)

        st.session_state.df = pd.concat([df, new], ignore_index=True)
        st.session_state.df = process(st.session_state.df)

        save()
        st.success("Data loaded successfully")

# =========================================================
# 📊 DASHBOARD
# =========================================================
elif page == "📊 Dashboard":
    st.title("📊 Executive Intelligence Dashboard")

    if df.empty:
        st.warning("No data")
        st.stop()

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Cases", len(df))
    c2.metric("Revenue", f"{df['Revenue'].sum():,.0f}")
    c3.metric("Profit", f"{df['Profit'].sum():,.0f}")
    c4.metric("AI Score", f"{df['AI_Score'].mean():.1f}")

    st.subheader("📈 Performance Trend")

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Month"] = df["Date"].dt.to_period("M").astype(str)
        st.line_chart(df.groupby("Month")["Revenue"].sum())

# =========================================================
# 🤖 AI ENGINE
# =========================================================
elif page == "🤖 AI Engine":
    st.title("🤖 AI Decision Engine")

    for i in ai_engine(df):
        st.success(i)

# =========================================================
# 📈 FORECAST
# =========================================================
elif page == "📈 Forecast":
    st.title("📈 Predictive Intelligence")

    pred = forecast(df)

    if pred:
        st.metric("Next Month Revenue Forecast", f"KES {pred:,.0f}")
    else:
        st.warning("Not enough data for prediction")

# =========================================================
# ⚠️ ALERTS
# =========================================================
elif page == "⚠️ Alerts":
    st.title("⚠️ Risk Alerts")

    alerts = []

    if df["Outcome"].mean() < 75:
        alerts.append("Low clinical outcomes detected")

    weak = df.groupby("Doctor")["AI_Score"].mean().sort_values().head(1)
    alerts.append(f"Doctor needing support: {weak.index[0]}")

    for a in alerts:
        st.warning(a)

# =========================================================
# 📑 REPORT
# =========================================================
elif page == "📑 Report":
    st.title("📑 Executive AI Report")

    rep = report(df)

    st.text(rep)

    st.download_button(
        "Download Report",
        rep,
        file_name="ai_executive_report.txt"
    )
