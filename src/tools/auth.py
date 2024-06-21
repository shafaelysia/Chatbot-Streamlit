import streamlit as st
from datetime import datetime, timezone
from utils.helpers import check_password, clear_session
from tools.user import get_one_user, create_user, save_picture, update_user

def login(username, password):
    """Logs in a user by checking their credentials."""
    user = get_one_user({"username": username})
    if user:
        user_data = {
            "username": username,
            "email": user["email"],
            "password": user["password"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "picture_path": user["picture_path"],
            "role": user["role"],
            "is_admin": user["is_admin"],
            "created_at": user["created_at"],
            "updated_at": user["updated_at"],
            "is_active": True,
            "last_login": user["last_login"]
        }
        update_user({"username": username}, user_data)
    else:
        return False

    if user is not None and check_password(password, user["password"]):
        st.session_state.username = user["username"]
        st.session_state.user_id = user["_id"]
        st.session_state.role = user["role"]
        st.session_state.is_admin = user["is_admin"]
        st.session_state.is_authenticated = True
        st.session_state.profile_picture = user["picture_path"]
        return True
    else:
        return False

def logout():
    """Logs out the current user by clearing the session."""
    user = get_one_user({"username": st.session_state.username})
    if user:
        user_data = {
            "username": user["username"],
            "email": user["email"],
            "password": user["password"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "picture_path": user["picture_path"],
            "role": user["role"],
            "is_admin": user["is_admin"],
            "created_at": user["created_at"],
            "updated_at": user["updated_at"],
            "is_active": False,
            "last_login": datetime.now(timezone.utc)
        }

        update_user({"username": st.session_state.username}, user_data)
        clear_session()

        st.switch_page("app.py")

def register(username, email, password, first_name, last_name, uploaded_file, role):
    """Registers a new user with the provided details."""

    user_data = {
        "username": username,
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "picture_path": uploaded_file,
        "role": role,
        "is_admin": False,
        "is_active": False
    }

    success, error_message = create_user(user_data)
    return success, error_message