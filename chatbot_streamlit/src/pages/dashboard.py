import streamlit as st
from services.auth_service import logout
from utils.helpers import initialize_session, check_auth, check_session_states

def main():
    initialize_session()
    if check_auth("Dashboard"):

        st.title("Dashboard")
        check_session_states()

        if (st.button("Logout")):
            logout()
            st.switch_page("app.py")
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
    main()