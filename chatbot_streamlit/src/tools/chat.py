import uuid
import streamlit as st
from datetime import datetime
from models.Conversation import Conversation
from tools.rag import get_retriever
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain_huggingface import HuggingFaceEndpoint, HuggingFaceEmbeddings, ChatHuggingFace
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
# from langchain_core.messages.human import HumanMessage
# from langchain_core.messages.ai import AIMessage

def create_chat(chat_data):
    return Conversation.create(chat_data)

@st.cache_data
def get_one_chat(criteria):
    return Conversation.get_one(criteria)

def get_all_users_chats(criteria):
    return list(Conversation.get_user_chats(criteria))

@st.cache_data
def get_all_chats_with_history():
    pass

def update_chat_title(criteria, chat_title):
    return Conversation.update_title(criteria, chat_title)

def update_chat_updated_at(criteria):
    return Conversation.update_updated_at(criteria)

def delete_chat(criteria):
    return Conversation.delete(criteria)

def generate_session_id():
    return str(uuid.uuid4())

def display_chat(message):
    return st.chat_message(message["role"]).markdown(message["content"])

def generate_response(prompt, model_config):
    if st.session_state.chat_session_id is None:
        chain, session_id = generate_response_without_history(prompt, model_config)
        response = chain.invoke(prompt)
        insert_chat_session(session_id, {"user": prompt, "ai": response})
    else:
        chain, session_id = generate_response_with_history(model_config)
        response = chain.invoke({"question": prompt}, {"configurable": {"session_id": session_id}})

    return response

def generate_response_without_history(prompt, model_config):
    session_id = generate_session_id()
    st.session_state.chat_session_id = session_id
    existing_chat = get_one_chat({"session_id": session_id})
    if existing_chat is None:
        chat_data = {
            "user_id": st.session_state.user_id,
            "title": prompt,
            "session_id": session_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        create_chat(chat_data)

    if st.session_state.llm_model is None:
        llm_model = load_llm_model(model_config)
    else:
        llm_model = st.session_state.llm_model

    if st.session_state.embedding_model is None:
        embedding_model = load_embedding_model("sentence-transformers/all-MiniLM-L6-v2")
    else:
        embedding_model = st.session_state.embedding_model

    retriever = get_retriever(embedding_model)
    retrieve = {"context": retriever | (lambda docs: "\n\n".join([d.page_content for d in docs])), "question": RunnablePassthrough()}

    template = """Anda adalah chatbot yang bertugas untuk menjawab pertanyaan terkait SMP Santo Leo III. Berikut ini diberikan konteks yang mungkin relevan dengan pertanyaan. Abaikan konteks jika tidak relevan dengan pertanyaan. Beri tanggapan yang singkat dan komprehensif terhadap pertanyaan pengguna. Konteks: \
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

    return naive_rag_chain, session_id

def generate_response_with_history(model_config):
    session_id = st.session_state.chat_session_id
    update_chat_updated_at({"session_id": session_id})

    if st.session_state.llm_model is None:
        llm_model = load_llm_model(model_config)
    else:
        llm_model = st.session_state.llm_model

    if st.session_state.embedding_model is None:
        embedding_model = load_embedding_model("sentence-transformers/all-MiniLM-L6-v2")
    else:
        embedding_model = st.session_state.embedding_model

    standalone_system_prompt = """
    Dengan riwayat chat dan pertanyaan lanjutan, buat ulang pertanyaan lanjutan menjadi pertanyaan tersendiri.  \
    JANGAN menjawab pertanyaan tersebut, cukup rumuskan ulang jika diperlukan, jika tidak, kembalikan apa adanya. \
    Hanya kembalikan pertanyaan tersendiri yang terakhir. \
    """
    standalone_question_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", standalone_system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ]
    )
    parse_output = StrOutputParser()
    question_chain = standalone_question_prompt | llm_model | parse_output

    retriever = get_retriever(embedding_model)
    retriever_chain = RunnablePassthrough.assign(context=question_chain | retriever | (lambda docs: "\n\n".join([d.page_content for d in docs])))

    rag_system_prompt = """Anda adalah chatbot yang bertugas untuk menjawab pertanyaan terkait SMP Santo Leo III. Berikut ini diberikan konteks yang mungkin relevan dengan pertanyaan. Abaikan konteks jika tidak relevan dengan pertanyaan. Beri tanggapan yang singkat dan komprehensif terhadap pertanyaan pengguna. Konteks: \
        {context}
    """
    rag_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", rag_system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ]
    )
    rag_chain = (
        retriever_chain
        | rag_prompt
        | ChatHuggingFace(llm=llm_model)
        | parse_output
    )

    with_message_history = RunnableWithMessageHistory(
        rag_chain,
        get_chat_session,
        input_messages_key="question",
        history_messages_key="history",
    )

    return with_message_history, session_id


def get_chat_history_by_session(session_id):
    chat_message_history = MongoDBChatMessageHistory(
        session_id=session_id,
        connection_string=st.secrets.mongo.MONGODB_ATLAS_CLUSTER_URI,
        database_name="chatbot_db",
        collection_name="chat_histories",
    )
    return chat_message_history.messages

def get_chat_session(session_id):
    return MongoDBChatMessageHistory(
        session_id=session_id,
        connection_string=st.secrets.mongo.MONGODB_ATLAS_CLUSTER_URI,
        database_name="chatbot_db",
        collection_name="chat_histories",
    )

def insert_chat_session(session_id, messages):
    chat_message_history = MongoDBChatMessageHistory(
        session_id=session_id,
        connection_string=st.secrets.mongo.MONGODB_ATLAS_CLUSTER_URI,
        database_name="chatbot_db",
        collection_name="chat_histories",
    )

    chat_message_history.add_user_message(messages["user"])
    chat_message_history.add_ai_message(messages["ai"])

@st.cache_resource
def load_llm_model(model_config):
    # if model_config["model_name"] == "mistralai/Mistral-7B-Instruct-v0.3":
        return HuggingFaceEndpoint(
            repo_id=model_config["model_name"],
            streaming=True,
            max_new_tokens=512,
            temperature=model_config["temperature"],
            top_k=model_config["top_k"],
            top_p=model_config["top_p"],
            repetition_penalty=model_config["repetition_penalty"],
            huggingfacehub_api_token=st.secrets.hf.HUGGINGFACEHUB_API_TOKEN,
        )

@st.cache_resource
def load_embedding_model(model_name):
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}

    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )