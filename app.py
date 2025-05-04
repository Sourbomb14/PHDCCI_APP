import streamlit as st
import streamlit_authenticator as stauth
import sqlite3
import os
from sqlite3 import Connection
from typing import List
import pandas as pd

# Define directories
DB_PATH = "data/users.db"
UPLOAD_FOLDER = "uploads/resumes/"

# Ensure required directories exist
if not os.path.exists(UPLOAD_FOLDER):
    try:
        os.makedirs(UPLOAD_FOLDER)
    except FileExistsError:
        pass

# Initialize DB
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create student table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            username TEXT PRIMARY KEY,
            name TEXT,
            contact TEXT,
            email TEXT,
            qualification TEXT,
            aadhar TEXT,
            resume TEXT
        )
    ''')

    # Create company table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            username TEXT PRIMARY KEY,
            name TEXT,
            description TEXT,
            email TEXT
        )
    ''')

    # Applications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            student_username TEXT,
            company_username TEXT,
            status TEXT DEFAULT "Applied"
        )
    ''')

    # Admin approval table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS approvals (
            student_username TEXT,
            company_username TEXT,
            phdcci_status TEXT,
            nttm_status TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# Helper function to get DB connection
def get_conn() -> Connection:
    return sqlite3.connect(DB_PATH)

# ------------------------ AUTH SETUP ------------------------
# Simple user dictionary (should ideally be in DB or env variables)
auth_users = {
    "students": {
        "names": ["student1"],
        "usernames": ["student1"],
        "passwords": ["1234"]
    },
    "companies": {
        "names": ["company1"],
        "usernames": ["company1"],
        "passwords": ["abcd"]
    },
    "admins": {
        "names": ["PHDCCI", "NTTM"],
        "usernames": ["phdcci", "nttm"],
        "passwords": ["admin1", "admin2"]
    }
}

def authenticate(role):
    names = auth_users[role]["names"]
    usernames = auth_users[role]["usernames"]
    passwords = auth_users[role]["passwords"]

    hashed_pw = stauth.Hasher(passwords).generate()

    authenticator = stauth.Authenticate(
        names, usernames, hashed_pw,
        role.capitalize() + " Login", "abc", cookie_expiry_days=0
    )
    name, auth_username, is_auth = authenticator.login()
    return is_auth, name, auth_username

# ------------------------ UI ------------------------
st.set_page_config("Internship Management App", layout="centered")

st.title("🎓 Internship Management Portal")

# Landing Page Buttons
role = st.selectbox("Select your role", ["Select", "Student", "Company", "PHDCCI", "NTTM"])

if role == "Student":
    is_auth, name, username = authenticate("students")
    if is_auth:
        st.success(f"Welcome, {name}")
        conn = get_conn()
        cursor = conn.cursor()

        student_exists = cursor.execute("SELECT * FROM students WHERE username=?", (username,)).fetchone()
        if not student_exists:
            st.subheader("Complete Your Registration")
            with st.form("student_form"):
                full_name = st.text_input("Full Name")
                contact = st.text_input("Contact Number")
                email = st.text_input("Email")
                qualification = st.text_input("Qualification")
                aadhar = st.text_input("Aadhar Number")
                resume = st.file_uploader("Upload Resume", type=["pdf"])

                submitted = st.form_submit_button("Submit")
                if submitted:
                    resume_path = os.path.join(UPLOAD_FOLDER, f"{username}_{resume.name}")
                    with open(resume_path, "wb") as f:
                        f.write(resume.read())
                    cursor.execute(
                        "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (username, full_name, contact, email, qualification, aadhar, resume_path)
                    )
                    conn.commit()
                    st.success("Registration complete.")
        else:
            st.subheader("Available Internships")
            companies = cursor.execute("SELECT * FROM companies").fetchall()
            for comp in companies:
                st.markdown(f"**{comp[1]}** — {comp[2]}")
                if st.button(f"Apply to {comp[1]}", key=comp[0]):
                    cursor.execute(
                        "INSERT INTO applications (student_username, company_username) VALUES (?, ?)",
                        (username, comp[0])
                    )
                    conn.commit()
                    st.success(f"Applied to {comp[1]}")
        conn.close()

elif role == "Company":
    is_auth, name, username = authenticate("companies")
    if is_auth:
        st.success(f"Welcome, {name}")
        conn = get_conn()
        cursor = conn.cursor()

        company_exists = cursor.execute("SELECT * FROM companies WHERE username=?", (username,)).fetchone()
        if not company_exists:
            st.subheader("Register Your Company")
            with st.form("company_form"):
                company_name = st.text_input("Company Name")
                description = st.text_area("Company Description")
                email = st.text_input("Contact Email")
                submitted = st.form_submit_button("Register")
                if submitted:
                    cursor.execute(
                        "INSERT INTO companies VALUES (?, ?, ?, ?)",
                        (username, company_name, description, email)
                    )
                    conn.commit()
                    st.success("Company registered.")
        else:
            st.subheader("Student Applications")
            apps = cursor.execute(
                "SELECT s.name, s.email, s.resume FROM applications a JOIN students s ON a.student_username = s.username WHERE a.company_username=?",
                (username,)
            ).fetchall()
            for app in apps:
                st.markdown(f"**{app[0]}** — {app[1]}")
                st.markdown(f"[View Resume]({app[2]})")
                if st.button(f"Shortlist {app[0]}", key=app[1]):
                    cursor.execute(
                        "INSERT OR REPLACE INTO approvals (student_username, company_username, phdcci_status, nttm_status) VALUES (?, ?, ?, ?)",
                        (app[1], username, "Pending", "Pending")
                    )
                    conn.commit()
                    st.success(f"{app[0]} shortlisted.")
        conn.close()

elif role == "PHDCCI":
    is_auth, name, username = authenticate("admins")
    if is_auth and username == "phdcci":
        st.success("Welcome PHDCCI Admin")
        conn = get_conn()
        df = pd.read_sql_query("SELECT * FROM approvals WHERE phdcci_status='Pending'", conn)
        st.dataframe(df)
        for index, row in df.iterrows():
            if st.button(f"Approve {row['student_username']} for {row['company_username']}", key=index):
                conn.execute("UPDATE approvals SET phdcci_status='Recommended' WHERE student_username=? AND company_username=?", (row['student_username'], row['company_username']))
                conn.commit()
        conn.close()

elif role == "NTTM":
    is_auth, name, username = authenticate("admins")
    if is_auth and username == "nttm":
        st.success("Welcome NTTM Admin")
        conn = get_conn()
        df = pd.read_sql_query("SELECT * FROM approvals WHERE phdcci_status='Recommended' AND nttm_status='Pending'", conn)
        st.dataframe(df)
        for index, row in df.iterrows():
            if st.button(f"Approve Stipend for {row['student_username']}", key=f"nttm_{index}"):
                conn.execute("UPDATE approvals SET nttm_status='Approved' WHERE student_username=? AND company_username=?", (row['student_username'], row['company_username']))
                conn.commit()
        conn.close()
