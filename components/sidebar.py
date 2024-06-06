import streamlit as st
from PIL import Image
from models.Conversation import Conversation
from services.auth_service import logout

def sidebar():
    with st.sidebar:
        with st.container(border=False):
            col1, col2 = st.columns([0.3, 0.7])
            with col1:
                st.image("assets/logo.jpeg", width=50)
            with col2:
                st.header("SMP Santo Leo III")
            st.divider()

        with st.container(height=500, border=False):
            if st.button("New Chat"):
                st.session_state.chosen_chat = None
            chat_titles = Conversation.get_all_chat_titles({"user_id": st.session_state.user_id})
            for chat_title in chat_titles:
                if st.button(chat_title):
                    st.session_state.chosen_chat = chat_title

            if (st.button("Logout")):
                logout()
            if (st.button("Dashboard")):
                st.switch_page("pages/dashboard.py")

        with st.container(height=100, border=False):
            pass