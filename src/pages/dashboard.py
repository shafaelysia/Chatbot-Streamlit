import streamlit as st
from components.users_menu import users_menu
from components.docs_menu import docs_menu
from components.llms_menu import llms_menu
from tools.auth import logout
from utils.helpers import initialize_session, check_auth, check_session_states
from components.profile_modal import profile_modal

def main():
    if check_auth("Dashboard"):
        with st.sidebar:
            with st.container(border=False):
                st.image("assets/LOGO.PNG")
            with st.container(border=False):
                st.divider()
                with st.popover("Settings", use_container_width=True):
                    if st.button("Account Details", use_container_width=True):
                        profile_modal(st.session_state.username)
                    if st.session_state.is_admin is True:
                        if st.button("Home", use_container_width=True):
                            st.switch_page("pages/home.py")
                    if st.button("Logout", use_container_width=True):
                        logout()

        st.header("Dashboard")
        tab1, tab2, tab3 = st.tabs(["Users", "Documents", "LLMs"])

        with tab1:
            users_menu()

        with tab2:
            docs_menu()

        with tab3:
            llms_menu()

    else:
        if not st.session_state.is_authenticated:
            st.warning("You need to log in first!")
            if st.button("Back"):
                st.switch_page("app.py")
        elif not st.session_state.is_admin:
            st.warning("You need to log in as administrator")
            if st.button("Back"):
                st.switch_page("pages/home.py")

if __name__ == "__main__":
    initialize_session()
    st.set_page_config(page_title="Dashboard", page_icon="", layout="wide")
    main()