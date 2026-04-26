"""
utils/database.py
-----------------
SQLite-based user management.
• PBKDF2-SHA256 password hashing (260,000 iterations + random salt)
• Role-based access: admin / user / guest
• Admin-key-protected admin account creation
• State-based hospital recommendations (5+ per state)
"""
import os, sqlite3, hashlib, secrets, csv, re, io
from datetime import datetime
import streamlit as st

ROOT     = os.path.dirname(os.path.dirname(__file__))
DB_PATH  = os.path.join(ROOT, "data", "ckd_users.db")
CSV_PATH = os.path.join(ROOT, "data", "patient_predictions.csv")
HOSP_CSV = os.path.join(ROOT, "data", "hospitals.csv")

# Admin creation secret key
ADMIN_SECRET_KEY = "CKD_ADMIN@2025"

# ── Password policy ────────────────────────────────────────────────────────────
def validate_password(pw: str) -> tuple:
    if len(pw) < 6:
        return False, "Password must be at least 6 characters."
    if not re.search(r'[A-Z]', pw):
        return False, "Must contain at least 1 uppercase letter (A-Z)."
    if not re.search(r'[a-z]', pw):
        return False, "Must contain at least 1 lowercase letter (a-z)."
    if not re.search(r'\d', pw):
        return False, "Must contain at least 1 number (0-9)."
    if not re.search(r'[!@#$%^&*()\-_=+\[\]{};:\'",.<>/?\\|`~]', pw):
        return False, "Must contain at least 1 special character (!@#$%...)."
    return True, ""

# ── Hashing ────────────────────────────────────────────────────────────────────
def hash_password(pw: str) -> str:
    salt = secrets.token_hex(16)
    key  = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 260000)
    return f"{salt}:{key.hex()}"

def verify_password(pw: str, stored: str) -> bool:
    try:
        salt, key_hex = stored.split(":", 1)
        key = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 260000)
        return secrets.compare_digest(key.hex(), key_hex)
    except Exception:
        return False

# ── DB init ────────────────────────────────────────────────────────────────────
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c    = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        contact TEXT, address TEXT, blood_group TEXT, gender TEXT,
        age INTEGER, city TEXT, state TEXT, pin TEXT,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")
    try:
        c.execute("ALTER TABLE users ADD COLUMN state TEXT")
        conn.commit()
    except Exception:
        pass
    c.execute("""CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id),
        timestamp TEXT,
        age_input REAL, bp REAL, specific_gravity REAL,
        albumin REAL, sugar REAL, blood_glucose REAL,
        blood_urea REAL, serum_creatinine REAL, sodium REAL,
        potassium REAL, hemoglobin REAL, packed_cell_volume REAL,
        wbc_count REAL, rbc_count REAL,
        red_blood_cells TEXT, pus_cells TEXT, pus_cell_clumps TEXT,
        bacteria TEXT, hypertension TEXT, diabetes TEXT,
        coronary_artery_disease TEXT, appetite TEXT, pedal_edema TEXT, anemia TEXT,
        risk_percent REAL, risk_level TEXT, stage TEXT, explanation TEXT, model_used TEXT)""")
    conn.commit()
    c.execute("SELECT id FROM users WHERE role='admin'")
    if not c.fetchone():
        c.execute("""INSERT OR IGNORE INTO users
            (patient_name,username,email,contact,address,blood_group,gender,age,city,state,pin,password_hash,role)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            ("System Admin","admin","admin@ckd.ai","9999999999","CKD HQ","O+",
             "Male",30,"New Delhi","Delhi","110001",hash_password("Admin@123"),"admin"))
        conn.commit()
    conn.close()

# ── User CRUD ──────────────────────────────────────────────────────────────────
def register_user(data: dict) -> tuple:
    init_db()
    ok, msg = validate_password(data.get("password",""))
    if not ok:
        return False, msg
    conn = sqlite3.connect(DB_PATH)
    c    = conn.cursor()
    try:
        c.execute("SELECT id FROM users WHERE LOWER(email)=?", (data["email"].lower(),))
        if c.fetchone():
            return False, "This email is already registered."
        c.execute("SELECT id FROM users WHERE LOWER(username)=?", (data["username"].lower(),))
        if c.fetchone():
            return False, "Username already taken."
        c.execute("""INSERT INTO users
            (patient_name,username,email,contact,address,blood_group,gender,age,city,state,pin,password_hash,role)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (data["patient_name"], data["username"].lower(), data["email"].lower(),
             data["contact"], data["address"], data["blood_group"], data["gender"],
             int(data["age"]), data["city"], data.get("state",""), data["pin"],
             hash_password(data["password"]), data.get("role","user")))
        conn.commit()
        return True, f"Account created! Welcome, {data['patient_name']}."
    except Exception as e:
        return False, f"Registration error: {e}"
    finally:
        conn.close()

