import streamlit as st
from utils.helpers import initialize_session, check_auth, check_session_states
from components.sidebar import sidebar
from services.inference_service import inference_zephyr, get_chat_history
from utils.helpers import display_chat
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.ai import AIMessage
import random
import time

def main():
    initialize_session()

    if check_auth("Home"):
        sidebar()

        st.header("Chatbot")
        tab1, tab2= st.tabs(["Chat", "Model Configuration"])
        with tab1:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        with tab2:
            TEMPERATURE_RANGE = (0.1, 2.0)
            TOP_K_RANGE = (1, 100)
            TOP_P_RANGE = (0.1, 1.0)
            REPETITION_PENALTY_RANGE = (1.0, 2.0)
            MAX_TOKENS_RANGE = (100, 5000)
            model_config = {
                "model_name": "mistralai/Mistral-7B-Instruct-v0.3",
                "temperature": 1.0,
                "top_k": 50,
                "top_p": 0.8,
                "repetition_penalty": 1.0,
                "max_tokens": 2048
            }

            with st.form("config"):
                col1, col2 = st.columns(2)
                with col1:
                    model_config["temperature"] = st.slider("Temperature", min_value=TEMPERATURE_RANGE[0], max_value=TEMPERATURE_RANGE[1], step=0.01, value=1.0)
                    model_config["top_k"] = st.slider("Top-K Sampling", min_value=TOP_K_RANGE[0], max_value=TOP_K_RANGE[1], step=1, value=50)
                    model_config["top_p"] = st.slider("Top-P (Nucleus) Sampling", min_value=TOP_P_RANGE[0], max_value=TOP_P_RANGE[1], step=0.01, value=0.8)
                    model_config["repetition_penalty"] = st.slider("Repetition Penalty", min_value=REPETITION_PENALTY_RANGE[0], max_value=REPETITION_PENALTY_RANGE[1], step=0.1, value=1.0)
                    model_config["max_tokens"] = st.slider("Max Tokens", min_value=MAX_TOKENS_RANGE[0], max_value=MAX_TOKENS_RANGE[1], step=100, value=2048)

                with col2:
                    model_config["model_name"] = st.radio("Choose model", ["mistralai/Mistral-7B-Instruct-v0.3"])
                st.form_submit_button("Save")

        if prompt := st.chat_input("Send a message"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with tab1.chat_message("user"):
                st.markdown(prompt)

            with tab1.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    time.sleep(5)
                    response=response_generator()
                    st.markdown(response)
            st.session_state.messages.append({"role": "asssistant", "content": response})
    else:
        if not st.session_state.is_authenticated:
            st.warning("You need to log in first!")
            if st.button("Back"):
                st.switch_page("app.py")
        elif st.session_state.is_admin:
            st.warning("You need to log in as user!")
            if st.button("Back"):
                st.switch_page("pages/dashboard.py")

def response_generator():
    time.sleep(3)
    response = random.choice(
        [
            "Hello there! How can I assist you today?",
            "Hi, human! Is there anything I can help you with?",
            "Do you need help?",
        ]
    )
    return response

if __name__ == "__main__":
    st.set_page_config(page_title="Home", page_icon="", layout="centered")
    main()