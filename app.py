import streamlit as st
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from pathlib import Path

try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except Exception:
    PLOTLY_AVAILABLE = False

# -----------------------------------------------
# App config
# -----------------------------------------------
st.set_page_config(page_title="Ortho Tracker", layout="wide", page_icon="🦴")
DATA_FILE = Path("procedures.csv")

DEFAULT_STAFF = [
    "JOSEPHINE", "JACOB", "NYOKABI", "NAOMI", "CHARITY", "KEVIN",
    "MIRIAM", "KIGEN", "FAITH", "JAMES", "GEOFFREY", "SPENCER",
    "EVANS", "KENYORU",
]

PROCEDURES = [
    "Arthroplasty", "Fracture Fixation", "Spinal Surgery",
    "Knee Replacement", "Hip Replacement", "Arthroscopy",
    "ACL Reconstruction", "Shoulder Replacement", "Wrist Fusion",
]

HOSPITALS = [
    "Nairobi Hosp", "Kijabe Hosp", "MTRH Eldoret",
    "Meru Hosp", "Mombasa Hosp", "Kisii Hosp",
]

REGIONS = ["Nairobi/Kijabe", "Eldoret", "Meru", "Mombasa", "Kisii"]

SURGEONS = ["Dr. Achieng", "Dr. Patel", "Dr. Kamau", "Dr. Smith", "Dr. Wang"]

FUN_FACTS = [
    "The femur is the longest and strongest bone in the human body.",
    "Arthroscopy lets surgeons see inside joints using tiny cameras — no large incision needed.",
    "Hip replacements are among the most successful elective surgeries in medicine.",
    "Children heal fractures faster than adults due to better periosteal blood supply.",
    "Orthopedic implants are often titanium alloy — strong, lightweight, and biocompatible.",
    "Knee replacement is the most common orthopedic procedure worldwide.",
    "The human skeleton is completely replaced (remodeled) roughly every 10 years.",
    "Bone is actually a living tissue — it constantly breaks down and rebuilds.",
]

OUTCOME_LABELS = {
    range(0, 60): "Poor",
    range(60, 75): "Fair",
    range(75, 90): "Good",
    range(90, 101): "Excellent",
}

def outcome_label(score):
    for r, label in OUTCOME_LABELS.items():
        if int(score) in r:
            return label
    return "Unknown"

# -----------------------------------------------
# Session-state initialization
# -----------------------------------------------
if "staff_list" not in st.session_state:
    st.session_state.staff_list = DEFAULT_STAFF.copy()

if "df" not in st.session_state:
    if DATA_FILE.exists():
        try:
            df_loaded = pd.read_csv(DATA_FILE)
            df_loaded["Date"] = pd.to_datetime(df_loaded["Date"], errors="coerce")
            st.session_state.df = df_loaded
        except Exception:
            st.session_state.df = pd.DataFrame(columns=[
                "Date", "Hospital", "Region", "Procedure",
                "Surgeon", "Staff", "DurationHrs", "Outcome", "Notes",
            ])
    else:
        st.session_state.df = pd.DataFrame(columns=[
            "Date", "Hospital", "Region", "Procedure",
            "Surgeon", "Staff", "DurationHrs", "Outcome", "Notes",
        ])

# -----------------------------------------------
# Helpers
# -----------------------------------------------
def save_df():
    try:
        st.session_state.df.to_csv(DATA_FILE, index=False)
    except Exception as e:
        st.error(f"Failed to save: {e}")


def get_df_clean():
    """Return df with guaranteed datetime Date column."""
    df = st.session_state.df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])
    return df


def generate_random(n=50, days_back=365):
    rows = []
    for _ in range(n):
        d = datetime.today() - timedelta(days=random.randint(0, days_back))
        rows.append({
            "Date": pd.Timestamp(d),
            "Hospital": random.choice(HOSPITALS),
            "Region": random.choice(REGIONS),
            "Procedure": random.choice(PROCEDURES),
            "Surgeon": random.choice(SURGEONS),
            "Staff": random.choice(st.session_state.staff_list),
            "DurationHrs": round(random.uniform(0.5, 6.0), 1),
            "Outcome": random.randint(60, 100),
            "Notes": "Auto-generated",
        })
    return pd.DataFrame(rows)


