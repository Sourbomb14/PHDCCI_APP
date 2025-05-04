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
            confirm_password = st.text_input("Confirm Password", type="password")

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
                          if app['student_email'] == st.session_state.user_id}
        if not my_applications: #fix
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
