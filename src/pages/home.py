import streamlit as st
from components.sidebar import sidebar
from tools.chat import display_chat, generate_response, load_llm_model, update_chat_title, delete_chat
from utils.helpers import check_auth, initialize_session, clear_chat_states

def main():
    initialize_session()

    if check_auth("Home"):
        sidebar()

        if st.session_state.chat_title is not None:
            title_col1, title_col2 = st.columns([0.8, 0.2])
            with title_col1:
                st.markdown("### " + st.session_state.chat_title)
            with title_col2:
                with st.popover("Edit title", use_container_width=True):
                    with st.form("edit", clear_on_submit=True):
                        new_title = st.text_input("New Title")
                        if st.form_submit_button("Submit"):
                            update_chat_title({"session_id": st.session_state.chat_session_id}, new_title)
                            st.session_state.chat_title = new_title
                            st.rerun()
                if st.button("Delete Chat", use_container_width=True, type="primary"):
                    delete_chat({"session_id": st.session_state.chat_session_id})
                    clear_chat_states()
                    st.rerun()
        else:
            st.markdown("### New Chat")
        tab1, tab2= st.tabs(["Chat", "Model Configuration"])
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
                "model_name": "meta-llama/Meta-Llama-3-8B-Instruct",
                "temperature": 1.0,
                "top_k": 50,
                "top_p": 0.8,
                "repetition_penalty": 1.0,
                "max_tokens": 8000
            }

            with st.form("config"):
                col1, col2 = st.columns(2)
                with col1:
                    model_config["temperature"] = st.slider("Temperature", min_value=TEMPERATURE_RANGE[0], max_value=TEMPERATURE_RANGE[1], step=0.01, value=1.0)
                    model_config["top_k"] = st.slider("Top-K Sampling", min_value=TOP_K_RANGE[0], max_value=TOP_K_RANGE[1], step=1, value=50)
                    model_config["top_p"] = st.slider("Top-P (Nucleus) Sampling", min_value=TOP_P_RANGE[0], max_value=TOP_P_RANGE[1], step=0.01, value=0.8)
                    model_config["repetition_penalty"] = st.slider("Repetition Penalty", min_value=REPETITION_PENALTY_RANGE[0], max_value=REPETITION_PENALTY_RANGE[1], step=0.1, value=1.0)
                    model_config["max_tokens"] = st.slider("Max Tokens", min_value=MAX_TOKENS_RANGE[0], max_value=MAX_TOKENS_RANGE[1], step=100, value=8000)

                with col2:
                    model_config["model_name"] = st.radio("Choose model", ["meta-llama/Meta-Llama-3-8B-Instruct", "mistralai/Mistral-7B-Instruct-v0.3", "HuggingFaceH4/zephyr-7b-beta"])
                if st.form_submit_button("Save"):
                    st.session_state.llm_model = load_llm_model(model_config)

        if prompt := st.chat_input("Send a message"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with tab1:
                display_chat({"role": "user", "content": prompt})

                with st.spinner("Thinking..."):
                    response=generate_response(prompt, model_config)
                    display_chat({"role": "assistant", "content": response})
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.chat_title = prompt

    else:
        if not st.session_state.is_authenticated:
            st.warning("You need to log in first!")
            if st.button("Back"):
                st.switch_page("app.py")

if __name__ == "__main__":
    st.set_page_config(page_title="Home", page_icon="assets/icon.jpeg", layout="centered")
    main()