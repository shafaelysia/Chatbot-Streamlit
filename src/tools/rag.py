import os
import streamlit as st
from PyPDF2 import PdfReader
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from tools.JSONLoader import JSONLoader
from tools.db import get_collection

DOCS_DIR = "../../assets/pdfs"
JSON_DIR = "../../assets/json"

def get_retriever(model):
    """Returns a retriever object using the specified embedding model."""
    vectors_collection = get_collection("vectors")
    index_name = "vector_index"

    vector_store = MongoDBAtlasVectorSearch(
        embedding=model,
        collection=vectors_collection,
        index_name=index_name,
    )

    return vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})

@st.cache_data(show_spinner=False)
def get_all_vectors():
    """Retrieves all vectors from the vectors collection."""
    vectors_collection = get_collection("vectors")
    cursor = vectors_collection.find({})

    vectors = []
    for document in cursor:
        vectors.append({
            "text": document["text"],
        })

    return vectors

def upload_pdf(uploaded_file):
    """Save PDF file to the DOCS_DIR directory."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        abs_dir_path = os.path.join(current_dir, DOCS_DIR)
        os.makedirs(abs_dir_path, exist_ok=True)

        file_path = os.path.join(abs_dir_path, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Successfully uploaded {uploaded_file.name}")
    except Exception as e:
        st.error(f"Failed to upload PDF: {e}")

def delete_pdf(filename):
    """Deletes PDF file from the DOCS_DIR directory."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        abs_dir_path = os.path.join(current_dir, DOCS_DIR)

        file_path = os.path.join(abs_dir_path, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            st.success(f"Successfully deleted {filename}")
        else:
            st.warning(f"File {filename} does not exist")
    except Exception as e:
        st.error(f"Failed to delete PDF: {e}")

def upload_json(uploaded_file):
    """Save JSON file to the JSON_DIR directory.."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        abs_dir_path = os.path.join(current_dir, JSON_DIR)
        os.makedirs(abs_dir_path, exist_ok=True)

        file_path = os.path.join(abs_dir_path, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Successfully uploaded {uploaded_file.name}")
    except Exception as e:
        st.error(f"Failed to upload JSON: {e}")

def delete_json(filename):
    """Deletes JSON file from the JSON_DIR directory."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        abs_dir_path = os.path.join(current_dir, JSON_DIR)

        file_path = os.path.join(abs_dir_path, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            st.success(f"Successfully deleted {filename}")
        else:
            st.warning(f"File {filename} does not exist")
    except Exception as e:
        st.error(f"Failed to delete JSON: {e}")

def delete_all_vectors():
    """Deletes all vectors from the vectors collection."""
    try:
        vectors_collection = get_collection("vectors")
        vectors_collection.delete_many({})
    except Exception as e:
        raise Exception("Failed to delete vectors!") from e

def create_vectors():
    """Create vectors from all the PDF files in the DOCS_DIR directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    abs_dir_path = os.path.join(current_dir, DOCS_DIR)
    return process_pdfs_in_folder(abs_dir_path)

def create_json_vectors():
    """Create vectors from all the JSON files in the JSON_DIR directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    abs_dir_path = os.path.join(current_dir, JSON_DIR)

    for filename in os.listdir(abs_dir_path):
        if filename.endswith(".json"):
            loader = JSONLoader(
                file_path=os.path.join(abs_dir_path, filename),
                text_content=False
            )

            data = loader.load()
            store_vectors(data)

def process_pdfs_in_folder(folder_path):
    """Processes all PDF files in the given folder path."""
    file_exception = ["Tatib Siswa 23-24.pdf", "Kalender Akademik 23-24.pdf"]
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, "rb") as f:
                    pdf_reader = PdfReader(f)
                    text = "".join(page.extract_text() for page in pdf_reader.pages)
                if filename in file_exception:
                    process_vectors_with_splitter(text)
                else:
                    process_vectors_without_splitter(text)
            except Exception as e:
                print(f"Error processing file {filename}: {e}")

def process_vectors_with_splitter(text):
    """Processes vectors with text splitting for a given text."""
    try:
        docs = get_text_chunks(text)
        store_vectors(docs)
    except Exception as e:
        print(f"Error in process_vectors_with_splitter: {e}")

def process_vectors_without_splitter(text):
    """Processes vectors without text splitting."""
    try:
        doc = Document(page_content=text, metadata={"source": "local"})
        store_vectors([doc])
    except Exception as e:
        print(f"Error in process_vectors_without_splitter: {e}")

def get_text_chunks(raw_text):
    """Splits raw text into chunks and returns a list of Document objects."""
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        text_chunks = text_splitter.split_text(raw_text)
        docs = text_splitter.create_documents(text_chunks)
        return docs
    except Exception as e:
        print(f"Error in get_text_chunks: {e}")
        return []

def store_vectors(text_chunks):
    """Stores vectors in the database from a list of Document objects."""
    try:
        model_name = "firqaaa/indo-sentence-bert-base"
        embeddings = load_embedding_model(model_name)

        vectors_collection = get_collection("vectors")
        index_name = "vector_index"

        MongoDBAtlasVectorSearch.from_documents(
            documents=text_chunks,
            embedding=embeddings,
            collection=vectors_collection,
            index_name=index_name,
        )
    except Exception as e:
        print(f"Error in store_vectors: {e}")

def load_embedding_model(model_name):
    """Loads the HuggingFace embedding model."""
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}

    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )