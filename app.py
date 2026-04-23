import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime, date
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import xlsxwriter

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OrthoTrack Pro",
    page_icon="🦴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bone:     #F5F0E8;
    --steel:    #1A2332;
    --titanium: #2D4A6E;
    --accent:   #E8552A;
    --mint:     #3ABFA0;
    --soft:     #8FA3B8;
    --card:     #FFFFFF;
    --border:   #E2E8F0;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bone);
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--steel) 0%, var(--titanium) 100%);
    border-right: none;
}
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .stRadio label { color: #CBD5E1 !important; }
[data-testid="stSidebar"] .stRadio [data-checked="true"] label { color: white !important; }

/* Main Header */
.main-header {
    background: linear-gradient(135deg, var(--steel) 0%, var(--titanium) 60%, #1e6b5a 100%);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.main-header::before {
    content: '🦴';
    position: absolute;
    right: 2rem; top: 50%;
    transform: translateY(-50%);
    font-size: 6rem;
    opacity: 0.1;
}
.main-header h1 { color: white !important; margin: 0; font-size: 2.2rem; letter-spacing: -1px; }
.main-header p  { color: #94A3B8; margin: 0.3rem 0 0; font-size: 0.95rem; }

/* KPI Cards */
.kpi-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.kpi-card {
    background: white;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    flex: 1; min-width: 160px;
    border-left: 4px solid var(--accent);
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.kpi-card.mint  { border-left-color: var(--mint); }
.kpi-card.blue  { border-left-color: var(--titanium); }
.kpi-card.soft  { border-left-color: var(--soft); }
.kpi-card .val  { font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800; color: var(--steel); }
.kpi-card .lbl  { font-size: 0.78rem; color: var(--soft); text-transform: uppercase; letter-spacing: 1px; font-weight: 500; }

/* Form Card */
.form-card {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.07);
    margin-bottom: 1.5rem;
}
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.8rem;
}

/* Streamlit form overrides */
.stTextInput input, .stTextArea textarea, .stSelectbox select,
.stDateInput input, .stMultiSelect .st-bh {
    border-radius: 8px !important;
    border: 1.5px solid var(--border) !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--titanium) !important;
    box-shadow: 0 0 0 3px rgba(45,74,110,0.12) !important;
}

/* Buttons */
.stButton > button {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    letter-spacing: 0.5px;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent), #c44422) !important;
    border: none !important;
    color: white !important;
}

/* Data Table */
.stDataFrame { border-radius: 12px; overflow: hidden; }

/* Tabs */
.stTabs [data-baseweb="tab"] {
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom-color: var(--accent) !important;
}

/* Success / info */
.stSuccess { border-radius: 10px !important; }
.element-container .stAlert { border-radius: 10px !important; }

