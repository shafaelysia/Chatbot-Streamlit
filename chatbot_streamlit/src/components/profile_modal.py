import streamlit as st
from datetime import datetime, timezone
from tools.user import get_one_user, update_user, change_password, remove_picture, change_picture
from utils.helpers import convert_image_to_base64

@st.experimental_dialog("User Details", width="large")
def profile_modal(username):
    user_data = get_one_user({"username": username})

    with st.form("edit_user", clear_on_submit=True):
        col1, col2 = st.columns([0.3, 0.7])
        with col1:
            st.markdown("Profile Picture")
            if user_data["picture_path"] == "" or user_data["picture_path"] is None:
                with st.container(height=150, border=True):
                    st.markdown("No picture yet.")
            else:
                st.image(convert_image_to_base64(user_data["picture_path"]), use_column_width=True)

            with st.popover("Change profile picture"):
                uploaded_file = st.file_uploader("Update Picture", ["jpg", "jpeg", "png"])
                if st.form_submit_button("Save Picture", type="primary"):
                    if change_picture(uploaded_file, user_data):
                        st.cache_data.clear()
                        st.rerun()

            if user_data["picture_path"] is not None and user_data["picture_path"] != "":
                if st.form_submit_button("Remove Picture", use_container_width=True, type="primary"):
                    remove_picture(user_data)
                    st.cache_data.clear()
                    st.rerun()

        with col2:
            st.text_input("User ID", value=user_data["_id"], disabled=True)
            username = st.text_input("Username", value=user_data["username"])
            email = st.text_input("Email", value=user_data["email"])

            name_col1, name_col2 = st.columns(2)
            with name_col1:
                first_name = st.text_input("First Name", value=user_data["first_name"])
            with name_col2:
                last_name = st.text_input("Last Name", value=user_data["last_name"])

            role = st.selectbox("User Role", options=["Student", "Teacher / Staff", "Parent"])
            role = user_data["role"]

            btn_col1, btn_col2= st.columns(2)
            with btn_col1:
                with st.popover("Change Password", use_container_width=True):
                    old_password = st.text_input("Old Password", type="password")
                    new_password = st.text_input("New Password", type="password")
                    if st.form_submit_button("Save Password"):
                        if change_password(user_data, old_password, new_password):
                            st.success("Password changed!")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("Old password is incorrect!")
            with btn_col2:
                if st.form_submit_button("Save Changes", use_container_width=True, type="primary"):
                    new_data = {
                        "username": username,
                        "email": email,
                        "password": user_data["password"],
                        "first_name": first_name,
                        "last_name": last_name,
                        "picture_path": user_data["picture_data"],
                        "role": role,
                        "is_admin": user_data["is_admin"],
                        "created_at": user_data["created_at"],
                        "updated_at": datetime.now(timezone.utc),
                        "last_login": user_data["last_login"]
                    }
                    if update_user({"username": username}, new_data):
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Error in updating user data!")