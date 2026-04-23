"""
OrthoTrack Pro — Orthopedic Procedure Management System
Complete production build: Dashboard · Log · Analytics · Reports
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json, os, io
from datetime import datetime, date, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import xlsxwriter

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OrthoTrack Pro",
    page_icon="🦴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# DESIGN SYSTEM & CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@300;400;500;600;700&display=swap');

:root {
    --ink:    #0D1B2A;
    --navy:   #1B3A5C;
    --cobalt: #2563EB;
    --sky:    #38BDF8;
    --teal:   #0D9488;
    --amber:  #F59E0B;
    --red:    #EF4444;
    --cream:  #F8F6F1;
    --white:  #FFFFFF;
    --muted:  #64748B;
    --border: #E2E8F0;
    --shadow: 0 1px 3px rgba(0,0,0,.06), 0 4px 16px rgba(0,0,0,.06);
}

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
    background: var(--cream) !important;
    color: var(--ink) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--ink) !important;
    border-right: 1px solid #1e2d3d !important;
}
[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
[data-testid="stSidebar"] .sb-brand {
    background: linear-gradient(135deg,var(--cobalt),var(--teal));
    padding: 1.4rem 1.2rem 1.2rem;
    margin-bottom:.5rem;
}
[data-testid="stSidebar"] .sb-brand h2 {
    font-family:'Bebas Neue',sans-serif !important;
    font-size:1.85rem !important; letter-spacing:3px;
    color:white !important; margin:0 !important;
}
[data-testid="stSidebar"] .sb-brand p {
    font-size:.7rem !important; color:rgba(255,255,255,.55) !important;
    margin:0 !important; letter-spacing:1.5px; text-transform:uppercase;
}
[data-testid="stSidebar"] .stRadio label {
    font-size:.88rem !important; font-weight:500 !important;
    padding:.4rem .2rem !important; color:#94A3B8 !important;
}
[data-testid="stSidebar"] .sp {
    background:rgba(255,255,255,.05);
    border:1px solid rgba(255,255,255,.08);
    border-radius:10px; padding:.65rem 1rem; margin:.3rem 0;
}
[data-testid="stSidebar"] .sp .sv {
    font-family:'Bebas Neue',sans-serif !important;
    font-size:1.5rem; color:white !important; line-height:1;
}
[data-testid="stSidebar"] .sp .sl {
    font-size:.68rem; color:#64748B !important;
    text-transform:uppercase; letter-spacing:1px;
}

/* ── Page header ── */
.ph {
    background:linear-gradient(135deg,var(--ink) 0%,var(--navy) 55%,#0f4c75 100%);
    border-radius:16px; padding:2rem 2.5rem;
    margin-bottom:1.75rem; position:relative; overflow:hidden;
}
.ph::after {
    content:''; position:absolute; right:-60px; top:-60px;
    width:220px; height:220px; border-radius:50%;
    background:radial-gradient(circle,rgba(37,99,235,.35) 0%,transparent 70%);
}
.ph::before {
    content:''; position:absolute; right:40px; bottom:-40px;
    width:160px; height:160px; border-radius:50%;
    background:radial-gradient(circle,rgba(13,148,136,.25) 0%,transparent 70%);
}
.ph h1 {
    font-family:'Bebas Neue',sans-serif !important;
    font-size:2.6rem !important; letter-spacing:3px;
    color:white !important; margin:0 0 .3rem !important; position:relative; z-index:1;
}
.ph p { color:rgba(255,255,255,.55) !important; font-size:.88rem !important; margin:0 !important; position:relative; z-index:1; }
.ph-badge {
    display:inline-block; background:rgba(37,99,235,.3);
    border:1px solid rgba(37,99,235,.5); color:var(--sky) !important;
    font-size:.7rem; font-weight:600; letter-spacing:1px; text-transform:uppercase;
    padding:.25rem .7rem; border-radius:20px; margin-bottom:.6rem; position:relative; z-index:1;
}

/* ── Section label ── */
.sec-lbl {
    font-size:.7rem; font-weight:700; text-transform:uppercase;
    letter-spacing:2px; color:var(--cobalt); margin-bottom:.6rem;
}

/* ── Form sections ── */
.fs  { background:#F0F4FF; border-left:3px solid var(--cobalt); border-radius:0 8px 8px 0; padding:.45rem .8rem .3rem; margin:1rem 0 .4rem; font-size:.7rem; font-weight:700; text-transform:uppercase; letter-spacing:1.5px; color:var(--cobalt); }
.fst { background:#F0FDFA; border-left-color:var(--teal); color:var(--teal); }
.fsa { background:#FFFBEB; border-left-color:var(--amber); color:#92400E; }

/* ── Record field ── */
.rf { margin-bottom:.5rem; padding:.6rem .9rem; background:#F8FAFC; border-radius:8px; }
.rf .rl { font-size:.68rem; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:var(--muted); margin-bottom:.2rem; }
.rf .rv { font-size:.9rem; color:var(--ink); font-weight:500; }

/* ── Chip ── */
.chip { display:inline-block; background:linear-gradient(135deg,#EFF6FF,#DBEAFE); color:var(--cobalt); font-size:.72rem; font-weight:600; padding:.25rem .7rem; border-radius:20px; border:1px solid #BFDBFE; margin:.2rem .2rem .2rem 0; }

/* ── Download card ── */
.dlc { background:var(--white); border:1.5px solid var(--border); border-radius:14px; padding:1.8rem; text-align:center; }
.dlc .di { font-size:2.5rem; margin-bottom:.5rem; }
.dlc .dt { font-weight:700; font-size:1rem; color:var(--ink); margin-bottom:.25rem; }
.dlc .dd { font-size:.8rem; color:var(--muted); }

/* ── Inputs ── */
.stTextInput input,.stTextArea textarea {
    border-radius:8px !important; border:1.5px solid var(--border) !important;
    font-family:'Outfit',sans-serif !important; font-size:.9rem !important;
}
.stTextInput input:focus,.stTextArea textarea:focus {
    border-color:var(--cobalt) !important;
    box-shadow:0 0 0 3px rgba(37,99,235,.12) !important;
}
.stTextInput label,.stTextArea label,.stSelectbox label,.stMultiSelect label,.stDateInput label {
    font-size:.78rem !important; font-weight:600 !important;
    color:var(--ink) !important; text-transform:uppercase !important; letter-spacing:.8px !important;
}

/* ── Buttons ── */
.stButton>button {
    font-family:'Outfit',sans-serif !important; font-weight:600 !important;
    border-radius:8px !important; transition:transform .15s,box-shadow .15s !important;
}
.stButton>button:hover { transform:translateY(-1px) !important; }
.stButton>button[kind="primary"] {
    background:linear-gradient(135deg,var(--cobalt),#1d4ed8) !important;
    color:white !important; border:none !important;
    box-shadow:0 4px 14px rgba(37,99,235,.3) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { background:transparent !important; border-bottom:2px solid var(--border) !important; }
.stTabs [data-baseweb="tab"] { font-family:'Outfit',sans-serif !important; font-weight:600 !important; font-size:.85rem !important; padding:.7rem 1.2rem !important; color:var(--muted) !important; }
.stTabs [aria-selected="true"] { color:var(--cobalt) !important; border-bottom:2px solid var(--cobalt) !important; }

/* ── Metric ── */
[data-testid="metric-container"] label { font-family:'Outfit',sans-serif !important; font-size:.72rem !important; font-weight:600 !important; text-transform:uppercase !important; letter-spacing:.8px !important; color:var(--muted) !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { font-family:'Bebas Neue',sans-serif !important; font-size:2.2rem !important; color:var(--ink) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-thumb { background:#CBD5E1; border-radius:3px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
DATA_FILE = "procedures.json"

REPS = sorted([
    "James Mwangi","Faith Otieno","Brian Koech","Grace Auma","Dennis Kiplangat",
    "Sharon Wanjiku","Paul Mutua","Lydia Chebet","Moses Odhiambo","Caroline Njeri"
])
FACILITIES = sorted([
    "Moi Teaching & Referral Hospital","Kenyatta National Hospital","Aga Khan Hospital Nairobi",
    "MP Shah Hospital","Nairobi Hospital","AAR Hospital","Coast General Hospital",
    "Eldoret Hospital","Kisumu County Referral","Nakuru Level 5 Hospital",
    "Thika Level 5 Hospital","Mombasa Hospital","Other"
])
REGIONS = ["East Africa","West Africa","North Africa","Southern Africa","Central Africa","Middle East","Europe","Other"]
SURGEONS = sorted([
    "Dr. A. Kimani","Dr. B. Otieno","Dr. C. Waweru","Dr. D. Mutai","Dr. E. Achieng",
    "Dr. F. Njenga","Dr. G. Kipchoge","Dr. H. Omondi","Dr. I. Wambua","Dr. J. Chege",
    "Dr. K. Maina","Dr. L. Rotich","Dr. M. Abdi","Dr. N. Kamau","Dr. O. Simiyu","Other"
])
PROCEDURES = sorted([
    "Total Hip Replacement","Total Knee Replacement","Partial Knee Replacement",
    "Shoulder Arthroplasty","Spinal Fusion L4-L5","Spinal Fusion L5-S1","Tibial Nail Fixation",
    "Femoral Nail Fixation","DHS Plate Fixation","Locking Plate Fixation","ACL Reconstruction",
    "Revision Hip Replacement","Revision Knee Replacement","Humeral Nail Fixation",
    "Ankle Replacement","External Fixator Application","Proximal Femur Replacement",
    "Wrist Arthroplasty","Other"
])
IMPLANTS = sorted([
    "Total Hip Replacement System","Total Knee Replacement System","Partial Knee System",
    "Shoulder Arthroplasty System","Spinal Fusion Cage","Pedicle Screws","Titanium Tibial Nail",
    "Femoral Intramedullary Nail","DHS Plate & Screw","Locking Compression Plate",
    "ACL Graft & Fixation","Revision Hip Stem","Revision Tibial Component","Humeral Nail",
    "Total Ankle Replacement","External Fixator Frame","Proximal Femoral Prosthesis",
    "Bone Cement","Augmentation Block","Trial Components","Other"
])
COLORS = ["#2563EB","#0D9488","#F59E0B","#EF4444","#8B5CF6","#06B6D4","#10B981","#F97316","#EC4899","#6366F1"]

# ─────────────────────────────────────────────────────────────────────────────
# DATA LAYER
# ─────────────────────────────────────────────────────────────────────────────
def load_data() -> list:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE,"r") as f: return json.load(f)
    return []

def save_data(data: list):
    with open(DATA_FILE,"w") as f: json.dump(data, f, indent=2, default=str)

@st.cache_data(ttl=2)
def get_df() -> pd.DataFrame:
    data = load_data()
    if not data: return pd.DataFrame()
    df = pd.DataFrame(data)
    df["date"]    = pd.to_datetime(df["date"])
    df["month"]   = df["date"].dt.to_period("M").astype(str)
    df["year"]    = df["date"].dt.year
    df["quarter"] = df["date"].dt.to_period("Q").astype(str)
    return df

def bust(): get_df.clear()

def next_inv(data: list) -> str:
    yr = datetime.now().year
    nums = []
    for r in data:
        inv = r.get("invoice","")
        if str(yr) in inv:
            try: nums.append(int(inv.split("-")[-1]))
            except: pass
    return f"INV-{yr}-{(max(nums)+1 if nums else 1):04d}"

# ─────────────────────────────────────────────────────────────────────────────
# CHART HELPER
# ─────────────────────────────────────────────────────────────────────────────
BASE = dict(paper_bgcolor="white", plot_bgcolor="#F8FAFC",
            font=dict(family="Outfit",color="#0D1B2A"),
            title_font=dict(family="Outfit",size=13,color="#64748B"),
            margin=dict(t=44,b=28,l=20,r=16),
            legend=dict(font=dict(size=11)))

def sc(fig, title=""):
    fig.update_layout(**BASE, title=dict(text=title))
    fig.update_xaxes(showgrid=False, linecolor="#E2E8F0", tickfont=dict(size=10))
    fig.update_yaxes(gridcolor="#F1F5F9", linecolor="#E2E8F0", tickfont=dict(size=10))
    return fig

# ─────────────────────────────────────────────────────────────────────────────
# PDF
# ─────────────────────────────────────────────────────────────────────────────
def build_pdf(df: pd.DataFrame, title: str, subtitle: str = "") -> io.BytesIO:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=1.8*cm, rightMargin=1.8*cm,
                            topMargin=2*cm, bottomMargin=1.8*cm)
    S = getSampleStyleSheet()
    ink    = colors.HexColor("#0D1B2A")
    cobalt = colors.HexColor("#2563EB")
    navy   = colors.HexColor("#1B3A5C")
    cream  = colors.HexColor("#F8F6F1")
    border = colors.HexColor("#E2E8F0")
    muted  = colors.HexColor("#64748B")
    story  = []

    story.append(Paragraph("ORTHOTRACK PRO",
        ParagraphStyle("Br",fontName="Helvetica-Bold",fontSize=20,
                       textColor=cobalt,spaceAfter=2,letterSpacing=4)))
    story.append(Paragraph(title,
        ParagraphStyle("Ti",fontName="Helvetica-Bold",fontSize=14,
                       textColor=ink,spaceAfter=4)))
    if subtitle:
        story.append(Paragraph(subtitle,
            ParagraphStyle("Su",fontName="Helvetica",fontSize=9,textColor=muted,spaceAfter=2)))
    story.append(Paragraph(
        f"Generated {datetime.now().strftime('%d %B %Y  ·  %H:%M')}   ·   {len(df)} record(s)",
        ParagraphStyle("Me",fontName="Helvetica",fontSize=8,textColor=muted,spaceAfter=8)))
    story.append(HRFlowable(width="100%",thickness=2,color=cobalt,spaceAfter=12))

    # Summary stats
    story.append(Paragraph("SUMMARY",
        ParagraphStyle("SH",fontName="Helvetica-Bold",fontSize=7,
                       textColor=cobalt,spaceBefore=2,spaceAfter=6,letterSpacing=2)))
    nf = df["facility"].nunique() if "facility" in df.columns else 0
    ns = df["surgeon"].nunique()  if "surgeon"  in df.columns else 0
    nr = df["rep"].nunique()      if "rep"      in df.columns else 0
    ng = df["region"].nunique()   if "region"   in df.columns else 0
    sd = [["PROCEDURES","FACILITIES","SURGEONS","REPS","REGIONS"],
          [str(len(df)),str(nf),str(ns),str(nr),str(ng)]]
    st_ = Table(sd, colWidths=[2.8*cm]*5)
    st_.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),ink),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,0),7),
        ("BACKGROUND",(0,1),(-1,1),cream),
        ("FONTNAME",(0,1),(-1,1),"Helvetica-Bold"),("FONTSIZE",(0,1),(-1,1),14),
        ("TEXTCOLOR",(0,1),(-1,1),ink),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
        ("BOX",(0,0),(-1,-1),.5,border),("INNERGRID",(0,0),(-1,-1),.5,border),
    ]))
    story.append(st_)
    story.append(Spacer(1,14))

    # Procedure table
    story.append(Paragraph("PROCEDURE LOG",
        ParagraphStyle("SH2",fontName="Helvetica-Bold",fontSize=7,
                       textColor=cobalt,spaceBefore=4,spaceAfter=6,letterSpacing=2)))
    wanted  = ["date","invoice","rep","facility","region","surgeon","procedure","implants"]
    present = [c for c in wanted if c in df.columns]
    cw_map  = {"date":10*mm,"invoice":18*mm,"rep":22*mm,"facility":27*mm,
               "region":17*mm,"surgeon":22*mm,"procedure":26*mm,"implants":28*mm}
    cwidths  = [cw_map.get(c,20*mm) for c in present]
    rows    = [[c.upper() for c in present]]
    for _,row in df.sort_values("date",ascending=False).head(200).iterrows():
        r=[]
        for c in present:
            v=row.get(c,"")
            if c=="date":
                try: v=pd.to_datetime(v).strftime("%d %b %Y")
                except: pass
            elif c=="implants" and isinstance(v,list): v=", ".join(v)
            v=str(v)
            if len(v)>26: v=v[:24]+"…"
            r.append(v)
        rows.append(r)
    t=Table(rows,colWidths=cwidths,repeatRows=1)
    rbgs=[]
    for i in range(1,len(rows)):
        bg=colors.white if i%2 else colors.HexColor("#F8FAFC")
        rbgs.append(("BACKGROUND",(0,i),(-1,i),bg))
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),navy),("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),7),
        ("FONTNAME",(0,1),(-1,-1),"Helvetica"),("TEXTCOLOR",(0,1),(-1,-1),ink),
        ("ALIGN",(0,0),(-1,-1),"LEFT"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),5),
        ("BOX",(0,0),(-1,-1),.5,border),("INNERGRID",(0,0),(-1,-1),.3,border),
        *rbgs,
    ]))
    story.append(t)
    if len(df)>200:
        story.append(Spacer(1,8))
        story.append(Paragraph(f"… and {len(df)-200} more. Download Excel/CSV for full dataset.",
            ParagraphStyle("N",fontName="Helvetica-Oblique",fontSize=8,textColor=muted)))
    doc.build(story)
    buf.seek(0)
    return buf

# ─────────────────────────────────────────────────────────────────────────────
# EXCEL
# ─────────────────────────────────────────────────────────────────────────────
def build_excel(df: pd.DataFrame, title: str) -> io.BytesIO:
    buf = io.BytesIO()
    wb  = xlsxwriter.Workbook(buf,{"in_memory":True})
    def f(**kw): return wb.add_format({**kw,"font_name":"Calibri"})
    f_title = f(bold=True,font_size=16,font_color="#0D1B2A")
    f_sub   = f(font_size=9,font_color="#64748B",italic=True)
    f_hdr   = f(bold=True,font_size=9,font_color="white",bg_color="#1B3A5C",
                border=1,border_color="#CBD5E1",align="center",valign="vcenter",text_wrap=True)
    f_cell  = f(font_size=9,border=1,border_color="#E2E8F0",valign="vcenter")
    f_alt   = f(font_size=9,border=1,border_color="#E2E8F0",bg_color="#F8F6F1",valign="vcenter")
    f_sv    = f(bold=True,font_size=9,font_color="white",bg_color="#0D1B2A",
                border=1,border_color="#CBD5E1",align="center",valign="vcenter")
    f_val   = f(bold=True,font_size=18,font_color="#2563EB",bg_color="#EFF6FF",
                border=1,border_color="#BFDBFE",align="center",valign="vcenter")
    f_sec   = f(bold=True,font_size=8,font_color="#2563EB",bg_color="#EFF6FF",
                border=1,border_color="#BFDBFE")
    f_dt    = f(font_size=9,border=1,border_color="#E2E8F0",num_format="dd mmm yyyy",valign="vcenter")
    f_dta   = f(font_size=9,border=1,border_color="#E2E8F0",bg_color="#F8F6F1",
                num_format="dd mmm yyyy",valign="vcenter")

    # Sheet 1 – Procedures
    ws = wb.add_worksheet("Procedures")
    ws.set_zoom(90); ws.freeze_panes(5,0)
    ws.merge_range("A1:J1","OrthoTrack Pro — "+title,f_title)
    ws.write("A2",f"Exported {datetime.now().strftime('%d %B %Y  ·  %H:%M')}   ·   {len(df)} records",f_sub)
    ws.set_row(0,26); ws.set_row(1,14); ws.set_row(2,6); ws.set_row(3,20)

    cols  = [c for c in ["date","invoice","rep","facility","region","surgeon","procedure","implants","challenges","feedback"] if c in df.columns]
    cw    = {"date":13,"invoice":16,"rep":22,"facility":30,"region":16,"surgeon":22,
             "procedure":28,"implants":35,"challenges":40,"feedback":40}
    for ci,col in enumerate(cols):
        ws.write(3,ci,col.upper(),f_hdr); ws.set_column(ci,ci,cw.get(col,18))

    for ri,(_,row) in enumerate(df.sort_values("date",ascending=False).iterrows()):
        alt=ri%2==1; ws.set_row(ri+4,16)
        for ci,col in enumerate(cols):
            v=row.get(col,"")
            if isinstance(v,list): v=", ".join(v)
            if not isinstance(v,str) and pd.isna(v): v=""
            cf=f_alt if alt else f_cell
            if col=="date":
                try:
                    ws.write_datetime(ri+4,ci,pd.to_datetime(v).to_pydatetime(),f_dta if alt else f_dt); continue
                except: pass
            ws.write(ri+4,ci,str(v),cf)

    # Sheet 2 – Summary
    ws2 = wb.add_worksheet("Summary")
    ws2.set_column("A:A",28); ws2.set_column("B:B",16); ws2.set_zoom(95)
    ws2.merge_range("A1:B1","OrthoTrack Pro — Summary Statistics",f_title)
    ws2.merge_range("A2:B2",f"Generated {datetime.now().strftime('%d %B %Y')}",f_sub)
    ws2.set_row(0,26); ws2.set_row(1,14); ws2.set_row(2,6)
    stats=[("Total Procedures",len(df)),
           ("Unique Facilities",df["facility"].nunique() if "facility" in df.columns else 0),
           ("Unique Surgeons",  df["surgeon"].nunique()  if "surgeon"  in df.columns else 0),
           ("Unique Reps",      df["rep"].nunique()       if "rep"      in df.columns else 0),
           ("Regions Covered",  df["region"].nunique()    if "region"   in df.columns else 0)]
    for i,(k,v) in enumerate(stats):
        ws2.set_row(i+3,26); ws2.write(i+3,0,k,f_sv); ws2.write(i+3,1,v,f_val)
    ro=len(stats)+5
    ws2.merge_range(ro,0,ro,1,"PROCEDURES BY REP",f_sec)
    if "rep" in df.columns:
        for i,(rep,cnt) in enumerate(df["rep"].value_counts().items()):
            ws2.set_row(ro+1+i,16)
            ws2.write(ro+1+i,0,rep,f_alt if i%2 else f_cell)
            ws2.write(ro+1+i,1,cnt,f_alt if i%2 else f_cell)

    # Sheet 3 – By Region
    ws3 = wb.add_worksheet("By Region")
    ws3.set_column("A:A",24); ws3.set_column("B:B",14); ws3.set_zoom(95)
    ws3.merge_range("A1:B1","Procedures by Region",f_title)
    ws3.set_row(0,24); ws3.set_row(1,6); ws3.set_row(2,20)
    ws3.write(2,0,"REGION",f_sv); ws3.write(2,1,"PROCEDURES",f_sv)
    if "region" in df.columns:
        for i,(reg,cnt) in enumerate(df["region"].value_counts().items()):
            ws3.set_row(i+3,16)
            ws3.write(i+3,0,reg,f_alt if i%2 else f_cell)
            ws3.write(i+3,1,cnt,f_alt if i%2 else f_cell)

    wb.close(); buf.seek(0)
    return buf

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-brand">
        <h2>🦴 ORTHOTRACK</h2>
        <p>Pro · Procedure Management</p>
    </div>""", unsafe_allow_html=True)

    page = st.radio("nav", [
        "📊  Dashboard","➕  Add Procedure","📋  Procedure Log","📈  Analytics","⬇️  Reports"
    ], label_visibility="collapsed")

    dfs = get_df()
    if not dfs.empty:
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:.65rem;color:#374151;letter-spacing:1.5px;padding:0 .2rem;margin-bottom:.3rem'>LIVE STATS</div>",
                    unsafe_allow_html=True)
        now_m = datetime.now()
        this_mo = dfs[(dfs["date"].dt.month==now_m.month)&(dfs["date"].dt.year==now_m.year)]
        for val,lbl in [(len(dfs),"Total Procedures"),(len(this_mo),"This Month"),
                        (dfs["rep"].nunique() if "rep" in dfs.columns else 0,"Active Reps"),
                        (dfs["facility"].nunique() if "facility" in dfs.columns else 0,"Facilities")]:
            st.markdown(f'<div class="sp"><div class="sv">{val}</div><div class="sl">{lbl}</div></div>',
                        unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:.62rem;color:#374151;letter-spacing:1px;padding:0 .2rem'>v2.0 · OrthoTrack Pro</div>",
                unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ██  DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
if page == "📊  Dashboard":
    st.markdown("""
    <div class="ph">
        <div class="ph-badge">Live Dashboard</div>
        <h1>ORTHOTRACK PRO</h1>
        <p>Orthopedic Procedure Intelligence · Rep Performance · Regional Coverage</p>
    </div>""", unsafe_allow_html=True)

    df = get_df()
    if df.empty:
        st.info("🦴 No procedures yet. Head to **Add Procedure** to get started!")
        st.stop()

    now = datetime.now()
    this_mo = df[(df["date"].dt.month==now.month)&(df["date"].dt.year==now.year)]

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("🔬 Total Procedures", len(df), delta=len(this_mo), help="All time · delta = this month")
    with c2: st.metric("🏥 Facilities",  df["facility"].nunique() if "facility" in df.columns else 0)
    with c3: st.metric("👨‍⚕️ Surgeons",   df["surgeon"].nunique()  if "surgeon"  in df.columns else 0)
    with c4: st.metric("👤 Active Reps", df["rep"].nunique()       if "rep"      in df.columns else 0)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # Row 1
    col1,col2 = st.columns([3,2])
    with col1:
        monthly = df.groupby("month").size().reset_index(name="Count")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=monthly["month"],y=monthly["Count"],
            marker=dict(color=monthly["Count"],colorscale=[[0,"#DBEAFE"],[1,"#2563EB"]],showscale=False),
            hovertemplate="%{x}<br><b>%{y} procedures</b><extra></extra>"))
        fig.add_trace(go.Scatter(x=monthly["month"],y=monthly["Count"],mode="lines",
            line=dict(color="#0D9488",width=2.5),hoverinfo="skip"))
        sc(fig,"Monthly Procedure Volume"); fig.update_layout(showlegend=False,height=280)
        st.plotly_chart(fig,use_container_width=True)
    with col2:
        if "region" in df.columns:
            rc = df["region"].value_counts().reset_index(); rc.columns=["Region","Count"]
            fig2=px.pie(rc,values="Count",names="Region",color_discrete_sequence=COLORS,hole=.4)
            fig2.update_traces(textposition="inside",textinfo="percent+label",textfont_size=10)
            sc(fig2,"Coverage by Region"); fig2.update_layout(showlegend=False,height=280)
            st.plotly_chart(fig2,use_container_width=True)

    # Row 2
    col3,col4 = st.columns(2)
    with col3:
        if "rep" in df.columns:
            rc2=df["rep"].value_counts().head(10).reset_index(); rc2.columns=["Rep","Count"]
            fig3=px.bar(rc2,x="Count",y="Rep",orientation="h",
                color="Count",color_continuous_scale=["#DBEAFE","#2563EB"],text="Count")
            fig3.update_traces(textposition="outside",textfont_size=10)
            sc(fig3,"Top Reps by Volume")
            fig3.update_layout(yaxis=dict(autorange="reversed"),showlegend=False,height=320,coloraxis_showscale=False)
            st.plotly_chart(fig3,use_container_width=True)
    with col4:
        if "procedure" in df.columns:
            pc=df["procedure"].value_counts().head(8).reset_index(); pc.columns=["Procedure","Count"]
            fig4=px.bar(pc,x="Count",y="Procedure",orientation="h",
                color="Count",color_continuous_scale=["#CCFBF1","#0D9488"],text="Count")
            fig4.update_traces(textposition="outside",textfont_size=10)
            sc(fig4,"Top Procedure Types")
            fig4.update_layout(yaxis=dict(autorange="reversed"),showlegend=False,height=320,coloraxis_showscale=False)
            st.plotly_chart(fig4,use_container_width=True)

    # Row 3
    col5,col6 = st.columns([2,3])
    with col5:
        if "facility" in df.columns:
            fc=df["facility"].value_counts().head(8).reset_index(); fc.columns=["Facility","Count"]
            fig5=px.bar(fc,x="Count",y="Facility",orientation="h",
                color="Count",color_continuous_scale=["#FEF3C7","#F59E0B"],text="Count")
            fig5.update_traces(textposition="outside",textfont_size=10)
            sc(fig5,"Top Facilities")
            fig5.update_layout(yaxis=dict(autorange="reversed"),showlegend=False,height=300,coloraxis_showscale=False)
            st.plotly_chart(fig5,use_container_width=True)
    with col6:
        st.markdown("<div class='sec-lbl'>Recent Procedures</div>", unsafe_allow_html=True)
        rcols=[c for c in ["date","invoice","rep","procedure","facility","surgeon"] if c in df.columns]
        rd=df.sort_values("date",ascending=False)[rcols].head(10).copy()
        if "date" in rd.columns: rd["date"]=rd["date"].dt.strftime("%d %b %Y")
        st.dataframe(rd,use_container_width=True,hide_index=True,height=300)

    # Row 4 – quarterly rep trend
    if "quarter" in df.columns and "rep" in df.columns:
        st.markdown("---")
        qr=df.groupby(["quarter","rep"]).size().reset_index(name="Count")
        fig6=px.line(qr,x="quarter",y="Count",color="rep",markers=True,
            color_discrete_sequence=COLORS)
        sc(fig6,"Quarterly Performance by Rep")
        fig6.update_layout(height=300,legend=dict(orientation="h",y=-0.25))
        st.plotly_chart(fig6,use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# ██  ADD PROCEDURE
# ─────────────────────────────────────────────────────────────────────────────
elif page == "➕  Add Procedure":
    st.markdown("""
    <div class="ph">
        <div class="ph-badge">New Entry</div>
        <h1>ADD PROCEDURE</h1>
        <p>Log a new orthopedic procedure · All starred fields are required</p>
    </div>""", unsafe_allow_html=True)

    raw = load_data()
    auto = next_inv(raw)

    with st.form("add_form", clear_on_submit=True):
        st.markdown("<div class='fs'>📋 Procedure Identification</div>", unsafe_allow_html=True)
        c1,c2,c3 = st.columns(3)
        with c1: proc_date = st.date_input("📅 Date *", value=date.today())
        with c2: invoice   = st.text_input("🧾 Invoice Number *", value=auto)
        with c3: rep_sel   = st.selectbox("👤 Rep *", ["— Select —"]+REPS+["Other"])
        rep_other = st.text_input("Rep full name *", key="rep_o") if rep_sel=="Other" else ""

        st.markdown("<div class='fs fst'>🏥 Location</div>", unsafe_allow_html=True)
        c4,c5 = st.columns(2)
        with c4: fac_sel = st.selectbox("🏥 Facility *", ["— Select —"]+FACILITIES)
        with c5: reg_sel = st.selectbox("🌍 Region *",   ["— Select —"]+REGIONS)
        fac_other = st.text_input("Facility name *", key="fac_o") if fac_sel=="Other" else ""

        st.markdown("<div class='fs'>🔬 Clinical Details</div>", unsafe_allow_html=True)
        c6,c7 = st.columns(2)
        with c6: surg_sel = st.selectbox("👨‍⚕️ Surgeon *",   ["— Select —"]+SURGEONS)
        with c7: proc_sel = st.selectbox("🔬 Procedure *", ["— Select —"]+PROCEDURES)
        surg_other = st.text_input("Surgeon full name *", key="surg_o") if surg_sel=="Other" else ""
        proc_other = st.text_input("Procedure name *",    key="proc_o") if proc_sel=="Other" else ""
        implants_sel = st.multiselect("🦴 Implants Used *", IMPLANTS)

        st.markdown("<div class='fs fsa'>📝 Notes & Feedback</div>", unsafe_allow_html=True)
        c8,c9 = st.columns(2)
        with c8: challenges = st.text_area("⚠️ Challenges Encountered", placeholder="Intraoperative challenges, complications, delays…", height=110)
        with c9: feedback   = st.text_area("💬 Surgeon / Outcome Feedback", placeholder="Post-procedure feedback, surgeon comments, outcomes…", height=110)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("✅  Save Procedure", use_container_width=True, type="primary")

    if submitted:
        rep_f  = rep_other.strip()  if rep_sel  =="Other" else rep_sel
        fac_f  = fac_other.strip()  if fac_sel  =="Other" else fac_sel
        surg_f = surg_other.strip() if surg_sel =="Other" else surg_sel
        proc_f = proc_other.strip() if proc_sel =="Other" else proc_sel

        errs=[]
        if not invoice.strip():             errs.append("Invoice Number")
        if rep_sel =="— Select —":          errs.append("Rep")
        if rep_sel =="Other" and not rep_f: errs.append("Rep Name")
        if fac_sel =="— Select —":          errs.append("Facility")
        if fac_sel =="Other" and not fac_f: errs.append("Facility Name")
        if reg_sel =="— Select —":          errs.append("Region")
        if surg_sel=="— Select —":          errs.append("Surgeon")
        if surg_sel=="Other" and not surg_f:errs.append("Surgeon Name")
        if proc_sel=="— Select —":          errs.append("Procedure")
        if proc_sel=="Other" and not proc_f:errs.append("Procedure Name")
        if not implants_sel:                errs.append("Implants Used")
        if invoice.strip() in [r.get("invoice","") for r in raw]:
            errs.append(f"Invoice {invoice.strip()} already exists")

        if errs:
            st.error(f"Please fix: **{' · '.join(errs)}**")
        else:
            rec = {"id":datetime.now().strftime("%Y%m%d%H%M%S%f"),"date":str(proc_date),
                   "invoice":invoice.strip(),"rep":rep_f,"facility":fac_f,"region":reg_sel,
                   "surgeon":surg_f,"procedure":proc_f,"implants":implants_sel,
                   "challenges":challenges.strip() or "None",
                   "feedback":feedback.strip() or "—",
                   "logged_at":datetime.now().isoformat()}
            raw.append(rec); save_data(raw); bust()
            st.success(f"✅ Saved — Invoice **{invoice.strip()}** · {proc_f} · {fac_f}")
            st.balloons()


# ─────────────────────────────────────────────────────────────────────────────
# ██  PROCEDURE LOG
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📋  Procedure Log":
    st.markdown("""
    <div class="ph">
        <div class="ph-badge">Records</div>
        <h1>PROCEDURE LOG</h1>
        <p>Search, filter, view, edit and manage all logged procedures</p>
    </div>""", unsafe_allow_html=True)

    df = get_df()
    if df.empty:
        st.info("No procedures found. Add one to get started!"); st.stop()

    with st.expander("🔍  Filters", expanded=True):
        fc1,fc2,fc3,fc4 = st.columns(4)
        with fc1: sr = st.selectbox("Rep",      ["All"]+sorted(df["rep"].dropna().unique().tolist())      if "rep"      in df.columns else ["All"])
        with fc2: sg = st.selectbox("Region",   ["All"]+sorted(df["region"].dropna().unique().tolist())   if "region"   in df.columns else ["All"])
        with fc3: sf = st.selectbox("Facility", ["All"]+sorted(df["facility"].dropna().unique().tolist()) if "facility" in df.columns else ["All"])
        with fc4: sp = st.selectbox("Procedure",["All"]+sorted(df["procedure"].dropna().unique().tolist())if "procedure" in df.columns else ["All"])
        dc1,dc2,dc3 = st.columns([2,2,3])
        with dc1: d_from = st.date_input("From", value=df["date"].min().date())
        with dc2: d_to   = st.date_input("To",   value=df["date"].max().date())
        with dc3: q = st.text_input("🔎 Search invoice / surgeon / facility / rep", placeholder="Type to search…")

    flt=df.copy()
    if sr!="All": flt=flt[flt["rep"]==sr]
    if sg!="All": flt=flt[flt["region"]==sg]
    if sf!="All": flt=flt[flt["facility"]==sf]
    if sp!="All": flt=flt[flt["procedure"]==sp]
    flt=flt[(flt["date"].dt.date>=d_from)&(flt["date"].dt.date<=d_to)]
    if q.strip():
        qx=q.strip().lower()
        mk=pd.Series(False,index=flt.index)
        for c in ["invoice","surgeon","facility","rep","procedure"]:
            if c in flt.columns: mk|=flt[c].astype(str).str.lower().str.contains(qx,na=False)
        flt=flt[mk]

    ch1,ch2 = st.columns([3,1])
    with ch1: st.markdown(f"<div class='sec-lbl'>Showing {len(flt)} of {len(df)} procedures</div>",unsafe_allow_html=True)
    with ch2: srt=st.selectbox("Sort",["Date ↓","Date ↑","Rep","Facility","Invoice"],label_visibility="collapsed")

    sm={"Date ↓":("date",False),"Date ↑":("date",True),"Rep":("rep",True),"Facility":("facility",True),"Invoice":("invoice",True)}
    sc_col,sa=sm[srt]; flt=flt.sort_values(sc_col,ascending=sa)

    sc_cols=[c for c in ["date","invoice","rep","procedure","facility","region","surgeon"] if c in flt.columns]
    disp=flt[sc_cols].copy()
    if "date" in disp.columns: disp["date"]=disp["date"].dt.strftime("%d %b %Y")
    st.dataframe(disp,use_container_width=True,hide_index=True,height=360)

    # Detail
    st.markdown("---")
    st.markdown("### 🔍 Record Detail")
    if flt.empty:
        st.info("No records match your filters.")
    else:
        il=flt.sort_values("date",ascending=False)["invoice"].tolist()
        si=st.selectbox("Select Invoice",il,key="det")
        rec=flt[flt["invoice"]==si].iloc[0]
        dv = rec.get("date","")
        dstr = dv.strftime("%d %b %Y") if hasattr(dv,"strftime") else str(dv)[:10]

        ca,cb,cc=st.columns(3)
        with ca:
            for lbl,val in [("Date",dstr),("Invoice",rec.get("invoice","")),("Rep",rec.get("rep",""))]:
                st.markdown(f'<div class="rf"><div class="rl">{lbl}</div><div class="rv">{val}</div></div>',unsafe_allow_html=True)
        with cb:
            for lbl,val in [("Facility",rec.get("facility","")),("Region",rec.get("region","")),("Surgeon",rec.get("surgeon",""))]:
                st.markdown(f'<div class="rf"><div class="rl">{lbl}</div><div class="rv">{val}</div></div>',unsafe_allow_html=True)
        with cc:
            for lbl,val in [("Procedure",rec.get("procedure","")),("Logged At",str(rec.get("logged_at",""))[:16])]:
                st.markdown(f'<div class="rf"><div class="rl">{lbl}</div><div class="rv">{val}</div></div>',unsafe_allow_html=True)

        impl=rec.get("implants",[])
        if isinstance(impl,list) and impl:
            chips=" ".join([f'<span class="chip">{i}</span>' for i in impl])
            st.markdown(f'<div class="rf"><div class="rl">Implants Used</div><div class="rv">{chips}</div></div>',unsafe_allow_html=True)

        cn1,cn2=st.columns(2)
        with cn1: st.markdown(f'<div class="rf"><div class="rl">⚠️ Challenges</div><div class="rv">{rec.get("challenges","—")}</div></div>',unsafe_allow_html=True)
        with cn2: st.markdown(f'<div class="rf"><div class="rl">💬 Feedback</div><div class="rv">{rec.get("feedback","—")}</div></div>',unsafe_allow_html=True)

    # Edit
    st.markdown("---")
    with st.expander("✏️  Edit a Record"):
        ei=st.text_input("Invoice number to edit",key="ei")
        raw2=load_data()
        er_list=[r for r in raw2 if r.get("invoice")==ei.strip()]
        if ei.strip() and er_list:
            er=er_list[0]
            with st.form("edit_form"):
                ec1,ec2,ec3=st.columns(3)
                with ec1: e_d=st.date_input("Date",value=date.fromisoformat(str(er["date"])[:10]))
                with ec2: e_r=st.selectbox("Rep",REPS,index=REPS.index(er["rep"]) if er["rep"] in REPS else 0)
                with ec3: e_f=st.selectbox("Facility",FACILITIES,index=FACILITIES.index(er["facility"]) if er["facility"] in FACILITIES else 0)
                ec4,ec5=st.columns(2)
                with ec4: e_g=st.selectbox("Region",REGIONS,index=REGIONS.index(er["region"]) if er["region"] in REGIONS else 0)
                with ec5: e_s=st.selectbox("Surgeon",SURGEONS,index=SURGEONS.index(er["surgeon"]) if er["surgeon"] in SURGEONS else 0)
                e_p=st.text_input("Procedure",value=er.get("procedure",""))
                e_c=st.text_area("Challenges",value=er.get("challenges",""),height=80)
                e_fb=st.text_area("Feedback",value=er.get("feedback",""),height=80)
                if st.form_submit_button("💾 Save Changes",type="primary"):
                    for r in raw2:
                        if r.get("invoice")==ei.strip():
                            r.update({"date":str(e_d),"rep":e_r,"facility":e_f,"region":e_g,
                                      "surgeon":e_s,"procedure":e_p,"challenges":e_c,"feedback":e_fb})
                    save_data(raw2); bust()
                    st.success("Record updated!"); st.rerun()
        elif ei.strip(): st.warning("Invoice not found.")

    with st.expander("🗑️  Delete a Record"):
        di=st.text_input("Invoice number to delete",key="di")
        if st.button("🗑️  Delete Record",type="primary"):
            raw3=load_data(); before=len(raw3)
            raw3=[r for r in raw3 if r.get("invoice")!=di.strip()]
            if len(raw3)<before:
                save_data(raw3); bust()
                st.success(f"Deleted `{di}`"); st.rerun()
            else: st.warning("Invoice not found.")


# ─────────────────────────────────────────────────────────────────────────────
# ██  ANALYTICS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📈  Analytics":
    st.markdown("""
    <div class="ph">
        <div class="ph-badge">Insights</div>
        <h1>ANALYTICS</h1>
        <p>Deep-dive into rep performance, facility coverage, procedure trends and implant usage</p>
    </div>""", unsafe_allow_html=True)

    df = get_df()
    if df.empty:
        st.info("No data available. Add procedures to unlock analytics."); st.stop()

    with st.expander("⚙️  Filter Analytics", expanded=False):
        fa1,fa2=st.columns(2)
        with fa1: sy=st.selectbox("Year",["All"]+sorted(df["year"].dropna().unique().astype(str).tolist(),reverse=True))
        with fa2: sa2=st.selectbox("Rep",["All"]+sorted(df["rep"].dropna().unique().tolist()) if "rep" in df.columns else ["All"])
    adf=df.copy()
    if sy !="All": adf=adf[adf["year"].astype(str)==sy]
    if sa2!="All": adf=adf[adf["rep"]==sa2]

    tab1,tab2,tab3,tab4 = st.tabs(["📅  Trends","🏥  Facility & Region","👤  Rep Performance","🦴  Implants"])

    with tab1:
        c1,c2=st.columns(2)
        with c1:
            mo=adf.groupby("month").size().reset_index(name="Count")
            fig=px.area(mo,x="month",y="Count",color_discrete_sequence=["#2563EB"])
            fig.update_traces(fill="tozeroy",fillcolor="rgba(37,99,235,.12)",line=dict(width=2.5))
            sc(fig,"Monthly Procedure Volume"); fig.update_layout(height=280)
            st.plotly_chart(fig,use_container_width=True)
        with c2:
            ord_=[c for c in ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]]
            dow=adf["date"].dt.day_name().value_counts().reindex(ord_,fill_value=0).reset_index()
            dow.columns=["Day","Count"]
            fig2=px.bar(dow,x="Day",y="Count",color="Count",color_continuous_scale=["#E0F2FE","#0284C7"])
            fig2.update_traces(text=dow["Count"],textposition="outside")
            sc(fig2,"Volume by Day of Week"); fig2.update_layout(height=280,showlegend=False,coloraxis_showscale=False)
            st.plotly_chart(fig2,use_container_width=True)

        if "quarter" in adf.columns and "rep" in adf.columns:
            qr=adf.groupby(["quarter","rep"]).size().reset_index(name="Count")
            fig3=px.line(qr,x="quarter",y="Count",color="rep",markers=True,color_discrete_sequence=COLORS)
            sc(fig3,"Quarterly Trends by Rep"); fig3.update_layout(height=300,legend=dict(orientation="h",y=-0.25))
            st.plotly_chart(fig3,use_container_width=True)

        if "procedure" in adf.columns:
            tp=adf["procedure"].value_counts().head(6).index.tolist()
            pt=adf[adf["procedure"].isin(tp)].groupby(["month","procedure"]).size().reset_index(name="Count")
            fig4=px.line(pt,x="month",y="Count",color="procedure",markers=True,color_discrete_sequence=COLORS)
            sc(fig4,"Top Procedure Types Over Time"); fig4.update_layout(height=300,legend=dict(orientation="h",y=-0.25))
            st.plotly_chart(fig4,use_container_width=True)

    with tab2:
        c1,c2=st.columns(2)
        with c1:
            if "facility" in adf.columns:
                fc2=adf["facility"].value_counts().reset_index(); fc2.columns=["Facility","Count"]
                fig5=px.bar(fc2,x="Count",y="Facility",orientation="h",
                    color="Count",color_continuous_scale=["#FEF3C7","#D97706"],text="Count")
                fig5.update_traces(textposition="outside")
                sc(fig5,"Procedures by Facility")
                fig5.update_layout(yaxis=dict(autorange="reversed"),height=380,showlegend=False,coloraxis_showscale=False)
                st.plotly_chart(fig5,use_container_width=True)
        with c2:
            if "region" in adf.columns:
                rg=adf["region"].value_counts().reset_index(); rg.columns=["Region","Count"]
                fig6=px.pie(rg,values="Count",names="Region",hole=.45,color_discrete_sequence=COLORS)
                fig6.update_traces(textposition="inside",textinfo="percent+label",textfont_size=11)
                sc(fig6,"Regional Distribution")
                fig6.update_layout(height=380,showlegend=True,legend=dict(orientation="v",x=1.02))
                st.plotly_chart(fig6,use_container_width=True)

        if "region" in adf.columns and "procedure" in adf.columns:
            hm=adf.groupby(["region","procedure"]).size().unstack(fill_value=0)
            fig7=px.imshow(hm,color_continuous_scale="Blues",aspect="auto",text_auto=True)
            sc(fig7,"Region × Procedure Heatmap"); fig7.update_layout(height=380,coloraxis_showscale=False)
            st.plotly_chart(fig7,use_container_width=True)

    with tab3:
        if "rep" in adf.columns:
            rs=adf.groupby("rep").agg(
                Procedures=("id","count"),Facilities=("facility","nunique"),
                Surgeons=("surgeon","nunique"),Regions=("region","nunique")
            ).reset_index().sort_values("Procedures",ascending=False)
            st.markdown("#### Rep Performance Summary")
            st.dataframe(rs,use_container_width=True,hide_index=True)

            c1,c2=st.columns(2)
            with c1:
                fig8=px.bar(rs.head(10),x="Procedures",y="rep",orientation="h",
                    color="Procedures",color_continuous_scale=["#DBEAFE","#1D4ED8"],text="Procedures")
                fig8.update_traces(textposition="outside")
                sc(fig8,"Total Procedures per Rep")
                fig8.update_layout(yaxis=dict(autorange="reversed"),height=340,showlegend=False,coloraxis_showscale=False)
                st.plotly_chart(fig8,use_container_width=True)
            with c2:
                fig9=px.scatter(rs,x="Facilities",y="Procedures",text="rep",
                    color="Regions",size="Procedures",size_max=40,color_continuous_scale="Blues")
                sc(fig9,"Reach: Procedures vs Facilities")
                fig9.update_traces(textposition="top center",textfont_size=9)
                fig9.update_layout(height=340,showlegend=False,coloraxis_showscale=False)
                st.plotly_chart(fig9,use_container_width=True)

            rm=adf.groupby(["rep","month"]).size().unstack(fill_value=0)
            fig10=px.imshow(rm,color_continuous_scale="Blues",aspect="auto",text_auto=True)
            sc(fig10,"Rep Activity Heatmap (Monthly)"); fig10.update_layout(height=360,coloraxis_showscale=False)
            st.plotly_chart(fig10,use_container_width=True)

    with tab4:
        if "implants" in adf.columns:
            imp=adf["implants"].dropna().explode().value_counts().reset_index()
            imp.columns=["Implant","Count"]
            c1,c2=st.columns(2)
            with c1:
                fig11=px.bar(imp.head(12),x="Count",y="Implant",orientation="h",
                    color="Count",color_continuous_scale=["#CCFBF1","#0D9488"],text="Count")
                fig11.update_traces(textposition="outside")
                sc(fig11,"Most Used Implants")
                fig11.update_layout(yaxis=dict(autorange="reversed"),height=380,showlegend=False,coloraxis_showscale=False)
                st.plotly_chart(fig11,use_container_width=True)
            with c2:
                fig12=px.pie(imp.head(10),values="Count",names="Implant",hole=.4,color_discrete_sequence=COLORS)
                fig12.update_traces(textposition="inside",textinfo="percent+label",textfont_size=10)
                sc(fig12,"Implant Mix (Top 10)"); fig12.update_layout(height=380,showlegend=False)
                st.plotly_chart(fig12,use_container_width=True)

            adf2=adf.copy(); adf2=adf2.explode("implants")
            ti=adf2["implants"].value_counts().head(6).index.tolist()
            it=adf2[adf2["implants"].isin(ti)].groupby(["month","implants"]).size().reset_index(name="Count")
            fig13=px.line(it,x="month",y="Count",color="implants",markers=True,color_discrete_sequence=COLORS)
            sc(fig13,"Top Implant Usage Over Time"); fig13.update_layout(height=300,legend=dict(orientation="h",y=-0.25))
            st.plotly_chart(fig13,use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# ██  REPORTS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "⬇️  Reports":
    st.markdown("""
    <div class="ph">
        <div class="ph-badge">Export</div>
        <h1>REPORTS</h1>
        <p>Generate and download professional procedure reports in PDF, Excel or CSV</p>
    </div>""", unsafe_allow_html=True)

    df = get_df()
    if df.empty:
        st.info("No procedures to report on yet."); st.stop()

    st.markdown("### ⚙️ Configure Report")
    rb1,rb2=st.columns(2)
    with rb1: scope=st.selectbox("Report Scope",["All Procedures","By Rep","By Region","By Facility","By Procedure Type","Date Range"])
    with rb2: fmt=st.selectbox("Export Format",["📄 PDF (Branded)","📊 Excel Workbook (.xlsx)","📑 CSV"])

    flt_r=df.copy(); lbl="All Procedures"
    if scope=="By Rep" and "rep" in df.columns:
        sr2=st.selectbox("Select Rep",sorted(df["rep"].dropna().unique().tolist()))
        flt_r=df[df["rep"]==sr2]; lbl=f"Rep: {sr2}"
    elif scope=="By Region" and "region" in df.columns:
        sg2=st.selectbox("Select Region",sorted(df["region"].dropna().unique().tolist()))
        flt_r=df[df["region"]==sg2]; lbl=f"Region: {sg2}"
    elif scope=="By Facility" and "facility" in df.columns:
        sf2=st.selectbox("Select Facility",sorted(df["facility"].dropna().unique().tolist()))
        flt_r=df[df["facility"]==sf2]; lbl=f"Facility: {sf2}"
    elif scope=="By Procedure Type" and "procedure" in df.columns:
        sp2=st.selectbox("Select Procedure",sorted(df["procedure"].dropna().unique().tolist()))
        flt_r=df[df["procedure"]==sp2]; lbl=f"Procedure: {sp2}"
    elif scope=="Date Range":
        dr1,dr2=st.columns(2)
        with dr1: df_from2=st.date_input("From",value=df["date"].min().date())
        with dr2: df_to2  =st.date_input("To",  value=df["date"].max().date())
        flt_r=df[(df["date"].dt.date>=df_from2)&(df["date"].dt.date<=df_to2)]
        lbl=f"{df_from2.strftime('%d %b %Y')} – {df_to2.strftime('%d %b %Y')}"

    st.markdown("---")
    st.markdown("### 📋 Report Preview")
    rp1,rp2,rp3,rp4=st.columns(4)
    with rp1: st.metric("Procedures",  len(flt_r))
    with rp2: st.metric("Facilities",  flt_r["facility"].nunique() if "facility" in flt_r.columns else 0)
    with rp3: st.metric("Surgeons",    flt_r["surgeon"].nunique()  if "surgeon"  in flt_r.columns else 0)
    with rp4: st.metric("Reps",        flt_r["rep"].nunique()       if "rep"      in flt_r.columns else 0)

    if not flt_r.empty:
        pc=[c for c in ["date","invoice","rep","procedure","facility","surgeon"] if c in flt_r.columns]
        pd2=flt_r.sort_values("date",ascending=False)[pc].head(6).copy()
        if "date" in pd2.columns: pd2["date"]=pd2["date"].dt.strftime("%d %b %Y")
        st.dataframe(pd2,use_container_width=True,hide_index=True)

    st.markdown("---")
    st.markdown("### ⬇️ Download")
    rt=f"OrthoTrack Pro — {lbl}"
    ts=datetime.now().strftime("%Y%m%d_%H%M")

    if "PDF" in fmt:
        st.markdown("""<div class="dlc"><div class="di">📄</div><div class="dt">Branded PDF Report</div>
        <div class="dd">Professional formatted report with summary stats, procedure log and OrthoTrack branding</div></div>""",
        unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("📄  Generate PDF Report", type="primary", use_container_width=True):
            with st.spinner("Building PDF…"):
                pb=build_pdf(flt_r,rt,lbl)
            st.download_button("⬇️  Download PDF", data=pb,
                file_name=f"orthotrack_{ts}.pdf", mime="application/pdf", use_container_width=True)

    elif "Excel" in fmt:
        st.markdown("""<div class="dlc"><div class="di">📊</div><div class="dt">Excel Workbook</div>
        <div class="dd">3-sheet workbook: Procedures · Summary Statistics · Regional Breakdown — fully formatted</div></div>""",
        unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("📊  Generate Excel Workbook", type="primary", use_container_width=True):
            with st.spinner("Building Excel workbook…"):
                xb=build_excel(flt_r,rt)
            st.download_button("⬇️  Download Excel", data=xb,
                file_name=f"orthotrack_{ts}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)

    elif "CSV" in fmt:
        st.markdown("""<div class="dlc"><div class="di">📑</div><div class="dt">CSV Export</div>
        <div class="dd">Raw data export — all columns, all records, comma-separated for Excel or any BI tool</div></div>""",
        unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        cd=flt_r.copy()
        if "date" in cd.columns: cd["date"]=cd["date"].dt.strftime("%Y-%m-%d")
        if "implants" in cd.columns: cd["implants"]=cd["implants"].apply(lambda x:", ".join(x) if isinstance(x,list) else str(x))
        for c in ["month","year","quarter"]:
            if c in cd.columns: cd.drop(columns=c,inplace=True)
        st.download_button("⬇️  Download CSV", data=cd.to_csv(index=False).encode(),
            file_name=f"orthotrack_{ts}.csv", mime="text/csv", use_container_width=True)
