import streamlit as st
from tools.auth import login
from utils.helpers import initialize_session, check_auth

def main():
    check_auth("Login")

    with st.form("login", clear_on_submit=True):
        st.html("<center><h2>Login</h2></center>")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        st.html("<br/>")

        col1, col2, col3 = st.columns(3)
        with col2:
            if st.form_submit_button("Login", use_container_width=True, type="primary"):
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

    st.page_link("pages/register.py", label="Create an account here!")

if __name__ == "__main__":
    initialize_session()
    st.set_page_config(page_title="Login", page_icon="assets/icon.jpeg", layout="centered")
    main()