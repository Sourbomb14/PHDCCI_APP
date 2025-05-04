import streamlit as st
import sqlite3
import os

# Path to the existing folders and database in your GitHub repository
UPLOAD_FOLDER = "uploads/resumes"
DATA_FOLDER = "data"
DB_PATH = os.path.join(DATA_FOLDER, "users.db")

# Initialize database if not already present
def initialize_db():
    # Ensure the 'data' folder exists
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        
    # Check if the database file exists
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create students table
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

        # Create companies table
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

# Function to get the database connection
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    return conn

# -------------------------------

# Admin credentials (hardcoded for now)
admin_credentials = {
    "phdcciadmin": "phdcci123",
    "nttadmin": "ntt123"
}

# Role-specific login or registration
role = st.sidebar.selectbox("Login As", ["Student", "Company", "PHDCCI", "NTTM"])

# Function for Student Registration
def student_registration():
    st.title("Student Registration")
    name = st.text_input("Name")
    contact = st.text_input("Contact Number")
    email = st.text_input("Email-ID")
    qualification = st.text_input("Qualification")
    aadhar = st.text_input("Aadhar Card Number")
    resume = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])

    if st.button("Register"):
        if name and contact and email and qualification and aadhar and resume:
            # Save data to database (Here, we are saving it to a file for simplicity)
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO students (name, contact, email, qualification, aadhar, resume) VALUES (?, ?, ?, ?, ?, ?)",
                           (name, contact, email, qualification, aadhar, resume.name))
            conn.commit()
            conn.close()
            st.success("Registration Successful!")
        else:
            st.error("Please fill all fields and upload a resume!")

# Function for Company Registration
def company_registration():
    st.title("Company Registration")
    company_name = st.text_input("Company Name")
    industry = st.text_input("Industry")
    description = st.text_area("Description of Company")
    openings = st.text_area("Internship/Job Openings")

    if st.button("Register"):
        if company_name and industry and description and openings:
            # Save data to database (Here, we are saving it to a file for simplicity)
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO companies (company_name, industry, description, openings) VALUES (?, ?, ?, ?)",
                           (company_name, industry, description, openings))
            conn.commit()
            conn.close()
            st.success("Company Registration Successful!")
        else:
            st.error("Please fill all fields!")

# Function for Admin Authentication (PHDCCI, NTTM)
def authenticate_admin(role):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in admin_credentials and admin_credentials[username] == password:
            st.success(f"Welcome {role} Admin!")
            return True
        else:
            st.error("Invalid username or password!")
            return False
    return False

# -------------------------------

# Call the initialize_db function to ensure the database is ready
initialize_db()

# Handle role-based login or registration

if role == "Student":
    # Student module
    is_registered = st.checkbox("Already registered? Login")
    if not is_registered:
        student_registration()
    else:
        st.write("Please log in here.")
        # Add login process here (could use email verification or other means)

elif role == "Company":
    # Company module
    is_registered = st.checkbox("Already registered? Login")
    if not is_registered:
        company_registration()
    else:
        st.write("Please log in here.")
        # Add login process here (could use company email verification or other means)

elif role == "PHDCCI":
    # Admin module for PHDCCI
    if authenticate_admin("PHDCCI"):
        st.write("You can now access all student and company data.")
        # Implement admin features like viewing all applicants, giving recommendations, etc.

elif role == "NTTM":
    # Admin module for NTTM
    if authenticate_admin("NTTM"):
        st.write("You can now access all student and company data.")
        # Implement admin features like viewing PHDCCI recommendations, approving final lists, etc.
