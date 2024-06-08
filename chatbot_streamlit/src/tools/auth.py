import streamlit as st
from utils.helpers import check_password, clear_session
from tools.user import get_one_user, create_user, save_picture

def login(username, password):
    user = get_one_user({"username": username})

    if user is not None and check_password(password, user.password):
        st.session_state.username = user.username
        st.session_state.user_id = user._id
        st.session_state.role = user.role
        st.session_state.is_admin = user.is_admin
        st.session_state.is_authenticated = True
        return True

    return False

def logout():
    clear_session()
    st.switch_page("app.py")

def register(username, email, password, first_name, last_name, uploaded_file, role):
    picture_path = ""
    if uploaded_file:
        picture_path = save_picture(uploaded_file, username)

    user_data = {
        "username": username,
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "picture_path": picture_path,
        "role": role,
        "is_admin": False
    }
    success, error_message = create_user(user_data)
    return success, error_message