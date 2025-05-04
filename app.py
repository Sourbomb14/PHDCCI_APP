import os
import sqlite3
import streamlit as st
import streamlit_authenticator as stauth
from datetime import datetime
from PIL import Image

# Constants
DB_PATH = "data/users.db"
UPLOAD_FOLDER = "uploads/resumes/"

# Ensure required folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("data", exist_ok=True)

# Admin credentials
auth_users = {
    "admins": {
        "names": ["PHDCCI Admin", "NTTM Admin"],
        "usernames": ["phdcci", "nttm"],
        "passwords": ["phdcci123", "nttm123"]  # Plaintext for hashing
    },
    "students": {
        "names": ["Student"],
        "usernames": ["student"],
        "passwords": ["student123"]
    },
    "companies": {
        "names": ["Company"],
        "usernames": ["company"],
        "passwords": ["company123"]
    }
}

# Database setup
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Student table
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            resume TEXT,
            timestamp TEXT
        )
    ''')

    # Company table
    c.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            description TEXT,
            timestamp TEXT
        )
    ''')

    conn.commit()
    conn.close()

def get_conn():
    return sqlite3.connect(DB_PATH)

def authenticate(role):
    names = auth_users[role]["names"]
    usernames = auth_users[role]["usernames"]
    passwords = auth_users[role]["passwords"]

    # Correct hashing
    hashed_pw = stauth.Hasher().generate(passwords)

    authenticator = stauth.Authenticate(
        names, usernames, hashed_pw,
        role.capitalize() + " Login", "auth", cookie_expiry_days=0
    )
    name, auth_username, is_auth = authenticator.login()
    return is_auth, name, auth_username

# Initialize DB
init_db()

# Main Interface
st.title("📋 PHDCCI Internship Management Portal")

role = st.sidebar.selectbox("Select Role", ["Student", "Company", "PHDCCI", "NTTM"])

# Student view
if role == "Student":
    is_auth, name, username = authenticate("students")
    if is_auth:
        st.success(f"Welcome {name}")
        with st.form("student_form"):
            student_name = st.text_input("Full Name")
            email = st.text_input("Email")
            resume = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
            submitted = st.form_submit_button("Submit")

            if submitted and resume:
                filepath = os.path.join(UPLOAD_FOLDER, resume.name)
                with open(filepath, "wb") as f:
                    f.write(resume.read())

                conn = get_conn()
                conn.execute(
                    "INSERT INTO students (name, email, resume, timestamp) VALUES (?, ?, ?, ?)",
                    (student_name, email, resume.name, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
                conn.commit()
                conn.close()
                st.success("Application submitted successfully!")

# Company view
elif role == "Company":
    is_auth, name, username = authenticate("companies")
    if is_auth:
        st.success(f"Welcome {name}")
        with st.form("company_form"):
            company_name = st.text_input("Company Name")
            email = st.text_input("Contact Email")
            description = st.text_area("Company Description")
            submitted = st.form_submit_button("Submit")

            if submitted:
                conn = get_conn()
                conn.execute(
                    "INSERT INTO companies (name, email, description, timestamp) VALUES (?, ?, ?, ?)",
                    (company_name, email, description, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
                conn.commit()
                conn.close()
                st.success("Company registered successfully!")

# Admin (PHDCCI) view
elif role == "PHDCCI":
    is_auth, name, username = authenticate("admins")
    if is_auth and username == "phdcci":
        st.success("Welcome PHDCCI Admin")
        conn = get_conn()
        st.subheader("📄 Student Applications")
        students = conn.execute("SELECT name, email, resume, timestamp FROM students").fetchall()
        for s in students:
            st.markdown(f"**{s[0]}** | {s[1]} | Uploaded: {s[2]} | {s[3]}")

        st.subheader("🏢 Company Registrations")
        companies = conn.execute("SELECT name, email, description, timestamp FROM companies").fetchall()
        for c in companies:
            st.markdown(f"**{c[0]}** | {c[1]} | {c[2]} | {c[3]}")
        conn.close()

# Admin (NTTM) view
elif role == "NTTM":
    is_auth, name, username = authenticate("admins")
    if is_auth and username == "nttm":
        st.success("Welcome NTTM Admin")
        conn = get_conn()
        st.subheader("📄 Student Applications")
        students = conn.execute("SELECT name, email, resume, timestamp FROM students").fetchall()
        for s in students:
            st.markdown(f"**{s[0]}** | {s[1]} | Uploaded: {s[2]} | {s[3]}")

        st.subheader("🏢 Company Registrations")
        companies = conn.execute("SELECT name, email, description, timestamp FROM companies").fetchall()
        for c in companies:
            st.markdown(f"**{c[0]}** | {c[1]} | {c[2]} | {c[3]}")
        conn.close()
