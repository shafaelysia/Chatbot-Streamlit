import streamlit as st
from tools.auth import login
from utils.helpers import initialize_session, check_auth

def main():
    check_auth("Login")

    with st.form("login", clear_on_submit=True):
        st.markdown("#### Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.form_submit_button("Login"):
            if not username or not password:
                st.warning("Please fill out the Username and Password fields.")
            else:
                if (login(username, password)):
                    st.success("Login Successful!")
                    if not st.session_state.is_admin:
                        st.switch_page("pages/home.py")
                    else:
                        st.switch_page("pages/dashboard.py")
                else:
                    st.error("Incorrect user credentials!")
        st.page_link("pages/register.py", label="Register here!")

if __name__ == "__main__":
    initialize_session()
    st.set_page_config(page_title="Login", page_icon="", layout="centered")
    main()