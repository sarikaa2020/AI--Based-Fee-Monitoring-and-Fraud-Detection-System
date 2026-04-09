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

# ---------------- BASIC ----------------
st.title("🎓 Smart AI Fee Tracking System")

# ---------------- TESSERACT ----------------
try:
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
except:
    st.warning("Tesseract not found")

# ---------------- FEE FUNCTION ----------------
def get_fees(category):
    if category == "Counselling":
        return {"Tuition": 50000, "Bus": 10000, "Training": 5000}
    elif category == "Management":
        return {"Tuition": 80000, "Bus": 15000, "Training": 8000}
    elif category == "Scholarship":
        return {"Exam": 2000}
    return {}

# ---------------- STUDENT STORAGE ----------------
if "students" not in st.session_state:
    st.session_state.students = []

st.subheader("➕ Add New Student")

with st.form("student_form"):
    name = st.text_input("Student Name")
    roll = st.text_input("Roll Number")
    category = st.selectbox("Category", ["Counselling", "Management", "Scholarship"])

    submitted = st.form_submit_button("Add Student")

    if submitted:
        if name and roll:
            st.session_state.students.append({
                "name": name,
                "roll": roll,
                "category": category
            })
            st.success("Student Added ✅")
        else:
            st.error("Fill all fields")

# ---------------- SELECT STUDENT ----------------
if not st.session_state.students:
    st.warning("⚠️ Add at least one student")
    st.stop()

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
    try:
        file_bytes = uploaded_file.read()

        np_arr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(np_arr, 1)

        pil_img = Image.open(io.BytesIO(file_bytes))

        st.image(img, width="stretch")

        text = pytesseract.image_to_string(img)

        st.subheader("📄 Extracted Text")
        st.text(text)

        # Amount detection
        amounts = re.findall(r'\d[\d,]*', text)

        detected_amount = max(
            [int(a.replace(",", "")) for a in amounts if 100 <= int(a.replace(",", "")) <= 100000],
            default=None
        )

        st.write("Detected Amount:", detected_amount)

        # TXN ID
        txn_ids = re.findall(r'(?:UTR|TXN|ID)?[:\s]*([A-Z0-9]{10,})', text)
        txn_id = txn_ids[0] if txn_ids else "Not Found"

        st.write("Transaction ID:", txn_id)

        # HASH
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

        # VALIDATION
        expected_amount = fees[selected_fee]

        st.subheader("🔍 Verification")

        if duplicate:
            st.error("🚫 Fraud: Duplicate Screenshot")
        elif detected_amount != expected_amount:
            st.warning("⚠️ Amount Mismatch")
        else:
            st.success("✅ Payment Verified")

            data = {
                "Name": student["name"],
                "Roll": student["roll"],
                "Fee": selected_fee,
                "Amount": detected_amount,
                "Txn ID": txn_id,
                "Status": "Paid"
            }

            df = pd.DataFrame([data])

            file_exists = os.path.isfile("records.csv")

            df.to_csv(
                "records.csv",
                mode="a",
                header=not file_exists,
                index=False
            )

    except Exception as e:
        st.error(f"Error: {e}")

# ---------------- DASHBOARD ----------------
st.subheader("📊 Mentor Dashboard")

try:
    df = pd.read_csv("records.csv")
    st.dataframe(df, width="stretch")
    st.success(f"Total Collection: ₹{df['Amount'].sum()}")
except:
    st.info("No records yet")