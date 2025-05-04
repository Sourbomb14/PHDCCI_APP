import streamlit as st
import sqlite3
import os

# --- Constants ---
UPLOAD_FOLDER = "uploads/resumes"
DATA_FOLDER = "data"
DB_PATH = os.path.join(DATA_FOLDER, "users.db")

# --- Ensure required folders are present ---
def ensure_directories():
    if os.path.exists(UPLOAD_FOLDER):
        if not os.path.isdir(UPLOAD_FOLDER):
            os.remove(UPLOAD_FOLDER)
            os.makedirs(UPLOAD_FOLDER)
    else:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    os.makedirs(DATA_FOLDER, exist_ok=True)

# --- Initialize the database ---
def initialize_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            contact TEXT,
            email TEXT,
            qualification TEXT,
            aadhar TEXT,
            resume TEXT
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            industry TEXT,
            description TEXT,
            openings TEXT
        )
        """)
        conn.commit()
        conn.close()

# --- Database Connection Helper ---
def get_conn():
    return sqlite3.connect(DB_PATH)

# --- Admin Credentials (Hardcoded for now) ---
admin_credentials = {
    "phdcciadmin": "phdcci123",
    "nttadmin": "ntt123"
}

# --- Student Registration ---
def student_register():
    st.subheader("Student Registration")
    name = st.text_input("Name")
    contact = st.text_input("Contact Number")
    email = st.text_input("Email-ID")
    qualification = st.text_input("Qualification")
    aadhar = st.text_input("Aadhar Card Number")
    resume = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])

    if st.button("Register"):
        if name and contact and email and qualification and aadhar and resume:
            resume_path = os.path.join(UPLOAD_FOLDER, resume.name)
            with open(resume_path, "wb") as f:
                f.write(resume.getbuffer())

            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO students (name, contact, email, qualification, aadhar, resume)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, contact, email, qualification, aadhar, resume.name))
            conn.commit()
            conn.close()
            st.success("Registration successful!")
        else:
            st.error("All fields are required.")

# --- Company Registration ---
def company_register():
    st.subheader("Company Registration")
    company_name = st.text_input("Company Name")
    industry = st.text_input("Industry")
    description = st.text_area("Description of Company")
    openings = st.text_area("Internship/Job Openings")

    if st.button("Register"):
        if company_name and industry and description and openings:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO companies (company_name, industry, description, openings)
                VALUES (?, ?, ?, ?)
            """, (company_name, industry, description, openings))
            conn.commit()
            conn.close()
            st.success("Company registration successful!")
        else:
            st.error("Please fill all fields.")

# --- Admin Login Function ---
def authenticate_admin(role):
    st.subheader(f"{role} Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in admin_credentials and admin_credentials[username] == password:
            st.success(f"Welcome {username}!")
            return username
        else:
            st.error("Invalid credentials.")
    return None

# --- Student Profile & Companies View Placeholder ---
def student_dashboard():
    st.info("Student dashboard under development.")
    # Add: View profile, Browse companies, Apply, etc.

# --- Company Dashboard Placeholder ---
def company_dashboard():
    st.info("Company dashboard under development.")
    # Add: View applicants, shortlist, etc.

# --- PHDCCI Dashboard Placeholder ---
def phdcci_admin_dashboard():
    st.info("PHDCCI admin dashboard under development.")
    # Add: View students, companies, recommend candidates, etc.

# --- NTTM Dashboard Placeholder ---
def nttm_admin_dashboard():
    st.info("NTTM admin dashboard under development.")
    # Add: View students, companies, recommendations, approve etc.

# --- Main Landing Page Logic ---
def main():
    st.title("Internship & Placement Portal")

    st.markdown("## Choose Your Role")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("Student"):
            student_choice = st.radio("Select Action", ["Register", "Login"])
            if student_choice == "Register":
                student_register()
            elif student_choice == "Login":
                student_dashboard()

    with col2:
        if st.button("Company"):
            company_choice = st.radio("Select Action", ["Register", "Login"])
            if company_choice == "Register":
                company_register()
            elif company_choice == "Login":
                company_dashboard()

    with col3:
        if st.button("PHDCCI"):
            user = authenticate_admin("PHDCCI")
            if user == "phdcciadmin":
                phdcci_admin_dashboard()

    with col4:
        if st.button("NTTM"):
            user = authenticate_admin("NTTM")
            if user == "nttadmin":
                nttm_admin_dashboard()

# --- Run App ---
ensure_directories()
initialize_db()
main()
