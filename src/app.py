import streamlit as st
from utils.helpers import initialize_session
from tools.chat import load_llm_model, load_embedding_model

def main():
    initialize_session()

    with st.spinner("Please wait..."):
        model_config = {
                "model_name": "meta-llama/Meta-Llama-3-8B-Instruct",
                "temperature": 1.0,
                "top_p": 0.8,
                "max_tokens": 4000
        }
        if st.session_state.llm_model is None:
            st.session_state.llm_model = load_llm_model(model_config)

        if st.session_state.embedding_model is None:
            st.session_state.embedding_model = load_embedding_model("firqaaa/indo-sentence-bert-base")

    st.switch_page("pages/login.py")

if __name__ == "__main__":
    main()