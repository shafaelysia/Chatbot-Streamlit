import streamlit as st
from components.users_menu import users_menu
from components.conversations_menu import conversations_menu
from components.docs_menu import docs_menu
from components.llms_menu import llms_menu
from components.profile_modal import profile_modal
from tools.auth import logout
from utils.helpers import check_auth, initialize_session, clear_chat_states

def main():
    initialize_session()
    clear_chat_states()

    if check_auth("Dashboard"):
        with st.sidebar:
            with st.container(border=False):
                st.image("assets/logo.png")
            with st.container(border=False):
                st.divider()
                st.markdown("## Settings")
                if st.button("Account Details", use_container_width=True):
                    profile_modal(st.session_state.username)
                if st.session_state.is_admin is True:
                    if st.button("Home", use_container_width=True):
                        st.switch_page("pages/home.py")
                if st.button("Logout", use_container_width=True):
                    logout()

        st.header("Dashboard")
        tab1, tab2, tab3, tab4 = st.tabs(["Users", "Conversations", "Documents", "LLMs"])

        with tab1:
            users_menu()

        with tab2:
            conversations_menu()

        with tab3:
            docs_menu()

        with tab4:
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
    st.set_page_config(page_title="Dashboard", page_icon="assets/icon.jpeg", layout="wide")
    main()