import streamlit as st
import sqlite3
import os
import pandas as pd
from email_validator import validate_email, EmailNotValidError

DB_PATH = "data/users.db"
UPLOAD_FOLDER = "uploads/resumes/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize the database
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        # Create tables
        c.execute('''CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT, contact TEXT, email TEXT,
                        qualification TEXT, aadhar TEXT, resume TEXT
                     )''')
        c.execute('''CREATE TABLE IF NOT EXISTS companies (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT, contact TEXT, email TEXT,
                        description TEXT
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS applications (
                        student_id INTEGER, company_id INTEGER,
                        status TEXT DEFAULT 'Applied'
                    )''')
        conn.commit()

# Utility for user login and registration
def user_auth(role):
    st.subheader(f"{role} Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    action = st.radio("Action", ["Login", "Register"] if role in ["Student", "Company"] else ["Login"])

    if st.button(action):
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            table = "students" if role == "Student" else "companies"
            if action == "Register":
                try:
                    validate_email(username)
                except EmailNotValidError as e:
                    st.error(str(e))
                    return None
                c.execute(f"SELECT * FROM {table} WHERE email=?", (username,))
                if c.fetchone():
                    st.warning("User already exists.")
                else:
                    c.execute(f"INSERT INTO {table} (email, contact) VALUES (?, ?)", (username, password))
                    conn.commit()
                    st.success("Registered successfully.")
            else:
                c.execute(f"SELECT * FROM {table} WHERE email=? AND contact=?", (username, password))
                if c.fetchone():
                    st.success("Login successful.")
                    return username
                else:
                    st.error("Invalid credentials.")
    return None

# Student dashboard
def student_dashboard(email):
    st.subheader("Student Dashboard")
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM students WHERE email=?", (email,))
        data = c.fetchone()
        if not data or not data[1]:  # If no name -> details not filled
            st.info("Please complete your profile.")
            name = st.text_input("Full Name")
            contact = st.text_input("Contact Number")
            qualification = st.text_input("Qualification")
            aadhar = st.text_input("Aadhar Card Number")
            resume = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
            if st.button("Submit"):
                if resume:
                    resume_path = os.path.join(UPLOAD_FOLDER, resume.name)
                    with open(resume_path, "wb") as f:
                        f.write(resume.read())
                    c.execute("UPDATE students SET name=?, contact=?, qualification=?, aadhar=?, resume=? WHERE email=?",
                              (name, contact, qualification, aadhar, resume_path, email))
                    conn.commit()
                    st.success("Profile updated successfully.")
                else:
                    st.warning("Resume is required.")
        else:
            st.success("Profile complete.")
            st.write(f"Welcome, {data[1]}")
            st.write("Available Companies:")
            companies = pd.read_sql("SELECT * FROM companies", conn)
            st.dataframe(companies)
            company_id = st.selectbox("Apply to Company ID", companies["id"])
            if st.button("Apply"):
                c.execute("INSERT INTO applications (student_id, company_id) VALUES (?, ?)",
                          (data[0], company_id))
                conn.commit()
                st.success("Applied successfully.")

# Company dashboard
def company_dashboard(email):
    st.subheader("Company Dashboard")
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM companies WHERE email=?", (email,))
        data = c.fetchone()
        if not data[1]:  # If name is missing
            st.info("Please complete your company profile.")
            name = st.text_input("Company Name")
            description = st.text_area("Description")
            contact = st.text_input("Contact Number")
            if st.button("Submit"):
                c.execute("UPDATE companies SET name=?, description=?, contact=? WHERE email=?",
                          (name, description, contact, email))
                conn.commit()
                st.success("Profile updated.")
        else:
            st.success(f"Welcome {data[1]}")
            st.write("Students who applied:")
            query = '''
                SELECT s.name, s.email, s.qualification, s.resume, a.status
                FROM applications a
                JOIN students s ON a.student_id = s.id
                WHERE a.company_id = ?
            '''
            df = pd.read_sql(query, conn, params=(data[0],))
            st.dataframe(df)

# Admin views
def admin_dashboard(admin_type):
    st.subheader(f"{admin_type} Dashboard")
    with sqlite3.connect(DB_PATH) as conn:
        st.write("All Students")
        students = pd.read_sql("SELECT * FROM students", conn)
        st.dataframe(students)

        st.write("All Companies")
        companies = pd.read_sql("SELECT * FROM companies", conn)
        st.dataframe(companies)

        st.write("All Applications")
        applications = pd.read_sql('''SELECT s.name, c.name as company, a.status
                                      FROM applications a
                                      JOIN students s ON a.student_id = s.id
                                      JOIN companies c ON a.company_id = c.id''', conn)
        st.dataframe(applications)

        if admin_type == "NTTM":
            st.success("View PHDCCI Recommendations here.")

# Main app logic
def main():
    st.title("Internship Management Portal")

    init_db()

    stakeholder = st.selectbox("I am a", ["Select", "Student", "Company", "PHDCCI", "NTTM"])

    if stakeholder != "Select":
        user = user_auth(stakeholder)
        if user:
            if stakeholder == "Student":
                student_dashboard(user)
            elif stakeholder == "Company":
                company_dashboard(user)
            else:
                admin_dashboard(stakeholder)

if __name__ == "__main__":
    main()

