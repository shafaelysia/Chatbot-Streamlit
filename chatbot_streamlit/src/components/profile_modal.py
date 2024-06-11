import streamlit as st
from datetime import datetime, timezone
from tools.user import get_one_user, update_user
from utils.helpers import convert_image_to_base64

@st.experimental_dialog("User Details", width="large")
def profile_modal(username):
    if "visibility" not in st.session_state:
        st.session_state.visibility = "visible"
        st.session_state.disabled = True

    with st.form("edit_user"):
        user_data = get_one_user({"username": username})

        id = st.text_input("User ID", value=user_data["_id"], disabled=True)
        username = st.text_input("Username", value=user_data["username"], disabled=st.session_state.disabled)
        email = st.text_input("Email", value=user_data["email"], disabled=st.session_state.disabled)
        password = st.text_input("Password", value=user_data["password"], type="password", disabled=st.session_state.disabled)

        name_col1, name_col2 = st.columns(2)
        with name_col1:
            first_name = st.text_input("First Name", value=user_data["first_name"], disabled=st.session_state.disabled)
        with name_col2:
            last_name = st.text_input("Last Name", value=user_data["last_name"], disabled=st.session_state.disabled)

        st.markdown("Profile Picture")
        if user_data["picture_path"] == "" or user_data["picture_path"] is None:
            with st.container(height=150, border=True):
                st.markdown("No picture yet.")
        else:
            st.image(convert_image_to_base64(user_data["picture_path"]), width=150)
        with st.expander("Change profile picture"):
            uploaded_file = st.file_uploader("Update Picture", ["jpg", "jpeg", "png"], disabled=st.session_state.disabled)

        role = st.selectbox("User Role", options=["Student", "Teacher / Staff", "Parent"],disabled=st.session_state.disabled)
        role = user_data["role"]

        btn_col1, btn_col2, btn_col3 = st.columns(3)
        with btn_col1:
            edit_button = st.form_submit_button("Enable Edit", use_container_width=True, type="primary") if st.session_state.disabled else st.form_submit_button("Disable Edit", use_container_width=True, type="primary")
            if edit_button:
                st.session_state.disabled = not st.session_state.disabled
                st.rerun()
        with btn_col2:
            if st.form_submit_button("Submit", use_container_width=True, type="primary"):
                new_data = {
                    "username": username,
                    "email": email,
                    "password": password,
                    "first_name": first_name,
                    "last_name": last_name,
                    "picture_path": uploaded_file if uploaded_file else None,
                    "role": role,
                    "is_admin": user_data["is_admin"],
                    "created_at": user_data["created_at"],
                    "updated_at": datetime.now(timezone.utc),
                    "last_login": user_data["last_login"]
                }
                if update_user({"username": username}, new_data, user_data):
                    st.session_state.disabled = True
                    st.rerun()
                else:
                    st.error("Error in updating user data!")