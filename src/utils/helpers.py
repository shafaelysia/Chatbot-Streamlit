import os
import bcrypt
import pytz
import base64
import huggingface_hub
import streamlit as st

SYSTEM_MESSAGE = """
Anda adalah chatbot berbahasa Indonesia yang bertugas untuk menjawab pertanyaan terkait SMP Santo Leo III. \
Gunakan konteks yang diberikan untuk menjawab pertanyaan dengan singkat, komprehensif, dan natural, tanpa menyebutka bahwa Anda diberikan konteks secara eksplisit. \
Abaikan konteks jika tidak relevan.
"""
SYSTEM_MESSAGE_DICT = {"role": "system", "content": SYSTEM_MESSAGE}

def hash_password(password):
    """Hashes a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def check_password(input_pass, db_pass):
    """Checks a password with the hashed password."""
    return bcrypt.checkpw(input_pass.encode("utf-8"), db_pass.encode('utf-8'))

def initialize_session():
    """Initializes session state variables."""
    session_defaults = {
        'is_authenticated': False,
        'role': None,
        'is_admin': False,
        'user_id': None,
        'username': None,
        'profile_picture': None,
        'chat_session_id': None,
        'chat_title': None,
        'messages': [SYSTEM_MESSAGE_DICT],
        'llm_model': None,
        'embedding_model': None,
        'user_preview_id': None
    }

    for key, value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def clear_session():
    """Clears session state variables."""
    session_keys = [
        'is_authenticated',
        'role',
        'is_admin',
        'username',
        'profile_picture',
        'user_id',
        'chat_session_id',
        'chat_title',
        'messages',
        'llm_model',
        'embedding_model',
        'user_preview_id'
    ]

    for key in session_keys:
        if key in st.session_state:
            del st.session_state[key]

def clear_chat_states():
    st.session_state.chat_session_id = None
    st.session_state.messages = [SYSTEM_MESSAGE_DICT]
    st.session_state.chat_title = None

def check_auth(page):
    """Checks if a user is authorized to view a page."""
    if page in ["Login", "Register"]:
        return not st.session_state.is_authenticated
    elif page == "Home":
        return st.session_state.is_authenticated
    elif page == "Dashboard":
        return st.session_state.is_authenticated and st.session_state.is_admin

def convert_to_local(utc_dt):
    """Converts UTC datetime to local timezone."""
    local_tz = pytz.timezone("Asia/Jakarta")
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)

def authorize_hf():
    """Authorizes Hugging Face API using a token."""
    huggingface_hub.login(st.secrets.hf.HUGGINGFACEHUB_API_TOKEN)

def convert_image_to_base64(filename):
    """Converts an image file to base64 string."""
    try:
        path = os.path.join("assets/users", filename)
        with open(path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
            return f"data:image/png;base64,{encoded_string}"
    except Exception as e:
        st.error(f"Error converting image to base64: {e}")
        return ""