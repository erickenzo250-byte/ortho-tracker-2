import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Ortho BI + AI System", layout="wide")

# =========================================================
# LOAD DATA
# =========================================================
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame()

df = st.session_state.df

# =========================================================
# SAFE PROCESSING
# =========================================================
def process(df):
    if df.empty:
        return df

    for c in ["Doctor","Rep","Hospital","Region","Procedure"]:
        if c not in df.columns:
            df[c] = "Unknown"

    df["Revenue"] = df.get("Revenue", 100000)
    df["Cost"] = df.get("Cost", 60000)
    df["Profit"] = df["Revenue"] - df["Cost"]

    df["Outcome"] = pd.to_numeric(df.get("Outcome", 70), errors="coerce").fillna(70)

    df["AI_Score"] = (
        df["Outcome"] * 0.4 +
        (df["Revenue"] / 100000) * 0.3 +
        (df["Profit"] / 100000) * 0.3
    )

    df["Date"] = pd.to_datetime(df.get("Date", pd.Timestamp.today()), errors="coerce")

    return df

df = process(df)

# =========================================================
# TIME FILTER ENGINE (POWER BI STYLE)
# =========================================================
def time_filter(df, period):
    if df.empty:
        return df

    now = pd.Timestamp.today()

    if period == "Last 7 Days":
        return df[df["Date"] >= now - pd.Timedelta(days=7)]

    if period == "Last 30 Days":
        return df[df["Date"] >= now - pd.Timedelta(days=30)]

    if period == "Last 90 Days":
        return df[df["Date"] >= now - pd.Timedelta(days=90)]

    return df

# =========================================================
# AI CHAT ENGINE
# =========================================================
def ai_chat(df, q):
    q = q.lower()

    if df.empty:
        return "No data available."

    if "doctor" in q and "weak" in q:
        d = df.groupby("Doctor")["AI_Score"].mean().sort_values().head(1)
        return f"⚠️ Weak Doctor: {d.index[0]}"

    if "best doctor" in q:
        d = df.groupby("Doctor")["AI_Score"].mean().sort_values(ascending=False).head(1)
        return f"🏆 Best Doctor: {d.index[0]}"

    if "revenue" in q:
        return f"💰 Revenue: {df['Revenue'].sum():,.0f}"

    if "drop" in q or "down" in q:
        r = df.groupby("Region")["Revenue"].sum()
        return f"📉 Weak Region: {r.idxmin()}"

    if "rep" in q:
        r = df.groupby("Rep")["Revenue"].sum().sort_values(ascending=False)
        return f"👥 Top Rep: {r.index[0]}"

    return "Ask: doctor, rep, revenue, region, performance, weak, best"

# =========================================================
# NAVIGATION
# =========================================================
page = st.sidebar.radio(
    "BI System",
    ["📊 Dashboard","🤖 AI Chat","📁 Upload"]
)

# =========================================================
# 📁 UPLOAD
# =========================================================
if page == "📁 Upload":
    st.title("📁 Upload Data")

    file = st.file_uploader("CSV / Excel")

    if file:
        if file.name.endswith(".csv"):
            new = pd.read_csv(file)
        else:
            new = pd.read_excel(file)

        st.session_state.df = pd.concat([df, new], ignore_index=True)
        st.session_state.df = process(st.session_state.df)

        st.success("Uploaded successfully")

# =========================================================
# 📊 DASHBOARD (POWER BI STYLE)
# =========================================================
elif page == "📊 Dashboard":
    st.title("📊 Power BI Style Dashboard")

    if df.empty:
        st.warning("No data available")
        st.stop()

    # -------------------------
    # TIME FILTER
    # -------------------------
    period = st.selectbox(
        "Time Filter",
        ["All Time","Last 7 Days","Last 30 Days","Last 90 Days"]
    )

    df_f = time_filter(df, period)

    # -------------------------
    # CROSS FILTERS
    # -------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        region = st.multiselect("Region", df_f["Region"].unique(), df_f["Region"].unique())

    with col2:
        doctor = st.multiselect("Doctor", df_f["Doctor"].unique(), df_f["Doctor"].unique())

    with col3:
        rep = st.multiselect("Rep", df_f["Rep"].unique(), df_f["Rep"].unique())

    df_f = df_f[
        df_f["Region"].isin(region) &
        df_f["Doctor"].isin(doctor) &
        df_f["Rep"].isin(rep)
    ]

    # -------------------------
    # KPIs
    # -------------------------
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Cases", len(df_f))
    c2.metric("Revenue", f"{df_f['Revenue'].sum():,.0f}")
    c3.metric("Profit", f"{df_f['Profit'].sum():,.0f}")
    c4.metric("AI Score", f"{df_f['AI_Score'].mean():.1f}")

    st.divider()

    # -------------------------
    # DRILLDOWN TABLES
    # -------------------------
    st.subheader("👨‍⚕️ Doctor Performance")

    doc = df_f.groupby("Doctor").agg({
        "Revenue":"sum",
        "Profit":"sum",
        "AI_Score":"mean"
    }).sort_values("AI_Score", ascending=False)

    selected = st.selectbox("Drill into Doctor", doc.index)

    st.dataframe(doc)
    st.dataframe(df_f[df_f["Doctor"] == selected])

    st.subheader("👥 Rep Performance")
    st.dataframe(df_f.groupby("Rep")["Revenue"].sum())

    st.subheader("🏥 Hospital Performance")
    st.dataframe(df_f.groupby("Hospital")["Revenue"].sum())

# =========================================================
# 🤖 AI CHAT (POWER BI COPILOT STYLE)
# =========================================================
elif page == "🤖 AI Chat":
    st.title("🤖 BI Copilot AI")

    st.info("Ask anything about your data")

    q = st.text_input("Ask a question")

    if st.button("Ask AI"):
        st.success(ai_chat(df, q))