def add_medals(df_counts, name_col):
    df = df_counts.reset_index(drop=True).copy()
    medals = ["🥇", "🥈", "🥉"]
    df[name_col] = df[name_col].astype(str)
    for i in range(min(3, len(df))):
        df.loc[i, name_col] = f"{medals[i]} {df.loc[i, name_col]}"
    return df


def color_outcome(val):
    try:
        v = int(val)
    except Exception:
        return ""
    if v >= 90:
        return "background-color: #d4edda; color: #155724"
    if v >= 75:
        return "background-color: #d1ecf1; color: #0c5460"
    if v >= 60:
        return "background-color: #fff3cd; color: #856404"
    return "background-color: #f8d7da; color: #721c24"

# -----------------------------------------------
# Sidebar / Navigation
# -----------------------------------------------
with st.sidebar:
    st.title("🦴 Ortho Tracker")
    st.caption("Orthopedic procedure management")
    st.write("---")
    page = st.radio(
        "Navigate",
        ["Dashboard", "Add Procedure", "Leaderboards", "Reports", "Test Data", "Settings"],
        label_visibility="collapsed",
    )
    st.write("---")

    if st.button("💡 Random fact"):
        st.info(random.choice(FUN_FACTS))

    total = len(st.session_state.df)
    st.caption(f"Total records: **{total}**")

