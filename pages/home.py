import streamlit as st
from utils.helpers import initialize_session, check_auth, check_session_states, show_chat_history
from components.sidebar import sidebar

def main():
    initialize_session()
    st.set_page_config(page_title="Home", page_icon="", layout="wide")

    if check_auth("Home"):
        sidebar()
        st.title("Chatbot")

        if st.session_state.chosen_chat is not None:
            show_chat_history()
        if st.chat_input("Say something"):
            pass
    else:
        if not st.session_state.is_authenticated:
            st.warning("You need to log in first!")
            if st.button("Back"):
                st.switch_page("app.py")
        elif st.session_state.is_admin:
            st.warning("You need to log in as user!")
            if st.button("Back"):
                st.switch_page("pages/dashboard.py")

if __name__ == "__main__":
    main()