import os
import streamlit as st
from models.User import User

USER_IMAGE_DIR = "../../assets/users"

def create_user(user_data):
    return User.create(user_data)

@st.cache_data
def get_one_user(criteria):
    return User.get_one(criteria)

@st.cache_data
def get_all_users():
    return User.get_all()

def update_user(criteria, user_data):
    return User.update(criteria, user_data)

def delete_user(criteria):
    return User.delete(criteria)

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