import streamlit as st
import huggingface_hub
from services.documents_service import retrieve_documents
from langchain_huggingface import HuggingFaceEndpoint
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from langchain_community.embeddings import HuggingFaceEmbeddings
from services.db import get_collection
from models.Conversation import Conversation

# prompt
# chat history
# rag
# final prompt
# llm inference

# @st.cache_data
def get_chat_history():
    chat_message_history = MongoDBChatMessageHistory(
        session_id=st.session_state.chat_session_id,
        connection_string=st.secrets.mongo.MONGODB_ATLAS_CLUSTER_URI,
        database_name="chatbot_db",
        collection_name="chat_histories",
    )
    return chat_message_history.messages

# @st.cache_resource
# def get_all_user_chats(_criteria):
#     return Conversation.get_user_chats(_criteria)

def generate_response(prompt, model_name, model_config):
    # get the chat history from mongodb
    session_history = get_session_history(st.session_state.chat_session_id)

    # load llm model
    llm_model = get_llm_model(model_name, model_config)

    # generate question chain using session history
    question_chain = get_standalone_question(prompt, llm_model)

    # load embedding model
    embedding_model = get_embedding_model("")

    # generate retriever from mongodb & embedding model
    retriever = get_retriever(embedding_model)

    # generate retriever chain
    retriever_chain = RunnablePassthrough.assign(context=question_chain | retriever | (lambda docs: "\n\n".join([d.page_content for d in docs])))

    # generate rag_prompt
    rag_prompt = get_rag_prompt(prompt, retriever_chain)

    # generate response
    return rag_prompt.invoke({"question": "What is the best movie to watch when sad?"}, {"configurable": {"session_id": "1"}})

@st.cache_resource
def get_llm_model(model_name, model_config):
    return HuggingFaceEndpoint(
        repo_id=model_name,
        streaming=True,
        max_new_tokens=512,
        temperature=model_config["temperature"],
        top_k=model_config["top_k"],
        top_p=model_config["top_p"],
        repetition_penalty=model_config["repetition_penalty"],
        huggingfacehub_api_token=st.secrets.hf.HUGGINGFACEHUB_API_TOKEN,
    )

def get_session_history(session_id: str) -> MongoDBChatMessageHistory:
    return MongoDBChatMessageHistory(st.secrets.mongo.MONGODB_ATLAS_CLUSTER_URI, session_id, database_name="chatbot_db", collection_name="history")

def get_standalone_question(prompt, model):
    standalone_system_prompt = """
    Given a chat history and a follow-up question, rephrase the follow-up question to be a standalone question. \
    Do NOT answer the question, just reformulate it if needed, otherwise return it as is. \
    Only return the final standalone question. \
    """
    standalone_question_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", standalone_system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{prompt}"),
        ]
    )

    parse_output = StrOutputParser()

    return standalone_question_prompt | model | parse_output

def get_retriever(model):
    vectors_collection = get_collection("vectors")
    index_name = "vector_index"

    vector_store = MongoDBAtlasVectorSearch(
        embedding=model,
        collection=vectors_collection,
        index_name=index_name,
    )

    return vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})

def get_rag_prompt(prompt, retriever_chain, model, parse_output, session_history):
    rag_system_prompt = """Answer the question based only on the following context: \
    {context}
    """
    rag_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", rag_system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{prompt}"),
        ]
    )

    # RAG chain
    rag_chain = (
        retriever_chain
        | rag_prompt
        | model
        | parse_output
    )

    # RAG chain with history
    return RunnableWithMessageHistory(
        rag_chain,
        session_history,
        input_messages_key="question",
        history_messages_key="history",
    )

def authorize_hf():
    HUGGINGFACEHUB_API_TOKEN = st.secrets.hf.HUGGINGFACEHUB_API_TOKEN
    huggingface_hub.login(HUGGINGFACEHUB_API_TOKEN)


def inference_zephyr(question, temperature, top_k, top_p, typical_p, repetition_penalty):
    client = huggingface_hub.InferenceClient("HuggingFaceH4/zephyr-orpo-141b-A35b-v0.1")
    messages = [{"role": "system", "content": "Kamu adalah chatbot yang membantu."}
    ]

    messages.append({"role": "user", "content": question})

    response = ""

    for message in client.chat_completion(
        messages,
        max_tokens=512,
        stream=False,
        temperature=temperature,
        top_p=top_p,
    ):
        token = message.choices[0].delta.content

        response += token
        # yield response
    return

def inference_mistral(question, temperature, top_k, top_p, typical_p, repetition_penalty):
    template = """Question: {question}

    Answer: Let's think step by step."""

    prompt = PromptTemplate.from_template(template)

    # repo_id = "HuggingFaceH4/zephyr-orpo-141b-A35b-v0.1"
    repo_id = "mistralai/Mistral-7B-Instruct-v0.3"
    llm = HuggingFaceEndpoint(
        repo_id=repo_id,
        streaming=True,
        max_new_tokens=512,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
        typical_p=typical_p,
        repetition_penalty=repetition_penalty,
        huggingfacehub_api_token=st.secrets.hf.HUGGINGFACEHUB_API_TOKEN,
    )
    llm_chain = prompt | llm
    return llm_chain.invoke({"question": question})

def load_llm_model(model_name):
    if model_name == "HuggingFaceH4/zephyr-orpo-141b-A35b-v0.1":
        return huggingface_hub.InferenceClient(model_name)

def generate_prompt_template(query, embedding_model):
    docs = retrieve_documents(query, embedding_model)
    messages = [
        {
            "role": "system",
            "content": "Kamu adalah chatbot yang bertugas untuk memberikan informasi terkait SMP Santo Leo III. Dengan menggunakan informasi yang terdapat dalam konteks, berikan jawaban yang komprehensif untuk pertanyaan tersebut. Tanggapi hanya pertanyaan yang diajukan, jawaban harus ringkas dan relevan dengan pertanyaan. Jika konteks tidak relevan dengan pertanyaan, abaikan konteks yang diberikan."
        },
        {
            "role": "question",
            "content": f"Konteks: {docs[0].page_content} ---- Sekarang, inilah pertanyaan yang perlu kamu jawab. Pertanyaan: {query}"
        }
    ]
    return messages

def model_inference(messages, model, tokenizer):
    authorize_hf()

    device = "cuda"
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(device)
    generated_ids = model.generate(
        input_ids=model_inputs.input_ids,
        # attention_mask=model_inputs.attention_mask,
        max_new_tokens=512,
        # eos_token_id=tokenizer.eos_token_id,
        top_k=10,
        top_p=0.8,
        temperature=0.8,
        do_sample=True
    )

    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return response
