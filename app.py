import streamlit as st
import pandas as pd
import numpy as np
import openai
from datetime import datetime
import random

st.set_page_config(page_title="Autonomous Sales AI", layout="wide")

# =========================================================
# AI CONFIG
# =========================================================
st.sidebar.title("🔐 AI Settings")
api_key = st.sidebar.text_input("OpenAI Key", type="password")

if api_key:
    openai.api_key = api_key

# =========================================================
# SESSION DATA
# =========================================================
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame()

df = st.session_state.df

# =========================================================
# MASTER DATA
# =========================================================
REPS = ["Kevin","Charity","Naomi","Carol","Josephine","Geoffrey","Jacob","Faith","Erick","Spencer","Evans","Miriam","Brian"]
DOCTORS = ["Dr Achieng","Dr Patel","Dr Kamau","Dr Smith","Dr Njoroge","Dr Otieno"]
HOSPITALS = ["MTRH","Kijabe","Nairobi Hospital","Mombasa Hospital","Meru Hospital"]

# =========================================================
# TEST DATA
# =========================================================
def generate_data(n=300):
    data = []

    for _ in range(n):
        revenue = random.randint(80000, 500000)
        cost = int(revenue * random.uniform(0.5, 0.75))

        data.append({
            "Date": datetime.today(),
            "Rep": random.choice(REPS),
            "Doctor": random.choice(DOCTORS),
            "Hospital": random.choice(HOSPITALS),
            "Revenue": revenue,
            "Cost": cost,
            "Profit": revenue - cost,
            "Outcome": random.randint(60,100)
        })

    return pd.DataFrame(data)

# =========================================================
# PROCESS DATA
# =========================================================
def process(df):
    if df.empty:
        return df

    df["Date"] = pd.to_datetime(df["Date"])

    df["Score"] = (
        df["Revenue"] * 0.4 +
        df["Profit"] * 0.4 +
        df["Outcome"] * 1000 * 0.2
    )

    return df

df = process(df)

# =========================================================
# AUTONOMOUS ANALYSIS ENGINE (CORE BRAIN)
# =========================================================
def autonomous_analysis(df):
    alerts = []
    insights = []

    if df.empty:
        return alerts, insights

    rep_perf = df.groupby("Rep")["Revenue"].sum()

    # ALERTS
    if len(rep_perf) > 0:
        worst_rep = rep_perf.idxmin()
        best_rep = rep_perf.idxmax()

        alerts.append(f"⚠️ Weak Rep Detected: {worst_rep}")
        alerts.append(f"🏆 Top Rep: {best_rep}")

    region_perf = df.groupby("Hospital")["Revenue"].sum()

    if len(region_perf) > 0:
        worst_hosp = region_perf.idxmin()
        alerts.append(f"🏥 Underperforming Hospital: {worst_hosp}")

    # INSIGHTS
    insights.append(f"Total Revenue: {df['Revenue'].sum():,.0f}")
    insights.append(f"Total Profit: {df['Profit'].sum():,.0f}")
    insights.append(f"Total Records: {len(df)}")

    return alerts, insights

# =========================================================
# FORECAST ENGINE
# =========================================================
def forecast(df):
    if df.empty:
        return None

    df = df.copy()
    df["Month"] = df["Date"].dt.month

    monthly = df.groupby("Month")["Revenue"].sum()

    if len(monthly) < 2:
        return None

    x = np.arange(len(monthly))
    slope = np.polyfit(x, monthly.values, 1)[0]

    return max(monthly.values[-1] + slope, 0)

# =========================================================
# GPT COPILOT
# =========================================================
def gpt(df, q):
    if df.empty:
        return "No data available"

    summary = f"""
    Revenue: {df['Revenue'].sum()}
    Profit: {df['Profit'].sum()}
    Top Rep: {df.groupby('Rep')['Revenue'].sum().idxmax()}
    Worst Rep: {df.groupby('Rep')['Revenue'].sum().idxmin()}
    """

    prompt = f"""
You are an enterprise autonomous AI analyst.

DATA:
{summary}

QUESTION:
{q}

Give precise business insight.
"""

    try:
        res = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"You are a senior BI AI."},
                {"role":"user","content":prompt}
            ],
            temperature=0.3
        )

        return res["choices"][0]["message"]["content"]

    except:
        return "AI not configured"

# =========================================================
# NAVIGATION
# =========================================================
page = st.sidebar.radio(
    "Autonomous AI System",
    ["🏠 Dashboard","🧠 AI Copilot","🚨 Alerts","📈 Forecast","⚙️ Data Engine"]
)

# =========================================================
# ⚙️ DATA ENGINE
# =========================================================
if page == "⚙️ Data Engine":
    st.title("Data Generator")

    if st.button("Generate 300 Records"):
        st.session_state.df = generate_data(300)
        st.success("Autonomous dataset created")

# =========================================================
# 🏠 DASHBOARD (AUTO INSIGHTS)
# =========================================================
elif page == "🏠 Dashboard":
    st.title("Autonomous Executive Dashboard")

    if df.empty:
        st.warning("Generate data first")
        st.stop()

    alerts, insights = autonomous_analysis(df)

    c1,c2,c3 = st.columns(3)
    c1.metric("Revenue", f"{df['Revenue'].sum():,.0f}")
    c2.metric("Profit", f"{df['Profit'].sum():,.0f}")
    c3.metric("Records", len(df))

    st.subheader("📊 Auto Insights")
    for i in insights:
        st.info(i)

# =========================================================
# 🚨 ALERTS
# =========================================================
elif page == "🚨 Alerts":
    st.title("🚨 Autonomous Alerts")

    alerts, _ = autonomous_analysis(df)

    for a in alerts:
        st.warning(a)

# =========================================================
# 📈 FORECAST
# =========================================================
elif page == "📈 Forecast":
    st.title("📈 Autonomous Forecast Engine")

    pred = forecast(df)

    if pred:
        st.metric("Next Revenue Forecast", f"{pred:,.0f}")
    else:
        st.warning("Not enough data")

# =========================================================
# 🧠 AI COPILOT
# =========================================================
elif page == "🧠 AI Copilot":
    st.title("Autonomous GPT Copilot")

    q = st.text_input("Ask anything")

    if st.button("Ask AI"):
        st.success(gpt(df, q))