def login_user(identifier: str, password: str) -> tuple:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM users WHERE LOWER(email)=? OR LOWER(username)=?",
                  (identifier.lower(), identifier.lower()))
        row = c.fetchone()
        if not row:
            return False, "No account found with this email or username.", None
        if not verify_password(password, row["password_hash"]):
            return False, "Incorrect password. Please try again.", None
        return True, "Login successful!", dict(row)
    finally:
        conn.close()

def get_user_by_id(user_id: int) -> dict:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def update_user_profile(user_id: int, data: dict) -> tuple:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("""UPDATE users SET patient_name=?,contact=?,address=?,
            blood_group=?,gender=?,age=?,city=?,state=?,pin=? WHERE id=?""",
            (data["patient_name"],data["contact"],data["address"],
             data["blood_group"],data["gender"],int(data["age"]),
             data["city"],data.get("state",""),data["pin"],user_id))
        conn.commit()
        return True, "Profile updated."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def change_password(user_id: int, old_pw: str, new_pw: str) -> tuple:
    ok, msg = validate_password(new_pw)
    if not ok:
        return False, msg
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    if not row or not verify_password(old_pw, row["password_hash"]):
        conn.close()
        return False, "Current password is incorrect."
    c.execute("UPDATE users SET password_hash=? WHERE id=?", (hash_password(new_pw), user_id))
    conn.commit()
    conn.close()
    return True, "Password changed successfully."

def get_all_users(role_filter: str = None) -> list:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if role_filter:
        c.execute("""SELECT id,patient_name,username,email,role,city,state,
            contact,blood_group,gender,age,created_at FROM users
            WHERE role=? ORDER BY id DESC""", (role_filter,))
    else:
        c.execute("""SELECT id,patient_name,username,email,role,city,state,
            contact,blood_group,gender,age,created_at FROM users ORDER BY id DESC""")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def delete_user(user_id: int) -> tuple:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("SELECT role FROM users WHERE id=?", (user_id,))
        row = c.fetchone()
        if not row:
            return False, "User not found."
        if row[0] == "admin":
            return False, "Cannot delete an admin account from here."
        c.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        return True, "User deleted."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# ── Predictions ────────────────────────────────────────────────────────────────
def save_prediction(user_id: int, patient_data: dict, result: dict, model_used: str = "") -> int:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c    = conn.cursor()
    pd_  = patient_data
    ts   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""INSERT INTO predictions
        (user_id,timestamp,age_input,bp,specific_gravity,albumin,sugar,
         blood_glucose,blood_urea,serum_creatinine,sodium,potassium,hemoglobin,
         packed_cell_volume,wbc_count,rbc_count,red_blood_cells,pus_cells,
         pus_cell_clumps,bacteria,hypertension,diabetes,coronary_artery_disease,
         appetite,pedal_edema,anemia,risk_percent,risk_level,stage,explanation,model_used)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (user_id,ts,
         pd_.get("Age"),pd_.get("BloodPressure"),pd_.get("SpecificGravity"),
         pd_.get("Albumin"),pd_.get("Sugar"),pd_.get("BloodGlucose"),
         pd_.get("BloodUrea"),pd_.get("SerumCreatinine"),pd_.get("Sodium"),
         pd_.get("Potassium"),pd_.get("Hemoglobin"),pd_.get("PackedCellVolume"),
         pd_.get("WBCCount"),pd_.get("RBCCount"),
         pd_.get("RedBloodCells"),pd_.get("PusCells"),pd_.get("PusCellClumps"),
         pd_.get("Bacteria"),pd_.get("Hypertension"),pd_.get("DiabetesMellitus"),
         pd_.get("CoronaryArteryDisease"),pd_.get("Appetite"),
         pd_.get("PedalEdema"),pd_.get("Anemia"),
         result.get("risk_percent"),result.get("risk_level"),
         result.get("stage"),result.get("explanation_text"),model_used))
    conn.commit()
    pred_id = c.lastrowid
    conn.close()
    _append_to_csv(pred_id, user_id, ts, pd_, result, model_used)
    return pred_id

