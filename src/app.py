import streamlit as st
from utils.helpers import initialize_session, check_auth
from tools.chat import load_llm_model, load_embedding_model

def main():
    with st.spinner("Please wait..."):
        model_config = {
                "model_name": "meta-llama/Meta-Llama-3-8B-Instruct",
                "temperature": 1.0,
                "top_k": 50,
                "top_p": 0.8,
                "repetition_penalty": 1.0,
                "max_tokens": 2048
        }
        if st.session_state.llm_model is None:
            st.session_state.llm_model = load_llm_model(model_config)

        if st.session_state.embedding_model is None:
            st.session_state.embedding_model = load_embedding_model("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    check_auth("App")

if __name__ == "__main__":
    initialize_session()
    main()