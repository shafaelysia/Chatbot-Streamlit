import streamlit as st
from components.profile_modal import profile_modal
from tools.auth import logout
from tools.chat import get_all_users_chats, get_chat_session
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.ai import AIMessage

def sidebar():
    with st.sidebar:
        with st.container(border=False):
            st.image("assets/logo.png")
            if st.session_state.chat_session_id is None:
                new_chat_button = st.button("New Chat", use_container_width=True, type="primary")
            else:
                new_chat_button = st.button("New Chat", use_container_width=True)
            if new_chat_button:
                st.session_state.chat_session_id = None
                st.session_state.messages = []
                st.session_state.chat_title = None
                st.rerun()

        with st.container(height=250, border=False):
            st.markdown("## History")
            for chat in get_all_users_chats({"user_id": st.session_state.user_id}):
                if st.session_state.chat_session_id == chat["session_id"]:
                    chat_button = st.button(chat["title"], use_container_width=True, type="primary", key=chat["session_id"])
                else:
                    chat_button = st.button(chat["title"], use_container_width=True, key=chat["session_id"])

                if chat_button:
                    st.session_state.chat_session_id = chat["session_id"]
                    st.session_state.chat_title = chat["title"]
                    st.session_state.messages = []

                    chat_session_messages = get_chat_session(st.session_state.chat_session_id)
                    for message in chat_session_messages.messages:
                        if isinstance(message, HumanMessage):
                            st.session_state.messages.append({"role": "user", "content": message.content})
                        elif isinstance(message, AIMessage):
                            st.session_state.messages.append({"role": "assistant", "content": message.content})
                    st.rerun()

        with st.container(border=False):
            st.divider()
            with st.popover("Settings", use_container_width=True):
                if st.button("Account Details", use_container_width=True):
                    profile_modal(st.session_state.username)
                if st.session_state.is_admin is True:
                    if st.button("Dashboard", use_container_width=True):
                        st.switch_page("pages/dashboard.py")
                if st.button("Logout", use_container_width=True):
                    logout()