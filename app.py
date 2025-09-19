# app.py
import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from pathlib import Path

# Optional Plotly (nice interactive charts) — fallback to built-in charts if missing
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except Exception:
    PLOTLY_AVAILABLE = False

# -------------------------------
# App config
# -------------------------------
st.set_page_config(page_title="Ortho Tracker — Improved", layout="wide")
DATA_FILE = Path("procedures.csv")

DEFAULT_STAFF = [
    "JOSEPHINE","JACOB","NYOKABI","NAOMI","CHARITY","KEVIN",
    "MIRIAM","KIGEN","FAITH","JAMES","GEOFFREY","SPENCER",
    "EVANS","KENYORU"
]

FUN_FACTS = [
    "The femur (thigh bone) is the longest and strongest bone in the human body.",
    "Arthroscopy allows surgeons to see inside joints using tiny cameras.",
    "Hip replacements are considered one of the most successful surgeries in medicine.",
    "Children heal bones faster than adults due to better blood supply.",
    "Orthopedic implants are often made of titanium which is biocompatible.",
    "Knee replacement is one of the most common orthopedic procedures worldwide."
]

# -------------------------------
# Session-state initialization
# -------------------------------
if "staff_list" not in st.session_state:
    st.session_state.staff_list = DEFAULT_STAFF.copy()

if "df" not in st.session_state:
    if DATA_FILE.exists():
        try:
            st.session_state.df = pd.read_csv(DATA_FILE, parse_dates=["Date"])
        except Exception:
            st.session_state.df = pd.DataFrame(columns=[
                "Date","Hospital","Region","Procedure","Surgeon","Staff","DurationHrs","Outcome","Notes"
            ])
    else:
        st.session_state.df = pd.DataFrame(columns=[
            "Date","Hospital","Region","Procedure","Surgeon","Staff","DurationHrs","Outcome","Notes"
        ])

# -------------------------------
# Helpers
# -------------------------------
def save_df():
    try:
        st.session_state.df.to_csv(DATA_FILE, index=False)
    except Exception as e:
        st.error(f"Failed to save data: {e}")

def generate_random(n=50, days_back=365):
    hospitals = ["Nairobi Hosp","Kijabe Hosp","MTRH Eldoret","Meru Hosp","Mombasa Hosp","Kisii Hosp"]
    regions = ["Nairobi/Kijabe","Eldoret","Meru","Mombasa","Kisii"]
    procedures = ["Arthroplasty","Fracture Fixation","Spinal Surgery","Knee Replacement","Hip Replacement","Arthroscopy"]
    surgeons = ["Dr. Achieng","Dr. Patel","Dr. Kamau","Dr. Smith","Dr. Wang"]
    rows = []
    for _ in range(n):
        d = datetime.today() - timedelta(days=random.randint(0, days_back))
        rows.append({
            "Date": d.date(),
            "Hospital": random.choice(hospitals),
            "Region": random.choice(regions),
            "Procedure": random.choice(procedures),
            "Surgeon": random.choice(surgeons),
            "Staff": random.choice(st.session_state.staff_list),
            "DurationHrs": round(random.uniform(0.5,6.0), 1),
            "Outcome": random.randint(60,100),
            "Notes": "Auto-generated"
        })
    return pd.DataFrame(rows)

def add_medals(df_counts, name_col):
    df = df_counts.copy()
    medals = ["🥇","🥈","🥉"]
    df[name_col] = df[name_col].astype(str)
    for i in range(min(3, len(df))):
        df.loc[i, name_col] = f"{medals[i]} {df.loc[i, name_col]}"
    return df

# -------------------------------
# Sidebar / Navigation
# -------------------------------
with st.sidebar:
    st.title("Ortho Tracker")
    page = st.radio("Navigate", ["Dashboard","Add Procedure","Leaderboards","Reports","Test Data","Settings"])
    st.write("---")
    if st.button("💡 Show random orthopedics fact"):
        fact = random.choice(FUN_FACTS)
        with st.modal("🦴 Did you know?"):
            st.write(fact)
            st.success("Nice, right?")
    st.caption("Preload test data in Test Data → Generate")

