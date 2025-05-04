import streamlit as st
import os
import sqlite3
from datetime import datetime

# Simulate database with a dictionary (for simplicity, use real databases in production)
students_db = {}
companies_db = {}

# Predefined admin credentials
admin_credentials = {
    "phdcciadmin": "phdcci123",  # PHDCCI admin
    "nttadmin": "ntt123"         # NTTM admin
}

# Ensure required folders exist
os.makedirs("uploads/resumes", exist_ok=True)
os.makedirs("data", exist_ok=True)

# Helper function to simulate database connection
def get_conn():
    conn = sqlite3.connect("data/users.db")
    return conn

# Student registration
def register_student():
    st.subheader("Student Registration")
    name = st.text_input("Name")
    email = st.text_input("Email")
    contact = st.text_input("Contact Number")
    qualification = st.text_input("Qualification")
    aadhar = st.text_input("Aadhar Card Number")
    resume = st.file_uploader("Upload Resume", type=["pdf", "doc", "docx"])

    if st.button("Register"):
        if name and email and contact and qualification and aadhar and resume:
            students_db[email] = {
                "name": name,
                "email": email,
                "contact": contact,
                "qualification": qualification,
                "aadhar": aadhar,
                "resume": resume
            }
            st.success("Registration successful!")
        else:
            st.error("Please fill in all details.")

# Student login
def student_login():
    st.subheader("Student Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if email in students_db:
            # For simplicity, we're assuming the password is just the email for demonstration.
            st.success(f"Welcome {students_db[email]['name']}!")
            student_module()
        else:
            st.error("Invalid email or password.")

# Company registration
def register_company():
    st.subheader("Company Registration")
    company_name = st.text_input("Company Name")
    industry = st.text_input("Industry")
    description = st.text_area("Company Description")
    openings = st.text_area("Internship/Job Openings")

    if st.button("Register"):
        if company_name and industry and description and openings:
            companies_db[company_name] = {
                "company_name": company_name,
                "industry": industry,
                "description": description,
                "openings": openings
            }
            st.success("Company registration successful!")
        else:
            st.error("Please fill in all details.")

# Admin login function
def admin_login():
    st.subheader("Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in admin_credentials and admin_credentials[username] == password:
            st.success(f"Welcome {username}!")
            if username == "phdcciadmin":
                phdcci_admin_module()
            elif username == "nttadmin":
                nttm_admin_module()
        else:
            st.error("Invalid credentials.")

# Modules for admins
def phdcci_admin_module():
    st.title("PHDCCI Admin Module")
    st.write("Here, the PHDCCI admin can oversee all operations.")

def nttm_admin_module():
    st.title("NTTM Admin Module")
    st.write("Here, the NTTM admin can oversee all operations.")

# Main module
def main():
    st.title("Internship Management System")
    
    role = st.sidebar.selectbox("Login As", ["Student", "Company", "PHDCCI", "NTTM"])

    if role == "Student":
        action = st.radio("Select Action", ["Login", "Register"])
        if action == "Login":
            student_login()
        elif action == "Register":
            register_student()

    elif role == "Company":
        action = st.radio("Select Action", ["Login", "Register"])
        if action == "Login":
            student_login()  # You can add a different login for companies later
        elif action == "Register":
            register_company()

    elif role == "PHDCCI":
        admin_login()

    elif role == "NTTM":
        admin_login()

if __name__ == "__main__":
    main()
