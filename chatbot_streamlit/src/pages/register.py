import streamlit as st
from tools.auth import register
from utils.helpers import initialize_session, check_auth

def main():
    check_auth("Register")

    with st.form("register", clear_on_submit=True):
        st.markdown("#### Register")

        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name*")
        with col2:
            last_name = st.text_input("Last Name*")
        username = st.text_input("Username*")
        email = st.text_input("Email*")
        password = st.text_input("Password*", type="password")
        role = st.selectbox("Role*", ("Student", "Parent", "Teacher/Staff"))
        uploaded_file = st.file_uploader("Upload profile picture (optional)", ["jpg", "jpeg", "png"])

        if st.form_submit_button("Register"):
            if not first_name or not last_name or not username or not email or not password or not role:
                st.warning("Please fill out all required fields.")
            else:
                success, error_message = register(username, email, password, first_name, last_name, uploaded_file, role)
                if success:
                    st.success("Successfully registered. You can now log in to your account!")
                    st.rerun()
                else:
                    st.warning(error_message if error_message else "Registration unsuccessful. Please try again.")

    st.page_link("pages/login.py", label="Login here!")

if __name__ == "__main__":
    initialize_session()
    st.set_page_config(page_title="Register", page_icon="", layout="centered")
    main()