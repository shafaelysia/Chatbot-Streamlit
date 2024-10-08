import os
import streamlit as st
from models.User import User
from utils.helpers import hash_password, check_password

USER_IMAGE_DIR = "../../assets/users"

def create_user(user_data):
    """Creates a new user and saves their profile picture if provided."""
    if user_data["picture_path"] != "" and user_data["picture_path"] is not None:
        picture_path = save_picture(user_data["picture_path"], user_data["username"])
        user_data["picture_path"] = picture_path
    return User.create(user_data)

@st.cache_data(show_spinner=False)
def get_one_user(criteria):
    """Retrieves one user based on the given criteria."""
    return User.get_one(criteria)

@st.cache_data(show_spinner=False)
def get_all_users():
    """Retrieves all users."""
    return User.get_all()

def update_user(criteria, new_data):
    """Updates user data based on the given criteria."""
    return User.update(criteria, new_data)

def delete_user(criteria, user_data):
    """Deletes a user and their profile picture if it exists."""
    if (user_data["picture_path"] != "" and user_data["picture_path"] is not None):
        delete_picture(user_data["picture_path"])
    return User.delete(criteria)

def change_password(user_data, old_password, new_password):
    """Changes the user's password if the old password matches."""
    if check_password(old_password, user_data["password"]):
        hashed_password = hash_password(new_password)
        user_data["password"] = hashed_password
        return update_user({"username": user_data["username"]}, user_data)
    else:
        return False

def change_picture(uploaded_file, user_data):
    """Changes the user's profile picture."""
    picture_path = update_picture(user_data["picture_path"], uploaded_file, user_data["username"])
    user_data["picture_path"] = picture_path
    return update_user({"username": user_data["username"]}, user_data)

def remove_picture(user_data):
    """Removes the user's profile picture."""
    delete_picture(user_data["picture_path"])
    user_data["picture_path"] = None
    return update_user({"username": user_data["username"]}, user_data)

def save_picture(uploaded_file, username):
    """Saves an uploaded picture to the USER_IMAGE_DIR directory."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        abs_dir_path = os.path.join(current_dir, USER_IMAGE_DIR)
        os.makedirs(abs_dir_path, exist_ok=True)

        file_extension = uploaded_file.name.split('.')[-1]
        file_path = os.path.join(abs_dir_path, f"{username}.{file_extension}")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        return f"{username}.{file_extension}"
    except Exception as e:
        st.error(f"Failed to save picture: {e}")
        return None

def delete_picture(filename):
    """Delete a picture from the USER_IMAGE_DIR directory."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        abs_dir_path = os.path.join(current_dir, USER_IMAGE_DIR)

        file_path = os.path.join(abs_dir_path, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        st.error(f"Failed to delete picture: {e}")

def update_picture(old_path, new_file, username):
    """Updates the user's profile picture."""
    if old_path is not None and old_path != "":
        delete_picture(old_path)
    return save_picture(new_file, username)