import streamlit as st
from PIL import Image
from models.Conversation import Conversation
from services.auth_service import logout
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.ai import AIMessage
from services.inference_service import get_chat_history

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
            if st.session_state.chat_session_id is None or not st.session_state.messages:
                new_chat_button = st.button("New Chat", use_container_width=True, type="primary")
            else:
                new_chat_button = st.button("New Chat", use_container_width=True)

            if new_chat_button:
                st.session_state.chat_session_id = None
                st.session_state.messages = []
                st.rerun()

            for chat in Conversation.get_user_chats({"user_id": st.session_state.user_id}):
                if st.session_state.chat_session_id == chat["session_id"]:
                    chat_button = st.button(chat["title"], use_container_width=True, type="primary")
                else:
                    chat_button = st.button(chat["title"], use_container_width=True)

                if chat_button:
                    st.session_state.chat_session_id = chat["session_id"]
                    st.session_state.messages = []
                    for message in get_chat_history():
                        if isinstance(message, HumanMessage):
                            st.session_state.messages.append({"role": "user", "content": message.content})
                        elif isinstance(message, AIMessage):
                            st.session_state.messages.append({"role": "assistant", "content": message.content})
                    st.rerun()

        with st.container(border=False):
            st.divider()
            if st.button("Logout"):
                logout()
            if st.button("Dashboard"):
                st.switch_page("pages/dashboard.py")