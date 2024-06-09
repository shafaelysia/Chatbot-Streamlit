import streamlit as st
from PIL import Image
from tools.auth import logout
from tools.chat import get_all_users_chats, get_chat_history_by_session
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.ai import AIMessage

def sidebar():
    with st.sidebar:
        with st.container(border=False):
            col1, col2 = st.columns([0.3, 0.7])
            with col1:
                st.image("assets/logo.jpeg", width=50)
            with col2:
                st.header("SMP Santo Leo III")
            st.divider()

        with st.container(height=300, border=False):
            if st.session_state.chat_session_id is None:
                new_chat_button = st.button("New Chat", use_container_width=True, type="primary")
            else:
                new_chat_button = st.button("New Chat", use_container_width=True)

            if new_chat_button:
                st.session_state.chat_session_id = None
                st.session_state.messages = []
                st.rerun()

            st.markdown("Chat histories")
            for chat in get_all_users_chats({"user_id": st.session_state.user_id}):
                if st.session_state.chat_session_id == chat["session_id"]:
                    chat_button = st.button(chat["title"], use_container_width=True, type="primary", key=chat["session_id"])
                else:
                    chat_button = st.button(chat["title"], use_container_width=True, key=chat["session_id"])

                if chat_button:
                    st.session_state.chat_session_id = chat["session_id"]
                    st.session_state.messages = []
                    for message in get_chat_history_by_session(st.session_state.chat_session_id):
                        if isinstance(message, HumanMessage):
                            st.session_state.messages.append({"role": "user", "content": message.content})
                        elif isinstance(message, AIMessage):
                            st.session_state.messages.append({"role": "assistant", "content": message.content})
                    st.rerun()

        with st.container(border=False):
            st.divider()
            if st.button("Logout"):
                logout()
            if st.session_state.is_admin is True:
                if st.button("Dashboard"):
                    st.switch_page("pages/dashboard.py")