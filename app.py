import streamlit as st
import sqlite3
import os
from PIL import Image  # Import for image handling

# --- Constants ---
UPLOAD_FOLDER = "uploads/resumes"
DATA_FOLDER = "data"
DB_PATH = os.path.join(DATA_FOLDER, "users.db")
ADMIN_CREDENTIALS = {  # Use a constant for credentials
    "phdcciadmin": "phdcci123",
    "nttadmin": "ntt123"
}

# --- Helper Functions ---

def ensure_directories():
    """
    Ensures that the necessary directories (UPLOAD_FOLDER, DATA_FOLDER) exist.
    Creates them if they don't.  Handles potential errors during directory creation.
    """
    for folder in [UPLOAD_FOLDER, DATA_FOLDER]:
        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
                st.info(f"Created directory: {folder}")  # Use st.info for non-error messages
            except OSError as e:
                st.error(f"Error creating directory {folder}: {e}")
                st.stop()  # Stop execution if directory creation fails

def initialize_db():
    """
    Initializes the SQLite database.  Creates the SQLite database file and the student and company tables if they
    don't exist. It handles potential errors during database operations.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                qualification TEXT NOT NULL,
                aadhar TEXT NOT NULL UNIQUE,
                resume TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL UNIQUE,
                industry TEXT NOT NULL,
                description TEXT NOT NULL,
                openings TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        st.info("Database initialized/connected.")
    except sqlite3.Error as e:
        st.error(f"Error initializing database: {e}")
        st.stop()  # Stop if database initialization fails

def get_conn():
    """
    Establishes and returns a database connection.  Handles potential connection errors.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to database: {e}")
        st.stop()

# --- UI Components ---

def create_spacer(height=20):
    """Creates vertical space in the Streamlit UI."""
    st.markdown(f"<div style='margin-top:{height}px;'></div>", unsafe_allow_html=True)

# --- Student Registration ---
def student_register():
    """
    Handles student registration.  Validates input, saves resume, and stores
    student data in the database.  Improves user feedback with st.messages.
    """
    st.subheader("Student Registration")

    # Use placeholders for better UI
    name = st.text_input("Name", placeholder="Enter your full name")
    contact = st.text_input("Contact Number", placeholder="Enter your phone number")
    email = st.text_input("Email-ID", placeholder="Enter your email address")
    qualification = st.text_input("Qualification", placeholder="Enter your highest qualification")
    aadhar = st.text_input("Aadhar Card Number", placeholder="Enter your Aadhar number")
    resume = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"],
                             help="Upload your resume in PDF, DOCX, or TXT format")

    if st.button("Register"):
        if not all([name, contact, email, qualification, aadhar, resume]):
            st.error("All fields are required. Please fill out the form completely.")
            return  # Stop if any field is missing

        # Basic email and phone validation (you can expand this)
        if "@" not in email or "." not in email:
            st.error("Invalid email address. Please enter a valid email.")
            return
        if not contact.isdigit() or len(contact) < 8:
            st.error("Invalid contact number. Please enter a valid phone number.")
            return

        try:
            resume_path = os.path.join(UPLOAD_FOLDER, resume.name)
            with open(resume_path, "wb") as f:
                f.write(resume.getbuffer())  # Use getbuffer() for file-like object

            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO students (name, contact, email, qualification, aadhar, resume)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, contact, email, qualification, aadhar, resume.name))
            conn.commit()
            conn.close()
            st.success("Registration successful!  You can now log in.") #changed from previous registration successful
        except (OSError, sqlite3.Error) as e:
            st.error(f"An error occurred during registration: {e}")
            st.stop()

# --- Company Registration ---
def company_register():
    """Handles company registration, storing data in the database."""
    st.subheader("Company Registration")
    company_name = st.text_input("Company Name", placeholder="Enter company name")
    industry = st.text_input("Industry", placeholder="Enter industry")
    description = st.text_area("Description of Company", placeholder="Enter company description")
    openings = st.text_area("Internship/Job Openings", placeholder="Describe openings")

    if st.button("Register"):
        if not all([company_name, industry, description, openings]):
            st.error("All fields are required.")
            return

        try:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO companies (company_name, industry, description, openings)
                VALUES (?, ?, ?, ?)
            """, (company_name, industry, description, openings))
            conn.commit()
            conn.close()
            st.success("Company registration successful!")
        except sqlite3.Error as e:
            st.error(f"Error during company registration: {e}")
            st.stop()

# --- Admin Login ---
def authenticate_admin(role):
    """Handles admin login and authentication."""
    st.subheader(f"{role} Admin Login")
    username = st.text_input("Username", placeholder="Enter username")
    password = st.text_input("Password", type="password", placeholder="Enter password")

    if st.button("Login"):
        if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
            st.success(f"Welcome {username}!")
            st.session_state.user_role = role  # Store role in session state
            st.session_state.logged_in = True
            return True  # Indicate successful login
        else:
            st.error("Invalid credentials.")
            return False
    return False

# --- Student/Company/Admin Dashboards ---
def student_dashboard():
    """Placeholder for student dashboard functionality."""
    st.header("Student Dashboard")
    st.info("Student dashboard is under development.  Here, students will be able to:")
    st.markdown("- View and update their profile")
    st.markdown("- Browse available internships and jobs")
    st.markdown("- Apply for opportunities")
    # Add: View profile, Browse companies, Apply, etc.

def company_dashboard():
    """Placeholder for company dashboard functionality."""
    st.header("Company Dashboard")
    st.info("Company dashboard is under development. Here, companies will be able to:")
    st.markdown("- View and update their company profile")
    st.markdown("- Post internship and job openings")
    st.markdown("- View and manage applications")

def phdcci_admin_dashboard():
    """Placeholder for PHDCCI admin dashboard functionality."""
    st.header("PHDCCI Admin Dashboard")
    st.info("PHDCCI admin dashboard is under development.  PHDCCI admins will be able to:")
    st.markdown("- Manage student and company accounts")
    st.markdown("- View application statistics")
    st.markdown("- Generate reports")

def nttm_admin_dashboard():
    """Placeholder for NTTM admin dashboard functionality."""
    st.header("NTTM Admin Dashboard")
    st.info("NTTM admin dashboard is under development.  NTTM admins will be able to:")
    st.markdown("- Manage and approve student and company registrations")
    st.markdown("- Oversee the internship and placement process")
    st.markdown("- Track key metrics")

# --- Main App ---
def main():
    """Main function to run the Streamlit app."""

    # --- Initialize Session State ---
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_role = None

    ensure_directories()  # Ensure directories exist
    initialize_db()  # Initialize the database

    # --- Separate Landing Pages ---
    if not st.session_state.logged_in:
        # st.title("Internship & Placement Portal")
        # st.markdown("## Choose Your Role")

        # col1, col2, col3, col4 = st.columns(4)

        # with col1:
        #     if st.button("Student"):
        #         student_landing_page()
        # with col2:
        #     if st.button("Company"):
        #         company_landing_page()
        # with col3:
        #     if st.button("PHDCCI"):
        #         phdcci_admin_landing_page()
        # with col4:
        #     if st.button("NTTM"):
        #         nttm_admin_landing_page()
        
        # --- New Landing Page Style ---
        st.markdown(
            """
            <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #f0f4f8;
                color: #333;
                margin: 0;
                padding: 0;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #fff;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                text-align: center;
            }
            h1 {
                font-size: 2.5rem;
                color: #007bff;
                margin-bottom: 20px;
            }
            p {
                font-size: 1.1rem;
                margin-bottom: 20px;
            }
            .button-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin-bottom: 20px;
            }
            .role-button {
                padding: 12px 24px;
                font-size: 1.2rem;
                font-weight: bold;
                color: white;
                background-color: #007bff;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                transition: background-color 0.3s ease, transform 0.2s ease;
            }
            .role-button:hover {
                background-color: #0056b3;
                transform: translateY(-2px);
            }
            @media (max-width: 600px) {
                .button-grid {
                    grid-template-columns: 1fr;
                }
                .role-button {
                    width: 100%;
                }
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<div class='container'>", unsafe_allow_html=True)
        st.markdown("<h1 class='display-4'>Internship & Placement Portal</h1>", unsafe_allow_html=True)
        st.markdown("<p class='lead'>Welcome to our platform, designed to connect students with exciting internship and placement opportunities.</p>", unsafe_allow_html=True)
        st.markdown("<div class='button-grid'>", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)  # Create four columns

        with col1:
            if st.button("Student", className="role-button"):
                student_landing_page()
        with col2:
            if st.button("Company", className="role-button"):
                company_landing_page()
        with col3:
            if st.button("PHDCCI", className="role-button"):
                phdcci_admin_landing_page()
        with col4:
            if st.button("NTTM", className="role-button"):
                nttm_admin_landing_page()

        st.markdown("</div>", unsafe_allow_html=True) # Close button-grid
        st.markdown("</div>", unsafe_allow_html=True) # Close container

    # ---  Route to correct dashboard ---
    if st.session_state.logged_in:
        if st.session_state.user_role == "student":
            student_dashboard()
        elif st.session_state.user_role == "company":
            company_dashboard()
        elif st.session_state.user_role == "phdcci":
            phdcci_admin_dashboard()
        elif st.session_state.user_role == "nttm":
            nttm_admin_dashboard()
        else:
            st.error("Unknown user role. Please contact administrator.")

# --- Student Landing Page ---
def student_landing_page():
    st.title("Welcome Students!")
    st.markdown("### Find your dream internship or job")
    st.markdown("Register or Login to get started:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Register", key="student_register"):
            student_register()
    with col2:
        if st.button("Login", key="student_login"):
            student_dashboard()
            st.session_state.logged_in = True
            st.session_state.user_role = "student"

# --- Company Landing Page ---
def company_landing_page():
    st.title("Welcome Companies!")
    st.markdown("### Post your internship/job openings and find the best talent")
    st.markdown("Register or Login to get started:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Register", key="company_register"):
            company_register()
    with col2:
        if st.button("Login", key="company_login"):
            company_dashboard()
            st.session_state.logged_in = True
            st.session_state.user_role = "company"

# --- PHDCCI Admin Landing Page ---
def phdcci_admin_landing_page():
    st.title("Welcome PHDCCI Admin!")
    st.markdown("### Manage the platform")
    if authenticate_admin("PHDCCI"):
        st.session_state.logged_in = True
        st.session_state.user_role = "phdcci"

# --- NTTM Admin Landing Page ---
def nttm_admin_landing_page():
    st.title("Welcome NTTM Admin!")
    st.markdown("### Oversee the internship and placement process")
    if authenticate_admin("NTTM"):
        st.session_state.logged_in = True
        st.session_state.user_role = "nttm"

if __name__ == "__main__":
    main()