# -----------------------------------------------
# Dashboard
# -----------------------------------------------
if page == "Dashboard":
    st.header("📊 Dashboard")

    df = get_df_clean()

    if df.empty:
        st.info("No records yet. Add procedures manually or generate test data in the Test Data page.")
        st.stop()

    # --- Date filter ---
    st.markdown("#### Filter by date range")
    col_f1, col_f2, col_f3 = st.columns([1, 1, 2])
    with col_f1:
        min_date = df["Date"].min().date()
        max_date = df["Date"].max().date()
        date_from = st.date_input("From", value=min_date, min_value=min_date, max_value=max_date, key="dash_from")
    with col_f2:
        date_to = st.date_input("To", value=max_date, min_value=min_date, max_value=max_date, key="dash_to")
    with col_f3:
        quick = st.selectbox("Quick range", ["All time", "Last 30 days", "Last 90 days", "Last 365 days"], key="dash_quick")

    if quick != "All time":
        days_map = {"Last 30 days": 30, "Last 90 days": 90, "Last 365 days": 365}
        cutoff = datetime.today() - timedelta(days=days_map[quick])
        df = df[df["Date"] >= cutoff]
    else:
        df = df[(df["Date"].dt.date >= date_from) & (df["Date"].dt.date <= date_to)]

    if df.empty:
        st.warning("No records in the selected date range.")
        st.stop()

    # --- Region filter ---
    regions_available = sorted(df["Region"].dropna().unique().tolist())
    selected_regions = st.multiselect("Filter by region", regions_available, default=regions_available, key="dash_region")
    if selected_regions:
        df = df[df["Region"].isin(selected_regions)]

    st.write("---")

    # --- KPI metrics ---
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Procedures", len(df))
    c2.metric("Hospitals", df["Hospital"].nunique())
    c3.metric("Regions", df["Region"].nunique())
    c4.metric("Active Staff", df["Staff"].nunique())
    avg_outcome = df["Outcome"].mean() if not df.empty else 0
    c5.metric("Avg Outcome", f"{avg_outcome:.1f}")

    st.write("---")

    # --- Charts ---
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("##### Monthly trend")
        monthly = df.groupby(df["Date"].dt.to_period("M")).size().sort_index()
        monthly.index = monthly.index.astype(str)
        if PLOTLY_AVAILABLE:
            fig = px.line(
                x=monthly.index, y=monthly.values,
                labels={"x": "Month", "y": "Procedures"},
                markers=True,
            )
            fig.update_layout(margin=dict(t=10, b=10, l=0, r=0), height=260)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.line_chart(monthly.rename("count"))

    with col_r:
        st.markdown("##### Region share")
        region_counts = df["Region"].value_counts()
        if PLOTLY_AVAILABLE:
            fig = px.pie(names=region_counts.index, values=region_counts.values, hole=0.35)
            fig.update_layout(margin=dict(t=10, b=10, l=0, r=0), height=260)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.bar_chart(region_counts)

    col_l2, col_r2 = st.columns(2)

    with col_l2:
        st.markdown("##### Procedures by type")
        proc_counts = df["Procedure"].value_counts()
        if PLOTLY_AVAILABLE:
            fig = px.bar(
                x=proc_counts.values, y=proc_counts.index,
                orientation="h",
                labels={"x": "Count", "y": "Procedure"},
            )
            fig.update_layout(margin=dict(t=10, b=10, l=0, r=0), height=280)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.bar_chart(proc_counts)

    with col_r2:
        st.markdown("##### Avg duration by procedure (hrs)")
        dur = df.groupby("Procedure")["DurationHrs"].mean().sort_values(ascending=False)
        if PLOTLY_AVAILABLE:
            fig = px.bar(
                x=dur.values, y=dur.index,
                orientation="h",
                labels={"x": "Avg Hours", "y": "Procedure"},
                color=dur.values,
                color_continuous_scale="Blues",
            )
            fig.update_layout(margin=dict(t=10, b=10, l=0, r=0), height=280, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.bar_chart(dur)

    st.write("---")

    # --- Outcome distribution ---
    st.markdown("##### Outcome score distribution")
    if PLOTLY_AVAILABLE:
        fig = px.histogram(df, x="Outcome", nbins=20, labels={"Outcome": "Outcome Score"})
        fig.update_layout(margin=dict(t=10, b=10, l=0, r=0), height=220)
        st.plotly_chart(fig, use_container_width=True)

    # --- Recent records ---
    st.markdown("##### Recent records")
    recent = df.sort_values("Date", ascending=False).head(15).copy()
    recent["Date"] = recent["Date"].dt.strftime("%Y-%m-%d")
    recent["Quality"] = recent["Outcome"].apply(outcome_label)
    st.dataframe(
        recent[["Date", "Hospital", "Region", "Procedure", "Surgeon", "Staff", "DurationHrs", "Outcome", "Quality", "Notes"]],
        use_container_width=True,
        hide_index=True,
    )

    # --- Top staff celebrate ---
    if st.button("🎉 Celebrate top staff"):
        top = df["Staff"].value_counts().index[0]
        top_count = df["Staff"].value_counts().iloc[0]
        st.success(f"🏆 Shoutout to **{top}** — assisted in **{top_count}** procedures!")
        st.balloons()

# -----------------------------------------------
# Add Procedure
# -----------------------------------------------
elif page == "Add Procedure":
    st.header("➕ Add Procedure")

    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            date = st.date_input("Date", datetime.today())
            hospital = st.selectbox("Hospital", [""] + HOSPITALS + ["Other (type below)"])
            hospital_custom = st.text_input("Custom hospital name (if 'Other' selected)", "")
            region = st.selectbox("Region", [""] + REGIONS + ["Other (type below)"])
            region_custom = st.text_input("Custom region name (if 'Other' selected)", "")

        with col2:
            procedure = st.selectbox("Procedure", [""] + PROCEDURES + ["Other (type below)"])
            procedure_custom = st.text_input("Custom procedure name (if 'Other' selected)", "")
            surgeon = st.text_input("Surgeon", placeholder="e.g. Dr. Achieng")
            staff = st.selectbox("Assisting staff", st.session_state.staff_list)

        duration = st.slider("Duration (hours)", min_value=0.5, max_value=12.0, step=0.5, value=2.0)
        outcome = st.slider("Outcome score (0 – 100)", 0, 100, 80)
        st.caption(f"Outcome quality: **{outcome_label(outcome)}**")
        notes = st.text_area("Notes", placeholder="Optional notes about the procedure...")

        submitted = st.form_submit_button("💾 Save procedure", use_container_width=True)

        if submitted:
            hosp_val = hospital_custom.strip() if hospital == "Other (type below)" else hospital.strip()
            reg_val = region_custom.strip() if region == "Other (type below)" else region.strip()
            proc_val = procedure_custom.strip() if procedure == "Other (type below)" else procedure.strip()

            warnings = []
            if not hosp_val:
                warnings.append("Hospital")
            if not reg_val:
                warnings.append("Region")
            if not proc_val:
                warnings.append("Procedure")
            if not surgeon.strip():
                warnings.append("Surgeon")

            if warnings:
                st.warning(f"Please fill in: {', '.join(warnings)}")
            else:
                new_row = {
                    "Date": pd.Timestamp(date),
                    "Hospital": hosp_val,
                    "Region": reg_val,
                    "Procedure": proc_val,
                    "Surgeon": surgeon.strip(),
                    "Staff": staff,
                    "DurationHrs": duration,
                    "Outcome": outcome,
                    "Notes": notes.strip(),
                }
                st.session_state.df = pd.concat(
                    [st.session_state.df, pd.DataFrame([new_row])],
                    ignore_index=True,
                )
                save_df()
                st.success(f"✅ Procedure saved — {proc_val} at {hosp_val}")

# -----------------------------------------------
# Leaderboards
# -----------------------------------------------
elif page == "Leaderboards":
    st.header("🏆 Leaderboards")

    df = get_df_clean()

    if df.empty:
        st.info("No data yet.")
        st.stop()

    # Optional period filter
    period = st.selectbox("Period", ["All time", "This month", "Last 3 months", "This year"])
    now = datetime.today()
    if period == "This month":
        df = df[df["Date"].dt.to_period("M") == pd.Period(now, "M")]
    elif period == "Last 3 months":
        df = df[df["Date"] >= now - timedelta(days=90)]
    elif period == "This year":
        df = df[df["Date"].dt.year == now.year]

    if df.empty:
        st.warning("No records in this period.")
        st.stop()

    st.write("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top Surgeons by procedures")
        surgeon_counts = df["Surgeon"].value_counts().reset_index()
        surgeon_counts.columns = ["Surgeon", "Procedures"]
        st.dataframe(
            add_medals(surgeon_counts, "Surgeon").head(10),
            use_container_width=True, hide_index=True,
        )

        st.markdown("##### Avg outcome by surgeon")
        surg_outcome = df.groupby("Surgeon")["Outcome"].mean().sort_values(ascending=False).reset_index()
        surg_outcome.columns = ["Surgeon", "Avg Outcome"]
        surg_outcome["Avg Outcome"] = surg_outcome["Avg Outcome"].round(1)
        st.dataframe(surg_outcome, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("Top Assisting Staff by procedures")
        staff_counts = df["Staff"].value_counts().reset_index()
        staff_counts.columns = ["Staff", "Procedures"]
        st.dataframe(
            add_medals(staff_counts, "Staff").head(10),
            use_container_width=True, hide_index=True,
        )

        st.markdown("##### Procedures by hospital")
        hosp_counts = df["Hospital"].value_counts().reset_index()
        hosp_counts.columns = ["Hospital", "Procedures"]
        st.dataframe(
            add_medals(hosp_counts, "Hospital").head(10),
            use_container_width=True, hide_index=True,
        )

    st.write("---")

    st.subheader("Staff performance detail")
    if PLOTLY_AVAILABLE:
        staff_detail = df.groupby("Staff").agg(
            Procedures=("Staff", "count"),
            Avg_Outcome=("Outcome", "mean"),
            Avg_Duration=("DurationHrs", "mean"),
        ).reset_index()
        staff_detail["Avg_Outcome"] = staff_detail["Avg_Outcome"].round(1)
        staff_detail["Avg_Duration"] = staff_detail["Avg_Duration"].round(1)
        fig = px.scatter(
            staff_detail, x="Procedures", y="Avg_Outcome",
            size="Avg_Duration", text="Staff",
            labels={"Procedures": "Procedure count", "Avg_Outcome": "Avg outcome score"},
        )
        fig.update_traces(textposition="top center")
        fig.update_layout(height=400, margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------
# Reports
# -----------------------------------------------
elif page == "Reports":
    st.header("📥 Reports & Export")

    df = get_df_clean()

    if df.empty:
        st.info("No data to export.")
        st.stop()

    # Summary stats
    st.subheader("Summary statistics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total procedures", len(df))
    col2.metric("Avg outcome", f"{df['Outcome'].mean():.1f}")
    col3.metric("Avg duration (hrs)", f"{df['DurationHrs'].mean():.1f}")

    st.write("---")

    # Filters
    st.subheader("Filter data for export")
    c1, c2 = st.columns(2)
    with c1:
        filter_region = st.multiselect("Region", sorted(df["Region"].dropna().unique()), key="rep_region")
    with c2:
        filter_proc = st.multiselect("Procedure", sorted(df["Procedure"].dropna().unique()), key="rep_proc")

    export_df = df.copy()
    if filter_region:
        export_df = export_df[export_df["Region"].isin(filter_region)]
    if filter_proc:
        export_df = export_df[export_df["Procedure"].isin(filter_proc)]

    st.caption(f"Showing {len(export_df)} records")
    display_df = export_df.copy()
    display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.write("---")
    st.subheader("Download")

    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        csv = export_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download CSV",
            csv, "procedures_export.csv", "text/csv",
            use_container_width=True,
        )
    with col_dl2:
        try:
            import io
            import openpyxl  # noqa: F401
            towrite = io.BytesIO()
            with pd.ExcelWriter(towrite, engine="openpyxl") as writer:
                export_df.to_excel(writer, index=False, sheet_name="Procedures")
            towrite.seek(0)
            st.download_button(
                "⬇️ Download Excel",
                towrite, "procedures_export.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        except ImportError:
            st.info("Excel export unavailable — install openpyxl.")

# -----------------------------------------------
# Test Data
# -----------------------------------------------
elif page == "Test Data":
    st.header("🧪 Test Data Generator")
    st.info("Generating test data will **overwrite** all existing records.")

    n = st.number_input("Number of records to generate", min_value=1, max_value=2000, value=50, step=10)
    days_back = st.slider("Spread across how many past days?", 30, 730, 365)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚡ Generate & overwrite", type="primary", use_container_width=True):
            st.session_state.df = generate_random(int(n), int(days_back))
            save_df()
            st.success(f"Generated {int(n)} records across the last {int(days_back)} days.")
            st.rerun()
    with col2:
        if st.button("➕ Append to existing", use_container_width=True):
            new_data = generate_random(int(n), int(days_back))
            st.session_state.df = pd.concat([st.session_state.df, new_data], ignore_index=True)
            save_df()
            st.success(f"Appended {int(n)} records. Total: {len(st.session_state.df)}")
            st.rerun()

    if not st.session_state.df.empty:
        st.write("---")
        st.subheader("Current data preview")
        preview = st.session_state.df.copy()
        preview["Date"] = pd.to_datetime(preview["Date"]).dt.strftime("%Y-%m-%d")
        st.dataframe(preview.head(20), use_container_width=True, hide_index=True)

# -----------------------------------------------
# Settings
# -----------------------------------------------
elif page == "Settings":
    st.header("⚙️ Settings")

    # --- Staff management ---
    st.subheader("Manage staff list")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Current staff**")
        for name in sorted(st.session_state.staff_list):
            st.markdown(f"- {name}")

    with col2:
        st.markdown("**Add staff member**")
        new_name = st.text_input("Name", key="new_staff_input", placeholder="e.g. WANJIKU")
        if st.button("➕ Add", use_container_width=True):
            name_clean = new_name.strip().upper()
            if not name_clean:
                st.warning("Please enter a name.")
            elif name_clean in st.session_state.staff_list:
                st.warning(f"{name_clean} is already in the list.")
            else:
                st.session_state.staff_list.append(name_clean)
                st.success(f"Added {name_clean}")
                st.rerun()

        st.markdown("**Remove staff member(s)**")
        to_remove = st.multiselect(
            "Select to remove",
            sorted(st.session_state.staff_list),
            key="remove_staff",
        )
        if st.button("🗑️ Remove selected", use_container_width=True, disabled=not to_remove):
            for name in to_remove:
                st.session_state.staff_list.remove(name)
            st.success(f"Removed: {', '.join(to_remove)}")
            st.rerun()

    st.write("---")

    # --- Data management ---
    st.subheader("Data management")

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("**Export backup**")
        if not st.session_state.df.empty:
            csv_backup = st.session_state.df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download full backup CSV",
                csv_backup, "ortho_backup.csv", "text/csv",
                use_container_width=True,
            )
        else:
            st.info("No data to back up.")

    with col4:
        st.markdown("**Clear all data**")
        if st.checkbox("I understand this will delete all records permanently"):
            if st.button("🗑️ Clear all data", type="primary", use_container_width=True):
                st.session_state.df = pd.DataFrame(columns=[
                    "Date", "Hospital", "Region", "Procedure",
                    "Surgeon", "Staff", "DurationHrs", "Outcome", "Notes",
                ])
                save_df()
                st.success("All records cleared.")
                st.rerun()

    st.write("---")

    # --- App info ---
    st.subheader("About")
    st.markdown("""
    **Ortho Tracker** — Orthopedic procedure management system.

    - Records stored locally in `procedures.csv`
    - Staff list persists in session only (re-add after restart if not saved)
    - For persistent staff across sessions, consider storing to a config file
    """)