def get_user_predictions(user_id: int) -> list:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM predictions WHERE user_id=? ORDER BY timestamp DESC", (user_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_all_predictions() -> list:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""SELECT p.*, u.patient_name,u.username,u.email,u.city,u.state
        FROM predictions p LEFT JOIN users u ON p.user_id=u.id
        ORDER BY p.timestamp DESC""")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_analytics_db() -> dict:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM predictions"); total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM predictions WHERE risk_level='High Risk'"); high = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM predictions WHERE risk_level='Moderate Risk'"); mod = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM predictions WHERE risk_level='Low Risk'"); low = c.fetchone()[0]
    c.execute("SELECT AVG(risk_percent) FROM predictions"); avg_r = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM users WHERE role='user'"); users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE role='admin'"); admins = c.fetchone()[0]
    conn.close()
    return {"total":total,"high":high,"moderate":mod,"low":low,
            "avg_risk":round(avg_r,1),"high_pct":round(high/total*100,1) if total else 0,
            "total_users":users,"total_admins":admins}

# ── CSV helpers ────────────────────────────────────────────────────────────────
CSV_HEADERS = ["ID","UserID","PatientName","Email","State","City","Timestamp",
    "Age","BloodPressure","SpecificGravity","Albumin","Sugar","BloodGlucose","BloodUrea",
    "SerumCreatinine","Sodium","Potassium","Hemoglobin","PackedCellVolume","WBCCount","RBCCount",
    "RedBloodCells","PusCells","PusCellClumps","Bacteria","Hypertension","DiabetesMellitus",
    "CoronaryArteryDisease","Appetite","PedalEdema","Anemia",
    "RiskPercent","RiskLevel","Stage","Explanation","ModelUsed"]

def _append_to_csv(pred_id, user_id, ts, pd_, result, model):
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    write_header = not os.path.exists(CSV_PATH)
    user = get_user_by_id(user_id) or {}
    row  = [pred_id,user_id,user.get("patient_name",""),user.get("email",""),
            user.get("state",""),user.get("city",""),ts,
            pd_.get("Age"),pd_.get("BloodPressure"),pd_.get("SpecificGravity"),
            pd_.get("Albumin"),pd_.get("Sugar"),pd_.get("BloodGlucose"),
            pd_.get("BloodUrea"),pd_.get("SerumCreatinine"),pd_.get("Sodium"),
            pd_.get("Potassium"),pd_.get("Hemoglobin"),pd_.get("PackedCellVolume"),
            pd_.get("WBCCount"),pd_.get("RBCCount"),pd_.get("RedBloodCells"),
            pd_.get("PusCells"),pd_.get("PusCellClumps"),pd_.get("Bacteria"),
            pd_.get("Hypertension"),pd_.get("DiabetesMellitus"),pd_.get("CoronaryArteryDisease"),
            pd_.get("Appetite"),pd_.get("PedalEdema"),pd_.get("Anemia"),
            result.get("risk_percent"),result.get("risk_level"),
            result.get("stage"),result.get("explanation_text"),model]
    with open(CSV_PATH,"a",newline="",encoding="utf-8") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(CSV_HEADERS)
        w.writerow(row)

def predictions_as_dataset_csv() -> bytes:
    """Export predictions in same format as original CKD dataset."""
    preds = get_all_predictions()
    dataset_cols = ["PatientID","Age","BloodPressure","SpecificGravity","Albumin","Sugar",
        "RedBloodCells","PusCells","PusCellClumps","Bacteria","BloodGlucose","BloodUrea",
        "SerumCreatinine","Sodium","Potassium","Hemoglobin","PackedCellVolume","WBCCount","RBCCount",
        "Hypertension","DiabetesMellitus","CoronaryArteryDisease","Appetite","PedalEdema","Anemia","CKD"]
    rows = []
    for p in preds:
        ckd = "ckd" if p.get("risk_level") in ("High Risk","Moderate Risk") else "notckd"
        rows.append({"PatientID":p["id"],"Age":p.get("age_input",""),
            "BloodPressure":p.get("bp",""),"SpecificGravity":p.get("specific_gravity",""),
            "Albumin":p.get("albumin",""),"Sugar":p.get("sugar",""),
            "RedBloodCells":p.get("red_blood_cells",""),"PusCells":p.get("pus_cells",""),
            "PusCellClumps":p.get("pus_cell_clumps",""),"Bacteria":p.get("bacteria",""),
            "BloodGlucose":p.get("blood_glucose",""),"BloodUrea":p.get("blood_urea",""),
            "SerumCreatinine":p.get("serum_creatinine",""),"Sodium":p.get("sodium",""),
            "Potassium":p.get("potassium",""),"Hemoglobin":p.get("hemoglobin",""),
            "PackedCellVolume":p.get("packed_cell_volume",""),"WBCCount":p.get("wbc_count",""),
            "RBCCount":p.get("rbc_count",""),"Hypertension":p.get("hypertension",""),
            "DiabetesMellitus":p.get("diabetes",""),
            "CoronaryArteryDisease":p.get("coronary_artery_disease",""),
            "Appetite":p.get("appetite",""),"PedalEdema":p.get("pedal_edema",""),
            "Anemia":p.get("anemia",""),"CKD":ckd})
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=dataset_cols)
    w.writeheader(); w.writerows(rows)
    return buf.getvalue().encode()

# ── Hospital lookup ────────────────────────────────────────────────────────────
def _load_hospitals() -> list:
    if not os.path.exists(HOSP_CSV):
        return []
    with open(HOSP_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def get_hospitals_for_state(state: str, n: int = 5) -> list:
    hospitals = _load_hospitals()
    state_lower = (state or "").strip().lower()
    matched = [h for h in hospitals if h.get("State","").lower() == state_lower]
    if len(matched) < n:
        extra = [h for h in hospitals if h not in matched]
        extra.sort(key=lambda h: float(h.get("Rating",0)), reverse=True)
        matched += extra[:n - len(matched)]
    matched.sort(key=lambda h: float(h.get("Rating",0)), reverse=True)
    return matched[:max(n, 5)]

def get_hospitals_for_city_state(city: str, state: str = "", n: int = 5) -> list:
    hospitals = _load_hospitals()
    city_lower  = (city  or "").strip().lower()
    state_lower = (state or "").strip().lower()
    city_match  = [h for h in hospitals if city_lower and city_lower in h.get("City","").lower()]
    state_match = [h for h in hospitals
                   if state_lower and h.get("State","").lower() == state_lower and h not in city_match]
    result = city_match + state_match
    if len(result) < n:
        rest = [h for h in hospitals if h not in result]
        rest.sort(key=lambda h: float(h.get("Rating",0)), reverse=True)
        result += rest[:n - len(result)]
    result.sort(key=lambda h: float(h.get("Rating",0)), reverse=True)
    return result[:max(n, 5)]

# Backward compat alias
get_hospitals_for_city = get_hospitals_for_city_state

# ── Session ────────────────────────────────────────────────────────────────────
def init_session():
    import time
    defaults = {"logged_in":False,"user_id":None,"user_role":None,"user_info":None,
                "current_page":"Home","last_result":None,"last_patient":None,
                "last_activity_time":None}
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    init_db()

def logout():
    for k in ["logged_in","user_id","user_role","user_info","last_result",
              "last_patient","last_activity_time"]:
        st.session_state[k] = None if k!="logged_in" else False
    st.session_state["current_page"] = "Home"

def refresh_activity():
    import time
    st.session_state["last_activity_time"] = time.time()

def check_session_timeout(timeout_seconds: int = 120):
    import time
    if not st.session_state.get("logged_in"):
        return
    last = st.session_state.get("last_activity_time")
    if last is None:
        refresh_activity(); return
    if time.time() - last > timeout_seconds:
        logout()
        st.warning("⏱️ Session expired due to 2 minutes of inactivity. Please log in again.")
        st.rerun()

def get_display_name() -> str:
    info = st.session_state.get("user_info")
    return (info.get("patient_name") or info.get("username","User")) if info else "Guest"

def get_current_user() -> dict:
    return st.session_state.get("user_info")
