import bcrypt
import streamlit as st
import pytz

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def check_password(input_pass, db_pass):
    return bcrypt.checkpw(input_pass.encode("utf-8"), db_pass.encode('utf-8'))

def initialize_session():
    if 'is_authenticated' not in st.session_state:
        st.session_state.is_authenticated = False

    if 'role' not in st.session_state:
        st.session_state.role = None

    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False

    if 'user_id' not in st.session_state:
        st.session_state.user_id = None

    if 'username' not in st.session_state:
        st.session_state.username = None

    if 'chat_session_id' not in st.session_state:
        st.session_state.chat_session_id = None

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    if 'llm_model' not in st.session_state:
        st.session_state.llm_model = None

    if 'embedding_model' not in st.session_state:
        st.session_state.embedding_model = None

def clear_session():
    del st.session_state.is_authenticated
    del st.session_state.role
    del st.session_state.is_admin
    del st.session_state.username
    del st.session_state.user_id
    del st.session_state.chat_session_id
    del st.session_state.messages
    del st.session_state.llm_model
    del st.session_state.embedding_model

def check_auth(page):
    if page in ["Login", "Register"]:
        if st.session_state.is_authenticated:
            if st.session_state.is_admin:
                st.switch_page("pages/dashboard.py")
            else:
                st.switch_page("pages/home.py")
    elif page == "Home":
        if not st.session_state.is_authenticated or st.session_state.is_admin:
            return False
        else:
            return True
    elif page == "Dashboard":
        if not st.session_state.is_authenticated or not st.session_state.is_admin:
            return False
        else:
            return True
    else:
        st.switch_page("pages/login.py")

def check_session_states():
    st.write("is_authenticated: " + str(st.session_state.is_authenticated))
    st.write("is_admin: " + str(st.session_state.is_admin))
    st.write("username: " + str(st.session_state.username))
    st.write("user_id: " + str(st.session_state.user_id))
    st.write("role: " + str(st.session_state.role))
    st.write("chat_session_id:  " + str(st.session_state.chat_session_id))

def convert_to_local(utc_dt):
    local_tz = pytz.timezone("YOUR_TIMEZONE")  # e.g., "America/New_York"
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)