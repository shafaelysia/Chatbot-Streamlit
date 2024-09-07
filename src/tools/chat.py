import uuid
import streamlit as st
from datetime import datetime, timezone
from huggingface_hub import InferenceClient
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain_core.runnables import RunnablePassthrough
from langchain_huggingface import HuggingFaceEmbeddings
from models.Conversation import Conversation
from tools.rag import get_retriever
from utils.helpers import convert_image_to_base64

def create_chat(chat_data):
    """Creates a new conversation."""
    return Conversation.create(chat_data)

@st.cache_data(show_spinner=False)
def get_one_chat(criteria):
    """Retrieves one conversation based on given criteria."""
    return Conversation.get_one(criteria)

def get_all_users_chats(criteria):
    """Retrieves all user's conversations based on given criteria."""
    return Conversation.get_user_chats(criteria)

def update_chat_title(criteria, chat_title):
    """Updates a conversation's title based on given criteria."""
    return Conversation.update_title(criteria, chat_title)

def update_chat_updated_at(criteria):
    """Updates a conversation's updated_at based on given criteria."""
    return Conversation.update_updated_at(criteria)

def delete_chat(criteria):
    """Deletes a conversation based on given criteria."""
    return Conversation.delete(criteria)

def generate_session_id():
    """Generates a new unique session ID."""
    return str(uuid.uuid4())

def display_chat(message):
    """Displays a chat message using Streamlit based on the message role and profile picture."""
    if (message["role"] == "user") and st.session_state.profile_picture not in [None, ""]:
        return st.chat_message(message["role"], avatar=convert_image_to_base64(st.session_state.profile_picture)).markdown(message["content"])
    else:
        return st.chat_message(message["role"]).markdown(message["content"])

def generate_response(prompt, model_config):
    """Generates a response based on the prompt and model configuration."""
    if st.session_state.chat_session_id is None:
        session_id = generate_session_id()
        st.session_state.chat_session_id = session_id
        existing_chat = get_one_chat({"session_id": session_id})
        if existing_chat is None:
            chat_data = {
                "user_id": st.session_state.user_id,
                "title": prompt,
                "session_id": session_id,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
            create_chat(chat_data)

    if st.session_state.embedding_model is None:
        embedding_model = load_embedding_model("firqaaa/indo-sentence-bert-base")
    else:
        embedding_model = st.session_state.embedding_model

    retriever = get_retriever(embedding_model)
    retrieve = {"context": retriever | (lambda docs: "\n\n".join([d.page_content for d in docs])), "question": RunnablePassthrough()}

    context = retrieve["context"].invoke(prompt)

    response = llm_chat_completion(prompt, context, model_config)
    insert_chat_session(st.session_state.chat_session_id, {"user": prompt, "ai": response})
    return response

def llm_chat_completion(prompt, context, model_config):
    """Generates a chat completion response from LLM using the provided prompt and model configuration."""
    if st.session_state.llm_model is None:
        llm_model = load_llm_model(model_config)
    else:
        llm_model = st.session_state.llm_model

    system_message = st.session_state.messages[0]["content"]
    messages = []

    if model_config["model_name"] == "mistralai/Mistral-7B-Instruct-v0.3":
        final_prompt = {
            "role": "user",
            "content": f"{system_message} \nKonteks: {context} \nBerikut ini adalah pertanyaan yang harus Anda jawab. Pertanyaan: {prompt}"
        }

        if len(st.session_state.messages) > 7:
            system_prompt = st.session_state.messages[0]
            last_six_messages = st.session_state.messages[-7:]
            messages = [system_prompt] + last_six_messages
        else:
            messages = st.session_state.messages[1:]
    else:
        final_prompt = {
            "role": "user",
            "content": f"\nKonteks: {context} \nBerikut ini adalah pertanyaan yang harus Anda jawab. Pertanyaan: {prompt}"
        }

        if len(st.session_state.messages) > 7:
            last_six_messages = st.session_state.messages[-7:]
            messages = last_six_messages
        else:
            messages = st.session_state.messages

    messages_copy = messages.copy()
    messages_copy[-1] = final_prompt

    response = llm_model.chat_completion(
        messages_copy,
        max_tokens=model_config["max_tokens"],
        temperature=model_config["temperature"],
        top_p=model_config["top_p"],
    )

    return response.choices[0].message.content

@st.cache_resource(show_spinner=False)
def get_chat_session(session_id):
    """Retrieves a chat session history from the database based on the session ID."""
    return MongoDBChatMessageHistory(
        session_id=session_id,
        connection_string=st.secrets.mongo.MONGODB_ATLAS_CLUSTER_URI,
        database_name="chatbot_db",
        collection_name="chat_histories",
    )

def insert_chat_session(session_id, messages):
    """Inserts user and chatbot messages into the database."""
    chat_message_history = MongoDBChatMessageHistory(
        session_id=session_id,
        connection_string=st.secrets.mongo.MONGODB_ATLAS_CLUSTER_URI,
        database_name="chatbot_db",
        collection_name="chat_histories",
    )

    chat_message_history.add_user_message(messages["user"])
    chat_message_history.add_ai_message(messages["ai"])

@st.cache_resource(show_spinner=False)
def load_llm_model(model_config):
    """Loads the large language model (LLM) based on the provided model configuration."""
    return InferenceClient(
        model_config["model_name"],
        token=st.secrets.hf.HUGGINGFACEHUB_API_TOKEN
    )

@st.cache_resource(show_spinner=False)
def load_embedding_model(model_name):
    """Loads the large embedding model based on the provided model name."""
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}

    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )