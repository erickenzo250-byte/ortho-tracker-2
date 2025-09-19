import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# -------------------------------
# Load or initialize data
# -------------------------------
DATA_FILE = "procedures.csv"

if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["Region", "Procedure", "Surgeon", "Staff", "Date"])

# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(page_title="Ortho Tracker", layout="wide")
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Orthopedic_surgery_icon.png/600px-Orthopedic_surgery_icon.png",
    width=120,
)
st.sidebar.title("Orthopedic Procedure Tracker")
menu = st.sidebar.radio(
    "📌 Menu", ["🏠 Dashboard", "➕ Add Procedure", "📊 Reports", "🏆 Leaderboard"]
)

# -------------------------------
# Dashboard
# -------------------------------
if menu == "🏠 Dashboard":
    st.title("🏥 Orthopedic Procedure Dashboard")
    st.markdown(
        "Welcome to the **Orthopedic Procedure Tracker**. "
        "Monitor surgical activity by region and staff participation."
    )

    if df.empty:
        st.warning("No records yet. Add procedures to see stats.")
    else:
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Procedures", len(df))
        col2.metric("Unique Surgeons", df["Surgeon"].nunique())
        col3.metric("Regions Covered", df["Region"].nunique())

        # Show latest records
        st.subheader("📝 Recent Entries")
        st.dataframe(df.tail(10))

# -------------------------------
# Add Procedure
# -------------------------------
elif menu == "➕ Add Procedure":
    st.title("➕ Add New Procedure Record")

    with st.form("procedure_form", clear_on_submit=True):
        region = st.selectbox(
            "Region", ["Eldoret", "Nairobi/Kijabe", "Meru", "Mombasa", "Kisii"]
        )
        procedure = st.text_input("Procedure Name")
        surgeon = st.text_input("Surgeon Name")
        staff = st.text_input("Staff Name")  # Added Staff
        date = st.date_input("Date")

        submitted = st.form_submit_button("💾 Save Record")
        if submitted:
            new_record = pd.DataFrame(
                [[region, procedure, surgeon, staff, date]],
                columns=["Region", "Procedure", "Surgeon", "Staff", "Date"],
            )
            df = pd.concat([df, new_record], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success("✅ Record saved successfully!")

# -------------------------------
# Reports
# -------------------------------
elif menu == "📊 Reports":
    st.title("📊 Reports & Analytics")

    if df.empty:
        st.warning("No data available for reporting.")
    else:
        # Group by Region
        st.subheader("🗺️ Procedures per Region")
        counts = df["Region"].value_counts()

        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots()
            counts.plot(kind="bar", ax=ax, color="skyblue", edgecolor="black")
            ax.set_ylabel("Count")
            ax.set_title("Procedures by Region")
            st.pyplot(fig)

        with col2:
            fig2, ax2 = plt.subplots()
            counts.plot(
                kind="pie",
                ax=ax2,
                autopct="%1.1f%%",
                startangle=90,
                colormap="Set3",
            )
            ax2.set_ylabel("")
            ax2.set_title("Region Share")
            st.pyplot(fig2)

        # Group by Surgeon
        st.subheader("👨‍⚕️ Procedures per Surgeon (Top 10)")
        surgeon_counts = df["Surgeon"].value_counts().head(10)
        st.bar_chart(surgeon_counts)

        # Option to download data
        st.subheader("📥 Download Data")
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download all data as CSV",
            data=csv,
            file_name="procedures_export.csv",
            mime="text/csv",
        )

# -------------------------------
# Leaderboard
# -------------------------------
elif menu == "🏆 Leaderboard":
    st.title("🏆 Leaderboards")

    if df.empty:
        st.warning("No data available yet.")
    else:
        def add_medals(df_counts, column_name):
            medals = ["🥇", "🥈", "🥉"]
            df_counts[column_name] = df_counts[column_name].astype(str)
            for i in range(min(3, len(df_counts))):
                df_counts.loc[i, column_name] = f"{medals[i]} {df_counts.loc[i, column_name]}"
            return df_counts

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("👨‍⚕️ Surgeon Leaderboard")
            surgeon_counts = df["Surgeon"].value_counts().reset_index()
            surgeon_counts.columns = ["Surgeon", "Procedure Count"]
            surgeon_counts = add_medals(surgeon_counts, "Surgeon")
            st.dataframe(surgeon_counts)

        with col2:
            st.subheader("👩‍⚕️ Staff Leaderboard")
            staff_counts = df["Staff"].value_counts().reset_index()
            staff_counts.columns = ["Staff", "Procedure Count"]
            staff_counts = add_medals(staff_counts, "Staff")
            st.dataframe(staff_counts)
