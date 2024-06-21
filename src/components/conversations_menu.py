import streamlit as st
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.ai import AIMessage
from tools.chat import get_all_users_chats, get_chat_session, display_chat
from tools.user import get_all_users
from utils.helpers import clear_chat_states

def conversations_menu():
    users = get_all_users()
    user_options = {user["username"]: user["_id"] for user in users}

    st.subheader("Chats Preview")
    with st.container(border=True, height=500):
        chat_ccol1, chat_col2 = st.columns([0.3, 0.7])
        with chat_ccol1:
            selected_username = st.selectbox("Select User", options=list(user_options.keys()))

            if selected_username:
                selected_user_id = user_options[selected_username]
                if st.session_state.user_preview_id != selected_user_id:
                    st.session_state.user_preview_id = selected_user_id
                    clear_chat_states()
                    st.rerun()

            if st.session_state.user_preview_id is not None:
                if st.session_state.user_preview_id is not None:
                    st.markdown("#### History")
                    for chat in get_all_users_chats({"user_id": st.session_state.user_preview_id}):
                        if st.session_state.chat_session_id == chat["session_id"]:
                            chat_button = st.button(chat["title"], use_container_width=True, type="primary", key=chat["session_id"])
                        else:
                            chat_button = st.button(chat["title"], use_container_width=True, key=chat["session_id"])

                        if chat_button:
                            st.session_state.chat_session_id = chat["session_id"]
                            st.session_state.chat_title = chat["title"]
                            st.session_state.messages = []
                            for message in get_chat_session(st.session_state.chat_session_id).messages:
                                if isinstance(message, HumanMessage):
                                    st.session_state.messages.append({"role": "user", "content": message.content})
                                elif isinstance(message, AIMessage):
                                    st.session_state.messages.append({"role": "assistant", "content": message.content})
                                st.rerun()

        with chat_col2:
            if st.session_state.chat_title is not None:
                st.subheader(st.session_state.chat_title)
                for message in st.session_state.messages:
                    display_chat(message)
            else:
                st.markdown("No chat selected.")