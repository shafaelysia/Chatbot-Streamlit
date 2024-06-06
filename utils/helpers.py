import bcrypt
import streamlit as st
import pytz
import os
from models.Conversation import Conversation

USER_IMAGE_DIR = "assets/users/"

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

    if 'chosen_chat' not in st.session_state:
        st.session_state.chosen_chat = None

def clear_session():
    del st.session_state.is_authenticated
    del st.session_state.role
    del st.session_state.is_admin
    del st.session_state.username
    del st.session_state.user_id
    del st.session_state.chosen_chat

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
    st.write("chosen_chat:  " + str(st.session_state.chosen_chat))

def convert_to_local(utc_dt):
    local_tz = pytz.timezone("YOUR_TIMEZONE")  # e.g., "America/New_York"
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)

def save_picture(uploaded_file, username):
    try:
        os.makedirs(USER_IMAGE_DIR, exist_ok=True)

        file_extension = uploaded_file.name.split('.')[-1]
        file_path = os.path.join(USER_IMAGE_DIR, f"{username}.{file_extension}")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        return file_path
    except Exception as e:
        st.error(f"Failed to save picture: {e}")
        return None

def delete_picture(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        st.error(f"Failed to delete picture: {e}")

def update_picture(old_path, new_file, username):
    delete_picture(old_path)
    return save_picture(new_file, username)

def display_chat(sender, content):
    with st.chat_message(sender):
        st.write(content)

def show_chat_history():
    chat_history = Conversation.get_one_chat({"title": st.session_state.chosen_chat})
    for message in chat_history.messages:
        display_chat("user", message.prompt)
        display_chat("assistant", message.response)