/* Tag pill */
.tag {
    display: inline-block;
    background: #EEF2FF;
    color: var(--titanium);
    font-size: 0.72rem;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 20px;
    margin: 2px;
}
.badge-accent { background: #FEE2D5; color: var(--accent); }
.badge-mint   { background: #D1FAF0; color: #1a7a65; }
</style>
""", unsafe_allow_html=True)

# ── Data Layer ────────────────────────────────────────────────────────────────
DATA_FILE = "procedures.json"

IMPLANT_OPTIONS = [
    "Total Hip Replacement", "Total Knee Replacement", "Partial Knee",
    "Shoulder Arthroplasty", "Spinal Fusion Cage", "Pedicle Screws",
    "Tibial Nail", "Femoral Nail", "DHS Plate", "Locking Plate",
    "ACL Graft", "Revision Hip Stem", "Revision Knee Tibial",
    "Humeral Nail", "Ankle Replacement", "External Fixator",
    "Other"
]

REGIONS = ["East Africa", "West Africa", "North Africa", "Southern Africa",
           "Central Africa", "Middle East", "Europe", "Other"]

FACILITIES = [
    "Moi Teaching & Referral Hospital", "Kenyatta National Hospital",
    "Aga Khan Hospital Nairobi", "MP Shah Hospital",
    "Nairobi Hospital", "AAR Hospital", "Coast General Hospital",
    "Eldoret Hospital", "Kisumu County Referral", "Other"
]

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)

def get_df():
    data = load_data()
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    return df

# ── PDF Report ────────────────────────────────────────────────────────────────
def generate_pdf(df, title="Procedure Report"):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            rightMargin=40, leftMargin=40,
                            topMargin=50, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"],
                                  fontSize=22, textColor=colors.HexColor("#1A2332"),
                                  spaceAfter=4, fontName="Helvetica-Bold")
    sub_style = ParagraphStyle("SubStyle", parent=styles["Normal"],
                                fontSize=10, textColor=colors.HexColor("#8FA3B8"),
                                spaceAfter=20)
    story.append(Paragraph("🦴 OrthoTrack Pro", title_style))
    story.append(Paragraph(title, sub_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", sub_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#E8552A")))
    story.append(Spacer(1, 16))

    # Summary stats
    story.append(Paragraph("SUMMARY", ParagraphStyle("Sec", fontName="Helvetica-Bold",
                            fontSize=9, textColor=colors.HexColor("#E8552A"),
                            spaceAfter=8, letterSpacing=2)))
    stats_data = [
        ["Total Procedures", "Facilities", "Surgeons", "Regions"],
        [str(len(df)),
         str(df["facility"].nunique()) if "facility" in df.columns else "—",
         str(df["surgeon"].nunique()) if "surgeon" in df.columns else "—",
         str(df["region"].nunique()) if "region" in df.columns else "—"],
    ]
    stats_table = Table(stats_data, colWidths=[120]*4)
    stats_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1A2332")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#F5F0E8"), colors.white]),
        ("FONTNAME", (0,1), (-1,1), "Helvetica-Bold"),
        ("FONTSIZE", (0,1), (-1,1), 14),
        ("TEXTCOLOR", (0,1), (-1,1), colors.HexColor("#1A2332")),
        ("BOX", (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
        ("INNERGRID", (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 20))

    # Procedures table
    story.append(Paragraph("PROCEDURE LOG", ParagraphStyle("Sec2", fontName="Helvetica-Bold",
                            fontSize=9, textColor=colors.HexColor("#E8552A"),
                            spaceAfter=8, letterSpacing=2)))

    cols = ["date", "invoice", "rep", "facility", "region", "surgeon", "procedure"]
    present = [c for c in cols if c in df.columns]
    headers = [c.upper() for c in present]
    rows = [headers]
    for _, row in df[present].iterrows():
        r = []
        for c in present:
            val = str(row[c])
            if c == "date":
                try: val = pd.to_datetime(val).strftime("%d %b %Y")
                except: pass
            if len(val) > 22: val = val[:20] + "…"
            r.append(val)
        rows.append(r)

    col_w = (520 / len(present))
    tbl = Table(rows, colWidths=[col_w]*len(present), repeatRows=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#2D4A6E")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("BOX", (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
        ("INNERGRID", (0,0), (-1,-1), 0.3, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(tbl)

    doc.build(story)
    buf.seek(0)
    return buf

# ── Excel Report ──────────────────────────────────────────────────────────────
def generate_excel(df):
    buf = io.BytesIO()
    workbook = xlsxwriter.Workbook(buf)

    # Formats
    hdr_fmt = workbook.add_format({"bold": True, "bg_color": "#1A2332", "font_color": "white",
                                    "border": 1, "font_size": 10, "font_name": "Calibri"})
    cell_fmt = workbook.add_format({"border": 1, "font_size": 9, "font_name": "Calibri"})
    alt_fmt  = workbook.add_format({"border": 1, "font_size": 9, "font_name": "Calibri",
                                     "bg_color": "#F5F0E8"})
    title_fmt = workbook.add_format({"bold": True, "font_size": 16, "font_name": "Calibri",
                                      "font_color": "#1A2332"})
    accent_fmt = workbook.add_format({"bold": True, "font_size": 22, "font_name": "Calibri",
                                       "font_color": "#E8552A"})
    sub_fmt = workbook.add_format({"font_size": 9, "font_color": "#8FA3B8", "font_name": "Calibri"})

    # Sheet 1: Procedures
    ws = workbook.add_worksheet("Procedures")
    ws.set_zoom(90)
    ws.write("A1", "OrthoTrack Pro", title_fmt)
    ws.write("A2", f"Exported {datetime.now().strftime('%B %d, %Y')}", sub_fmt)

    cols = list(df.columns)
    for ci, col in enumerate(cols):
        ws.write(3, ci, col.upper(), hdr_fmt)
        ws.set_column(ci, ci, 20)

    for ri, (_, row) in enumerate(df.iterrows()):
        fmt = alt_fmt if ri % 2 else cell_fmt
        for ci, col in enumerate(cols):
            val = row[col]
            if isinstance(val, list): val = ", ".join(val)
            if pd.isna(val): val = ""
            ws.write(ri + 4, ci, str(val), fmt)

    # Sheet 2: Summary
    ws2 = workbook.add_worksheet("Summary")
    ws2.write("A1", "SUMMARY STATISTICS", title_fmt)
    stats = [
        ("Total Procedures", len(df)),
        ("Unique Facilities", df["facility"].nunique() if "facility" in df.columns else 0),
        ("Unique Surgeons", df["surgeon"].nunique() if "surgeon" in df.columns else 0),
        ("Unique Reps", df["rep"].nunique() if "rep" in df.columns else 0),
        ("Regions Covered", df["region"].nunique() if "region" in df.columns else 0),
    ]
    for i, (k, v) in enumerate(stats):
        ws2.write(i + 2, 0, k, hdr_fmt)
        ws2.write(i + 2, 1, v, accent_fmt)
    ws2.set_column(0, 0, 25)
    ws2.set_column(1, 1, 15)

    workbook.close()
    buf.seek(0)
    return buf

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🦴 OrthoTrack Pro")
    st.markdown("---")
    page = st.radio("Navigate", [
        "📊 Dashboard",
        "➕ Add Procedure",
        "📋 Procedure Log",
        "📈 Analytics",
        "⬇️ Reports",
    ])
    st.markdown("---")
    df_all = get_df()
    if not df_all.empty:
        st.markdown(f"**{len(df_all)}** procedures logged")
        if "date" in df_all.columns:
            latest = df_all["date"].max()
            st.markdown(f"Last: `{latest.strftime('%d %b %Y')}`")
    st.markdown("---")
    st.markdown("<small style='color:#4a6fa5'>v1.0 · OrthoTrack Pro</small>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.markdown("""
    <div class="main-header">
        <h1>OrthoTrack Pro</h1>
        <p>Orthopedic Procedure Management · Rep Performance · Analytics</p>
    </div>
    """, unsafe_allow_html=True)

    df = get_df()
    if df.empty:
        st.info("🦴 No procedures logged yet. Use **Add Procedure** to get started!")
    else:
        # KPIs
        total = len(df)
        facilities = df["facility"].nunique() if "facility" in df.columns else 0
        surgeons   = df["surgeon"].nunique()   if "surgeon"  in df.columns else 0
        reps       = df["rep"].nunique()        if "rep"      in df.columns else 0

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("🔬 Total Procedures", total)
        with c2:
            st.metric("🏥 Facilities", facilities)
        with c3:
            st.metric("👨‍⚕️ Surgeons", surgeons)
        with c4:
            st.metric("👤 Reps", reps)

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            # Procedures over time
            if "date" in df.columns:
                monthly = df.groupby(df["date"].dt.to_period("M")).size().reset_index()
                monthly.columns = ["Month", "Count"]
                monthly["Month"] = monthly["Month"].astype(str)
                fig = px.area(monthly, x="Month", y="Count",
                              title="Procedures Over Time",
                              color_discrete_sequence=["#E8552A"])
                fig.update_layout(paper_bgcolor="white", plot_bgcolor="#FAFAFA",
                                  font_family="DM Sans", title_font_family="Syne",
                                  title_font_size=14, margin=dict(t=40, b=20, l=20, r=20))
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            if "region" in df.columns:
                reg_counts = df["region"].value_counts().reset_index()
                reg_counts.columns = ["Region", "Count"]
                fig2 = px.bar(reg_counts, x="Region", y="Count",
                              title="Procedures by Region",
                              color="Count", color_continuous_scale=["#2D4A6E", "#3ABFA0"])
                fig2.update_layout(paper_bgcolor="white", plot_bgcolor="#FAFAFA",
                                   font_family="DM Sans", title_font_family="Syne",
                                   title_font_size=14, margin=dict(t=40, b=20, l=20, r=20),
                                   showlegend=False)
                st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            if "rep" in df.columns:
                rep_counts = df["rep"].value_counts().head(10).reset_index()
                rep_counts.columns = ["Rep", "Procedures"]
                fig3 = px.bar(rep_counts, x="Procedures", y="Rep", orientation="h",
                              title="Top Reps by Volume",
                              color="Procedures", color_continuous_scale=["#2D4A6E", "#E8552A"])
                fig3.update_layout(paper_bgcolor="white", plot_bgcolor="#FAFAFA",
                                   font_family="DM Sans", title_font_family="Syne",
                                   title_font_size=14, margin=dict(t=40, b=20, l=20, r=20),
                                   yaxis=dict(autorange="reversed"), showlegend=False)
                st.plotly_chart(fig3, use_container_width=True)

        with col4:
            if "procedure" in df.columns:
                proc_counts = df["procedure"].value_counts().head(8).reset_index()
                proc_counts.columns = ["Procedure", "Count"]
                fig4 = px.pie(proc_counts, values="Count", names="Procedure",
                              title="Procedure Types",
                              color_discrete_sequence=px.colors.sequential.Blues_r[::-1])
                fig4.update_layout(paper_bgcolor="white", font_family="DM Sans",
                                   title_font_family="Syne", title_font_size=14,
                                   margin=dict(t=40, b=20, l=20, r=20))
                st.plotly_chart(fig4, use_container_width=True)

        # Recent procedures
        st.markdown("### Recent Procedures")
        recent = df.sort_values("date", ascending=False).head(8)
        show_cols = [c for c in ["date","rep","procedure","facility","surgeon","region"] if c in recent.columns]
        st.dataframe(recent[show_cols], use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ADD PROCEDURE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "➕ Add Procedure":
    st.markdown("## ➕ Log New Procedure")
    st.markdown("Fill in all procedure details below. Fields marked * are required.")

    with st.form("procedure_form", clear_on_submit=True):
        st.markdown("#### 📋 Core Details")
        c1, c2, c3 = st.columns(3)
        with c1:
            proc_date = st.date_input("📅 Date *", value=date.today())
        with c2:
            invoice   = st.text_input("🧾 Invoice Number *", placeholder="INV-2024-0001")
        with c3:
            rep_name  = st.text_input("👤 Rep Name *", placeholder="Full name")

        st.markdown("#### 🏥 Location")
        c4, c5 = st.columns(2)
        with c4:
            facility  = st.selectbox("🏥 Facility *", ["— Select —"] + FACILITIES)
        with c5:
            region    = st.selectbox("🌍 Region *", ["— Select —"] + REGIONS)

        st.markdown("#### 🔬 Clinical")
        c6, c7 = st.columns(2)
        with c6:
            surgeon   = st.text_input("👨‍⚕️ Surgeon Name *", placeholder="Dr. Full Name")
        with c7:
            procedure = st.text_input("🔬 Procedure Name *", placeholder="e.g. Total Knee Replacement")

        implants = st.multiselect("🦴 Implants Used *", IMPLANT_OPTIONS)

        st.markdown("#### 📝 Notes")
        challenges = st.text_area("⚠️ Challenges Encountered", placeholder="Describe any intraoperative challenges, complications, or notes…", height=100)
        feedback   = st.text_area("💬 Feedback / Outcome", placeholder="Post-procedure feedback, surgeon comments, outcome observations…", height=100)

        submitted = st.form_submit_button("✅ Save Procedure", use_container_width=True, type="primary")

    if submitted:
        errors = []
        if not invoice.strip():   errors.append("Invoice Number")
        if not rep_name.strip():  errors.append("Rep Name")
        if facility == "— Select —": errors.append("Facility")
        if region   == "— Select —": errors.append("Region")
        if not surgeon.strip():   errors.append("Surgeon Name")
        if not procedure.strip(): errors.append("Procedure Name")
        if not implants:          errors.append("Implants Used")

        if errors:
            st.error(f"Please fill in: **{', '.join(errors)}**")
        else:
            record = {
                "id":         datetime.now().strftime("%Y%m%d%H%M%S"),
                "date":       str(proc_date),
                "invoice":    invoice.strip(),
                "rep":        rep_name.strip(),
                "facility":   facility,
                "region":     region,
                "surgeon":    surgeon.strip(),
                "procedure":  procedure.strip(),
                "implants":   implants,
                "challenges": challenges.strip(),
                "feedback":   feedback.strip(),
                "logged_at":  datetime.now().isoformat(),
            }
            data = load_data()
            data.append(record)
            save_data(data)
            st.success(f"✅ Procedure logged successfully! Invoice **{invoice}**")
            st.balloons()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PROCEDURE LOG
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Procedure Log":
    st.markdown("## 📋 Procedure Log")

    df = get_df()
    if df.empty:
        st.info("No procedures found. Start by adding one!")
    else:
        # Filters
        with st.expander("🔍 Filter Procedures", expanded=True):
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                reps_avail = ["All"] + sorted(df["rep"].unique().tolist()) if "rep" in df.columns else ["All"]
                sel_rep = st.selectbox("Rep", reps_avail)
            with fc2:
                regs_avail = ["All"] + sorted(df["region"].unique().tolist()) if "region" in df.columns else ["All"]
                sel_reg = st.selectbox("Region", regs_avail)
            with fc3:
                facs_avail = ["All"] + sorted(df["facility"].unique().tolist()) if "facility" in df.columns else ["All"]
                sel_fac = st.selectbox("Facility", facs_avail)

            fc4, fc5 = st.columns(2)
            with fc4:
                date_from = st.date_input("From", value=df["date"].min().date())
            with fc5:
                date_to   = st.date_input("To",   value=df["date"].max().date())

        filtered = df.copy()
        if sel_rep != "All" and "rep" in filtered.columns:
            filtered = filtered[filtered["rep"] == sel_rep]
        if sel_reg != "All" and "region" in filtered.columns:
            filtered = filtered[filtered["region"] == sel_reg]
        if sel_fac != "All" and "facility" in filtered.columns:
            filtered = filtered[filtered["facility"] == sel_fac]
        filtered = filtered[
            (filtered["date"].dt.date >= date_from) &
            (filtered["date"].dt.date <= date_to)
        ]

        st.markdown(f"Showing **{len(filtered)}** of **{len(df)}** procedures")

        # Show table
        show_cols = [c for c in ["date","invoice","rep","procedure","facility","region","surgeon"] if c in filtered.columns]
        display_df = filtered[show_cols].copy()
        if "date" in display_df.columns:
            display_df["date"] = display_df["date"].dt.strftime("%d %b %Y")
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Detail view
        st.markdown("---")
        st.markdown("### 🔍 View Full Record")
        if "invoice" in filtered.columns:
            inv_list = filtered["invoice"].tolist()
            sel_inv = st.selectbox("Select Invoice", inv_list)
            record_df = filtered[filtered["invoice"] == sel_inv]
            if not record_df.empty:
                rec = record_df.iloc[0]
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"**Date:** {rec.get('date','')}")
                    st.markdown(f"**Invoice:** `{rec.get('invoice','')}`")
                    st.markdown(f"**Rep:** {rec.get('rep','')}")
                    st.markdown(f"**Surgeon:** {rec.get('surgeon','')}")
                with col_b:
                    st.markdown(f"**Facility:** {rec.get('facility','')}")
                    st.markdown(f"**Region:** {rec.get('region','')}")
                    st.markdown(f"**Procedure:** {rec.get('procedure','')}")
                    implants_val = rec.get("implants", [])
                    if isinstance(implants_val, list):
                        st.markdown("**Implants:** " + " ".join([f"`{i}`" for i in implants_val]))
                st.markdown(f"**⚠️ Challenges:** {rec.get('challenges','—')}")
                st.markdown(f"**💬 Feedback:** {rec.get('feedback','—')}")

        # Delete
        st.markdown("---")
        with st.expander("🗑️ Delete a Record"):
            del_inv = st.text_input("Invoice number to delete")
            if st.button("Delete", type="primary"):
                data = load_data()
                before = len(data)
                data = [r for r in data if r.get("invoice") != del_inv]
                if len(data) < before:
                    save_data(data)
                    st.success(f"Deleted record with invoice `{del_inv}`")
                    st.rerun()
                else:
                    st.warning("Invoice not found.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Analytics":
    st.markdown("## 📈 Analytics")

    df = get_df()
    if df.empty:
        st.info("No data yet. Add procedures to see analytics.")
    else:
        tab1, tab2, tab3 = st.tabs(["📅 Trends", "🏥 Facility & Region", "👤 Rep Performance"])

        with tab1:
            if "date" in df.columns:
                monthly = df.groupby(df["date"].dt.to_period("M")).size().reset_index()
                monthly.columns = ["Month", "Count"]
                monthly["Month"] = monthly["Month"].astype(str)

                fig = px.bar(monthly, x="Month", y="Count",
                             title="Monthly Procedure Volume",
                             color_discrete_sequence=["#2D4A6E"])
                fig.update_layout(paper_bgcolor="white", plot_bgcolor="#FAFAFA",
                                  font_family="DM Sans", title_font_family="Syne")
                st.plotly_chart(fig, use_container_width=True)

                dow = df["date"].dt.day_name().value_counts().reset_index()
                dow.columns = ["Day", "Count"]
                fig2 = px.bar(dow, x="Day", y="Count", title="Procedures by Day of Week",
                              color_discrete_sequence=["#E8552A"])
                fig2.update_layout(paper_bgcolor="white", plot_bgcolor="#FAFAFA",
                                   font_family="DM Sans", title_font_family="Syne")
                st.plotly_chart(fig2, use_container_width=True)

        with tab2:
            c1, c2 = st.columns(2)
            with c1:
                if "facility" in df.columns:
                    fac_c = df["facility"].value_counts().reset_index()
                    fac_c.columns = ["Facility", "Count"]
                    fig3 = px.bar(fac_c, x="Count", y="Facility", orientation="h",
                                  title="Procedures by Facility",
                                  color="Count", color_continuous_scale=["#2D4A6E","#3ABFA0"])
                    fig3.update_layout(yaxis=dict(autorange="reversed"), paper_bgcolor="white",
                                       plot_bgcolor="#FAFAFA", font_family="DM Sans",
                                       title_font_family="Syne", showlegend=False)
                    st.plotly_chart(fig3, use_container_width=True)
            with c2:
                if "region" in df.columns:
                    reg_c = df["region"].value_counts().reset_index()
                    reg_c.columns = ["Region", "Count"]
                    fig4 = px.pie(reg_c, values="Count", names="Region",
                                  title="Coverage by Region",
                                  color_discrete_sequence=px.colors.sequential.Blues_r)
                    fig4.update_layout(paper_bgcolor="white", font_family="DM Sans",
                                       title_font_family="Syne")
                    st.plotly_chart(fig4, use_container_width=True)

        with tab3:
            if "rep" in df.columns:
                rep_monthly = df.groupby([df["date"].dt.to_period("M"), "rep"]).size().reset_index()
                rep_monthly.columns = ["Month", "Rep", "Count"]
                rep_monthly["Month"] = rep_monthly["Month"].astype(str)
                fig5 = px.line(rep_monthly, x="Month", y="Count", color="Rep",
                               title="Rep Procedure Trends",
                               markers=True)
                fig5.update_layout(paper_bgcolor="white", plot_bgcolor="#FAFAFA",
                                   font_family="DM Sans", title_font_family="Syne")
                st.plotly_chart(fig5, use_container_width=True)

                rep_summary = df.groupby("rep").agg(
                    Total_Procedures=("id", "count"),
                    Facilities=("facility", "nunique"),
                    Surgeons=("surgeon", "nunique"),
                    Regions=("region", "nunique")
                ).reset_index().sort_values("Total_Procedures", ascending=False)
                st.markdown("#### Rep Performance Summary")
                st.dataframe(rep_summary, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: REPORTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⬇️ Reports":
    st.markdown("## ⬇️ Download Reports")

    df = get_df()
    if df.empty:
        st.info("No procedures logged yet.")
    else:
        st.markdown("### 🔧 Report Options")
        c1, c2 = st.columns(2)
        with c1:
            report_type = st.selectbox("Report Scope", ["All Procedures", "By Rep", "By Region", "By Facility", "Date Range"])
        with c2:
            fmt = st.selectbox("Format", ["PDF", "Excel (.xlsx)", "CSV"])

        # Filters based on scope
        filtered = df.copy()
        if report_type == "By Rep" and "rep" in df.columns:
            sel = st.selectbox("Select Rep", sorted(df["rep"].unique().tolist()))
            filtered = df[df["rep"] == sel]
        elif report_type == "By Region" and "region" in df.columns:
            sel = st.selectbox("Select Region", sorted(df["region"].unique().tolist()))
            filtered = df[df["region"] == sel]
        elif report_type == "By Facility" and "facility" in df.columns:
            sel = st.selectbox("Select Facility", sorted(df["facility"].unique().tolist()))
            filtered = df[df["facility"] == sel]
        elif report_type == "Date Range" and "date" in df.columns:
            dc1, dc2 = st.columns(2)
            with dc1:
                d_from = st.date_input("From", value=df["date"].min().date())
            with dc2:
                d_to = st.date_input("To", value=df["date"].max().date())
            filtered = df[(df["date"].dt.date >= d_from) & (df["date"].dt.date <= d_to)]

        st.markdown(f"**{len(filtered)} procedures** will be included in this report.")
        st.markdown("---")

        report_title = f"OrthoTrack Pro — {report_type}"

        if fmt == "PDF":
            if st.button("📄 Generate & Download PDF", type="primary", use_container_width=True):
                with st.spinner("Generating PDF…"):
                    pdf_buf = generate_pdf(filtered, report_title)
                st.download_button(
                    "⬇️ Download PDF",
                    data=pdf_buf,
                    file_name=f"orthotrack_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

        elif fmt == "Excel (.xlsx)":
            if st.button("📊 Generate & Download Excel", type="primary", use_container_width=True):
                with st.spinner("Building Excel workbook…"):
                    xl_buf = generate_excel(filtered)
                st.download_button(
                    "⬇️ Download Excel",
                    data=xl_buf,
                    file_name=f"orthotrack_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

        elif fmt == "CSV":
            csv_df = filtered.copy()
            if "date" in csv_df.columns:
                csv_df["date"] = csv_df["date"].dt.strftime("%Y-%m-%d")
            if "implants" in csv_df.columns:
                csv_df["implants"] = csv_df["implants"].apply(
                    lambda x: ", ".join(x) if isinstance(x, list) else x)
            csv_bytes = csv_df.to_csv(index=False).encode()
            st.download_button(
                "⬇️ Download CSV",
                data=csv_bytes,
                file_name=f"orthotrack_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True,
            )
