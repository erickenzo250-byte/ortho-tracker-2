import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Ortho Command System V5", layout="wide")
DATA_FILE = Path("procedures.csv")

# -----------------------------
# LOGIN (SIMPLE)
# -----------------------------
USERS = {
    "admin": "admin123",
    "erick": "1234",
    "kevin": "1234"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Ortho Command Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if USERS.get(user) == pwd:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()

# -----------------------------
# UI STYLE
# -----------------------------
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg,#0f172a,#1e293b); color:white;}
.kpi {background:#1e3a8a;padding:15px;border-radius:10px;text-align:center;}
</style>
""", unsafe_allow_html=True)

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
def generate(n=300):
    rows=[]
    for _ in range(n):
        p=random.choice(PROCEDURES)
        rows.append({
            "Date":datetime.today()-timedelta(days=random.randint(0,365)),
            "Region":random.choice(["Eldoret","Nairobi","Mombasa","Meru"]),
            "Procedure":p,
            "Category":CATEGORY_MAP[p],
            "Rep":random.choice(REPS),
            "Revenue":VALUE[p],
            "Cost":COST[p],
            "Outcome":random.randint(65,100)
        })
    df=pd.DataFrame(rows)
    df["Profit"]=df["Revenue"]-df["Cost"]
    return df

# -----------------------------
# TABS
# -----------------------------
tab1,tab2,tab3,tab4,tab5 = st.tabs([
    "📊 Executive","👥 Reps","🏥 Hospitals","📈 Forecast","📑 Reports"
])

df = st.session_state.df

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
        st.stop()

    total=len(df)
    revenue=df["Revenue"].sum()
    profit=df["Profit"].sum()
    outcome=df["Outcome"].mean()

    c1,c2,c3,c4=st.columns(4)
    c1.metric("Procedures",total)
    c2.metric("Revenue",f"KES {revenue:,.0f}")
    c3.metric("Profit",f"KES {profit:,.0f}")
    c4.metric("Outcome",f"{outcome:.1f}")

# -----------------------------
# REPS
# -----------------------------
with tab2:
    st.title("👥 Rep Command Center")

    rep=df.groupby("Rep").agg({"Procedure":"count","Revenue":"sum","Profit":"sum"})
    rep=rep.rename(columns={"Procedure":"Cases"})

    TARGET=50
    rep["Target"]=TARGET
    rep["Achievement %"]=(rep["Cases"]/TARGET*100).round(1)
    rep["Commission"]=rep["Profit"]*0.05

    st.dataframe(rep.sort_values("Revenue",ascending=False))

    st.subheader("🔍 Drill Down")
    r=st.selectbox("Select Rep",rep.index)
    st.line_chart(df[df["Rep"]==r].groupby("Date").size())

# -----------------------------
# HOSPITALS
# -----------------------------
with tab3:
    st.title("🏥 Hospital Intelligence")

    hosp=df.groupby("Region").agg({"Revenue":"sum","Profit":"sum"})
    st.bar_chart(hosp)

# -----------------------------
# FORECAST
# -----------------------------
with tab4:
    st.title("📈 Forecast Engine")

    days=(datetime.today()-df["Date"].min()).days
    avg=len(df)/max(days,1)
    proj=int(avg*90)

    st.metric("Projected Quarter",proj)

# -----------------------------
# INSIGHTS
# -----------------------------
def insights(df):
    msgs=[]
    if df["Outcome"].mean()<75:
        msgs.append("⚠️ Outcomes dropping → investigate")
    if df["Profit"].sum()<0:
        msgs.append("⚠️ Business running at loss")
    if len(df[df["Category"]=="Trauma"])>len(df[df["Category"]=="Arthroplasty"])*2:
        msgs.append("⚠️ Over-reliance on Trauma → push Arthroplasty")
    return msgs

st.sidebar.subheader("🧠 Insights")
for m in insights(df):
    st.sidebar.warning(m)

# -----------------------------
# REPORTS
# -----------------------------
with tab5:
    st.title("📑 Reports")

    if st.button("Download Executive Report"):
        st.download_button("Download CSV",df.to_csv(index=False),"report.csv")

# -----------------------------
# UPLOAD
# -----------------------------
upload=st.sidebar.file_uploader("Upload Data")
if upload:
    new=pd.read_csv(upload)
    st.session_state.df=pd.concat([df,new])
    save()
    st.success("Uploaded")
