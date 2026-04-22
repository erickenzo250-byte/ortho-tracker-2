import streamlit as st
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="Relationship AI System", layout="wide")

# =========================================================
# DATA INIT
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
# TEST DATA GENERATION (RELATIONSHIP STRUCTURED)
# =========================================================
def generate_data(n=300):
    data = []

    for _ in range(n):
        hospital = random.choice(HOSPITALS)
        doctor = random.choice(DOCTORS)
        rep = random.choice(REPS)

        revenue = random.randint(80000, 400000)
        cost = int(revenue * random.uniform(0.5, 0.8))
        profit = revenue - cost

        data.append({
            "Date": datetime.today() - timedelta(days=random.randint(0, 365)),
            "Rep": rep,
            "Doctor": doctor,
            "Hospital": hospital,
            "Revenue": revenue,
            "Cost": cost,
            "Profit": profit,
            "Outcome": random.randint(60,100)
        })

    return pd.DataFrame(data)

# =========================================================
# PROCESSING
# =========================================================
def process(df):
    if df.empty:
        return df

    df["Score"] = (
        df["Revenue"] * 0.4 +
        df["Profit"] * 0.4 +
        df["Outcome"] * 1000 * 0.2
    )

    return df

df = process(df)

# =========================================================
# FORECAST ENGINE
# =========================================================
def forecast(df):
    if df.empty:
        return None

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    monthly = df.groupby("Month")["Revenue"].sum().values

    if len(monthly) < 2:
        return None

    x = np.arange(len(monthly))
    slope = np.polyfit(x, monthly, 1)[0]

    return max(monthly[-1] + slope, 0)

# =========================================================
# RELATIONSHIP GRAPH BUILDER
# =========================================================
def build_graph(df):
    G = nx.Graph()

    if df.empty:
        return G

    for _, row in df.iterrows():
        rep = row["Rep"]
        doctor = row["Doctor"]
        hospital = row["Hospital"]
        revenue = row["Revenue"]

        # Nodes
        G.add_node(rep, type="Rep")
        G.add_node(doctor, type="Doctor")
        G.add_node(hospital, type="Hospital")

        # Edges (RELATIONSHIPS)
        G.add_edge(rep, doctor, weight=revenue)
        G.add_edge(doctor, hospital, weight=revenue)
        G.add_edge(rep, hospital, weight=revenue)

    return G

# =========================================================
# NAVIGATION
# =========================================================
page = st.sidebar.radio(
    "AI System",
    ["📊 Dashboard","🕸️ Network Map","📈 Forecast","🧪 Generate Data"]
)

# =========================================================
# 🧪 GENERATE DATA
# =========================================================
if page == "🧪 Generate Data":
    st.title("Generate Relationship Dataset (300 rows)")

    if st.button("Generate"):
        st.session_state.df = generate_data(300)
        st.success("Dataset generated")
        st.dataframe(st.session_state.df.head())

# =========================================================
# 📊 DASHBOARD
# =========================================================
elif page == "📊 Dashboard":
    st.title("📊 Relationship Intelligence Dashboard")

    if df.empty:
        st.warning("No data available")
        st.stop()

    c1,c2,c3 = st.columns(3)
    c1.metric("Cases", len(df))
    c2.metric("Revenue", f"{df['Revenue'].sum():,.0f}")
    c3.metric("Profit", f"{df['Profit'].sum():,.0f}")

    st.subheader("👥 Rep Performance")
    st.dataframe(df.groupby("Rep")[["Revenue","Profit","Score"]].sum())

# =========================================================
# 📈 FORECAST
# =========================================================
elif page == "📈 Forecast":
    st.title("📈 Revenue Forecast Engine")

    pred = forecast(df)

    if pred:
        st.metric("Next Month Forecast", f"KES {pred:,.0f}")
    else:
        st.warning("Not enough data")

# =========================================================
# 🕸️ NETWORK MAP (KEY FEATURE)
# =========================================================
elif page == "🕸️ Network Map":
    st.title("🕸️ Relationship Network Map")

    if df.empty:
        st.warning("No data available")
        st.stop()

    G = build_graph(df)

    plt.figure(figsize=(10,7))

    pos = nx.spring_layout(G, k=0.5)

    node_colors = []

    for node in G.nodes(data=True):
        if node[1]["type"] == "Rep":
            node_colors.append("blue")
        elif node[1]["type"] == "Doctor":
            node_colors.append("green")
        else:
            node_colors.append("orange")

    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color=node_colors,
        node_size=800,
        font_size=8
    )

    st.pyplot(plt)
