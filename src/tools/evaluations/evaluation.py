import os
import csv
import logging
import streamlit as st
from datetime import datetime, timezone
from langchain_huggingface import ChatHuggingFace
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from datasets import load_dataset
from utils.helpers import authorize_hf
from tools.chat import load_llm_model, load_embedding_model
from tools.rag import get_retriever

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def evaluate_chatbot(model_config):
    logging.info("Starting chatbot evaluation.")
    authorize_hf()
    questions, answers = load_and_extract_conversations("semv/sl-dataset")
    evaluation_results = []

    for i, (question, expected_answer) in enumerate(zip(questions, answers), start=1):
        logging.info(f"Evaluating question {i}: {question}")
        response = simulate_response(question, model_config)
        evaluation_results.append({
            "No.": i,
            "Question": question,
            "Response": response,
            "Expected": expected_answer,
        })

    logging.info("Evaluation completed. Saving results.")
    return save_results(evaluation_results, model_config)

def load_and_extract_conversations(dataset_name):
    logging.info(f"Loading dataset: {dataset_name}")
    dataset = load_dataset(dataset_name)
    questions = []
    answers = []
    for item in dataset['train']:
        conversation = item['conversations']
        for i in range(len(conversation) - 1):
            if conversation[i]['role'] == 'user' and conversation[i+1]['role'] == 'assistant':
                questions.append(conversation[i]['content'])
                answers.append(conversation[i+1]['content'])
    logging.info(f"Extracted {len(questions)} question-answer pairs.")
    return questions, answers

def save_results(results, model_config):
    filename = "evaluation_results/evaluation_results_" + datetime.now(timezone.utc).strftime('%Y-%m-%d_%H-%M-%S') + ".csv"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, filename)

    logging.info(f"Saving results to {file_path}")

    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["No.", "Question", "Response", "Expected"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result)

        writer.writerow({})
        writer.writerow({"No.": "Model Configuration"})
        for key, value in model_config.items():
            writer.writerow({"No.": key, "Question": value})

        writer.writerow({})
        writer.writerow({"Question": "Date", "Response": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')})

    logging.info(f"Evaluation results saved to {file_path}")
    return filename

def simulate_response(prompt, model_config):
    logging.info("Simulating response for the prompt.")
    if st.session_state.llm_model is None:
        logging.info("Loading LLM model.")
        llm_model = load_llm_model(model_config)
    else:
        llm_model = st.session_state.llm_model

    if st.session_state.embedding_model is None:
        logging.info("Loading embedding model.")
        embedding_model = load_embedding_model("sentence-transformers/all-MiniLM-L6-v2")
    else:
        embedding_model = st.session_state.embedding_model

    retriever = get_retriever(embedding_model)
    retrieve = {"context": retriever | (lambda docs: "\n\n".join([d.page_content for d in docs])), "question": RunnablePassthrough()}

    template = """Anda adalah chatbot yang bertugas untuk menjawab pertanyaan terkait SMP Santo Leo III. Berikut ini diberikan konteks yang mungkin relevan dengan pertanyaan. Abaikan konteks jika tidak relevan dengan pertanyaan. Beri tanggapan yang singkat dan komprehensif terhadap pertanyaan pengguna dan jangan katakan kepada pengguna bahwa Anda menerima konteks. Konteks: \
    {context}

    Pertanyaan: {question}
    """
    final_prompt = ChatPromptTemplate.from_template(template)

    parse_output = StrOutputParser()
    naive_rag_chain = (
        retrieve
        | final_prompt
        | ChatHuggingFace(llm=llm_model)
        | parse_output
    )

    response = naive_rag_chain.invoke(prompt)
    logging.info("Response generated.")
    return response