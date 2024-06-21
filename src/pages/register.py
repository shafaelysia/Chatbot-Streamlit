import streamlit as st
from tools.auth import register
from utils.helpers import check_auth, initialize_session

def main():
    initialize_session()

    if check_auth("Register"):
        with st.form("register"):
            st.html("<center><h2>Register</h2></center>")

            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name*")
            with col2:
                last_name = st.text_input("Last Name*")
            username = st.text_input("Username*")
            email = st.text_input("Email*")
            password = st.text_input("Password*", type="password")
            role = st.selectbox("Select Role*", ("Student", "Parent", "Teacher/Staff", "Other"))
            uploaded_file = st.file_uploader("Upload Profile Picture (optional)", ["jpg", "jpeg", "png"])
            st.html("<br/>")

            col1, col2, col3 = st.columns(3)
            with col2:
                if st.form_submit_button("Register", use_container_width=True, type="primary"):
                    if not first_name or not last_name or not username or not email or not password or not role:
                        st.warning("Please fill out all required fields.")
                    else:
                        success, error_message = register(username, email, password, first_name, last_name, uploaded_file, role)
                        if success:
                            st.success("Successfully registered. You can now log in to your account!")
                        else:
                            st.warning(error_message if error_message else "Registration unsuccessful. Please try again.")

        st.page_link("pages/login.py", label="Log in to your account here!")
    else:
        if st.session_state.is_admin:
            st.switch_page("pages/dashboard.py")
        else:
            st.switch_page("pages/home.py")

if __name__ == "__main__":
    st.set_page_config(page_title="Register", page_icon="assets/icon.jpeg", layout="centered")
    main()