import streamlit as st
import pytesseract
import cv2
import numpy as np
import re
import pandas as pd
from PIL import Image
import imagehash
import json
import io
import os

st.set_page_config(layout="wide")

# ---------------- LOGIN ----------------
if "login" not in st.session_state:
    st.session_state.login = False

def login():
    st.title("🔐 Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "mentor" and pwd == "123":
            st.session_state.login = True
            st.success("Login Successful")
            st.rerun()
        else:
            st.error("Invalid login")

if not st.session_state.login:
    login()
    st.stop()

# ---------------- TITLE ----------------
st.title("🎓 Smart AI Fee Tracking System")

# ---------------- TESSERACT ----------------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------------- FEE FUNCTION ----------------
def get_fees(category):
    if category == "Counselling":
        return {"Tuition": 60000, "Bus": 40000, "Training": 25000}
    elif category == "Management":
        return {"Tuition": 80000, "Bus": 40000, "Training": 8000}
    elif category == "Scholarship":
        return {"Exam": 2000}
    return {}

# ---------------- STUDENTS ----------------
if "students" not in st.session_state:
    st.session_state.students = [
        {"name": "ABHINAND N", "roll": "711523BAM001", "category": "Management"},
        {"name": "ADITHYAN", "roll": "711523BAM002", "category": "Management"},
        {"name": "AJITH A I", "roll": "711523BAM003", "category": "Management"},
        {"name": "ALWAR SAMY", "roll": "711523BAM004", "category": "Management"},
        {"name": "AMRITHA VARSHINI M", "roll": "711523BAM006", "category": "Management"},
        {"name": "ANTONY BENATICT A", "roll": "711523BAM007", "category": "Management"},
        {"name": "ARCHSUNAND", "roll": "711523BAM008", "category": "Management"},
        {"name": "ATHULRAJ K K", "roll": "711523BAM009", "category": "Management"},
        {"name": "DAVID BACKAM S", "roll": "711523BAM010", "category": "Management"},
        {"name": "DAVID VENSILIN R", "roll": "711523BAM011", "category": "Management"},
        {"name": "DEEPAK V", "roll": "711523BAM012", "category": "Management"},
        {"name": "DHAANISH NIHAAL M", "roll": "711523BAM013", "category": "Management"},
        {"name": "DHANYATHAA", "roll": "711523BAM014", "category": "Management"},
        {"name": "DHARSHINI M", "roll": "711523BAM015", "category": "Management"},
        {"name": "DHINAKARAN M S", "roll": "711523BAM016", "category": "Management"},
        {"name": "ELANGO E", "roll": "711523BAM017", "category": "Management"},
        {"name": "ELSON BENANZAL", "roll": "711523BAM018", "category": "Management"},
        {"name": "ETHU KRISHNA S", "roll": "711523BAM019", "category": "Management"},
        {"name": "GIRIBALAN K", "roll": "711523BAM020", "category": "Management"},
        {"name": "GOWTHAMRAJ B", "roll": "711523BAM021", "category": "Management"},
        {"name": "HARISH V R", "roll": "711523BAM022", "category": "Management"},
        {"name": "HARISHWAR R", "roll": "711523BAM023", "category": "Management"},
        {"name": "HEMACHANDRAN D", "roll": "711523BAM024", "category": "Management"},
        {"name": "KAMALI J", "roll": "711523BAM025", "category": "Management"},
        {"name": "KARTHICK M", "roll": "711523BAM026", "category": "Management"},
        {"name": "KAVYA G", "roll": "711523BAM027", "category": "Management"},
        {"name": "MALATHI K", "roll": "711523BAM028", "category": "Management"},
        {"name": "MOHANKUMAR S", "roll": "711523BAM029", "category": "Management"},
        {"name": "MOHANRAJ S", "roll": "711523BAM030", "category": "Management"},
        {"name": "MONICA AISHWARYA R", "roll": "711523BAM031", "category": "Management"},
        {"name": "MUKESH KUMAR K", "roll": "711523BAM032", "category": "Management"},
        {"name": "NITHISH KUMAR N", "roll": "711523BAM034", "category": "Management"},
        {"name": "PANDI HARSHAN K", "roll": "711523BAM035", "category": "Management"},
        {"name": "PANDU RANG S", "roll": "711523BAM036", "category": "Management"},
        {"name": "PRADEEPAN L", "roll": "711523BAM037", "category": "Management"},
        {"name": "PRAKASH P", "roll": "711523BAM038", "category": "Management"},
        {"name": "PRIYANGA G", "roll": "711523BAM039", "category": "Management"},
        {"name": "RAGA T", "roll": "711523BAM040", "category": "Management"},
        {"name": "RUTHRAYINI M", "roll": "711523BAM041", "category": "Management"},
        {"name": "SACHIN D", "roll": "711523BAM042", "category": "Management"},
        {"name": "SANDHIYA V S", "roll": "711523BAM043", "category": "Management"},
        {"name": "SANJAI VEERAN S", "roll": "711523BAM044", "category": "Management"},
        {"name": "SANJAY S", "roll": "711523BAM045", "category": "Management"},
        {"name": "SARIKAA SHREE V", "roll": "711523BAM046", "category": "Management"},
        {"name": "SARVESH RAM A", "roll": "711523BAM047", "category": "Management"},
        {"name": "SATHYA R S", "roll": "711523BAM048", "category": "Management"},
        {"name": "SATHYA T", "roll": "711523BAM049", "category": "Management"},
        {"name": "SHADYA P", "roll": "711523BAM050", "category": "Management"},
        {"name": "SHANMUGAM A", "roll": "711523BAM051", "category": "Management"},
        {"name": "SILAMBARASAN K", "roll": "711523BAM052", "category": "Management"},
        {"name": "SRIDHARAN I", "roll": "711523BAM053", "category": "Management"},
        {"name": "SUDARSHAN P", "roll": "711523BAM054", "category": "Management"},
        {"name": "SUMAN M", "roll": "711523BAM055", "category": "Management"},
        {"name": "SURIYA T", "roll": "711523BAM056", "category": "Management"},
        {"name": "VIJAY E", "roll": "711523BAM057", "category": "Management"},
        {"name": "VIJAY PRASATH R", "roll": "711523BAM058", "category": "Management"},
        {"name": "VIKNESH T", "roll": "711523BAM059", "category": "Management"},
        {"name": "VISHAL RAJ", "roll": "711523BAM060", "category": "Management"},
        {"name": "VISWA S S", "roll": "711523BAM061", "category": "Management"},
        {"name": "YOGESH PRIYAN P", "roll": "711523BAM062", "category": "Management"},
        {"name": "YUVANRAJ K S", "roll": "711523BAM063", "category": "Management"},
        {"name": "GUNAL RAJA A", "roll": "711523BAM301", "category": "Management"},
        {"name": "PRATHAP P", "roll": "711523BAM302", "category": "Management"},
        {"name": "SABARISHWARAN", "roll": "711523BAM304", "category": "Management"},
        {"name": "SUKANT", "roll": "711523BAM305", "category": "Management"}
    ]

# ---------------- SELECT STUDENT ----------------
student_names = [s["name"] for s in st.session_state.students]
selected_name = st.selectbox("Select Student", student_names)

student = next(s for s in st.session_state.students if s["name"] == selected_name)

# ---------------- PROFILE ----------------
st.subheader("👤 Student Profile")
st.write(student)

fees = get_fees(student["category"])

st.subheader("💰 Fee Structure")
st.json(fees)

selected_fee = st.selectbox("Select Fee", list(fees.keys()))

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader("Upload Payment Screenshot")

if uploaded_file:
    file_bytes = uploaded_file.read()

    np_arr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(np_arr, 1)
    pil_img = Image.open(io.BytesIO(file_bytes))

    st.image(img, width="stretch")

    # OCR
    text = pytesseract.image_to_string(img)
    st.subheader("📄 Extracted Text")
    st.text(text)

    # ---------------- AMOUNT DETECTION ----------------
    amounts = re.findall(r'\d[\d,]*', text)

    clean_amounts = []
    for amt in amounts:
        try:
            val = int(amt.replace(",", ""))
            if 1000 <= val <= 100000:
                clean_amounts.append(val)
        except:
            pass

    detected_amount = max(clean_amounts) if clean_amounts else None
    st.write("Detected Amount:", detected_amount)

    # ---------------- TXN ID ----------------
    txn_ids = re.findall(r'(?:UTR|TXN|ID)?[:\s]*([A-Z0-9]{10,})', text)
    txn_id = txn_ids[0] if txn_ids else "Not Found"
    st.write("Transaction ID:", txn_id)

    # ---------------- HASH ----------------
    img_hash = str(imagehash.average_hash(pil_img))

    try:
        with open("hashes.json") as f:
            hashes = json.load(f)
    except:
        hashes = []

    duplicate = img_hash in hashes

    if not duplicate:
        hashes.append(img_hash)
        with open("hashes.json", "w") as f:
            json.dump(hashes, f)

    # ---------------- VERIFICATION ----------------
    expected_amount = fees[selected_fee]

    def is_close(a, b, tol=3000):
        return abs(a - b) <= tol

    st.subheader("🔍 Verification")

    if duplicate:
        st.error("🚫 Fraud: Duplicate Screenshot")

    elif detected_amount is None:
        st.error("❌ Could not detect amount")

    elif detected_amount > expected_amount + 3000:
        st.error("🚫 Fraud: Overpayment suspicious")

    else:
        if is_close(detected_amount, expected_amount):
            status = "Fully Paid"
            st.success("✅ Full Payment Verified")
        else:
            status = "Partially Paid"
            st.success("✅ Partial Payment Accepted")

        # ---------------- SAVE ----------------
        data = {
            "Name": student["name"],
            "Roll": student["roll"],
            "Fee": selected_fee,
            "Amount": detected_amount,
            "Txn ID": txn_id,
            "Status": status
        }

        df = pd.DataFrame([data])
        file_exists = os.path.isfile("records.csv")

        df.to_csv(
            "records.csv",
            mode="a",
            header=not file_exists,
            index=False
        )

# ---------------- DASHBOARD ----------------
st.subheader("📊 Mentor Dashboard")

try:
    df = pd.read_csv("records.csv")
    st.dataframe(df, width="stretch")
    st.success(f"Total Collection: ₹{df['Amount'].sum()}")
except:
    st.info("No records yet")