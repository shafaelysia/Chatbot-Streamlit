import os
import csv
import logging
import streamlit as st
from datetime import datetime, timezone
from time import time
from langchain_huggingface import ChatHuggingFace
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from datasets import load_dataset
from utils.helpers import authorize_hf
from tools.chat import load_llm_model, load_embedding_model
from tools.rag import get_retriever

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def evaluate_chatbot(model_config):
    logging.info("Starting chatbot evaluation.")
    authorize_hf()
    questions, answers = load_and_extract_conversations("semv/chatbot-sl-test-dataset")
    evaluation_results = []

    for i, (question, expected_answer) in enumerate(zip(questions, answers), start=1):
        logging.info(f"Evaluating question {i}: {question}")

        start_time = time()
        response = simulate_response(question, model_config)
        duration = time() - start_time

        evaluation_results.append({
            "No.": i,
            "Question": question,
            "Response": response,
            "Expected": expected_answer,
            "Time Taken (s)": duration
        })

    logging.info("Evaluation completed. Saving results.")
    return save_results(evaluation_results, model_config)

def load_and_extract_conversations(dataset_name):
    logging.info(f"Loading dataset: {dataset_name}")
    dataset = load_dataset(dataset_name)
    questions = []
    answers = []
    for item in dataset['test']:
        conversation = item['conversations']
        for i in range(len(conversation) - 1):
            if conversation[i]['role'] == 'user' and conversation[i+1]['role'] == 'assistant':
                questions.append(conversation[i]['content'])
                answers.append(conversation[i+1]['content'])
    logging.info(f"Extracted {len(questions)} question-answer pairs.")
    return questions, answers

def save_results(results, model_config):
    filename = "evaluation_results/evaluation_results_" + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + ".csv"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, filename)

    logging.info(f"Saving results to {file_path}")

    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["No.", "Question", "Response", "Expected", "Time Taken (s)"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

        writer.writerow({})
        writer.writerow({"No.": "Model Configuration"})
        for key, value in model_config.items():
            writer.writerow({"No.": key, "Question": value})

        writer.writerow({})
        writer.writerow({"Question": "Date", "Response": datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

    logging.info(f"Evaluation results saved to {file_path}")
    return filename

def simulate_response(prompt, model_config):
    """Generates a response based on the prompt and model configuration."""
    logging.info("Loading embedding model.")
    if st.session_state.embedding_model is None:
        embedding_model = load_embedding_model("firqaaa/indo-sentence-bert-base")
    else:
        embedding_model = st.session_state.embedding_model

    retriever = get_retriever(embedding_model)
    retrieve = {"context": retriever | (lambda docs: "\n\n".join([d.page_content for d in docs])), "question": RunnablePassthrough()}

    context = retrieve["context"].invoke(prompt)

    response = llm_chat_completion(prompt, context, model_config)
    logging.info("Response generated.")
    return response

def llm_chat_completion(prompt, context, model_config):
    """Generates a chat completion response from LLM using the provided prompt and model configuration."""
    logging.info("Loading LLM.")
    if st.session_state.llm_model is None:
        llm_model = load_llm_model(model_config)
    else:
        llm_model = st.session_state.llm_model

    messages = []
    SYSTEM_MESSAGE = """
    Anda adalah chatbot berbahasa Indonesia yang bertugas untuk menjawab pertanyaan terkait SMP Santo Leo III. \
    Gunakan konteks yang diberikan untuk menjawab pertanyaan dengan singkat, komprehensif, dan natural, tanpa menyebutka bahwa Anda diberikan konteks secara eksplisit. \
    Abaikan konteks jika tidak relevan dengan pertanyaan pengguna.
    """
    SYSTEM_MESSAGE_DICT = {"role": "system", "content": SYSTEM_MESSAGE}

    if model_config["model_name"] == "mistralai/Mistral-7B-Instruct-v0.3":
        final_prompt = {
            "role": "user",
            "content": f"{SYSTEM_MESSAGE} \nKonteks: {context} \nBerikut ini adalah pertanyaan yang harus Anda jawab. Pertanyaan: {prompt}"
        }
        messages.append(final_prompt)
    else:
        final_prompt = {
            "role": "user",
            "content": f"Konteks: {context} \nBerikut ini adalah pertanyaan yang harus Anda jawab. Pertanyaan: {prompt}"
        }
        messages.append(SYSTEM_MESSAGE_DICT)
        messages.append(final_prompt)

    response = llm_model.chat_completion(
        messages,
        max_tokens=model_config["max_tokens"],
        temperature=model_config["temperature"],
        top_p=model_config["top_p"],
    )

    return response.choices[0].message.content