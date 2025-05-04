# internship_portal_app.py

import streamlit as st
import sqlite3
import os
import pandas as pd

# ------------------------ Configuration ------------------------
UPLOAD_FOLDER = "uploads/resumes"
DATA_FOLDER = "data"
DB_PATH = os.path.join(DATA_FOLDER, "users.db")

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ------------------------ Database Initialization ------------------------
def initialize_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        contact TEXT,
        email TEXT UNIQUE,
        qualification TEXT,
        aadhar TEXT,
        resume TEXT
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT,
        industry TEXT,
        description TEXT,
        openings TEXT
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        student_id INTEGER,
        company_id INTEGER,
        status TEXT DEFAULT 'Applied',
        FOREIGN KEY(student_id) REFERENCES students(id),
        FOREIGN KEY(company_id) REFERENCES companies(id)
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recommendations (
        student_id INTEGER,
        company_id INTEGER,
        recommendation TEXT,
        approved TEXT DEFAULT 'Pending',
        FOREIGN KEY(student_id) REFERENCES students(id),
        FOREIGN KEY(company_id) REFERENCES companies(id)
    )""")

    conn.commit()
    conn.close()

initialize_db()

# ------------------------ Utilities ------------------------
def get_conn():
    return sqlite3.connect(DB_PATH)

def get_student_by_email(email):
    conn = get_conn()
    student = pd.read_sql(f"SELECT * FROM students WHERE email='{email}'", conn)
    conn.close()
    return student

# ------------------------ Registration & Login ------------------------
def student_register():
    st.title("Student Registration")
    name = st.text_input("Name")
    contact = st.text_input("Contact Number")
    email = st.text_input("Email-ID")
    qualification = st.text_input("Qualification")
    aadhar = st.text_input("Aadhar Card Number")
    resume = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])

    if st.button("Register"):
        if all([name, contact, email, qualification, aadhar, resume]):
            resume_path = os.path.join(UPLOAD_FOLDER, resume.name)
            with open(resume_path, "wb") as f:
                f.write(resume.read())
            try:
                conn = get_conn()
                conn.execute("INSERT INTO students (name, contact, email, qualification, aadhar, resume) VALUES (?, ?, ?, ?, ?, ?)",
                             (name, contact, email, qualification, aadhar, resume.name))
                conn.commit()
                conn.close()
                st.success("Registration successful!")
            except sqlite3.IntegrityError:
                st.error("Email already registered!")
        else:
            st.error("Please fill in all fields.")

def student_login():
    st.title("Student Login")
    email = st.text_input("Email-ID")
    if st.button("Login"):
        student = get_student_by_email(email)
        if not student.empty:
            st.success(f"Welcome, {student.iloc[0]['name']}")
            st.subheader("Your Profile")
            st.dataframe(student)

            st.subheader("Available Companies")
            companies = pd.read_sql("SELECT * FROM companies", get_conn())
            st.dataframe(companies)

            selected = st.selectbox("Apply to Company", companies["company_name"])
            if st.button("Apply"):
                company_id = companies[companies["company_name"] == selected]["id"].values[0]
                conn = get_conn()
                student_id = student["id"].values[0]
                conn.execute("INSERT INTO applications (student_id, company_id) VALUES (?, ?)", (student_id, company_id))
                conn.commit()
                conn.close()
                st.success("Applied Successfully!")
        else:
            st.error("Student not found!")

def company_register():
    st.title("Company Registration")
    name = st.text_input("Company Name")
    industry = st.text_input("Industry")
    desc = st.text_area("Company Description")
    openings = st.text_area("Internship/Job Openings")

    if st.button("Register"):
        if all([name, industry, desc, openings]):
            conn = get_conn()
            conn.execute("INSERT INTO companies (company_name, industry, description, openings) VALUES (?, ?, ?, ?)",
                         (name, industry, desc, openings))
            conn.commit()
            conn.close()
            st.success("Company Registered Successfully!")
        else:
            st.error("Please fill all fields!")

def company_login():
    st.title("Company Login")
    name = st.text_input("Company Name")
    if st.button("Login"):
        conn = get_conn()
        companies = pd.read_sql("SELECT * FROM companies WHERE company_name=?", conn, params=(name,))
        if not companies.empty:
            st.success(f"Welcome {name}")
            comp_id = companies["id"].values[0]
            applicants = pd.read_sql(f"SELECT s.* FROM students s JOIN applications a ON s.id = a.student_id WHERE a.company_id={comp_id}", conn)
            st.dataframe(applicants)

            student_to_shortlist = st.selectbox("Shortlist a student", applicants["name"] if not applicants.empty else [])
            if st.button("Shortlist") and student_to_shortlist:
                student_id = applicants[applicants["name"] == student_to_shortlist]["id"].values[0]
                conn.execute("INSERT OR REPLACE INTO recommendations (student_id, company_id, recommendation) VALUES (?, ?, ?)",
                             (student_id, comp_id, 'recommended'))
                conn.commit()
                st.success("Student Shortlisted")
        else:
            st.error("Company not found")

# Admin (PHDCCI and NTTM)
admin_credentials = {"phdcciadmin": "phdcci123", "nttadmin": "ntt123"}

def admin_login(admin_type):
    st.title(f"{admin_type} Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if admin_credentials.get(username) == password:
            st.success(f"Welcome {admin_type}")
            conn = get_conn()
            if admin_type == "PHDCCI":
                df = pd.read_sql("SELECT * FROM recommendations", conn)
                st.dataframe(df)
            elif admin_type == "NTTM":
                df = pd.read_sql("SELECT * FROM recommendations WHERE recommendation='recommended'", conn)
                st.dataframe(df)
                approve_id = st.number_input("Enter Student ID to Approve", min_value=1, step=1)
                if st.button("Approve"):
                    conn.execute("UPDATE recommendations SET approved='approved' WHERE student_id=?", (approve_id,))
                    conn.commit()
                    st.success("Approved")
        else:
            st.error("Invalid credentials")

# ------------------------ Main App ------------------------

def main():
    st.title("Internship & Placement Portal")
    choice = st.selectbox("Choose User Type", ["Landing Page", "Student", "Company", "PHDCCI", "NTTM"])

    if choice == "Landing Page":
        st.header("Welcome to the Internship & Placement Portal")
        st.info("Choose a category from the sidebar")
    elif choice == "Student":
        mode = st.radio("Mode", ["Register", "Login"])
        if mode == "Register":
            student_register()
        else:
            student_login()
    elif choice == "Company":
        mode = st.radio("Mode", ["Register", "Login"])
        if mode == "Register":
            company_register()
        else:
            company_login()
    elif choice == "PHDCCI":
        admin_login("PHDCCI")
    elif choice == "NTTM":
        admin_login("NTTM")

if __name__ == '__main__':
    main()
