import os
import streamlit as st
import json
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union, Any
from PyPDF2 import PdfReader
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders.base import BaseLoader
from tools.db import get_collection

DOCS_DIR = "../../assets/pdfs"
JSON_DIR = "../../assets/json"

class JSONLoader(BaseLoader):
    def __init__(
        self,
        file_path: Union[str, Path],
        content_key: Optional[str] = None,
        metadata_func: Optional[Callable[[Dict, Dict], Dict]] = None,
        text_content: bool = True,
        json_lines: bool = False,
    ):
        """
        Initializes the JSONLoader with a file path, an optional content key to extract specific content,
        and an optional metadata function to extract metadata from each record.
        """
        self.file_path = Path(file_path).resolve()
        self._content_key = content_key
        self._metadata_func = metadata_func
        self._text_content = text_content
        self._json_lines = json_lines

    def load(self) -> List[Document]:
        """Load and return documents from the JSON file."""
        docs: List[Document] = []
        if self._json_lines:
            with self.file_path.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self._parse(line, docs)
        else:
            self._parse(self.file_path.read_text(encoding="utf-8"), docs)
        return docs

    def _parse(self, content: str, docs: List[Document]) -> None:
        """Convert given content to documents."""
        data = json.loads(content)

        # Perform some validation
        # This is not a perfect validation, but it should catch most cases
        # and prevent the user from getting a cryptic error later on.
        if self._content_key is not None:
            self._validate_content_key(data)
        if self._metadata_func is not None:
            self._validate_metadata_func(data)

        for i, sample in enumerate(data, len(docs) + 1):
            text = self._get_text(sample=sample)
            metadata = self._get_metadata(sample=sample, source=str(self.file_path), seq_num=i)
            docs.append(Document(page_content=text, metadata=metadata))

    def _get_text(self, sample: Any) -> str:
        """Convert sample to string format"""
        if self._content_key is not None:
            content = sample.get(self._content_key)
        else:
            content = sample

        if self._text_content and not isinstance(content, str):
            raise ValueError(
                f"Expected page_content is string, got {type(content)} instead. \
                    Set `text_content=False` if the desired input for \
                    `page_content` is not a string"
            )

        # In case the text is None, set it to an empty string
        elif isinstance(content, str):
            return content
        elif isinstance(content, dict):
            return json.dumps(content) if content else ""
        else:
            return str(content) if content is not None else ""

    def _get_metadata(self, sample: Dict[str, Any], **additional_fields: Any) -> Dict[str, Any]:
        """
        Return a metadata dictionary base on the existence of metadata_func
        :param sample: single data payload
        :param additional_fields: key-word arguments to be added as metadata values
        :return:
        """
        if self._metadata_func is not None:
            return self._metadata_func(sample, additional_fields)
        else:
            return additional_fields

    def _validate_content_key(self, data: Any) -> None:
        """Check if a content key is valid"""
        sample = data.first()
        if not isinstance(sample, dict):
            raise ValueError(
                f"Expected the jq schema to result in a list of objects (dict), \
                    so sample must be a dict but got `{type(sample)}`"
            )

        if sample.get(self._content_key) is None:
            raise ValueError(
                f"Expected the jq schema to result in a list of objects (dict) \
                    with the key `{self._content_key}`"
            )

    def _validate_metadata_func(self, data: Any) -> None:
        """Check if the metadata_func output is valid"""

        sample = data.first()
        if self._metadata_func is not None:
            sample_metadata = self._metadata_func(sample, {})
            if not isinstance(sample_metadata, dict):
                raise ValueError(
                    f"Expected the metadata_func to return a dict but got \
                        `{type(sample_metadata)}`"
                )

def get_retriever(model):
    vectors_collection = get_collection("vectors")
    index_name = "vector_index"

    vector_store = MongoDBAtlasVectorSearch(
        embedding=model,
        collection=vectors_collection,
        index_name=index_name,
    )

    return vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})

@st.cache_data(show_spinner=False)
def get_all_vectors():
    vectors_collection = get_collection("vectors")
    cursor = vectors_collection.find({})

    vectors = []
    for document in cursor:
        vectors.append({
            "text": document["text"],
        })

    return vectors

def upload_pdf(uploaded_file):
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
    try:
        vectors_collection = get_collection("vectors")
        vectors_collection.delete_many({})
    except Exception as e:
        raise Exception("Failed to delete vectors!") from e

def create_vectors():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    abs_dir_path = os.path.join(current_dir, DOCS_DIR)
    return process_pdfs_in_folder(abs_dir_path)

def create_json_vectors():
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

def load_embedding_model(model_name):
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}

    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )