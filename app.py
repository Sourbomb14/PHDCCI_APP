import streamlit as st
import pandas as pd
import uuid
import os
import pickle
import datetime
from PIL import Image
import base64
from io import BytesIO
import hashlib
import re

# Set page configuration
st.set_page_config(
    page_title="PHDCCI - NTTM Placement Portal",
    page_icon="🏢",
    layout="wide",
)

# Initialize session state variables if they don't exist
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'page' not in st.session_state:
    st.session_state.page = 'landing'

# Create data directories if they don't exist
os.makedirs('data', exist_ok=True)

# Initialize or load data files
def initialize_or_load_data(filename, default_data):
    filepath = f'data/{filename}'
    if os.path.exists(filepath):
        try:
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            st.error(f"Error loading {filename}: {e}")
            return default_data
    else:
        with open(filepath, 'wb') as f:
            pickle.dump(default_data, f)
        return default_data

# Initialize data stores
students_data = initialize_or_load_data('students.pkl', {})
companies_data = initialize_or_load_data('companies.pkl', {})
applications_data = initialize_or_load_data('applications.pkl', {})
admin_data = initialize_or_load_data('admin.pkl', {
    'phdcci@admin.com': {
        'password': hashlib.sha256('phdcci123'.encode()).hexdigest(),
        'type': 'phdcci'
    },
    'nttm@admin.com': {
        'password': hashlib.sha256('nttm123'.encode()).hexdigest(),
        'type': 'nttm'
    }
})

# Function to save data
def save_data(data, filename):
    with open(f'data/{filename}', 'wb') as f:
        pickle.dump(data, f)

# Custom CSS for better UI
def apply_custom_css():
    st.markdown("""
    <style>
        .main {
            padding: 2rem;
        }
        .stButton>button {
            width: 100%;
            border-radius: 5px;
            height: 3em;
            font-weight: bold;
        }
        .stTextInput>div>div>input {
            border-radius: 5px;
        }
        .stFileUploader>div>div {
            border-radius: 5px;
        }
        .login-container {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header-style {
            text-align: center;
            padding: 1rem;
            margin-bottom: 2rem;
            background-color: #f0f2f6;
            border-radius: 10px;
        }
        .card {
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            background-color: white;
        }
        .application-card {
            padding: 15px;
            border-radius: 5px;
            border: 1px solid #ddd;
            margin-bottom: 10px;
        }
        .highlight {
            background-color: #e8f4f8;
        }
        .success-msg {
            color: #0f5132;
            background-color: #d1e7dd;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .warning-msg {
            color: #856404;
            background-color: #fff3cd;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .admin-actions {
            margin-top: 20px;
            padding: 15px;
            border: 1px solid #ccc;
            border-radius: 5px;
            background-color: #f9f9f9;
        }
    </style>
    """, unsafe_allow_html=True)

# Function to validate email format
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Function to validate Aadhar number
def is_valid_aadhar(aadhar):
    return aadhar.isdigit() and len(aadhar) == 12

# Function to validate phone number
def is_valid_phone(phone):
    return phone.isdigit() and len(phone) == 10

# Function to convert uploaded file to bytes
def file_to_bytes(uploaded_file):
    if uploaded_file is not None:
        return uploaded_file.getvalue()
    return None

# Landing Page
def landing_page():
    st.markdown("<h1 class='header-style'>PHDCCI - NTTM Placement Portal</h1>", unsafe_allow_html=True)

    # Create two columns layout
    col1, col2 = st.columns(2)

    # Left column for the image
    with col1:
        st.image("https://via.placeholder.com/500x300?text=PHDCCI-NTTM+Portal", use_column_width=True)
        st.markdown("""
        <div style='text-align: center; padding: 20px;'>
            <h3>Welcome to the Placement Portal</h3>
            <p>Connecting Students and Companies for Better Opportunities</p>
        </div>
        """, unsafe_allow_html=True)

    # Right column for the buttons
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>Choose Your Role</h2>", unsafe_allow_html=True)

        # Student button
        if st.button("Students", key="student_btn", help="For students looking for opportunities"):
            st.session_state.page = 'student_auth'

        # Company button
        if st.button("Companies", key="company_btn", help="For companies looking to hire talents"):
            st.session_state.page = 'company_auth'

        # PHDCCI Admin button
        if st.button("PHDCCI Admin", key="phdcci_btn", help="For PHDCCI administrators"):
            st.session_state.page = 'phdcci_auth'

        # NTTM Admin button
        if st.button("NTTM Admin", key="nttm_btn", help="For NTTM administrators"):
            st.session_state.page = 'nttm_auth'

        st.markdown("</div>", unsafe_allow_html=True)

# Authentication pages
def student_auth_page():
    st.markdown("<h1 class='header-style'>Student Portal</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        auth_option = st.radio("Select Option:", ("Login", "Register"), horizontal=True)

        if auth_option == "Login":
            email = st.text_input("Email", key="student_login_email")
            password = st.text_input("Password", type="password", key="student_login_password")

            if st.button("Login", key="student_login_btn"):
                if email in students_data and hashlib.sha256(password.encode()).hexdigest() == students_data[email]['password']:
                    st.session_state.logged_in = True
                    st.session_state.user_type = 'student'
                    st.session_state.user_id = email
                    st.session_state.page = 'student_dashboard'
                    st.experimental_rerun()
                else:
                    st.error("Invalid email or password")

        else:  # Register
            with st.form("student_registration_form"):
                name = st.text_input("Full Name")
                email = st.text_input("Email")
                phone = st.text_input("Contact Number (10 digits)")
                qualification = st.selectbox("Qualification",
                                          ["B.Tech", "M.Tech", "BCA", "MCA", "BSc", "MSc", "MBA", "Other"])
                aadhar = st.text_input("Aadhar Number (12 digits)")
                resume = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")

                submitted = st.form_submit_button("Register")

                if submitted:
                    # Validate inputs
                    if not name or not email or not phone or not aadhar or not password:
                        st.error("All fields are required")
                    elif not is_valid_email(email):
                        st.error("Please enter a valid email address")
                    elif not is_valid_phone(phone):
                        st.error("Phone number must be 10 digits")
                    elif not is_valid_aadhar(aadhar):
                        st.error("Aadhar number must be 12 digits")
                    elif password != confirm_password:
                        st.error("Passwords do not match")
                    elif email in students_data:
                        st.error("Email already registered")
                    elif resume is None:
                        st.error("Please upload your resume")
                    else:
                        # Save student data
                        students_data[email] = {
                            'id': str(uuid.uuid4()),
                            'name': name,
                            'email': email,
                            'phone': phone,
                            'qualification': qualification,
                            'aadhar': aadhar,
                            'resume': file_to_bytes(resume),
                            'resume_name': resume.name if resume else "",
                            'password': hashlib.sha256(password.encode()).hexdigest(),
                            'registered_on': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        save_data(students_data, 'students.pkl')

                        st.success("Registration successful! You can now login.")
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Back to Home", key="student_back_btn"):
            st.session_state.page = 'landing'
            st.experimental_rerun()

def company_auth_page():
    st.markdown("<h1 class='header-style'>Company Portal</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        auth_option = st.radio("Select Option:", ("Login", "Register"), horizontal=True)

        if auth_option == "Login":
            email = st.text_input("Email", key="company_login_email")
            password = st.text_input("Password", type="password", key="company_login_password")

            if st.button("Login", key="company_login_btn"):
                if email in companies_data and hashlib.sha256(password.encode()).hexdigest() == companies_data[email]['password']:
                    st.session_state.logged_in = True
                    st.session_state.user_type = 'company'
                    st.session_state.user_id = email
                    st.session_state.page = 'company_dashboard'
                    st.experimental_rerun()
                else:
                    st.error("Invalid email or password")

        else:  # Register
            with st.form("company_registration_form"):
                company_name = st.text_input("Company Name")
                email = st.text_input("Email")
                phone = st.text_input("Contact Number (10 digits)")
                industry = st.selectbox("Industry", [
                    "Information Technology", "Manufacturing", "Healthcare",
                    "Finance", "Education", "Retail", "Real Estate", "Other"
                ])
                company_description = st.text_area("Company Description")
                website = st.text_input("Website URL")
                logo = st.file_uploader("Upload Company Logo (Optional)", type=["jpg", "jpeg", "png"])
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")

                submitted = st.form_submit_button("Register")

                if submitted:
                    # Validate inputs
                    if not company_name or not email or not phone or not company_description or not password:
                        st.error("Required fields cannot be empty")
                    elif not is_valid_email(email):
                        st.error("Please enter a valid email address")
                    elif not is_valid_phone(phone):
                        st.error("Phone number must be 10 digits")
                    elif password != confirm_password:
                        st.error("Passwords do not match")
                    elif email in companies_data:
                        st.error("Email already registered")
                    else:
                        # Save company data
                        companies_data[email] = {
                            'id': str(uuid.uuid4()),
                            'company_name': company_name,
                            'email': email,
                            'phone': phone,
                            'industry': industry,
                            'description': company_description,
                            'website': website,
                            'logo': file_to_bytes(logo) if logo else None,
                            'logo_name': logo.name if logo else "",
                            'password': hashlib.sha256(password.encode()).hexdigest(),
                            'registered_on': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'opportunities': []
                        }
                        save_data(companies_data, 'companies.pkl')

                        st.success("Registration successful! You can now login.")
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Back to Home", key="company_back_btn"):
            st.session_state.page = 'landing'
            st.experimental_rerun()

def admin_auth_page(admin_type):
    st.markdown(f"<h1 class='header-style'>{admin_type.upper()} Admin Portal</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)

        email = st.text_input("Admin Email", key=f"{admin_type}_email")
        password = st.text_input("Password", type="password", key=f"{admin_type}_password")

        if st.button("Login", key=f"{admin_type}_login_btn"):
            # Check if email exists and is of the correct admin type
            if (email in admin_data and
                admin_data[email]['type'] == admin_type and
                hashlib.sha256(password.encode()).hexdigest() == admin_data[email]['password']):

                st.session_state.logged_in = True
                st.session_state.user_type = admin_type
                st.session_state.user_id = email
                st.session_state.page = f'{admin_type}_dashboard'
                st.experimental_rerun()
            else:
                st.error("Invalid email or password")

        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Back to Home", key=f"{admin_type}_back_btn"):
            st.session_state.page = 'landing'
            st.experimental_rerun()

# Dashboard pages
def student_dashboard():
    st.markdown("<h1 class='header-style'>Student Dashboard</h1>", unsafe_allow_html=True)

    # Get current student data
    student = students_data[st.session_state.user_id]

    # Sidebar menu
    with st.sidebar:
        st.markdown(f"<h3>Welcome, {student['name']}!</h3>", unsafe_allow_html=True)
        st.markdown("---")

        menu = st.radio(
            "Navigation",
            ["My Profile", "Browse Companies", "My Applications"]
        )

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_type = None
            st.session_state.user_id = None
            st.session_state.page = 'landing'
            st.experimental_rerun()

    # Main content based on menu selection
    if menu == "My Profile":
        st.subheader("My Profile")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h4>Personal Information</h4>", unsafe_allow_html=True)
            st.markdown(f"**Name:** {student['name']}")
            st.markdown(f"**Email:** {student['email']}")
            st.markdown(f"**Phone:** {student['phone']}")
            st.markdown(f"**Qualification:** {student['qualification']}")
            st.markdown(f"**Aadhar:** {'X' * 8 + student['aadhar'][-4:]}")  # Display only last 4 digits
            st.markdown(f"**Registered on:** {student['registered_on']}")
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h4>Resume</h4>", unsafe_allow_html=True)
            st.markdown(f"**Filename:** {student['resume_name']}")

            # Create a download button for the resume
            if student['resume'] is not None:
                st.download_button(
                    label="Download Resume",
                    data=student['resume'],
                    file_name=student['resume_name'],
                    mime="application/pdf"
                )
            st.markdown("</div>", unsafe_allow_html=True)

        # Edit profile section
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Edit Profile")

        with st.form("edit_student_profile"):
            name = st.text_input("Full Name", value=student['name'])
            phone = st.text_input("Contact Number", value=student['phone'])
            qualification = st.selectbox("Qualification",
                                      ["B.Tech", "M.Tech", "BCA", "MCA", "BSc", "MSc", "MBA", "Other"],
                                      index=["B.Tech", "M.Tech", "BCA", "MCA", "BSc", "MSc", "MBA", "Other"].index(student['qualification']))
            new_resume = st.file_uploader("Upload New Resume (PDF)", type=["pdf"])
            current_password = st.text_input("Current Password (required to save changes)", type="password")
            new_password = st.text_input("New Password (leave blank to keep current)", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")

            submitted = st.form_submit_button("Save Changes")

            if submitted:
                # Validate inputs
                if not name or not phone:
                    st.error("Name and phone number cannot be empty")
                elif not is_valid_phone(phone):
                    st.error("Phone number must be 10 digits")
                elif hashlib.sha256(current_password.encode()).hexdigest() != student['password']:
                    st.error("Current password is incorrect")
                elif new_password and new_password != confirm_password:
                    st.error("New passwords do not match")
                else:
                    # Update student data
                    students_data[st.session_state.user_id]['name'] = name
                    students_data[st.session_state.user_id]['phone'] = phone
                    students_data[st.session_state.user_id]['qualification'] = qualification

                    if new_resume is not None:
                        students_data[st.session_state.user_id]['resume'] = file_to_bytes(new_resume)
                        students_data[st.session_state.user_id]['resume_name'] = new_resume.name

                    if new_password:
                        students_data[st.session_state.user_id]['password'] = hashlib.sha256(new_password.encode()).hexdigest()

                    save_data(students_data, 'students.pkl')
                    st.success("Profile updated successfully!")
                    # Force refresh to show updated data
                    st.experimental_rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "Browse Companies":
        st.subheader("Available Companies and Opportunities")

        if not companies_data:
            st.info("No companies have registered yet.")
        else:
            # Create a list of companies with opportunities
            companies_with_opportunities = {email: company for email, company in companies_data.items()
                                          if 'opportunities' in company and company['opportunities']}

            if not companies_with_opportunities:
                st.info("No companies have posted opportunities yet.")
            else:
                for company_email, company in companies_with_opportunities.items():
                    st.markdown(f"<div class='card'>", unsafe_allow_html=True)

                    # Company header
                    st.markdown(f"<h3>{company['company_name']}</h3>", unsafe_allow_html=True)
                    st.markdown(f"**Industry:** {company['industry']}")
                    st.markdown(f"**Website:** {company['website']}")
                    st.markdown(f"**Description:** {company['description']}")

                    # Opportunities
                    st.markdown("### Opportunities")

                    for idx, opportunity in enumerate(company['opportunities']):
                        st.markdown(f"<div class='application-card'>", unsafe_allow_html=True)
                        st.markdown(f"#### {opportunity['title']}")
                        st.markdown(f"**Type:** {opportunity['type']}")
                        st.markdown(f"**Location:** {opportunity['location']}")
                        st.markdown(f"**Salary/Stipend:** ₹{opportunity['salary']}")
                        st.markdown(f"**Skills Required:** {opportunity['skills']}")
                        st.markdown(f"**Description:** {opportunity['description']}")

                        # Check if the student has already applied to this opportunity
                        opportunity_id = f"{company_email}-{idx}"
                        already_applied = False

                        for app_id, application in applications_data.items():
                            if (application['student_email'] == st.session_state.user_id and
                                application['company_email'] == company_email and
                                application['opportunity_index'] == idx):
                                already_applied = True
                                break

                        if already_applied:
                            st.markdown("<p class='success-msg'>You have already applied for this opportunity</p>", unsafe_allow_html=True)
                        else:
                            if st.button("Apply Now", key=f"apply_{opportunity_id}"):
                                # Create application
                                application_id = str(uuid.uuid4())
                                applications_data[application_id] = {
                                    'id': application_id,
                                    'student_email': st.session_state.user_id,
                                    'company_email': company_email,
                                    'opportunity_index': idx,
                                    'opportunity_title': opportunity['title'],
                                    'applied_on': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'status': 'applied',
                                    'shortlisted': False,
                                    'phdcci_recommendation': None,
                                    'nttm_approval': None
                                }
                                save_data(applications_data, 'applications.pkl')
                                st.success("Application submitted successfully!")
                                st.experimental_rerun()

                        st.markdown("</div>", unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "My Applications":
        st.subheader("My Applications")

        # Filter applications for the current student
        my_applications = {app_id: app for app_id, app in applications_data.items()
                          if app['student_email'] == st.session_state.user_id}if not my_applications:
            st.info("You haven't applied to any opportunities yet.")
        else:
            for app_id, application in my_applications.items():
                company = companies_data[application['company_email']]
                opportunity = company['opportunities'][application['opportunity_index']]

                st.markdown(f"<div class='card'>", unsafe_allow_html=True)

                # Application header
                st.markdown(f"<h3>{opportunity['title']} at {company['company_name']}</h3>", unsafe_allow_html=True)

                # Create two columns for application details
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Application Details:**")
                    st.markdown(f"**Applied on:** {application['applied_on']}")
                    st.markdown(f"**Opportunity Type:** {opportunity['type']}")
                    st.markdown(f"**Location:** {opportunity['location']}")
                    st.markdown(f"**Salary/Stipend:** ₹{opportunity['salary']}")

                with col2:
                    st.markdown("**Application Status:**")

                    # Status indicators based on the application status
                    if application['status'] == 'applied':
                        st.markdown("🟡 **Status:** Under Review")
                    elif application['status'] == 'shortlisted':
                        st.markdown("🟢 **Status:** Shortlisted")
                    elif application['status'] == 'rejected':
                        st.markdown("🔴 **Status:** Not Selected")
                    elif application['status'] == 'selected':
                        st.markdown("🟢 **Status:** Selected")

                    # PHDCCI recommendation status
                    if application['phdcci_recommendation'] is None:
                        st.markdown("🟡 **PHDCCI Recommendation:** Pending")
                    elif application['phdcci_recommendation']:
                        st.markdown("🟢 **PHDCCI Recommendation:** Recommended")
                    else:
                        st.markdown("🔴 **PHDCCI Recommendation:** Not Recommended")

                    # NTTM approval status
                    if application['nttm_approval'] is None:
                        st.markdown("🟡 **NTTM Approval:** Pending")
                    elif application['nttm_approval']:
                        st.markdown("🟢 **NTTM Approval:** Approved")
                    else:
                        st.markdown("🔴 **NTTM Approval:** Not Approved")

                st.markdown("</div>", unsafe_allow_html=True)
def company_dashboard():
    st.markdown("<h1 class='header-style'>Company Dashboard</h1>", unsafe_allow_html=True)

    # Get current company data
    company = companies_data[st.session_state.user_id]

    # Sidebar menu
    with st.sidebar:
        st.markdown(f"<h3>Welcome, {company['company_name']}!</h3>", unsafe_allow_html=True)
        st.markdown("---")

        menu = st.radio(
            "Navigation",
            ["Company Profile", "Manage Opportunities", "View Applications"]
        )

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_type = None
            st.session_state.user_id = None
            st.session_state.page = 'landing'
            st.experimental_rerun()

    # Main content based on menu selection
    if menu == "Company Profile":
        st.subheader("Company Profile")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h4>Company Information</h4>", unsafe_allow_html=True)
            st.markdown(f"**Company Name:** {company['company_name']}")
            st.markdown(f"**Email:** {company['email']}")
            st.markdown(f"**Phone:** {company['phone']}")
            st.markdown(f"**Industry:** {company['industry']}")
            st.markdown(f"**Website:** {company['website']}")
            st.markdown(f"**Registered on:** {company['registered_on']}")
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h4>Company Description</h4>", unsafe_allow_html=True)
            st.write(company['description'])

            # Display logo if available
            if company['logo'] is not None:
                st.markdown("<h4>Company Logo</h4>", unsafe_allow_html=True)
                st.image(company['logo'], width=200)
            st.markdown("</div>", unsafe_allow_html=True)

        # Edit profile section
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Edit Profile")

        with st.form("edit_company_profile"):
            company_name = st.text_input("Company Name", value=company['company_name'])
            phone = st.text_input("Contact Number", value=company['phone'])
            industry = st.selectbox("Industry", [
                "Information Technology", "Manufacturing", "Healthcare",
                "Finance", "Education", "Retail", "Real Estate", "Other"
            ], index=["Information Technology", "Manufacturing", "Healthcare",
                     "Finance", "Education", "Retail", "Real Estate", "Other"].index(company['industry']))
            website = st.text_input("Website URL", value=company['website'])
            description = st.text_area("Company Description", value=company['description'])
            new_logo = st.file_uploader("Upload New Logo (Optional)", type=["jpg", "jpeg", "png"])
            current_password = st.text_input("Current Password (required to save changes)", type="password")
            new_password = st.text_input("New Password (leave blank to keep current)", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")

            submitted = st.form_submit_button("Save Changes")

            if submitted:
                # Validate inputs
                if not company_name or not phone or not description:
                    st.error("Company name, phone number, and description cannot be empty")
                elif not is_valid_phone(phone):
                    st.error("Phone number must be 10 digits")
                elif hashlib.sha256(current_password.encode()).hexdigest() != company['password']:
                    st.error("Current password is incorrect")
                elif new_password and new_password != confirm_password:
                    st.error("New passwords do not match")
                else:
                    # Update company data
                    companies_data[st.session_state.user_id]['company_name'] = company_name
                    companies_data[st.session_state.user_id]['phone'] = phone
                    companies_data[st.session_state.user_id]['industry'] = industry
                    companies_data[st.session_state.user_id]['website'] = website
                    companies_data[st.session_state.user_id]['description'] = description

                    if new_logo is not None:
                        companies_data[st.session_state.user_id]['logo'] = file_to_bytes(new_logo)
                        companies_data[st.session_state.user_id]['logo_name'] = new_logo.name

                    if new_password:
                        companies_data[st.session_state.user_id]['password'] = hashlib.sha256(new_password.encode()).hexdigest()

                    save_data(companies_data, 'companies.pkl')
                    st.success("Profile updated successfully!")
                    st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "Manage Opportunities":
        st.subheader("Manage Opportunities")

        # Display existing opportunities
        if 'opportunities' in company and company['opportunities']:
            st.markdown("<h4>Current Opportunities</h4>", unsafe_allow_html=True)
            for idx, opportunity in enumerate(company['opportunities']):
                st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"<h5>{opportunity['title']}</h5>", unsafe_allow_html=True)
                st.markdown(f"**Type:** {opportunity['type']}")
                st.markdown(f"**Location:** {opportunity['location']}")
                st.markdown(f"**Salary/Stipend:** ₹{opportunity['salary']}")
                st.markdown(f"**Skills Required:** {opportunity['skills']}")
                st.markdown(f"**Description:** {opportunity['description']}")

                # Buttons to edit and delete opportunities.
                col1, col2 = st.columns(2)
                with col1:
                  if st.button("Edit", key=f"edit_opportunity_{idx}"):
                    st.session_state.page = 'edit_opportunity'
                    st.session_state.opportunity_index = idx #store index
                    st.experimental_rerun()
                with col2:
                  if st.button("Delete", key=f"delete_opportunity_{idx}"):
                    del companies_data[st.session_state.user_id]['opportunities'][idx]
                    save_data(companies_data, 'companies.pkl')
                    st.success("Opportunity deleted successfully!")
                    st.experimental_rerun()
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No opportunities posted yet.")

        # Button to add a new opportunity
        if st.button("Add New Opportunity"):
            st.session_state.page = 'add_opportunity'
            st.experimental_rerun()

    elif menu == "View Applications":
        st.subheader("Applications for Your Company")
        
        company_applications = []
        for app_id, application in applications_data.items():
            if application['company_email'] == st.session_state.user_id:
                company_applications.append(application)
        
        if not company_applications:
            st.info("No applications received yet.")
        else:
            for application in company_applications:
                student = students_data[application['student_email']]
                opportunity = company['opportunities'][application['opportunity_index']]
                
                st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"<h4>Application for {opportunity['title']} by {student['name']}</h4>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Student Email:** {student['email']}")
                    st.markdown(f"**Qualification:** {student['qualification']}")
                    st.markdown(f"**Applied On:** {application['applied_on']}")
                    #add a download button
                    if student['resume'] is not None:
                        st.download_button(
                            label="Download Resume",
                            data=student['resume'],
                            file_name=student['resume_name'],
                            mime="application/pdf",
                        )
                with col2:
                    st.markdown("**Application Status:**")
                    if application['status'] == 'applied':
                        st.markdown("🟡 **Status:** Under Review")
                    elif application['status'] == 'shortlisted':
                        st.markdown("🟢 **Status:** Shortlisted")
                    elif application['status'] == 'rejected':
                        st.markdown("🔴 **Status:** Rejected")
                    elif application['status'] == 'selected':
                        st.markdown("🟢 **Status:** Selected")
                    
                    # PHDCCI recommendation status
                    if application['phdcci_recommendation'] is None:
                        st.markdown("🟡 **PHDCCI Recommendation:** Pending")
                    elif application['phdcci_recommendation']:
                        st.markdown("🟢 **PHDCCI Recommendation:** Recommended")
                    else:
                        st.markdown("🔴 **PHDCCI Recommendation:** Not Recommended")
                    
                    # NTTM approval status
                    if application['nttm_approval'] is None:
                        st.markdown("🟡 **NTTM Approval:** Pending")
                    elif application['nttm_approval']:
                        st.markdown("🟢 **NTTM Approval:** Approved")
                    else:
                        st.markdown("🔴 **NTTM Approval:** Not Approved")
                
                # Create three columns for buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Shortlist", key=f"shortlist_{application['id']}"):
                        applications_data[application['id']]['status'] = 'shortlisted'
                        save_data(applications_data, 'applications.pkl')
                        st.success("Student shortlisted!")
                        st.experimental_rerun()
                with col2:
                    if st.button("Reject", key=f"reject_{application['id']}"):
                        applications_data[application['id']]['status'] = 'rejected'
                        save_data(applications_data, 'applications.pkl')
                        st.success("Student rejected!")
                        st.experimental_rerun()
                with col3:
                    if st.button("Select", key=f"select_{application['id']}"):
                        applications_data[application['id']]['status'] = 'selected'
                        save_data(applications_data, 'applications.pkl')
                        st.success("Student selected!")
                        st.experimental_rerun()
                st.markdown("</div>", unsafe_allow_html=True)

def add_opportunity_page():
    st.markdown("<h1 class='header-style'>Add New Opportunity</h1>", unsafe_allow_html=True)
    
    with st.form("add_opportunity_form"):
        title = st.text_input("Job Title")
        type = st.selectbox("Type", ["Internship", "Full-Time", "Part-Time", "Contract"])
        location = st.text_input("Location")
        salary = st.number_input("Salary / Stipend (₹)", min_value=0)
        skills = st.text_input("Skills Required (comma-separated)")
        description = st.text_area("Job Description")
        
        submitted = st.form_submit_button("Add Opportunity")
        
        if submitted:
            # Validate inputs
            if not title or not location or not skills or not description or salary <= 0:
                st.error("All fields are required and salary must be greater than 0")
            else:
                # Get the current company's email
                company_email = st.session_state.user_id
                
                # Create the opportunity dictionary
                new_opportunity = {
                    'title': title,
                    'type': type,
                    'location': location,
                    'salary': salary,
                    'skills': skills,
                    'description': description
                }
                
                # Add the new opportunity to the company's list of opportunities
                if 'opportunities' not in companies_data[company_email]:
                    companies_data[company_email]['opportunities'] = []
                companies_data[company_email]['opportunities'].append(new_opportunity)
                
                # Save the updated data
                save_data(companies_data, 'companies.pkl')
                
                st.success("Opportunity added successfully!")
                st.session_state.page = 'company_dashboard'
                st.experimental_rerun()
    if st.button("Back to Company Dashboard"):
        st.session_state.page = 'company_dashboard'
        st.experimental_rerun()

def edit_opportunity_page():
    st.markdown("<h1 class='header-style'>Edit Opportunity</h1>", unsafe_allow_html=True)
    
    company_email = st.session_state.user_id
    opportunity_index = st.session_state.opportunity_index
    opportunity = companies_data[company_email]['opportunities'][opportunity_index]
    
    with st.form("edit_opportunity_form"):
        title = st.text_input("Job Title", value=opportunity['title'])
        type = st.selectbox("Type", ["Internship", "Full-Time", "Part-Time", "Contract"], 
                           index=["Internship", "Full-Time", "Part-Time", "Contract"].index(opportunity['type']))
        location = st.text_input("Location", value=opportunity['location'])
        salary = st.number_input("Salary / Stipend (₹)", min_value=0, value=opportunity['salary'])
        skills = st.text_input("Skills Required (comma-separated)", value=opportunity['skills'])
        description = st.text_area("Job Description", value=opportunity['description'])
        
        submitted = st.form_submit_button("Save Changes")
        
        if submitted:
            # Validate
            if not title or not location or not skills or not description or salary <= 0:
                st.error("All fields are required and salary must be greater than 0")
            else:
                # Update the opportunity
                companies_data[company_email]['opportunities'][opportunity_index]['title'] = title
                companies_data[company_email]['opportunities'][opportunity_index]['type'] = type
                companies_data[company_email]['opportunities'][opportunity_index]['location'] = location
                companies_data[company_email]['opportunities'][opportunity_index]['salary'] = salary
                companies_data[company_email]['opportunities'][opportunity_index]['skills'] = skills
                companies_data[company_email]['opportunities'][opportunity_index]['description'] = description
                
                # Save
                save_data(companies_data, 'companies.pkl')
                st.success("Opportunity updated")
                st.session_state.page = 'company_dashboard'
                st.experimental_rerun()
    if st.button("Back to Company Dashboard"):
        st.session_state.page = 'company_dashboard'
        st.experimental_rerun()

def phdcci_dashboard():
    st.markdown("<h1 class='header-style'>PHDCCI Admin Dashboard</h1>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("<h3>PHDCCI Admin</h3>", unsafe_allow_html=True)
        st.markdown("---")
        menu = st.radio("Navigation", ["View Applications", "Manage Students", "Manage Companies"])
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_type = None
            st.session_state.user_id = None
            st.session_state.page = 'landing'
            st.experimental_rerun()
    
    if menu == "View Applications":
        st.subheader("Applications")
        
        if not applications_data:
            st.info("No applications found.")
        else:
            for app_id, application in applications_data.items():
                student = students_data[application['student_email']]
                company = companies_data[application['company_email']]
                opportunity = company['opportunities'][application['opportunity_index']]
                
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"<h4>Application by {student['name']} for {opportunity['title']} at {company['company_name']}</h4>", unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**Student Details:**")
                    st.markdown(f"**Email:** {student['email']}")
                    st.markdown(f"**Qualification:** {student['qualification']}")
                    st.markdown(f"**Applied On:** {application['applied_on']}")
                    if student['resume'] is not None:
                        st.download_button(
                            label="Download Resume",
                            data=student['resume'],
                            file_name=student['resume_name'],
                            mime="application/pdf",
                        )
                    
                with col2:
                    st.markdown("**Company Details:**")
                    st.markdown(f"**Company:** {company['company_name']}")
                    st.markdown(f"**Industry:** {company['industry']}")
                    st.markdown(f"**Opportunity:** {opportunity['title']}")
                    
                with col3:
                    st.markdown("**Application Status:**")
                    if application['status'] == 'applied':
                        st.markdown("🟡 **Status:** Under Review")
                    elif application['status'] == 'shortlisted':
                        st.markdown("🟢 **Status:** Shortlisted")
                    elif application['status'] == 'rejected':
                        st.markdown("🔴 **Status:** Rejected")
                    elif application['status'] == 'selected':
                        st.markdown("🟢 **Status:** Selected")
                    
                    st.markdown("**PHDCCI Recommendation:**")
                    if application['phdcci_recommendation'] is None:
                        st.markdown("🟡 Pending")
                    elif application['phdcci_recommendation']:
                        st.markdown("🟢 Recommended")
                    else:
                        st.markdown("🔴 Not Recommended")
                    
                    st.markdown("**NTTM Approval:**")
                    if application['nttm_approval'] is None:
                        st.markdown("🟡 Pending")
                    elif application['nttm_approval']:
                        st.markdown("🟢 Approved")
                    else:
                        st.markdown("🔴 Not Approved")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Recommend", key=f"recommend_{application['id']}"):
                        applications_data[application['id']]['phdcci_recommendation'] = True
                        save_data(applications_data, 'applications.pkl')
                        st.success("Application recommended!")
                        st.experimental_rerun()
                with col2:
                    if st.button("Do Not Recommend", key=f"not_recommend_{application['id']}"):
                        applications_data[application['id']]['phdcci_recommendation'] = False
                        save_data(applications_data, 'applications.pkl')
                        st.success("Application not recommended!")
                        st.experimental_rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)
    
    elif menu == "Manage Students":
        st.subheader("Registered Students")
        
        if not students_data:
            st.info("No students registered yet.")
        else:
            for email, student in students_data.items():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"<h4>{student['name']}</h4>", unsafe_allow_html=True)
                st.markdown(f"**Email:** {student['email']}")
                st.markdown(f"**Phone:** {student['phone']}")
                st.markdown(f"**Qualification:** {student['qualification']}")
                st.markdown(f"**Registered On:** {student['registered_on']}")
                st.markdown("</div>", unsafe_allow_html=True)
    
    elif menu == "Manage Companies":
        st.subheader("Registered Companies")
        
        if not companies_data:
            st.info("No companies registered yet.")
        else:
            for email, company in companies_data.items():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"<h4>{company['company_name']}</h4>", unsafe_allow_html=True)
                st.markdown(f"**Email:** {company['email']}")
                st.markdown(f"**Phone:** {company['phone']}")
                st.markdown(f"**Industry:** {company['industry']}")
                st.markdown(f"**Registered On:** {company['registered_on']}")
                st.markdown("</div>", unsafe_allow_html=True)

def nttm_dashboard():
    st.markdown("<h1 class='header-style'>NTTM Admin Dashboard</h1>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("<h3>NTTM Admin</h3>", unsafe_allow_html=True)
        st.markdown("---")
        menu = st.radio("Navigation", ["View Applications", "Manage Students", "Manage Companies"])
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_type = None
            st.session_state.user_id = None
            st.session_state.page = 'landing'
            st.experimental_rerun()
    
    if menu == "View Applications":
        st.subheader("Applications")
        
        if not applications_data:
            st.info("No applications found.")
        else:
            for app_id, application in applications_data.items():
                student = students_data[application['student_email']]
                company = companies_data[application['company_email']]
                opportunity = company['opportunities'][application['opportunity_index']]
                
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"<h4>Application by {student['name']} for {opportunity['title']} at {company['company_name']}</h4>", unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**Student Details:**")
                    st.markdown(f"**Email:** {student['email']}")
                    st.markdown(f"**Qualification:** {student['qualification']}")
                    st.markdown(f"**Applied On:** {application['applied_on']}")
                    if student['resume'] is not None:
                        st.download_button(
                            label="Download Resume",
                            data=student['resume'],
                            file_name=student['resume_name'],
                            mime="application/pdf",
                        )
                    
                with col2:
                    st.markdown("**Company Details:**")
                    st.markdown(f"**Company:** {company['company_name']}")
                    st.markdown(f"**Industry:** {company['industry']}")
                    st.markdown(f"**Opportunity:** {opportunity['title']}")
                    
                with col3:
                    st.markdown("**Application Status:**")
                    if application['status'] == 'applied':
                        st.markdown("🟡 **Status:** Under Review")
                    elif application['status'] == 'shortlisted':
                        st.markdown("🟢 **Status:** Shortlisted")
                    elif application['status'] == 'rejected':st.markdown("🔴 **Status:** Rejected")
                    elif application['status'] == 'selected':
                        st.markdown("🟢 **Status:** Selected")
                    
                    st.markdown("**PHDCCI Recommendation:**")
                    if application['phdcci_recommendation'] is None:
                        st.markdown("🟡 Pending")
                    elif application['phdcci_recommendation']:
                        st.markdown("🟢 Recommended")
                    else:
                        st.markdown("🔴 Not Recommended")
                    
                    st.markdown("**NTTM Approval:**")
                    if application['nttm_approval'] is None:
                        st.markdown("🟡 Pending")
                    elif application['nttm_approval']:
                        st.markdown("🟢 Approved")
                    else:
                        st.markdown("🔴 Not Approved")
                
                if application['phdcci_recommendation']: # Only allow NTTM to approve if PHDCCI has recommended.
                    if st.button("Approve", key=f"approve_{application['id']}"):
                        applications_data[application['id']]['nttm_approval'] = True
                        save_data(applications_data, 'applications.pkl')
                        st.success("Application approved!")
                        st.experimental_rerun()
                    if st.button("Reject", key=f"reject_nttm_{application['id']}"):
                            applications_data[application['id']]['nttm_approval'] = False
                            save_data(applications_data, 'applications.pkl')
                            st.success("Application rejected!")
                            st.experimental_rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)
    
    elif menu == "Manage Students":
        st.subheader("Registered Students")
        
        if not students_data:
            st.info("No students registered yet.")
        else:
            for email, student in students_data.items():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"<h4>{student['name']}</h4>", unsafe_allow_html=True)
                st.markdown(f"**Email:** {student['email']}")
                st.markdown(f"**Phone:** {student['phone']}")
                st.markdown(f"**Qualification:** {student['qualification']}")
                st.markdown(f"**Registered On:** {student['registered_on']}")
                st.markdown("</div>", unsafe_allow_html=True)
    
    elif menu == "Manage Companies":
        st.subheader("Registered Companies")
        
        if not companies_data:
            st.info("No companies registered yet.")
        else:
            for email, company in companies_data.items():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"<h4>{company['company_name']}</h4>", unsafe_allow_html=True)
                st.markdown(f"**Email:** {company['email']}")
                st.markdown(f"**Phone:** {company['phone']}")
                st.markdown(f"**Industry:** {company['industry']}")
                st.markdown(f"**Registered On:** {company['registered_on']}")
                st.markdown("</div>", unsafe_allow_html=True)

# Main App Function
def main():
    apply_custom_css()
    
    # Check the current page in session state
    if st.session_state.page == 'landing':
        landing_page()
    elif st.session_state.page == 'student_auth':
        student_auth_page()
    elif st.session_state.page == 'company_auth':
        company_auth_page()
    elif st.session_state.page == 'phdcci_auth':
        admin_auth_page('phdcci')
    elif st.session_state.page == 'nttm_auth':
        admin_auth_page('nttm')
    elif st.session_state.page == 'student_dashboard':
        student_dashboard()
    elif st.session_state.page == 'company_dashboard':
        company_dashboard()
    elif st.session_state.page == 'add_opportunity':
        add_opportunity_page()
    elif st.session_state.page == 'edit_opportunity':
        edit_opportunity_page()
    elif st.session_state.page == 'phdcci_dashboard':
        phdcci_dashboard()
    elif st.session_state.page == 'nttm_dashboard':
        nttm_dashboard()

if __name__ == "__main__":
    main()
