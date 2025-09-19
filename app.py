import streamlit as st
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# ✅ Custom CSS
st.markdown("""
    <style>
        .main {
            background-color: #f5fbfb;
        }
        h1, h2, h3, h4 {
            color: #007272;
        }
        .stMetric {
            background: #e6f7f7;
            border-radius: 15px;
            padding: 15px;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# ✅ Fun Facts
facts = [
    "🦵 Knee replacement is one of the most common orthopedic procedures worldwide.",
    "🦴 Orthopedic implants can last 15–20 years depending on patient activity.",
    "📖 The word 'orthopedic' comes from Greek meaning 'straight child'.",
    "🏃 Hip replacements are considered one of the most successful surgeries of the 20th century.",
    "🧬 Bone is the only tissue that can regenerate without scarring.",
    "🦴 The femur (thigh bone) is the longest and strongest bone in the body.",
    "💀 The smallest bone is the stapes in the ear, just 3mm long!",
    "🏥 In some countries, over 1 million hip and knee replacements are performed annually."
]

# ✅ Staff
default_staff = [
    "JOSEPHINE","JACOB","NYOKABI","NAOMI","CHARITY","KEVIN",
    "MIRIAM","KIGEN","FAITH","JAMES","GEOFFREY","SPENCER",
    "EVANS","KENYORU"
]

if "staff_list" not in st.session_state:
    st.session_state.staff_list = default_staff.copy()

# ✅ Initialize data
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Date", "Hospital", "Region", "Procedure", "Surgeon", "Staff", "Notes"
    ])

# ✅ Sidebar menu
menu = ["Dashboard", "Add Procedure", "Generate Monthly Report", "Region Report", 
        "Forecast Procedures", "Leaderboards", "Manage Staff", "Generate Test Data"]
choice = st.sidebar.radio("📌 Menu", menu)


# ----------------- Dashboard -----------------
def show_dashboard(procedures_df):
    st.markdown("<h1 style='text-align: center;'>🦴 Ortho Tracker Dashboard</h1>", unsafe_allow_html=True)

    if procedures_df.empty:
        st.info("No data yet. Add records or generate test data from the sidebar.")
        return

    # ✅ Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📝 Total Procedures", len(procedures_df))
    with col2:
        st.metric("🏥 Hospitals", procedures_df["Hospital"].nunique())
    with col3:
        st.metric("🌍 Regions", procedures_df["Region"].nunique())
    with col4:
        st.metric("👩‍⚕️ Active Staff", procedures_df["Staff"].nunique())

    st.markdown("---")

    # ✅ Growth Insights
    st.subheader("📈 Growth Insights")
    monthly_growth = procedures_df.groupby(procedures_df["Date"].dt.to_period("M")).size()
    fig, ax = plt.subplots(figsize=(6,3))
    monthly_growth.plot(kind="line", marker="o", color="#009999", ax=ax)
    ax.set_ylabel("Procedures")
    ax.set_xlabel("Month")
    ax.set_title("Monthly Growth of Procedures")
    st.pyplot(fig)

    st.markdown("---")

    # ✅ Regional Performance
    st.subheader("🌍 Procedures per Region")
    region_counts = procedures_df["Region"].value_counts()
    region_percent = (region_counts / region_counts.sum() * 100).round(1)

    fig3, ax3 = plt.subplots(figsize=(6,3))
    region_counts.plot(kind="bar", color="#66b3ff", ax=ax3)

    # Add percentage labels
    for i, (count, pct) in enumerate(zip(region_counts, region_percent)):
        ax3.text(i, count + 0.5, f"{pct}%", ha="center", va="bottom", fontsize=9, color="black")

    ax3.set_ylabel("Procedures")
    ax3.set_xlabel("Region")
    ax3.set_title("Regional Procedure Counts & % Share")
    st.pyplot(fig3)

    st.markdown("---")

    # ✅ Staff Participation
    st.subheader("👩‍⚕️ Staff Participation")
    staff_counts = procedures_df["Staff"].value_counts().head(10)
    fig2, ax2 = plt.subplots(figsize=(6,3))
    staff_counts.plot(kind="bar", color="#33cccc", ax=ax2)
    ax2.set_ylabel("Procedures")
    ax2.set_xlabel("Staff")
    ax2.set_title("Top Staff Participation")
    st.pyplot(fig2)

    st.markdown("---")

    # ✅ Popups
    if st.button("💡 Show Orthopedic Fun Fact"):
        with st.modal("🦴 Did You Know?"):
            st.write(random.choice(facts))
            st.success("Keep learning more about orthopedics!")

    if st.button("🎉 Celebrate Top Staff"):
        top_staff = staff_counts.index[0]
        with st.modal("👏 Staff Recognition"):
            st.write(f"Big shoutout to **{top_staff}** for assisting in the most procedures!")
            st.balloons()


# ----------------- Add Procedure -----------------
if choice == "Add Procedure":
    st.subheader("➕ Add Procedure Record")
    with st.form("entry_form"):
        date = st.date_input("Date")
        hospital = st.text_input("Hospital (enter name)")
        region = st.text_input("Region (enter name)")
        procedure = st.text_input("Procedure")
        surgeon = st.text_input("Surgeon")
        staff = st.selectbox("Staff", st.session_state.staff_list)
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Submit")

        if submitted:
            new_record = {
                "Date": pd.to_datetime(date),
                "Hospital": hospital.strip(),
                "Region": region.strip(),
                "Procedure": procedure.strip(),
                "Surgeon": surgeon.strip(),
                "Staff": staff.strip(),
                "Notes": notes.strip(),
            }
            st.session_state.data = pd.concat(
                [st.session_state.data, pd.DataFrame([new_record])],
                ignore_index=True
            )
            st.success("✅ Record added successfully!")


# ----------------- Monthly Report -----------------
elif choice == "Generate Monthly Report":
    st.subheader("📑 Monthly Report")
    if not st.session_state.data.empty:
        st.write(st.session_state.data)
        monthly_report = (
            st.session_state.data.groupby(
                [st.session_state.data["Date"].dt.to_period("M"), "Region"]
            )["Procedure"].count().reset_index()
        )
        monthly_report.columns = ["Month", "Region", "Procedure Count"]
        st.write(monthly_report)
    else:
        st.warning("No data available")


# ----------------- Region Report -----------------
elif choice == "Region Report":
    st.subheader("📍 Region Report")
    if not st.session_state.data.empty:
        regions = st.session_state.data["Region"].unique().tolist()
        selected_region = st.selectbox("Select Region", regions)
        region_data = st.session_state.data[st.session_state.data["Region"] == selected_region]

        st.write(f"### Records for {selected_region}")
        st.write(region_data)

        region_summary = (
            region_data.groupby(region_data["Date"].dt.to_period("M"))["Procedure"]
            .count()
            .reset_index()
        )
        region_summary.columns = ["Month", "Procedure Count"]

        st.write("### Monthly Summary")
        st.write(region_summary)
        st.line_chart(region_summary.set_index("Month"))
    else:
        st.warning("No data available")


# ----------------- Forecast -----------------
elif choice == "Forecast Procedures":
    st.subheader("🔮 Forecast Procedure Counts (Simple Projection)")
    if not st.session_state.data.empty:
        df = st.session_state.data.copy()
        df["Month"] = df["Date"].dt.to_period("M")
        monthly_counts = df.groupby("Month")["Procedure"].count().to_timestamp()

        if len(monthly_counts) >= 2:
            last_val = monthly_counts.iloc[-1]
            forecast = pd.Series(
                [last_val + random.randint(-2, 5) for _ in range(3)],
                index=pd.date_range(monthly_counts.index[-1] + pd.offsets.MonthBegin(),
                                    periods=3, freq="MS")
            )
            st.line_chart(pd.concat([monthly_counts, forecast]))
        else:
            st.warning("Not enough data for forecasting.")
    else:
        st.warning("No data available.")


# ----------------- Leaderboards -----------------
elif choice == "Leaderboards":
    st.subheader("🏆 Leaderboards")
    if not st.session_state.data.empty:
        staff_counts = st.session_state.data["Staff"].value_counts()
        surgeon_counts = st.session_state.data["Surgeon"].value_counts()

        col1, col2 = st.columns(2)
        with col1:
            st.write("### 👩‍⚕️ Staff Leaderboard")
            st.bar_chart(staff_counts.head(10))

        with col2:
            st.write("### 🧑‍⚕️ Surgeon Leaderboard")
            st.bar_chart(surgeon_counts.head(10))

        # ✅ Popup for surgeon recognition
        if st.button("🏅 Celebrate Top Surgeon"):
            top_surgeon = surgeon_counts.index[0]
            with st.modal("👏 Surgeon Recognition"):
                st.write(f"Special recognition to **{top_surgeon}** for leading the most procedures!")
                st.balloons()
    else:
        st.warning("No data available.")


# ----------------- Manage Staff -----------------
elif choice == "Manage Staff":
    st.subheader("👩‍⚕️ Manage Staff")
    st.write("Current staff list:", st.session_state.staff_list)

    new_staff = st.text_input("Add new staff (name)")
    if st.button("Add Staff"):
        if new_staff and new_staff not in st.session_state.staff_list:
            st.session_state.staff_list.append(new_staff.strip())
            st.success(f"✅ {new_staff} added to staff list!")
        else:
            st.warning("Enter a valid unique staff name.")


# ----------------- Generate Test Data -----------------
elif choice == "Generate Test Data":
    st.subheader("🧪 Generate Random Test Data (50 procedures)")

    if st.button("Generate"):
        hospitals = ["Nairobi Hosp", "Kijabe Hosp", "MTRH Eldoret", "Meru Hosp", "Mombasa Hosp", "Kisii Hosp"]
        regions = ["Nairobi/Kijabe", "Eldoret", "Meru", "Mombasa", "Kisii"]
        procedures = ["Arthroplasty", "Fracture Fixation", "Spinal Surgery", "Knee Replacement", "Hip Replacement"]
        surgeons = ["Dr. A", "Dr. B", "Dr. C", "Dr. D"]

        new_data = []
        for _ in range(50):
            new_data.append({
                "Date": datetime.today() - timedelta(days=random.randint(0, 365)),
                "Hospital": random.choice(hospitals),
                "Region": random.choice(regions),
                "Procedure": random.choice(procedures),
                "Surgeon": random.choice(surgeons),
                "Staff": random.choice(st.session_state.staff_list),
                "Notes": "Auto-generated test record"
            })

        st.session_state.data = pd.DataFrame(new_data)
        st.success("✅ 50 random test procedures generated!")


# ----------------- Default Dashboard -----------------
else:
    show_dashboard(st.session_state.data)
