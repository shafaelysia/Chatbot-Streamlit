import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from tools.user import get_all_users, get_one_user, create_user, update_user, delete_user, change_password, change_picture, remove_picture
from utils.helpers import convert_image_to_base64

def users_menu():
    users = get_all_users()
    if users:
        user_data_list = []
        for i, user in enumerate(users, start=1):
            user_data = {
                "No": i,
                "Username": user["username"],
                "Email": user["email"],
                "Name": user["first_name"] + ' ' + user["last_name"],
                "Role": user["role"],
                "Picture": convert_image_to_base64(user["picture_path"]) if user["picture_path"] !=  "" else user["picture_path"],
                "Administrator": user["is_admin"],
                "Join Date": user["created_at"],
                "Update Date": user["updated_at"],
                "Last Login": user["last_login"],
                "Active": user["is_active"]
            }
            user_data_list.append(user_data)

        users_df = pd.DataFrame(user_data_list)
        with st.container():
            col1, col2, col3 = st.columns(3)
            with col1.container(border=True):
                num_users = len(users_df)
                st.metric("Total Users", num_users)
            with col2.container(border=True):
                active_users = users_df['Active'].sum()
                st.metric("Active Users", active_users)

        user_event = st.dataframe(
            users_df,
            column_config={
                "Picture": st.column_config.ImageColumn(
                    "Picture", help="Profile Picture"
                ),
                "Join Date": st.column_config.DatetimeColumn(
                    "Join Date",
                    format="D MMM YYYY, h:mm a",
                ),
                "Update Date": st.column_config.DatetimeColumn(
                    "Update Date",
                    format="D MMM YYYY, h:mm a",
                ),
                "Last Login": st.column_config.DatetimeColumn(
                    "Last Login",
                    format="D MMM YYYY, h:mm a",
                ),
            },
            hide_index=True,
            on_select='rerun',
            selection_mode='single-row'
        )

        sub_col1, sub_col2 = st.columns([0.15, 0.85])
        with sub_col1:
            if st.button("Add new user", type="primary"):
                add_modal()
        with sub_col2:
            if st.button("Refresh table"):
                st.cache_data.clear()
                st.rerun()

        if len(user_event.selection['rows']):
            selected_row = user_event.selection['rows'][0]
            username = users_df.iloc[selected_row]['Username']
            details_modal(username)

    else:
        st.error("No users found.")

@st.experimental_dialog("User Details", width="large")
def details_modal(username):
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

            admin = st.toggle("Administrator Privileges", value=user_data["is_admin"])

            btn_col1, btn_col2, btn_col3 = st.columns(3)
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
                        "is_admin": admin,
                        "created_at": user_data["created_at"],
                        "updated_at": datetime.now(timezone.utc),
                        "last_login": user_data["last_login"]
                    }
                    if update_user({"username": username}, new_data):
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Error in updating user data!")
            with btn_col3:
                if st.form_submit_button("Delete", use_container_width=True, type="primary"):
                    delete_user({"username": username}, user_data)
                    st.cache_data.clear()
                    st.rerun()

@st.experimental_dialog("Create New User", width="large")
def add_modal():
    with st.form("add", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name*")
        with col2:
            last_name = st.text_input("Last Name*")
        username = st.text_input("Username*")
        email = st.text_input("Email*")
        password = st.text_input("Password*", type="password")
        role = st.selectbox("Role*", ("Student", "Parent", "Teacher/Staff"))
        uploaded_file = st.file_uploader("Upload profile picture (optional)", ["jpg", "jpeg", "png"])
        admin = st.toggle("Administrator Privileges")

        if st.form_submit_button("Submit", type="primary"):
            if not first_name or not last_name or not username or not email or not password or not role:
                st.warning("Please fill out all required fields.")
            else:
                user_data = {
                    "username": username,
                    "email": email,
                    "password": password,
                    "first_name": first_name,
                    "last_name": last_name,
                    "picture_path": uploaded_file if uploaded_file else None,
                    "role": role,
                    "is_admin": admin,
                }
                success, error_message = create_user(user_data)
                if success:
                    st.success("Successfully created new user!")
                    st.rerun()
                else:
                    st.warning(error_message if error_message else "Failed in creating new user!")