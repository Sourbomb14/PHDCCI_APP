import streamlit as st
import streamlit_authenticator as stauth
import sqlite3
import os
import shutil
from datetime import datetime

# Ensure required folders exist
if not os.path.exists("uploads/resumes"):
    os.makedirs("uploads/resumes")

if not os.path.exists("data"):
    os.makedirs("data")

# -------------------------------
# Database setup
DB_PATH = "data/users.db"
UPLOAD_FOLDER = "uploads/resumes/"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            role TEXT,
            company TEXT,
            resume TEXT,
            approved INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_conn():
    return sqlite3.connect(DB_PATH)

# -------------------------------
# Authentication Setup

# Pre-hashed passwords generated via Hasher(['student@123', 'company@123', 'phdcci@123'])
hashed_passwords = {
    "students": ['$2b$12$A0yK3pH3t/IOWDz3nYmG0uQxKXac/8svfkpq0I4fAqre8AMnxVyiW'],
    "companies": ['$2b$12$6o20qvmQoRBkVRch0xXYi.1VuK9HtthxwHYf3ErEsg0KkuKkvyKsm'],
    "admins": ['$2b$12$7FeyHBiFx1MIcDeZ6f5Ldu4OlAgmR1USZtU2D3Eh9ZCvW38kkfYZa']
}

auth_users = {
    "students": {
        "usernames": ["student"],
        "names": ["Student"],
        "hashed_passwords": hashed_passwords["students"]
    },
    "companies": {
        "usernames": ["company"],
        "names": ["Company"],
        "hashed_passwords": hashed_passwords["companies"]
    },
    "admins": {
        "usernames": ["phdcci"],
        "names": ["PHDCCI Admin"],
        "hashed_passwords": hashed_passwords["admins"]
    }
}

def authenticate(role):
    usernames = auth_users[role]["usernames"]
    names = auth_users[role]["names"]
    passwords = auth_users[role]["hashed_passwords"]
    
    authenticator = stauth.Authenticate(
        names, usernames, passwords, 
        "internapp", "abcdef", cookie_expiry_days=1
    )
    name, auth_status, username = authenticator.login(f"Login as {role.capitalize()}", "main")
    return auth_status, name, username

# -------------------------------
# Page Sections

def student_section():
    st.header("Student Dashboard")
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "docx"])

    if st.button("Submit"):
        if name and email and uploaded_file:
            resume_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
            with open(resume_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            conn = get_conn()
            c = conn.cursor()
            c.execute("INSERT INTO users (name, email, role, resume) VALUES (?, ?, ?, ?)", 
                      (name, email, "student", resume_path))
            conn.commit()
            conn.close()
            st.success("Application submitted successfully!")
        else:
            st.error("Please fill all fields and upload your resume.")

def company_section():
    st.header("Company Dashboard")
    name = st.text_input("Company Representative Name")
    email = st.text_input("Company Email")
    company = st.text_input("Company Name")

    if st.button("Register"):
        if name and email and company:
            conn = get_conn()
            c = conn.cursor()
            c.execute("INSERT INTO users (name, email, role, company) VALUES (?, ?, ?, ?)", 
                      (name, email, "company", company))
            conn.commit()
            conn.close()
            st.success("Company registered successfully!")
        else:
            st.error("Please fill all fields.")

def admin_section():
    st.header("Admin Dashboard")
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, name, email, role, company, resume, approved FROM users")
    data = c.fetchall()
    conn.close()

    for row in data:
        st.write(f"**ID:** {row[0]}")
        st.write(f"**Name:** {row[1]}")
        st.write(f"**Email:** {row[2]}")
        st.write(f"**Role:** {row[3]}")
        if row[3] == "company":
            st.write(f"**Company:** {row[4]}")
        if row[3] == "student":
            st.write(f"**Resume:** {row[5]}")
        approved = "✅ Approved" if row[6] else "❌ Not Approved"
        st.write(f"**Status:** {approved}")

        if not row[6]:
            if st.button(f"Approve {row[1]} (ID: {row[0]})"):
                conn = get_conn()
                c = conn.cursor()
                c.execute("UPDATE users SET approved = 1 WHERE id = ?", (row[0],))
                conn.commit()
                conn.close()
                st.success(f"Approved {row[1]}")
                st.experimental_rerun()
        st.markdown("---")

# -------------------------------
# App Logic

init_db()
st.title("Internship Management Portal")

role = st.sidebar.selectbox("Login As", ["Student", "Company", "PHDCCI"])

if role == "Student":
    is_auth, name, username = authenticate("students")
    if is_auth:
        st.success(f"Welcome, {name}")
        student_section()

elif role == "Company":
    is_auth, name, username = authenticate("companies")
    if is_auth:
        st.success(f"Welcome, {name}")
        company_section()

elif role == "PHDCCI":
    is_auth, name, username = authenticate("admins")
    if is_auth and username == "phdcci":
        st.success("Welcome PHDCCI Admin")
        admin_section()
