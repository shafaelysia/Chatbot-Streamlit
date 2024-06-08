import os
from PyPDF2 import PdfReader
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from langchain_community.embeddings import HuggingFaceEmbeddings
from services.db import get_collection

def load_embedding_model(model_name):
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}

    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

def process_pdfs_in_folder(folder_path):
    file_exception = ["Tatib Siswa 23-24.pdf"]
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
    try:
        docs = get_text_chunks(text)
        store_vectors(docs)
    except Exception as e:
        print(f"Error in process_vectors_with_splitter: {e}")

def process_vectors_without_splitter(text):
    try:
        doc = Document(page_content=text, metadata={"source": "local"})
        store_vectors([doc])
    except Exception as e:
        print(f"Error in process_vectors_without_splitter: {e}")

def get_text_chunks(raw_text):
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
            separators=["\n\n", "\n"]
        )
        text_chunks = text_splitter.split_text(raw_text)
        docs = text_splitter.create_documents(text_chunks)
        return docs
    except Exception as e:
        print(f"Error in get_text_chunks: {e}")
        return []

def store_vectors(text_chunks):
    try:
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
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

def retrieve_documents(query, embedding_model):
    vectors_collection = get_collection("vectors")
    index_name = "vector_index"

    vector_store = MongoDBAtlasVectorSearch(
        embedding=embedding_model,
        collection=vectors_collection,
        index_name=index_name,
    )

    return vector_store.max_marginal_relevance_search(query, K=1)

def delete_vectors():
    try:
        vectors_collection = get_collection("vectors")
        vectors_collection.deleteMany({})
    except Exception as e:
        raise Exception("Failed to delete vectors!") from e