# -------------------------------
# Pages
# -------------------------------
# Dashboard
if page == "Dashboard":
    st.header("📊 Dashboard — Key insights")
    df = st.session_state.df.copy()
    if df.empty:
        st.info("No records yet. Add procedures or generate test data.")
    else:
        # ensure Date dtype
        if df["Date"].dtype == object:
            try:
                df["Date"] = pd.to_datetime(df["Date"])
            except Exception:
                pass

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Procedures", len(df))
        c2.metric("Hospitals", df["Hospital"].nunique())
        c3.metric("Regions", df["Region"].nunique())
        c4.metric("Active Staff", df["Staff"].nunique())

        st.markdown("### Monthly trend")
        monthly = df.groupby(df["Date"].dt.to_period("M")).size().sort_index()
        if PLOTLY_AVAILABLE:
            fig = px.line(x=monthly.index.astype(str), y=monthly.values, labels={"x":"Month","y":"Count"}, title="Monthly Procedures")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.line_chart(monthly.rename("count"))

        st.markdown("### Region share")
        region_counts = df["Region"].value_counts()
        if PLOTLY_AVAILABLE:
            fig = px.pie(names=region_counts.index, values=region_counts.values, title="Region Share")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.bar_chart(region_counts)

        st.markdown("### Recent records")
        st.dataframe(df.sort_values("Date", ascending=False).head(12))

        if st.button("🎉 Celebrate top staff"):
            top = df["Staff"].value_counts().index[0]
            with st.modal("👏 Staff recognition"):
                st.write(f"Shoutout to **{top}** — top staff by assisted procedures.")
                st.balloons()

# Add Procedure
elif page == "Add Procedure":
    st.header("➕ Add Procedure")
    with st.form("add_form", clear_on_submit=True):
        date = st.date_input("Date", datetime.today())
        hospital = st.text_input("Hospital", "")
        region = st.text_input("Region", "")
        procedure = st.text_input("Procedure", "")
        surgeon = st.text_input("Surgeon", "")
        staff = st.selectbox("Staff", st.session_state.staff_list)
        duration = st.number_input("Duration (hours)", min_value=0.1, max_value=24.0, step=0.1, value=2.0)
        outcome = st.slider("Outcome (0-100)", 0, 100, 80)
        notes = st.text_area("Notes", "")
        submitted = st.form_submit_button("Save")
        if submitted:
            new = {
                "Date": date,
                "Hospital": hospital.strip() or "Unknown",
                "Region": region.strip() or "Unknown",
                "Procedure": procedure.strip() or "Unknown",
                "Surgeon": surgeon.strip() or "Unknown",
                "Staff": staff,
                "DurationHrs": duration,
                "Outcome": outcome,
                "Notes": notes.strip()
            }
            st.session_state.df = pd.concat([st.session_state.df, pd.DataFrame([new])], ignore_index=True)
            save_df()
            st.success("Record saved ✅")

# Leaderboards
elif page == "Leaderboards":
    st.header("🏆 Leaderboards")
    df = st.session_state.df.copy()
    if df.empty:
        st.info("No data yet.")
    else:
        surgeon_counts = df["Surgeon"].value_counts().reset_index()
        surgeon_counts.columns = ["Surgeon","Procedures"]
        staff_counts = df["Staff"].value_counts().reset_index()
        staff_counts.columns = ["Staff","Procedures"]

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Top Surgeons")
            st.dataframe(add_medals(surgeon_counts, "Surgeon").head(10), use_container_width=True)
        with col2:
            st.subheader("Top Staff")
            st.dataframe(add_medals(staff_counts, "Staff").head(10), use_container_width=True)

# Reports
elif page == "Reports":
    st.header("📥 Reports & Export")
    df = st.session_state.df.copy()
    if df.empty:
        st.info("No data.")
    else:
        st.subheader("Raw data")
        st.dataframe(df)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "procedures_export.csv", "text/csv")
        # Excel export (optional)
        try:
            import io, openpyxl
            towrite = io.BytesIO()
            with pd.ExcelWriter(towrite, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="procedures")
            towrite.seek(0)
            st.download_button("Download Excel", towrite, "procedures.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except Exception:
            st.info("Excel export not available (openpyxl not installed).")

# Test Data
elif page == "Test Data":
    st.header("🧪 Test Data Generator")
    n = st.number_input("Number of records", min_value=1, max_value=2000, value=50)
    if st.button("Generate & Overwrite"):
        st.session_state.df = generate_random(n)
        save_df()
        st.success(f"Generated {n} records and saved to {DATA_FILE}")

# Settings
elif page == "Settings":
    st.header("⚙️ Settings")
    st.subheader("Manage staff")
    st.write(st.session_state.staff_list)
    new = st.text_input("Add staff name")
    if st.button("Add staff"):
        if new and new not in st.session_state.staff_list:
            st.session_state.staff_list.append(new.strip())
            st.success(f"Added {new}")
        else:
            st.warning("Invalid or duplicate name")
