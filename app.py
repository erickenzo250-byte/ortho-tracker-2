import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="Enterprise SaaS AI", layout="wide")

# =========================================================
# SIMPLE LOGIN (SaaS STYLE)
# =========================================================
USERS = {
    "admin": "admin123",
    "manager": "manager123"
}

if "auth" not in st.session_state:
    st.session_state.auth = False

def login():
    st.title("🔐 Enterprise AI Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user in USERS and USERS[user] == pwd:
            st.session_state.auth = True
            st.success("Login successful")
        else:
            st.error("Invalid credentials")

if not st.session_state.auth:
    login()
    st.stop()

# =========================================================
# DATA INITIALIZATION
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
# DATA GENERATOR (300 ROWS)
# =========================================================
def generate_data(n=300):
    data = []

    for _ in range(n):
        revenue = random.randint(80000, 500000)
        cost = int(revenue * random.uniform(0.5, 0.8))

        data.append({
            "Date": datetime.today() - timedelta(days=random.randint(0, 365)),
            "Rep": random.choice(REPS),
            "Doctor": random.choice(DOCTORS),
            "Hospital": random.choice(HOSPITALS),
            "Revenue": revenue,
            "Cost": cost,
            "Profit": revenue - cost
        })

    return pd.DataFrame(data)

# =========================================================
# INSIGHTS AI (STABLE)
# =========================================================
def insights(df):
    if df.empty:
        return []

    out = []

    rep = df.groupby("Rep")["Revenue"].sum()
    hosp = df.groupby("Hospital")["Revenue"].sum()

    out.append(f"🏆 Top Rep: {rep.idxmax()}")
    out.append(f"⚠️ Weak Rep: {rep.idxmin()}")
    out.append(f"🏥 Best Hospital: {hosp.idxmax()}")
    out.append(f"📉 Lowest Hospital: {hosp.idxmin()}")

    margin = (df["Profit"] / df["Revenue"]).mean()
    out.append(f"💰 Avg Margin: {margin:.2f}")

    return out

# =========================================================
# ANOMALY DETECTION
# =========================================================
def anomalies(df):
    alerts = []

    if df.empty:
        return alerts

    for col in ["Revenue", "Profit"]:
        mean = df[col].mean()
        std = df[col].std()

        if std == 0:
            continue

        z = (df[col] - mean) / std

        if (abs(z) > 2).any():
            alerts.append(f"⚠️ Anomaly detected in {col}")

    return alerts

# =========================================================
# FORECASTING (SIMPLE TREND)
# =========================================================
def forecast(df):
    if df.empty:
        return None

    monthly = df.groupby(df["Date"].dt.month)["Revenue"].sum()

    if len(monthly) < 2:
        return None

    x = np.arange(len(monthly))
    slope = np.polyfit(x, monthly.values, 1)[0]

    return monthly.iloc[-1] + slope

# =========================================================
# EXECUTIVE REPORT
# =========================================================
def report(df):
    if df.empty:
        return "No data"

    return f"""
EXECUTIVE REPORT

Revenue: {df['Revenue'].sum():,.0f}
Profit: {df['Profit'].sum():,.0f}

Top Rep: {df.groupby('Rep')['Revenue'].sum().idxmax()}
Weak Rep: {df.groupby('Rep')['Revenue'].sum().idxmin()}

Insight:
- Performance imbalance exists across reps
- Revenue concentrated in top performers
- Opportunity in low-performing hospitals

Recommendation:
- Rebalance territories
- Focus training on weak reps
"""

# =========================================================
# NAVIGATION
# =========================================================
page = st.sidebar.radio(
    "Enterprise SaaS AI",
    ["📊 Dashboard","🧪 Data Engine","🚨 Alerts","📈 Forecast","🤖 AI Report"]
)

# =========================================================
# 🧪 DATA ENGINE
# =========================================================
if page == "🧪 Data Engine":
    st.title("Data Engine")

    if st.button("Generate 300 Records"):
        st.session_state.df = generate_data(300)
        st.success("Data generated")

    if not df.empty:
        st.dataframe(df.head())

# =========================================================
# 📊 DASHBOARD
# =========================================================
elif page == "📊 Dashboard":
    st.title("📊 Executive Dashboard")

    if df.empty:
        st.warning("Generate dataset first")
        st.stop()

    # FILTERS
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
    c1,c2,c3 = st.columns(3)
    c1.metric("Revenue", f"{df_f['Revenue'].sum():,.0f}")
    c2.metric("Profit", f"{df_f['Profit'].sum():,.0f}")
    c3.metric("Records", len(df_f))

    st.divider()

    st.subheader("🧠 AI Insights")
    for i in insights(df_f):
        st.info(i)

    st.subheader("📊 Data Table")
    st.dataframe(df_f, use_container_width=True)

# =========================================================
# 🚨 ALERTS
# =========================================================
elif page == "🚨 Alerts":
    st.title("🚨 Alerts Engine")

    if df.empty:
        st.warning("No data")
        st.stop()

    for a in anomalies(df):
        st.warning(a)

# =========================================================
# 📈 FORECAST
# =========================================================
elif page == "📈 Forecast":
    st.title("📈 Forecast Engine")

    pred = forecast(df)

    if pred:
        st.metric("Next Revenue Forecast", f"{pred:,.0f}")
    else:
        st.warning("Not enough data")

# =========================================================
# 🤖 AI REPORT
# =========================================================
elif page == "🤖 AI Report":
    st.title("🤖 Executive AI Report")

    st.text_area("Report", report(df), height=400)

    st.download_button(
        "Download Report",
        report(df),
        file_name="executive_report.txt"
    )
