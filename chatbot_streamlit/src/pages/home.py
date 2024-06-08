import streamlit as st
from utils.helpers import initialize_session, check_auth, check_session_states
from components.sidebar import sidebar
from tools.chat import display_chat, generate_response, load_llm_model
import random
import time

def main():
    if check_auth("Home"):
        sidebar()

        st.header("Chatbot")
        tab1, tab2= st.tabs(["Chat", "Model Configuration"])
        #root > div:nth-child(1) > div.withScreencast > div > div > div > section.main.st-emotion-cache-bm2z3a.ea3mdgi8 > div.block-container.st-emotion-cache-1eo1tir.ea3mdgi5 > div > div > div > div.stTabs.st-emotion-cache-0.esjhkag0 > div > div:nth-child(1)
        with tab1:
            for message in st.session_state.messages:
                display_chat(message)

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
                    model_config["model_name"] = st.radio("Choose model", ["mistralai/Mistral-7B-Instruct-v0.3", "google/gemma-7b"])
                if st.form_submit_button("Save"):
                    with st.spinner("Loading model..."):
                        st.session_state.llm_model = load_llm_model(model_config)

        if prompt := st.chat_input("Send a message"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with tab1:
                display_chat({"role": "user", "content": prompt})

                with st.spinner("Thinking..."):
                    response=generate_response(prompt, model_config)
                    display_chat({"role": "assistant", "content": response})
            st.session_state.messages.append({"role": "assistant", "content": response})
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
    initialize_session()
    st.set_page_config(page_title="Home", page_icon="", layout="centered")
    main()