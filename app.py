import streamlit as st
import sqlite3
import os
from datetime import datetime
import streamlit_authenticator as stauth

# Folder paths (assumes they already exist in the repo)
UPLOAD_FOLDER = "uploads/resumes"
DB_PATH = "data/users.db"

# Ensure the database exists
if not os.path.exists(DB_PATH):
    os.makedirs(DB_PATH)

# Admin credentials setup
auth_users = {
    "students": {
        "usernames": ["student1", "student2"],
        "passwords": ["pass1", "pass2"]
    },
    "companies": {
        "usernames": ["company1", "company2"],
        "passwords": ["compass1", "compass2"]
    },
    "admins": {
        "usernames": ["phdcci", "nttm"],
        "passwords": ["admin123", "nttmadmin"]
    }
}

# Authenticate function using streamlit-authenticator
def authenticate(role):
    usernames = auth_users[role]["usernames"]
    passwords = auth_users[role]["passwords"]
    hashed_pw = stauth.Hasher(passwords).generate()
    authenticator = stauth.Authenticate(usernames, hashed_pw, usernames, "Login", "sidebar")
    
    return authenticator.login("Login", "sidebar")

# Define modules for different user roles
def student_module():
    st.header("Student Dashboard")
    st.write("This is where students can view their details and apply to opportunities.")
    # Student-specific functionality here

def company_module():
    st.header("Company Dashboard")
    st.write("This is where companies can view student applications and shortlist candidates.")
    # Company-specific functionality here

def phdcci_module():
    st.header("PHDCCI Dashboard")
    st.write("This is where PHDCCI can review and manage recommendations.")
    # PHDCCI-specific functionality here

def nttm_module():
    st.header("NTTM Dashboard")
    st.write("This is where NTTM can approve recommendations for fund/disbursements.")
    # NTTM-specific functionality here

# Landing Page
st.title("Internship Management App")
role = st.sidebar.selectbox("Login As", ["Student", "Company", "PHDCCI", "NTTM"])

# Role-specific login or registration
if role == "Student":
    is_auth, name, username = authenticate("students")
    if is_auth:
        st.success(f"Welcome {name}")
        student_module()

elif role == "Company":
    is_auth, name, username = authenticate("companies")
    if is_auth:
        st.success(f"Welcome {name}")
        company_module()

elif role == "PHDCCI":
    is_auth, name, username = authenticate("admins")
    if is_auth:
        st.success("Welcome PHDCCI Admin")
        phdcci_module()

elif role == "NTTM":
    is_auth, name, username = authenticate("admins")
    if is_auth:
        st.success("Welcome NTTM Admin")
        nttm_module()
