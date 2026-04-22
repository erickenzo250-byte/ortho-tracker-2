import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Enterprise Sales AI", layout="wide")

# =========================================================
# LOAD DATA
# =========================================================
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame()

df = st.session_state.df

# =========================================================
# PROCESS DATA (SAFE + INTELLIGENT)
# =========================================================
def process(df):
    if df.empty:
        return df

    for c in ["Rep","Hospital","Region"]:
        if c not in df.columns:
            df[c] = "Unknown"

    df["Revenue"] = df.get("Revenue", 100000)
    df["Cost"] = df.get("Cost", 60000)
    df["Profit"] = df["Revenue"] - df["Cost"]

    df["Outcome"] = pd.to_numeric(df.get("Outcome", 70), errors="coerce").fillna(70)

    # SALES PERFORMANCE SCORE
    df["Sales_Score"] = (
        df["Revenue"] * 0.5 +
        df["Profit"] * 0.3 +
        df["Outcome"] * 1000 * 0.2
    )

    df["Date"] = pd.to_datetime(df.get("Date", pd.Timestamp.today()), errors="coerce")

    return df

df = process(df)

# =========================================================
# FORECAST ENGINE (PER REP + TOTAL)
# =========================================================
def forecast(df):
    if df.empty:
        return None, None

    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    monthly = df.groupby("Month")["Revenue"].sum().reset_index()

    if len(monthly) < 2:
        return None, None

    x = np.arange(len(monthly))
    y = monthly["Revenue"].values

    slope = np.polyfit(x, y, 1)[0]
    total_forecast = max(y[-1] + slope, 0)

    # rep forecast
    rep_forecast = df.groupby("Rep")["Revenue"].sum() * 1.05

    return total_forecast, rep_forecast

# =========================================================
# COMMISSION ENGINE
# =========================================================
def commission(df, rate=0.08):
    if df.empty:
        return pd.DataFrame()

    comm = df.groupby("Rep").agg({
        "Revenue":"sum",
        "Profit":"sum"
    })

    comm["Commission"] = comm["Profit"] * rate
    return comm.sort_values("Commission", ascending=False)

# =========================================================
# GPT-STYLE SALES CHAT (SIMPLIFIED COPILOT)
# =========================================================
def gpt_chat(df, q):
    q = q.lower()

    if df.empty:
        return "No sales data available."

    if "best rep" in q:
        r = df.groupby("Rep")["Sales_Score"].sum().idxmax()
        return f"🏆 Best performing rep: {r}"

    if "underperform" in q:
        r = df.groupby("Rep")["Sales_Score"].sum().idxmin()
        return f"⚠️ Underperforming rep: {r}"

    if "forecast" in q:
        total, _ = forecast(df)
        return f"📈 Next period forecast revenue: {total:,.0f}"

    if "commission" in q:
        top = commission(df).head(1).index[0]
        return f"💰 Top commission earner: {top}"

    if "region" in q:
        r = df.groupby("Region")["Revenue"].sum().idxmin()
        return f"📉 Weak region: {r}"

    return "Ask: best rep, underperforming rep, forecast, commission, region"

# =========================================================
# NAVIGATION
# =========================================================
page = st.sidebar.radio(
    "Enterprise AI System",
    ["📊 Dashboard","🤖 GPT Sales Chat","💰 Commission","📁 Upload"]
)

# =========================================================
# 📁 UPLOAD
# =========================================================
if page == "📁 Upload":
    st.title("Upload Sales Data")

    file = st.file_uploader("CSV / Excel")

    if file:
        if file.name.endswith(".csv"):
            new = pd.read_csv(file)
        else:
            new = pd.read_excel(file)

        st.session_state.df = pd.concat([df, new], ignore_index=True)
        st.session_state.df = process(st.session_state.df)

        st.success("Data loaded successfully")

# =========================================================
# 📊 DASHBOARD (ENTERPRISE VIEW)
# =========================================================
elif page == "📊 Dashboard":
    st.title("📊 Enterprise Sales Command Center")

    if df.empty:
        st.warning("No data available")
        st.stop()

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Sales Entries", len(df))
    c2.metric("Revenue", f"{df['Revenue'].sum():,.0f}")
    c3.metric("Profit", f"{df['Profit'].sum():,.0f}")
    c4.metric("Avg Score", f"{df['Sales_Score'].mean():.1f}")

    st.divider()

    st.subheader("👥 Rep Ranking")

    rep = df.groupby("Rep").agg({
        "Revenue":"sum",
        "Profit":"sum",
        "Sales_Score":"sum"
    }).sort_values("Sales_Score", ascending=False)

    st.dataframe(rep)

# =========================================================
# 🤖 GPT CHAT
# =========================================================
elif page == "🤖 GPT Sales Chat":
    st.title("🤖 Sales AI Copilot")

    q = st.text_input("Ask your sales AI")

    if st.button("Ask"):
        st.success(gpt_chat(df, q))

# =========================================================
# 💰 COMMISSION
# =========================================================
elif page == "💰 Commission":
    st.title("💰 Commission Engine")

    rate = st.slider("Commission Rate (%)", 1, 20, 8) / 100

    comm = commission(df, rate)

    st.dataframe(comm)

    st.download_button(
        "Download Commission Report",
        comm.to_csv(),
        "commission_report.csv"
    )
