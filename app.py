import os
import sqlite3
import streamlit as st
import streamlit_authenticator as stauth
from datetime import datetime
from PIL import Image

# Constants
DB_PATH = "data/users.db"
UPLOAD_FOLDER = "uploads/resumes/"

# Ensure required folders exist, with error handling
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
except FileExistsError:
    pass

try:
    os.makedirs("data", exist_ok=True)
except FileExistsError:
    pass

# Admin credentials (hashed inside authenticate())
auth_users = {
    "students": {
        "names": ["Student"],
        "usernames": ["student"],
        "passwords": ["student123"]
    },
    "companies": {
        "names": ["Company"],
        "usernames": ["company"],
        "passwords": ["company123"]
    },
    "admins": {
        "names": ["PHDCCI", "NTTM"],
        "usernames": ["phdcci", "nttm"],
        "passwords": ["phdcci123", "nttm123"]
    }
}

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT,
                    resume_path TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    description TEXT
                )''')
    conn.commit()
    conn.close()

def authenticate(role):
    names = auth_users[role]["names"]
    usernames = auth_users[role]["usernames"]
    passwords = auth_users[role]["passwords"]

    hashed_pw = stauth.Hasher().generate(passwords)

    authenticator = stauth.Authenticate(
        names,
        usernames,
        hashed_pw,
        role,
        cookie_expiry_days=1
    )

    name, auth_status, username = authenticator.login(f"Login as {role.capitalize()}", "main")
    return auth_status, name, username

def student_section():
    st.subheader("Student Dashboard")
    name = st.text_input("Enter your name")
    email = st.text_input("Enter your email")
    resume = st.file_uploader("Upload Resume (PDF only)", type=['pdf'])
    
    if st.button("Submit"):
        if name and email and resume:
            file_path = os.path.join(UPLOAD_FOLDER, resume.name)
            with open(file_path, "wb") as f:
                f.write(resume.read())
            conn = get_conn()
            c = conn.cursor()
            c.execute("INSERT INTO students (name, email, resume_path) VALUES (?, ?, ?)", (name, email, file_path))
            conn.commit()
            conn.close()
            st.success("Resume submitted successfully!")
        else:
            st.warning("Please fill all fields and upload resume.")

def company_section():
    st.subheader("Company Dashboard")
    name = st.text_input("Company Name")
    description = st.text_area("About the company")

    if st.button("Register Company"):
        if name and description:
            conn = get_conn()
            c = conn.cursor()
            c.execute("INSERT INTO companies (name, description) VALUES (?, ?)", (name, description))
            conn.commit()
            conn.close()
            st.success("Company registered successfully!")
        else:
            st.warning("Please complete all fields.")

def admin_view():
    st.subheader("Admin View")
    conn = get_conn()
    c = conn.cursor()

    st.markdown("### Registered Students")
    students = c.execute("SELECT name, email, resume_path FROM students").fetchall()
    for name, email, resume in students:
        st.write(f"**Name:** {name}, **Email:** {email}, **Resume:** {resume}")

    st.markdown("### Registered Companies")
    companies = c.execute("SELECT name, description FROM companies").fetchall()
    for name, desc in companies:
        st.write(f"**Company:** {name}, **Description:** {desc}")

    conn.close()

# Initialize DB
init_db()

st.title("PHDCCI Internship Management System")

role = st.sidebar.selectbox("Login As", ["Student", "Company", "PHDCCI", "NTTM"])

if role == "Student":
    is_auth, name, username = authenticate("students")
    if is_auth and username == "student":
        st.success("Welcome Student")
        student_section()
elif role == "Company":
    is_auth, name, username = authenticate("companies")
    if is_auth and username == "company":
        st.success("Welcome Company")
        company_section()
elif role == "PHDCCI":
    is_auth, name, username = authenticate("admins")
    if is_auth and username == "phdcci":
        st.success("Welcome PHDCCI Admin")
        admin_view()
elif role == "NTTM":
    is_auth, name, username = authenticate("admins")
    if is_auth and username == "nttm":
        st.success("Welcome NTTM Admin")
        admin_view()
