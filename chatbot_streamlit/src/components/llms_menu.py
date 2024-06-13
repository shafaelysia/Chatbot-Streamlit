import os
import streamlit as st
from tools.evaluations.evaluation import evaluate_chatbot
from tools.chat import load_llm_model

def llms_menu():
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
        "max_tokens": 2048
    }

    st.subheader("Model Configuration")
    with st.form("config"):
        col1, col2 = st.columns(2)
        with col1:
            model_config["temperature"] = st.slider("Temperature", min_value=TEMPERATURE_RANGE[0], max_value=TEMPERATURE_RANGE[1], step=0.01, value=1.0)
            model_config["top_k"] = st.slider("Top-K Sampling", min_value=TOP_K_RANGE[0], max_value=TOP_K_RANGE[1], step=1, value=50)
            model_config["top_p"] = st.slider("Top-P (Nucleus) Sampling", min_value=TOP_P_RANGE[0], max_value=TOP_P_RANGE[1], step=0.01, value=0.8)
            model_config["repetition_penalty"] = st.slider("Repetition Penalty", min_value=REPETITION_PENALTY_RANGE[0], max_value=REPETITION_PENALTY_RANGE[1], step=0.1, value=1.0)
            model_config["max_tokens"] = st.slider("Max Tokens", min_value=MAX_TOKENS_RANGE[0], max_value=MAX_TOKENS_RANGE[1], step=100, value=2048)

        with col2:
            model_config["model_name"] = st.radio("Choose model", ["meta-llama/Meta-Llama-3-8B-Instruct", "mistralai/Mistral-7B-Instruct-v0.3", "HuggingFaceH4/zephyr-7b-beta"])
        if st.form_submit_button("Save"):
            st.session_state.llm_model = load_llm_model(model_config)

    st.subheader("Model Evaluation")
    if st.button("Evaluate Model Performance", type="primary"):
        csv = evaluate_chatbot(model_config)
        if csv:
            st.success("Model evaluation successful!")
            file_path = os.path.join("tools/evaluatioins", csv)
            with open(file_path, "rb") as f:
                st.download_button("Download CSV", data=f, file_name="evaluation_result.csv")
        else:
            st.error("Model evaluation unsuccessful!")
