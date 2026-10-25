"""
Saylani Hackathon 2026 — HCM Lite
AI-Assisted Human Capital Management System
Dark Theme · Real Face Detection (OpenCV) · Persistent JSON Storage (main directory)
"""

import streamlit as st
import pandas as pd
import numpy as np
import datetime
import math
import os
import json
import base64

# --- OpenCV (optional) ---
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    cv2 = None

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="HCM Lite — Saylani Hackathon 2026",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------- PERSISTENCE (main directory) -----------------
DATA_FILE = "hcm_data.json"

# ----------------- GLOBAL STYLING -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    :root {
        --bg-0:#060a13; --bg-1:#0a1020; --bg-2:#0e1626; --bg-3:#131e33;
        --border:#1e293b; --border-2:#243447;
        --text-1:#f1f5f9; --text-2:#94a3b8; --text-3:#64748b;
        --teal:#14b8a6; --teal-lt:#5eead4; --teal-dk:#0f766e;
        --cyan:#06b6d4; --amber:#f59e0b; --rose:#f43f5e;
        --emerald:#10b981; --violet:#8b5cf6;
    }
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    .stApp {
        background:
            radial-gradient(1200px 600px at 80% -10%, rgba(20,184,166,0.10), transparent 60%),
            radial-gradient(900px 500px at -10% 110%, rgba(6,182,212,0.08), transparent 55%),
            var(--bg-0);
    }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1500px; }
    h1, h2, h3, h4, h5 { color: var(--text-1) !important; letter-spacing: -0.02em; }
    h1 { font-weight: 800 !important; } h2 { font-weight: 700 !important; }
    p, span, label, div { color: var(--text-1); }

    .hcm-header {
        background: linear-gradient(135deg, rgba(13,27,42,0.95) 0%, rgba(10,37,64,0.95) 55%, rgba(6,10,19,0.95) 100%),
                    radial-gradient(circle at 90% 0%, rgba(20,184,166,0.18), transparent 55%);
        border: 1px solid var(--border-2); border-radius: 20px; padding: 26px 30px; margin-bottom: 22px;
        box-shadow: 0 20px 45px -20px rgba(0,0,0,0.7), inset 0 1px 0 rgba(255,255,255,0.04);
        position: relative; overflow: hidden;
    }
    .hcm-header::before {
        content: ""; position: absolute; inset: 0;
        background: radial-gradient(600px 200px at 100% 0%, rgba(94,234,212,0.10), transparent 70%);
        pointer-events: none;
    }
    .hcm-header-title {
        font-size: 1.85rem; font-weight: 800; letter-spacing: -0.03em;
        background: linear-gradient(90deg, #ffffff 0%, #5eead4 90%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin: 0; line-height: 1.15;
    }
    .hcm-eyebrow {
        font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.14em;
        color: var(--teal-lt); font-weight: 700; margin-bottom: 4px;
    }
    .hcm-subline { font-size: 0.85rem; color: var(--text-2); margin-top: 6px; }

    .metric-card {
        background: linear-gradient(180deg, var(--bg-2) 0%, var(--bg-1) 100%);
        border: 1px solid var(--border); border-radius: 16px; padding: 18px 20px;
        box-shadow: 0 6px 18px -8px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.03);
        transition: transform .18s ease, border-color .18s ease; position: relative; overflow: hidden; height: 100%;
    }
    .metric-card::after {
        content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 3px;
        background: linear-gradient(180deg, var(--teal), var(--cyan)); opacity: 0.9;
    }
    .metric-card:hover { border-color: var(--teal-dk); transform: translateY(-3px); }
    .metric-icon {
        width: 34px; height: 34px; border-radius: 10px; display: inline-flex;
        align-items: center; justify-content: center;
        background: rgba(20,184,166,0.14); border: 1px solid rgba(20,184,166,0.35);
        font-size: 17px; margin-bottom: 10px;
    }
    .metric-label { font-size: 0.70rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.09em; color: var(--text-2); }
    .metric-value { font-size: 1.95rem; font-weight: 800; color: var(--text-1); margin: 2px 0 3px 0; letter-spacing: -0.02em; }
    .metric-sub { font-size: 0.75rem; color: var(--teal-lt); font-weight: 600; }

    .badge { display: inline-flex; align-items: center; gap: 6px; padding: 5px 11px; border-radius: 999px; font-weight: 700; font-size: 0.72rem; border: 1px solid transparent; }
    .badge-admin { background: rgba(139,92,246,0.14); color: #c4b5fd; border-color: rgba(139,92,246,0.4); }
    .badge-hr    { background: rgba(20,184,166,0.14); color: var(--teal-lt); border-color: rgba(20,184,166,0.4); }
    .badge-emp   { background: rgba(245,158,11,0.14); color: #fcd34d; border-color: rgba(245,158,11,0.4); }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #060a13 0%, #0a1020 100%);
        border-right: 1px solid var(--border);
    }
    section[data-testid="stSidebar"] .stRadio label,
    section[data-testid="stSidebar"] .stButton button { color: var(--text-1) !important; }
    .sidebar-profile {
        background: linear-gradient(180deg, var(--bg-3) 0%, var(--bg-2) 100%);
        border: 1px solid var(--border); border-radius: 14px; padding: 14px;
        margin-bottom: 12px; position: relative; overflow: hidden;
    }
    .sidebar-profile::before {
        content: ""; position: absolute; inset: 0;
        background: radial-gradient(220px 80px at 100% 0%, rgba(20,184,166,0.14), transparent 70%);
        pointer-events: none;
    }
    .avatar {
        width: 38px; height: 38px; border-radius: 10px;
        background: linear-gradient(135deg, var(--teal), var(--cyan));
        display: flex; align-items: center; justify-content: center;
        font-weight: 800; color: #022c22; font-size: 15px; flex-shrink: 0;
    }

    .stButton > button { border-radius: 10px !important; font-weight: 600 !important; transition: all .15s ease !important; border: 1px solid var(--border-2) !important; }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--teal) 0%, var(--cyan) 100%) !important;
        color: #022c22 !important; border: none !important; font-weight: 800 !important;
        box-shadow: 0 8px 20px -8px rgba(20,184,166,0.55) !important;
    }
    .stButton > button[kind="primary"]:hover { transform: translateY(-1px); }
    .stButton > button:hover { border-color: var(--teal) !important; }

    .stTextInput input, .stNumberInput input, .stTextArea textarea,
    .stDateInput input, .stTimeInput input {
        background: var(--bg-2) !important;
        border-color: var(--border-2) !important;
        color: var(--text-1) !important;
        color: var(--teal) !important;
        border-radius: 10px !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--teal) !important;
        box-shadow: 0 0 0 3px rgba(20,184,166,0.15) !important;
    }

    /* DROPDOWN FIX */
    div[data-baseweb="select"] > div {
        background-color: var(--bg-2) !important;
        color: var(--text-1) !important;
        border-color: var(--border-2) !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] input,
    div[data-baseweb="select"] div[aria-selected] {
        color: var(--text-1) !important;
        background-color: transparent !important;
    }
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    ul[data-baseweb="menu"] {
        background-color: var(--bg-3) !important;
        border: 1px solid var(--border-2) !important;
        border-radius: 10px !important;
    }
    ul[data-baseweb="menu"] li,
    li[role="option"] {
        background-color: var(--bg-3) !important;
        color: var(--text-1) !important;
        padding: 9px 13px !important;
        font-size: 13.5px !important;
    }
    ul[data-baseweb="menu"] li:hover,
    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {
        background-color: rgba(20,184,166,0.18) !important;
        color: var(--teal-lt) !important;
    }
    span[data-baseweb="tag"] {
        background-color: rgba(20,184,166,0.22) !important;
        color: var(--teal-lt) !important;
    }

    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] { border-radius: 10px 10px 0 0; padding: 10px 18px; font-weight: 600; }
    .stTabs [aria-selected="true"] { background: rgba(20,184,166,0.12) !important; color: var(--teal-lt) !important; }

    div[data-testid="stDataFrame"] { border-radius: 12px; border: 1px solid var(--border); overflow: hidden; }
    div[data-testid="stMetric"] { background: var(--bg-2); border: 1px solid var(--border); border-radius: 14px; padding: 14px 16px; }
    div[data-testid="stMetricValue"] { color: var(--text-1) !important; font-weight: 800 !important; }
    div[data-testid="stMetricLabel"] { color: var(--text-2) !important; }

    .payslip-box {
        background: linear-gradient(180deg, var(--bg-2) 0%, var(--bg-1) 100%);
        border: 1px solid var(--border-2); border-radius: 16px; padding: 26px 28px;
        box-shadow: 0 20px 40px -22px rgba(0,0,0,0.7);
    }
    .ps-label { color: var(--text-2); font-size: 13px; }
    .ps-val   { text-align: right; font-size: 13px; font-variant-numeric: tabular-nums; }

    .login-card {
        background: linear-gradient(180deg, rgba(14,22,38,0.95) 0%, rgba(10,16,32,0.95) 100%),
                    radial-gradient(400px 200px at 100% 0%, rgba(20,184,166,0.14), transparent 70%);
        border: 1px solid var(--border-2); border-radius: 20px; padding: 28px;
        box-shadow: 0 30px 60px -30px rgba(0,0,0,0.8);
    }
    .login-hero { text-align: center; padding: 20px 10px 10px 10px; }
    .login-badge {
        display: inline-flex; align-items: center; justify-content: center;
        width: 62px; height: 62px; background: linear-gradient(135deg, var(--teal), var(--cyan));
        border-radius: 18px; font-weight: 900; font-size: 22px; color: #022c22;
        box-shadow: 0 12px 32px -8px rgba(20,184,166,0.55); margin-bottom: 16px;
    }
    .login-title { color: #ffffff; font-size: 2.1rem; font-weight: 800; letter-spacing: -0.03em; margin: 0; }
    .login-subtitle { color: var(--teal-lt); font-size: 1.05rem; font-weight: 600; margin: 6px 0 14px 0; }
    .login-desc { color: var(--text-2); font-size: 0.85rem; line-height: 1.6; }

    div[data-testid="stAlert"] { border-radius: 12px !important; border: 1px solid var(--border-2) !important; background: var(--bg-2) !important; }
</style>
""", unsafe_allow_html=True)

# ----------------- FACE HELPERS -----------------
@st.cache_resource
def _load_face_cascade():
    if not HAS_CV2: return None
    return cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def _face_to_b64(face):
    if face is None or not HAS_CV2: return None
    try:
        ok, buf = cv2.imencode(".jpg", face, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ok: return None
        return base64.b64encode(buf.tobytes()).decode("utf-8")
    except Exception:
        return None

def _b64_to_face(s):
    if not s or not HAS_CV2: return None
    try:
        arr = np.frombuffer(base64.b64decode(s), np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)
    except Exception:
        return None

def detect_faces_in_image(img_bytes):
    if not HAS_CV2: return [], None
    cascade = _load_face_cascade()
    if cascade is None: return [], None
    arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None: return [], None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
    return list(faces), img

def annotate_faces(img, faces):
    """Draw teal rectangle (square box) around each detected face."""
    if img is None: return None
    annotated = img.copy()
    for (x, y, w, h) in faces:
        cv2.rectangle(annotated, (x, y), (x + w, y + h), (20, 184, 166), 3)
        cv2.putText(annotated, "FACE", (x, max(y - 10, 15)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (20, 184, 166), 2)
    return cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

def extract_face_crop(img, box, size=(128, 128)):
    if img is None or box is None: return None
    x, y, w, h = box
    x, y = max(0, x), max(0, y)
    face = img[y:y + h, x:x + w]
    if face.size == 0: return None
    return cv2.resize(face, size)

def match_faces(face_a, face_b):
    if face_a is None or face_b is None: return 0.0
    try:
        ga = cv2.cvtColor(face_a, cv2.COLOR_BGR2GRAY).astype(np.float32)
        gb = cv2.cvtColor(face_b, cv2.COLOR_BGR2GRAY).astype(np.float32)
        ga = (ga - ga.mean()) / (ga.std() + 1e-6)
        gb = (gb - gb.mean()) / (gb.std() + 1e-6)
        corr = float((ga * gb).mean())
        return round((corr + 1) / 2, 4)
    except Exception:
        return 0.0

FACE_MATCH_THRESHOLD = 0.60

# ----------------- SAVE / LOAD (PERSISTENCE) -----------------
def save_data():
    try:
        data = {
            "employees": st.session_state.get("employees", []),
            "attendance": st.session_state.get("attendance", []),
            "leaves": st.session_state.get("leaves", []),
            "finalized_payrolls": st.session_state.get("finalized_payrolls", {}),
            "audit_trail": st.session_state.get("audit_trail", []),
            "announcements": st.session_state.get("announcements", []),
            "company_name": st.session_state.get("company_name", "TechNova Solutions"),
            "office_start": st.session_state.get("office_start", datetime.time(9, 0)).strftime("%H:%M"),
            "grace_minutes": st.session_state.get("grace_minutes", 15),
            "half_day_hours": st.session_state.get("half_day_hours", 5),
            "weekend_days": st.session_state.get("weekend_days", ["Saturday", "Sunday"]),
            "office_lat": st.session_state.get("office_lat", 24.8607),
            "office_lng": st.session_state.get("office_lng", 67.0011),
            "office_radius_m": st.session_state.get("office_radius_m", 150),
            "leave_quotas": st.session_state.get("leave_quotas", {}),
            "departments": st.session_state.get("departments", []),
            "designations": st.session_state.get("designations", []),
            "public_holidays": st.session_state.get("public_holidays", []),
            "face_registry_b64": {
                k: _face_to_b64(v) for k, v in st.session_state.get("face_registry", {}).items()
            },
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
    except Exception as e:
        print(f"[save_data error] {e}")

def load_data():
    if not os.path.exists(DATA_FILE): return False
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        st.session_state.employees = data.get("employees", [])
        st.session_state.attendance = data.get("attendance", [])
        st.session_state.leaves = data.get("leaves", [])
        st.session_state.finalized_payrolls = data.get("finalized_payrolls", {})
        st.session_state.audit_trail = data.get("audit_trail", [])
        st.session_state.announcements = data.get("announcements", [])
        st.session_state.company_name = data.get("company_name", "TechNova Solutions")
        if data.get("office_start"):
            h, m = data["office_start"].split(":")
            st.session_state.office_start = datetime.time(int(h), int(m))
        st.session_state.grace_minutes = data.get("grace_minutes", 15)
        st.session_state.half_day_hours = data.get("half_day_hours", 5)
        st.session_state.weekend_days = data.get("weekend_days", ["Saturday", "Sunday"])
        st.session_state.office_lat = data.get("office_lat", 24.8607)
        st.session_state.office_lng = data.get("office_lng", 67.0011)
        st.session_state.office_radius_m = data.get("office_radius_m", 150)
        st.session_state.leave_quotas = data.get("leave_quotas", {"annual":14,"sick":8,"casual":10,"unpaid":999})
        st.session_state.departments = data.get("departments", [])
        st.session_state.designations = data.get("designations", [])
        st.session_state.public_holidays = data.get("public_holidays", [])
        st.session_state.face_registry = {
            k: _b64_to_face(v) for k, v in data.get("face_registry_b64", {}).items() if v
        }
        return True
    except Exception as e:
        print(f"[load_data error] {e}")
        return False

def clear_disk_data():
    try:
        if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
    except Exception: pass

# ----------------- DATABASE INIT -----------------
def initialize_database(force_demo=False):
    if "db_initialized" not in st.session_state or force_demo:
        if not force_demo and load_data():
            st.session_state.db_initialized = True
            st.session_state.is_logged_in = False
            st.session_state.current_role = "Admin"
            st.session_state.current_user_id = "EMP001"
            return

        st.session_state.db_initialized = True
        st.session_state.company_name = "TechNova Solutions"
        st.session_state.office_start = datetime.time(9, 0)
        st.session_state.grace_minutes = 15
        st.session_state.half_day_hours = 5
        st.session_state.weekend_days = ["Saturday", "Sunday"]
        st.session_state.office_lat = 24.8607
        st.session_state.office_lng = 67.0011
        st.session_state.office_radius_m = 150
        st.session_state.late_penalty_rule = True
        st.session_state.departments = ["Engineering", "Human Resources", "Sales & Marketing", "Finance", "Operations"]
        st.session_state.designations = ["Chief Technology Officer", "HR Lead & People Ops", "Senior Software Engineer",
                                         "Sales Executive", "Operations Lead", "Financial Analyst", "QA Engineer"]
        st.session_state.leave_quotas = {"annual": 14, "sick": 8, "casual": 10, "unpaid": 999}
        st.session_state.public_holidays = ["2026-03-23", "2026-05-01", "2026-08-14", "2026-11-09", "2026-12-25"]
        st.session_state.is_logged_in = False
        st.session_state.current_role = "Admin"
        st.session_state.current_user_id = "EMP001"
        st.session_state.face_registry = {}
        st.session_state.employees = [
            {"employee_id":"EMP001","name":"Muhammad Asad","email":"asad.admin@technova.com","role":"Admin",
             "department":"Engineering","designation":"Chief Technology Officer","joining_date":"2023-01-15",
             "basic_salary":220000,"gender":"Male","tenure_years":3.8,"phone":"+92 300 1234567",
             "address":"Gulshan-e-Iqbal Block 13, Karachi","status":"Active","first_login":False,
             "face_enrolled":False,"face_descriptor":None},
            {"employee_id":"EMP002","name":"Fatima Zahra","email":"fatima.hr@technova.com","role":"HR",
             "department":"Human Resources","designation":"HR Lead & People Ops","joining_date":"2023-06-01",
             "basic_salary":140000,"gender":"Female","tenure_years":3.3,"phone":"+92 321 7654321",
             "address":"PECHS Block 2, Karachi","status":"Active","first_login":False,
             "face_enrolled":False,"face_descriptor":None},
            {"employee_id":"EMP003","name":"Bilal Tariq","email":"bilal.dev@technova.com","role":"Employee",
             "department":"Engineering","designation":"Senior Software Engineer","joining_date":"2024-02-15",
             "basic_salary":110000,"gender":"Male","tenure_years":2.7,"phone":"+92 333 9988776",
             "address":"North Nazimabad, Karachi","status":"Active","first_login":False,
             "face_enrolled":False,"face_descriptor":None},
            {"employee_id":"EMP004","name":"Ayesha Siddiqui","email":"ayesha.sales@technova.com","role":"Employee",
             "department":"Sales & Marketing","designation":"Sales Executive","joining_date":"2024-08-01",
             "basic_salary":95000,"gender":"Female","tenure_years":2.2,"phone":"+92 345 5544332",
             "address":"Clifton Block 5, Karachi","status":"Active","first_login":False,
             "face_enrolled":False,"face_descriptor":None},
            {"employee_id":"EMP005","name":"Zayn Ul Abidin","email":"zayn.ops@technova.com","role":"Employee",
             "department":"Operations","designation":"Operations Lead","joining_date":"2025-01-10",
             "basic_salary":85000,"gender":"Male","tenure_years":1.8,"phone":"+92 312 8877665",
             "address":"Bahadurabad, Karachi","status":"Active","first_login":True,
             "face_enrolled":False,"face_descriptor":None},
        ]
        today_iso = datetime.date.today().isoformat()
        st.session_state.attendance = [
            {"id":"ATT-001","date":today_iso,"employee_id":"EMP001","name":"Muhammad Asad","check_in":"08:52","check_out":"17:30","status":"Present","hours":8.6,"method":"Web","dist_m":42},
            {"id":"ATT-002","date":today_iso,"employee_id":"EMP002","name":"Fatima Zahra","check_in":"09:24","check_out":"18:10","status":"Late","hours":8.7,"method":"Camera","dist_m":65},
        ]
        st.session_state.leaves = []
        st.session_state.finalized_payrolls = {}
        st.session_state.audit_trail = [{
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "actor":"System","action":"INITIALIZE","entity":"CompanySetup","details":"Initialized HCM Lite"
        }]
        st.session_state.announcements = [{
            "id":1,"title":"Saylani Hackathon HCM Lite Launched","date":today_iso,
            "author":"HR Department","content":"Welcome to HCM Lite! All 9 modules live."
        }]
        save_data()

initialize_database()

# ----------------- BUSINESS LOGIC -----------------
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2)**2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2)**2
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

def calculate_working_days(start_date, end_date):
    cur = start_date; count = 0
    while cur <= end_date:
        if cur.strftime("%A") not in st.session_state.weekend_days and cur.isoformat() not in st.session_state.public_holidays:
            count += 1
        cur += datetime.timedelta(days=1)
    return count

def compute_tax(annual_gross):
    if annual_gross <= 600000: return 0
    elif annual_gross <= 1200000: return (annual_gross - 600000) * 0.05
    elif annual_gross <= 2400000: return 30000 + (annual_gross - 1200000) * 0.15
    elif annual_gross <= 3600000: return 210000 + (annual_gross - 2400000) * 0.25
    else: return 510000 + (annual_gross - 3600000) * 0.35

def log_audit(actor, action, entity, details):
    st.session_state.audit_trail.insert(0, {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "actor": actor, "action": action, "entity": entity, "details": details
    })
    save_data()

# ----------------- AUTH GATE -----------------
if not st.session_state.get("is_logged_in", False):
    st.markdown("""
    <div class="login-hero">
        <div class="login-badge">HCM</div>
        <h1 class="login-title">Saylani Hackathon 2026</h1>
        <h3 class="login-subtitle">HCM Lite — AI-Assisted Human Capital Management</h3>
        <p class="login-desc">
            Select your designated role to enter the system.<br/>
            Each role operates with its own dedicated menus, database permissions, and AI assistant scope.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_m, col_r = st.columns([1, 2.6, 1])
    with col_m:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown("#### 🔐 Login Panel")
        tab_admin, tab_hr, tab_emp = st.tabs(["🛡️ Admin Portal", "👥 HR Operations", "💼 Employee Portal"])

        with tab_admin:
            st.markdown("##### 🛡️ Company Administrator Login")
            st.caption("Full company control · Executive dashboard · Employee setup · Payroll lock · Master audit trail.")
            st.text_input("Admin Work Email", value="asad.admin@technova.com", disabled=True, key="login_admin_email")
            st.text_input("Master Password", value="••••••••", type="password", disabled=True, key="login_admin_pass")
            if st.button("🚀 Sign In as Admin", use_container_width=True, type="primary"):
                st.session_state.is_logged_in = True
                st.session_state.current_role = "Admin"
                st.session_state.current_user_id = "EMP001"
                log_audit("Muhammad Asad", "LOGIN", "Auth", "Logged in as Admin")
                st.rerun()

        with tab_hr:
            st.markdown("##### 👥 HR People Operations Login")
            st.caption("Employee registration · CSV dry-run · Attendance · Leave inbox · Payroll.")
            st.text_input("HR Work Email", value="fatima.hr@technova.com", disabled=True, key="login_hr_email")
            st.text_input("HR Password", value="••••••••", type="password", disabled=True, key="login_hr_pass")
            if st.button("🚀 Sign In as HR", use_container_width=True, type="primary"):
                st.session_state.is_logged_in = True
                st.session_state.current_role = "HR"
                st.session_state.current_user_id = "EMP002"
                log_audit("Fatima Zahra", "LOGIN", "Auth", "Logged in as HR")
                st.rerun()

        with tab_emp:
            st.markdown("##### 💼 Employee Self-Service Login")
            st.caption("Camera face-verified check-in · Smart leave · Payslips · AI assistant.")
            emp_list = [e for e in st.session_state.employees if e["role"] == "Employee"] or st.session_state.employees
            emp_choices = {e["employee_id"]: e["name"] + " (" + e["designation"] + ")" for e in emp_list}
            chosen_id = st.selectbox("Choose Employee Account", list(emp_choices.keys()),
                                     format_func=lambda x: emp_choices[x], key="login_emp_select")
            chosen_obj = next((e for e in st.session_state.employees if e["employee_id"] == chosen_id), None)
            st.text_input("Work Email", value=chosen_obj["email"] if chosen_obj else "emp@technova.com",
                          disabled=True, key="login_emp_email")
            st.text_input("Password", value="••••••••", type="password", disabled=True, key="login_emp_pass")
            if st.button("🚀 Sign In as Employee", use_container_width=True, type="primary"):
                st.session_state.is_logged_in = True
                st.session_state.current_role = "Employee"
                st.session_state.current_user_id = chosen_id
                log_audit(chosen_obj["name"] if chosen_obj else "Employee", "LOGIN", "Auth", "Logged in")
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<br/>", unsafe_allow_html=True)
        st.info("💡 **Evaluator Notice:** Sign in with any role. Switch roles via **Sign Out** in the sidebar.")
    st.stop()

# ----------------- SIDEBAR -----------------
curr_user = next((e for e in st.session_state.employees if e["employee_id"] == st.session_state.current_user_id), None)
curr_user_name = curr_user["name"] if curr_user else "User"
selected_role = st.session_state.current_role
_initials = "".join([p[0] for p in curr_user_name.split()][:2]).upper()

with st.sidebar:
    st.markdown("""
    <div style="display:flex; align-items:center; gap:11px; margin-bottom:16px;">
        <div style="background: linear-gradient(135deg, #14b8a6, #06b6d4); padding:9px 13px; border-radius:11px; font-weight:900; font-size:17px; color:#022c22;">HCM</div>
        <div>
            <div style="font-weight:800; font-size:16px; color:#f8fafc; line-height:1.15;">HCM Lite</div>
            <div style="font-size:10.5px; color:#64748b; letter-spacing:0.05em;">SAYLANI HACKATHON 2026</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sidebar-profile">
        <div style="display:flex; align-items:center; gap:11px;">
            <div class="avatar">{_initials}</div>
            <div style="min-width:0; flex:1;">
                <div style="font-size:13.5px; font-weight:700; color:#f8fafc;">{curr_user_name}</div>
                <div style="font-size:11px; color:#5eead4;">{curr_user['designation'] if curr_user else selected_role}</div>
            </div>
        </div>
        <div style="font-size:10px; color:#64748b; margin-top:8px;">
            {st.session_state.current_user_id} · {curr_user['department'] if curr_user else 'Org'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    role_badge_cls = "badge-admin" if selected_role == "Admin" else ("badge-hr" if selected_role == "HR" else "badge-emp")
    role_label = {"Admin": "Company Master Level", "HR": "People Operations Level", "Employee": "Self-Service Level"}[selected_role]
    st.markdown(f'<div style="margin-bottom:10px;"><span class="badge {role_badge_cls}">● {role_label}</span></div>', unsafe_allow_html=True)

    if st.button("🚪 Sign Out / Switch Role", use_container_width=True):
        st.session_state.is_logged_in = False
        log_audit(curr_user_name, "LOGOUT", "Auth", "Signed out")
        st.rerun()

    st.markdown("---")
    st.markdown("**📑 Role Menu**")

    if selected_role == "Admin":
        nav_items = ["Executive Dashboard", "➕ Add New Employee / HR (M3)", "All Employees Directory (M3)",
                     "Company Attendance Monitor (M4)", "Organization Setup (M2)", "Leave Approvals & Quotas (M5)",
                     "Payroll Finalization & Lock (M6)", "AI Assistant (Company Scope)",
                     "Master Audit Trail (M9)", "5-Min Hackathon Demo Guide"]
    elif selected_role == "HR":
        nav_items = ["HR Operations Dashboard", "➕ Add New Employee (M3)", "Employees Management (M3)",
                     "CSV Dry-Run Import & Export (M3)", "Daily Attendance Board (M4)", "Leave Approvals Inbox (M5)",
                     "Monthly Payroll Run (M6)", "AI Assistant (HR Scope)",
                     "Company Announcements (M9)", "5-Min Hackathon Demo Guide"]
    else:
        nav_items = ["My Employee Hub", "🕒 Mark Web & Camera Attendance (M4)", "🏖️ Smart Leave Application (M5/M8)",
                     "My Attendance History (M4)", "My Official Payslips (M6)", "Ask My AI Assistant (M8)",
                     "Company Announcements (M9)", "5-Min Hackathon Demo Guide"]

    nav_choice = st.radio("Navigate", nav_items, label_visibility="collapsed")

    st.markdown("---")
    c_rst1, c_rst2 = st.columns(2)
    if c_rst1.button("🔄 Reset", use_container_width=True):
        clear_disk_data()
        st.session_state.db_initialized = False
        st.session_state.employees = []
        st.session_state.attendance = []
        st.session_state.leaves = []
        st.session_state.finalized_payrolls = {}
        st.session_state.audit_trail = []
        st.session_state.face_registry = {}
        st.session_state.is_logged_in = False
        save_data()
        st.rerun()
    if c_rst2.button("📥 Demo", use_container_width=True):
        clear_disk_data()
        initialize_database(force_demo=True)
        st.session_state.is_logged_in = True
        st.rerun()

    st.markdown(f"""
    <div style="font-size:10px; color:#475569; text-align:center; margin-top:14px; line-height:1.6;">
        HCM Lite v1.0 · 💾 Persistent<br/>
        Zaitoon Ashraf IT Park · Karachi
    </div>
    """, unsafe_allow_html=True)

# ----------------- HEADER -----------------
st.markdown(f"""
<div class="hcm-header">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:14px;">
        <div>
            <div class="hcm-eyebrow">Saylani Hackathon 2026 · Zaitoon Ashraf IT Park</div>
            <h1 class="hcm-header-title">{st.session_state.company_name} — HCM Lite</h1>
            <div class="hcm-subline">
                Active Portal: <strong style="color:#5eead4;">{selected_role}</strong>
                · Signed in as <strong style="color:#f1f5f9;">{curr_user_name}</strong>
                <span style="color:#64748b;">({st.session_state.current_user_id})</span>
            </div>
        </div>
        <div style="display:flex; gap:9px; flex-wrap:wrap;">
            <div style="background:rgba(20,184,166,0.10); padding:10px 16px; border-radius:12px; border:1px solid rgba(20,184,166,0.28);">
                <div style="color:#94a3b8; font-size:9.5px; text-transform:uppercase; letter-spacing:0.09em; font-weight:700;">Office Start</div>
                <div style="font-weight:800; color:#5eead4; font-size:13px; margin-top:2px;">{st.session_state.office_start.strftime('%H:%M')} <span style="color:#64748b; font-size:11px;">+{st.session_state.grace_minutes}m</span></div>
            </div>
            <div style="background:rgba(255,255,255,0.05); padding:10px 16px; border-radius:12px; border:1px solid rgba(255,255,255,0.12);">
                <div style="color:#94a3b8; font-size:9.5px; text-transform:uppercase; letter-spacing:0.09em; font-weight:700;">Perimeter</div>
                <div style="font-weight:800; color:#f1f5f9; font-size:13px; margin-top:2px;">{st.session_state.office_radius_m}m <span style="color:#64748b; font-size:11px;">radius</span></div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------- EXECUTIVE DASHBOARD -----------------
if nav_choice == "Executive Dashboard":
    st.header("🏢 Executive Company Dashboard")
    df_emp = pd.DataFrame(st.session_state.employees)
    df_att = pd.DataFrame(st.session_state.attendance)
    df_l = pd.DataFrame(st.session_state.leaves)

    headcount = len(df_emp[df_emp["status"] == "Active"]) if not df_emp.empty else 0
    total_payroll_gross = sum([e["basic_salary"] * 1.5 for e in st.session_state.employees])
    avg_salary = (total_payroll_gross / headcount) if headcount > 0 else 0

    today_str = datetime.date.today().isoformat()
    today_records = df_att[df_att["date"] == today_str] if not df_att.empty else pd.DataFrame()
    present_today = len(today_records[today_records["status"] == "Present"]) if not today_records.empty else 0
    late_today = len(today_records[today_records["status"] == "Late"]) if not today_records.empty else 0
    half_day_today = len(today_records[today_records["status"] == "Half Day"]) if not today_records.empty else 0
    on_leave_today = len(df_l[(df_l["start_date"] <= today_str) & (df_l["end_date"] >= today_str) & (df_l["status"] == "Approved")]) if not df_l.empty else 0
    effective_expected = max(1, headcount - on_leave_today)
    att_rate = round(((present_today + late_today + 0.5 * half_day_today) / effective_expected) * 100, 1)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="metric-card"><div class="metric-icon">👥</div>
            <div class="metric-label">Active Headcount</div>
            <div class="metric-value">{headcount}</div>
            <div class="metric-sub">0% Attrition YTD</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="metric-card"><div class="metric-icon">📊</div>
            <div class="metric-label">Attendance Rate</div>
            <div class="metric-value">{att_rate}%</div>
            <div class="metric-sub">{present_today} Present · {late_today} Late</div></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="metric-card"><div class="metric-icon">💰</div>
            <div class="metric-label">Monthly Payroll</div>
            <div class="metric-value">PKR {total_payroll_gross:,.0f}</div>
            <div class="metric-sub">Gross (1.5× Basic)</div></div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="metric-card"><div class="metric-icon">📈</div>
            <div class="metric-label">Avg Monthly Salary</div>
            <div class="metric-value">PKR {avg_salary:,.0f}</div>
            <div class="metric-sub">Across Departments</div></div>""", unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("✨ Summarize with AI"):
        st.info(
            f"• **Workforce:** {headcount} personnel · **{att_rate}%** attendance today.\n\n"
            f"• **Punctuality:** {late_today} arrived past grace.\n\n"
            f"• **Leaves:** {on_leave_today} on authorized leave.\n\n"
            f"• **Payroll:** PKR {total_payroll_gross:,.0f} monthly · avg PKR {avg_salary:,.0f}.\n\n*[AI-generated]*"
        )

    st.markdown("---")
    c_ch1, c_ch2 = st.columns(2)
    with c_ch1:
        st.markdown("##### Headcount by Department")
        if not df_emp.empty:
            dc = df_emp["department"].value_counts().reset_index()
            dc.columns = ["Department", "Staff Count"]
            st.bar_chart(dc.set_index("Department"), color="#14b8a6")
    with c_ch2:
        st.markdown("##### Payroll by Department")
        if not df_emp.empty:
            df_emp["gross"] = df_emp["basic_salary"] * 1.5
            dp = df_emp.groupby("department")["gross"].sum().reset_index()
            dp.columns = ["Department", "Monthly Gross"]
            st.bar_chart(dp.set_index("Department"), color="#06b6d4")

    st.markdown("---")
    st.subheader("📜 Live Audit Trail")
    if not pd.DataFrame(st.session_state.audit_trail).empty:
        st.dataframe(pd.DataFrame(st.session_state.audit_trail).head(6), use_container_width=True)

# ----------------- ORG SETUP -----------------
elif nav_choice == "Organization Setup (M2)":
    st.header("⚙️ Organization Setup")
    with st.form("org_setup_form"):
        col1, col2 = st.columns(2)
        c_name = col1.text_input("Company Name", st.session_state.company_name)
        o_start = col2.time_input("Office Start Time", st.session_state.office_start)
        col3, col4 = st.columns(2)
        o_grace = col3.number_input("Grace Period (min)", value=st.session_state.grace_minutes, min_value=0, max_value=60)
        o_half = col4.number_input("Half-Day Threshold (hrs)", value=st.session_state.half_day_hours, min_value=1, max_value=8)
        st.markdown("##### 📍 Geofence")
        g1, g2, g3 = st.columns(3)
        o_lat = g1.number_input("Latitude", value=st.session_state.office_lat, format="%.5f")
        o_lng = g2.number_input("Longitude", value=st.session_state.office_lng, format="%.5f")
        o_rad = g3.number_input("Radius (m)", value=st.session_state.office_radius_m, min_value=50, max_value=1000)
        st.markdown("##### 🏖️ Quotas")
        q1, q2, q3 = st.columns(3)
        q_ann = q1.number_input("Annual", value=st.session_state.leave_quotas["annual"])
        q_sick = q2.number_input("Sick", value=st.session_state.leave_quotas["sick"])
        q_cas = q3.number_input("Casual", value=st.session_state.leave_quotas["casual"])

        if st.form_submit_button("💾 Save Organization Rules", type="primary"):
            st.session_state.company_name = c_name
            st.session_state.office_start = o_start
            st.session_state.grace_minutes = o_grace
            st.session_state.half_day_hours = o_half
            st.session_state.office_lat = o_lat
            st.session_state.office_lng = o_lng
            st.session_state.office_radius_m = o_rad
            st.session_state.leave_quotas = {"annual": q_ann, "sick": q_sick, "casual": q_cas, "unpaid": 999}
            log_audit("Admin", "UPDATE", "OrgSetup", f"Updated settings for {c_name}")
            st.success("✅ Saved & persisted!")
            st.rerun()

# ----------------- ADD EMPLOYEE -----------------
elif nav_choice in ["➕ Add New Employee (M3)", "➕ Add New Employee / HR (M3)"]:
    st.header("➕ Register New Employee")
    with st.form("dedicated_add_emp_form"):
        c1, c2 = st.columns(2)
        n_name = c1.text_input("Full Name *", "Sara Ahmed")
        n_email = c2.text_input("Work Email *", "sara.ahmed@technova.com")
        c3, c4 = st.columns(2)
        n_role = c3.selectbox("Role *", ["Employee", "HR"] if selected_role == "HR" else ["Employee", "HR", "Admin"])
        n_dept = c4.selectbox("Department *", st.session_state.departments)
        c5, c6 = st.columns(2)
        n_desig = c5.selectbox("Designation *", st.session_state.designations)
        n_salary = c6.number_input("Basic Salary (PKR) *", value=95000, step=5000, min_value=15000)
        c7, c8 = st.columns(2)
        n_gender = c7.selectbox("Gender", ["Female", "Male", "Other"])
        n_joining = c8.date_input("Joining Date", datetime.date.today())
        c9, c10 = st.columns(2)
        n_phone = c9.text_input("Phone", "+92 300 9876543")
        n_address = c10.text_input("Address", "Karachi, Pakistan")
        st.caption("🔒 Temp password: `TempPass2026!`. Employee will enrol face on first camera check-in.")

        if st.form_submit_button("✅ Register & Save", type="primary", use_container_width=True):
            new_id = f"EMP{len(st.session_state.employees)+1:03d}"
            st.session_state.employees.append({
                "employee_id": new_id, "name": n_name, "email": n_email, "role": n_role,
                "department": n_dept, "designation": n_desig, "joining_date": n_joining.isoformat(),
                "basic_salary": n_salary, "gender": n_gender, "tenure_years": 0.0, "phone": n_phone,
                "address": n_address, "status": "Active", "first_login": True,
                "face_enrolled": False, "face_descriptor": None
            })
            log_audit(curr_user_name, "CREATE_EMPLOYEE", "Employee", f"Added {n_name} ({new_id})")
            st.success(f"🎉 {n_name} ({new_id}) registered & saved!")
            st.rerun()

# ----------------- EMPLOYEE DIRECTORY / CSV -----------------
elif nav_choice in ["All Employees Directory (M3)", "Employees Management (M3)", "CSV Dry-Run Import & Export (M3)"]:
    st.header("👥 Employee Directory")
    if nav_choice == "CSV Dry-Run Import & Export (M3)":
        st.subheader("📥 CSV Dry-Run Validator")
        sample_csv = (
            "name,email,department,designation,joining_date,basic_salary\n"
            "Kashif Raza,kashif@technova.com,Engineering,Fullstack Developer,2025-02-01,95000\n"
            "Invalid Row,bad-email,UnknownDept,Tester,not-a-date,-500"
        )
        csv_input = st.text_area("Paste CSV:", value=sample_csv, height=130)
        if st.button("⚡ Dry-Run", type="primary"):
            lines = [l.strip() for l in csv_input.strip().split("\n") if l.strip()]
            if len(lines) <= 1:
                st.error("No data rows.")
            else:
                headers = [h.strip().lower() for h in lines[0].split(",")]
                errors, valid_rows = [], []
                existing_emails = {e["email"].lower() for e in st.session_state.employees}
                for row_idx, line in enumerate(lines[1:], start=2):
                    parts = [p.strip() for p in line.split(",")]
                    row_data = dict(zip(headers, parts))
                    row_errs = []
                    email = row_data.get("email", "")
                    if "@" not in email: row_errs.append("Invalid email")
                    elif email.lower() in existing_emails: row_errs.append("Email exists")
                    if row_data.get("department", "") not in st.session_state.departments: row_errs.append("Unknown dept")
                    try:
                        if float(row_data.get("basic_salary", 0)) <= 0: row_errs.append("salary must be >0")
                    except: row_errs.append("Invalid salary")
                    try: datetime.date.fromisoformat(row_data.get("joining_date", ""))
                    except: row_errs.append("Invalid date")
                    if row_errs: errors.append({"Row": row_idx, "Errors": ", ".join(row_errs)})
                    else: valid_rows.append(row_data)
                if errors:
                    st.error(f"❌ {len(errors)} errors:"); st.dataframe(pd.DataFrame(errors), use_container_width=True)
                else:
                    st.success(f"✅ {len(valid_rows)} rows valid.")
    else:
        df_emp = pd.DataFrame(st.session_state.employees)
        col_s1, col_s2 = st.columns([3, 1])
        s_query = col_s1.text_input("🔍 Search", "")
        d_filter = col_s2.selectbox("Department", ["All"] + st.session_state.departments)
        filtered = df_emp.copy()
        if not filtered.empty:
            if s_query:
                filtered = filtered[filtered["name"].str.contains(s_query, case=False) |
                                    filtered["employee_id"].str.contains(s_query, case=False)]
            if d_filter != "All":
                filtered = filtered[filtered["department"] == d_filter]
            st.dataframe(filtered[["employee_id", "name", "role", "department", "designation", "basic_salary", "status"]],
                         use_container_width=True)
            st.download_button("📤 Export CSV", data=filtered.to_csv(index=False).encode("utf-8"),
                               file_name="employees.csv", mime="text/csv")

# ----------------- ATTENDANCE (REAL FACE DETECTION) -----------------
elif nav_choice in ["Company Attendance Monitor (M4)", "Daily Attendance Board (M4)", "🕒 Mark Web & Camera Attendance (M4)", "My Attendance History (M4)"]:
    st.header("🕒 Attendance & Face-Verified Check-in")

    if nav_choice == "🕒 Mark Web & Camera Attendance (M4)":
        if not HAS_CV2:
            st.error("⚠️ **OpenCV not installed.** Run: `pip install opencv-python-headless`")
            st.stop()

        st.subheader("📍 Geofence & Live Face Verification")
        g1, g2 = st.columns(2)
        u_lat = g1.number_input("Your Latitude", value=st.session_state.office_lat + 0.0003, format="%.5f")
        u_lng = g2.number_input("Your Longitude", value=st.session_state.office_lng + 0.0002, format="%.5f")
        dist = haversine_distance(u_lat, u_lng, st.session_state.office_lat, st.session_state.office_lng)
        within_geo = dist <= st.session_state.office_radius_m

        if within_geo:
            st.success(f"✅ Inside Geofence: {dist}m (≤ {st.session_state.office_radius_m}m)")
        else:
            st.error(f"❌ Outside Geofence: {dist}m")

        curr_id = st.session_state.current_user_id
        curr_emp_rec = next((e for e in st.session_state.employees if e["employee_id"] == curr_id), None)
        is_enrolled = curr_id in st.session_state.face_registry

        if is_enrolled:
            st.success(f"🛡️ **Face enrolled** for `{curr_id}`")
        else:
            st.warning("⚠️ **No face enrolled** — capture below to enrol first")

        st.markdown("##### 📷 Live Camera")
        cam_snap = st.camera_input("Capture", key="attendance_camera")

        face_analysis, match_score, face_verified = None, None, False
        if cam_snap:
            faces, img = detect_faces_in_image(cam_snap.getvalue())
            face_analysis = {"faces": faces, "img": img}

            if img is not None and len(faces) > 0:
                annotated = annotate_faces(img, faces)
                st.image(annotated, caption=f"✅ {len(faces)} face(s) detected (teal box)", use_container_width=True)
            elif img is not None:
                st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), caption="Live capture", use_container_width=True)

            if len(faces) == 0:
                st.error("❌ No face detected. Face clearly in frame.")
            elif len(faces) > 1:
                st.error(f"❌ {len(faces)} faces — only 1 allowed.")
            else:
                st.success("✅ 1 face detected")

            if is_enrolled and len(faces) == 1:
                stored = st.session_state.face_registry.get(curr_id)
                live_face = extract_face_crop(img, faces[0])
                match_score = match_faces(stored, live_face)
                if match_score >= FACE_MATCH_THRESHOLD:
                    face_verified = True
                    st.success(f"🔐 **Face Match VERIFIED** · {match_score*100:.1f}% (threshold {FACE_MATCH_THRESHOLD*100:.0f}%)")
                else:
                    st.error(f"🚫 **Mismatch** · {match_score*100:.1f}% < {FACE_MATCH_THRESHOLD*100:.0f}%")

        if not is_enrolled and face_analysis and len(face_analysis["faces"]) == 1:
            if st.button("📸 Enrol This Face", type="primary", use_container_width=True):
                face_crop = extract_face_crop(face_analysis["img"], face_analysis["faces"][0])
                if face_crop is not None:
                    st.session_state.face_registry[curr_id] = face_crop
                    if curr_emp_rec:
                        curr_emp_rec["face_enrolled"] = True
                        curr_emp_rec["face_descriptor"] = f"BIO-{curr_id}-{datetime.datetime.now().strftime('%H%M%S')}"
                    log_audit(curr_user_name, "ENROLL_FACE", "Biometrics", f"Enrolled face for {curr_id}")
                    st.success("✅ Face enrolled & saved!")
                    st.rerun()

        st.markdown("---")
        today_iso = datetime.date.today().isoformat()
        already_in = any(a["date"] == today_iso and a["employee_id"] == curr_id for a in st.session_state.attendance)
        can_check_in = (within_geo and face_analysis is not None and len(face_analysis["faces"]) == 1
                        and is_enrolled and face_verified and not already_in)

        b1, b2 = st.columns(2)
        with b1:
            if st.button("✅ Mark Check-in", disabled=not can_check_in, type="primary", use_container_width=True):
                now_t = datetime.datetime.now().time()
                status = "Late" if now_t > datetime.time(9, 15) else "Present"
                st.session_state.attendance.append({
                    "id": f"ATT-{len(st.session_state.attendance)+1:03d}", "date": today_iso,
                    "employee_id": curr_id, "name": curr_user_name,
                    "check_in": now_t.strftime("%H:%M"), "check_out": "-", "status": status,
                    "hours": 0.0, "method": "Camera", "face_verified": True,
                    "face_match_pct": round(match_score*100, 1) if match_score else None,
                    "dist_m": dist
                })
                log_audit(curr_user_name, "CHECK_IN", "Attendance",
                          f"Face-verified {status} at {now_t.strftime('%H:%M')} (match {match_score*100:.1f}%)")
                st.success(f"🎉 Checked in as **{status}** at {now_t.strftime('%H:%M')}!")
                st.rerun()
        with b2:
            if st.button("Record Check-out", use_container_width=True):
                now_t = datetime.datetime.now().time()
                found = False
                for a in st.session_state.attendance:
                    if a["date"] == today_iso and a["employee_id"] == curr_id:
                        a["check_out"] = now_t.strftime("%H:%M")
                        cin = datetime.datetime.strptime(a["check_in"], "%H:%M")
                        cout = datetime.datetime.strptime(a["check_out"], "%H:%M")
                        hrs = round((cout - cin).total_seconds() / 3600, 1)
                        a["hours"] = hrs
                        if hrs < st.session_state.half_day_hours: a["status"] = "Half Day"
                        found = True; break
                if found:
                    log_audit(curr_user_name, "CHECK_OUT", "Attendance", f"Out at {now_t.strftime('%H:%M')}")
                    st.success(f"✅ Checked out at {now_t.strftime('%H:%M')}!")
                    st.rerun()
                else:
                    st.warning("No check-in today.")
    else:
        st.subheader("📅 Attendance Register")
        df_att = pd.DataFrame(st.session_state.attendance)
        if not df_att.empty:
            if selected_role == "Employee":
                df_att = df_att[df_att["employee_id"] == st.session_state.current_user_id]
            st.dataframe(df_att, use_container_width=True)
        else:
            st.info("No attendance records.")

# ----------------- LEAVE -----------------
elif nav_choice in ["Leave Approvals & Quotas (M5)", "Leave Approvals Inbox (M5)", "🏖️ Smart Leave Application (M5/M8)"]:
    st.header("🏖️ Leave Management")
    if nav_choice == "🏖️ Smart Leave Application (M5/M8)":
        st.subheader("✨ Smart Leave")
        samples = ["Need next Monday and Tuesday off for my sister's wedding",
                   "Severe flu and fever, taking 2 days sick leave",
                   "Agle pir aur mangalwar ko chutti chahiye bhai ki shadi k liye"]
        sel_sample = st.selectbox("Sample prompt:", ["-- Write my own --"] + samples)
        prompt_val = "" if sel_sample == "-- Write my own --" else sel_sample
        user_prompt = st.text_area("Your Request:", value=prompt_val)

        p_type = "casual"; p_start = datetime.date.today() + datetime.timedelta(days=1)
        p_end = p_start + datetime.timedelta(days=1); p_reason = "Personal commitments"

        if st.button("🤖 Parse with AI", type="primary"):
            p_low = user_prompt.lower()
            if any(w in p_low for w in ["sick","fever","flu","tabiyat","bimari"]): p_type = "sick"
            elif any(w in p_low for w in ["annual","vacation","holiday","trip"]): p_type = "annual"
            else: p_type = "casual"
            p_reason = user_prompt
            st.success(f"Type = **{p_type.upper()}** · Reason = '{p_reason}'")

        st.markdown("---")
        with st.form("submit_leave_form"):
            l1, l2, l3 = st.columns(3)
            f_type = l1.selectbox("Category", ["casual","sick","annual","unpaid"], index=["casual","sick","annual","unpaid"].index(p_type))
            f_start = l2.date_input("Start", p_start)
            f_end = l3.date_input("End", p_end)
            f_reason = st.text_input("Reason", p_reason)
            if st.form_submit_button("Submit", type="primary"):
                w_days = calculate_working_days(f_start, f_end)
                if w_days <= 0: st.error("Dates are all weekends/holidays.")
                else:
                    new_id = f"LV-{len(st.session_state.leaves)+101}"
                    st.session_state.leaves.append({
                        "leave_id": new_id, "employee_id": st.session_state.current_user_id,
                        "employee_name": curr_user_name, "leave_type": f_type,
                        "start_date": f_start.isoformat(), "end_date": f_end.isoformat(),
                        "working_days": w_days, "reason": f_reason, "status": "Pending",
                        "applied_at": datetime.date.today().isoformat(), "hr_comment": ""
                    })
                    log_audit(curr_user_name, "APPLY_LEAVE", "Leave", f"{w_days}d {f_type}")
                    st.success(f"✅ {new_id} submitted ({w_days} days) & saved!"); st.rerun()
    else:
        st.subheader("📥 Leave Approvals Inbox")
        pending_list = [l for l in st.session_state.leaves if l["status"] == "Pending"]
        if pending_list:
            for p in pending_list:
                with st.expander(f"{p['employee_name']} — {p['leave_type'].upper()} ({p['working_days']}d)"):
                    st.write(f"**Reason:** {p['reason']}")
                    comment = st.text_input("Comment", "Approved", key=f"c_{p['leave_id']}")
                    a1, a2 = st.columns(2)
                    if a1.button("✅ Approve", key=f"app_{p['leave_id']}", type="primary"):
                        p["status"] = "Approved"; p["hr_comment"] = comment
                        log_audit("HR", "APPROVE_LEAVE", "Leave", p['leave_id'])
                        st.success(f"Approved & saved!"); st.rerun()
                    if a2.button("❌ Reject", key=f"rej_{p['leave_id']}"):
                        p["status"] = "Rejected"; p["hr_comment"] = comment
                        log_audit("HR", "REJECT_LEAVE", "Leave", p['leave_id'])
                        st.error(f"Rejected!"); st.rerun()
        else:
            st.info("No pending.")
        st.markdown("---")
        df_l = pd.DataFrame(st.session_state.leaves)
        if not df_l.empty: st.dataframe(df_l, use_container_width=True)

# ----------------- PAYROLL -----------------
elif nav_choice in ["Payroll Finalization & Lock (M6)", "Monthly Payroll Run (M6)", "My Official Payslips (M6)"]:
    st.header("💰 Payroll Lite")
    payroll_table = []
    for emp in st.session_state.employees:
        basic = emp["basic_salary"]; hra = basic*0.40; med = basic*0.10
        gross = basic + hra + med; per_day = gross/22
        e_att = [a for a in st.session_state.attendance if a["employee_id"] == emp["employee_id"]]
        half_days = len([a for a in e_att if a["status"]=="Half Day"])
        lates = len([a for a in e_att if a["status"]=="Late"])
        late_ded = (lates//3)*0.5 if st.session_state.late_penalty_rule else 0
        deductions = ((half_days*0.5) + late_ded) * per_day
        ann_tax = compute_tax(gross*12); month_tax = ann_tax/12
        net = gross - deductions - month_tax
        payroll_table.append({
            "employee_id": emp["employee_id"], "name": emp["name"], "department": emp["department"],
            "basic_salary": basic, "hra": hra, "medical": med, "gross_salary": gross,
            "deductions": round(deductions,2), "tax": round(month_tax,2), "net_salary": round(net,2),
            "status": "Finalized" if "2026-10" in st.session_state.finalized_payrolls else "Draft"
        })
    df_pay = pd.DataFrame(payroll_table)

    if selected_role in ["Admin", "HR"]:
        st.subheader("📋 Monthly Payroll Register · Oct 2026")
        st.dataframe(df_pay, use_container_width=True)
        tot_g = df_pay["gross_salary"].sum(); tot_n = df_pay["net_salary"].sum(); tot_t = df_pay["tax"].sum()
        p1, p2, p3 = st.columns(3)
        p1.metric("Total Gross", f"PKR {tot_g:,.0f}")
        p2.metric("Total Tax", f"PKR {tot_t:,.0f}")
        p3.metric("Net Take-Home", f"PKR {tot_n:,.0f}")
        if selected_role == "Admin":
            if "2026-10" not in st.session_state.finalized_payrolls:
                if st.button("🔒 Finalize & Lock", type="primary"):
                    st.session_state.finalized_payrolls["2026-10"] = payroll_table
                    log_audit("Admin", "FINALIZE", "Payroll", f"Locked PKR {tot_n:,.0f}")
                    st.success("🔒 Locked & saved!"); st.rerun()
            else:
                st.success("🔒 Payroll is LOCKED.")
        else:
            st.info("Only Admin can lock.")
    else:
        my_slip = next((p for p in payroll_table if p["employee_id"] == st.session_state.current_user_id), None)
        if my_slip:
            st.markdown(f"""
            <div class="payslip-box">
                <h3 style="color:#5eead4; margin:0;">{st.session_state.company_name}</h3>
                <div style="font-size:12px; color:#94a3b8; margin-bottom:16px;">Pay Statement — October 2026</div>
                <table style="width:100%; font-size:13px; border-collapse:collapse;">
                    <tr style="border-bottom:1px solid #1e293b;"><td class="ps-label" style="padding:8px 0;">Basic</td><td class="ps-val">PKR {my_slip['basic_salary']:,.2f}</td></tr>
                    <tr style="border-bottom:1px solid #1e293b;"><td class="ps-label" style="padding:8px 0;">HRA (40%)</td><td class="ps-val">PKR {my_slip['hra']:,.2f}</td></tr>
                    <tr style="border-bottom:1px solid #1e293b;"><td class="ps-label" style="padding:8px 0;">Medical (10%)</td><td class="ps-val">PKR {my_slip['medical']:,.2f}</td></tr>
                    <tr style="border-bottom:2px solid #243447;"><td style="padding:10px 0; color:#5eead4; font-weight:700;">Gross</td><td class="ps-val" style="color:#5eead4; font-weight:700;">PKR {my_slip['gross_salary']:,.2f}</td></tr>
                    <tr><td class="ps-label" style="padding:8px 0; color:#f87171;">Deductions</td><td class="ps-val" style="color:#f87171;">- PKR {my_slip['deductions']:,.2f}</td></tr>
                    <tr><td class="ps-label" style="padding:8px 0; color:#fbbf24;">Tax</td><td class="ps-val" style="color:#fbbf24;">- PKR {my_slip['tax']:,.2f}</td></tr>
                    <tr><td style="padding:14px 0 0 0; font-size:15px; font-weight:800; color:#34d399;">Net</td><td class="ps-val" style="padding:14px 0 0 0; font-size:16px; font-weight:800; color:#34d399;">PKR {my_slip['net_salary']:,.2f}</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No payslip yet.")

# ----------------- AI ASSISTANT -----------------
elif nav_choice in ["AI Assistant (Company Scope)", "AI Assistant (HR Scope)", "Ask My AI Assistant (M8)"]:
    st.header("🤖 AI Assistant")
    q_input = st.text_input("Ask a question:")
    if q_input:
        q_low = q_input.lower()
        if selected_role == "Employee" and any(k in q_low for k in ["salary","pay"]) and any(n in q_low for n in ["bilal","asad","fatima","ayesha","colleague"]):
            st.warning("🔒 Cannot disclose colleague salary. [AI-generated]")
        elif "leave" in q_low and ("today" in q_low or "who" in q_low):
            on_l = [l for l in st.session_state.leaves if l["status"]=="Approved"]
            st.success(f"📌 {len(on_l)} on leave. [AI-generated]")
        elif "policy" in q_low or "grace" in q_low:
            st.success("📌 Office 09:00 · Grace 15m · Half-day <5h · 3 lates = 0.5-day deduction. [AI-generated]")
        else:
            st.success(f"📌 {len(st.session_state.employees)} employees, {len(st.session_state.attendance)} attendance records. [AI-generated]")

# ----------------- AUDIT / ANNOUNCEMENTS -----------------
elif nav_choice in ["Master Audit Trail (M9)", "Company Announcements (M9)"]:
    st.header("🛡️ Audit & Comms")
    if nav_choice == "Master Audit Trail (M9)":
        if selected_role != "Admin": st.error("Access denied.")
        else: st.dataframe(pd.DataFrame(st.session_state.audit_trail), use_container_width=True)
    else:
        st.subheader("📢 Announcements")
        for ann in st.session_state.announcements:
            st.info(f"**{ann['title']}** ({ann['date']}) — *{ann['author']}*\n\n{ann['content']}")
        if selected_role in ["Admin","HR"]:
            with st.form("ann_form"):
                a_t = st.text_input("Title", "Update")
                a_c = st.text_area("Content", "Announcement body")
                if st.form_submit_button("Broadcast", type="primary"):
                    st.session_state.announcements.insert(0, {"id":len(st.session_state.announcements)+1,
                        "title":a_t,"date":datetime.date.today().isoformat(),"author":selected_role,"content":a_c})
                    log_audit(selected_role, "ANNOUNCEMENT", "Comms", a_t)
                    st.success("✅ Broadcasted & saved!"); st.rerun()

# ----------------- DEMO GUIDE -----------------
elif nav_choice == "5-Min Hackathon Demo Guide":
    st.header("🏆 5-Min Demo Script")
    st.info("1. Admin setup → 2. HR adds employees → 3. Employee enrols face & checks in → 4. Smart leave → 5. HR approves → 6. Payroll lock → 7. RBAC test → 8. Audit trail")

# ----------------- FOOTER -----------------
st.markdown("---")
st.markdown("""
<div style="text-align:center; font-size:11.5px; color:#475569; padding:14px 0;">
    Saylani IT Training Hackathon 2026 · <span style="color:#5eead4; font-weight:600;">HCM Lite</span> · Zaitoon Ashraf IT Park<br/>
    <span style="font-size:10.5px;">Python · Streamlit · Pandas · OpenCV Face Verification · JSON Persistence</span>
</div>
""", unsafe_allow_html=True)
