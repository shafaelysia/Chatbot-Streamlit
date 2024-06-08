from tools.db import get_collection
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch

def get_retriever(model):
    vectors_collection = get_collection("vectors")
    index_name = "vector_index"

    vector_store = MongoDBAtlasVectorSearch(
        embedding=model,
        collection=vectors_collection,
        index_name=index_name,
    )

    return vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 2})

def retrieve_documents(query, embedding_model):
    vectors_collection = get_collection("vectors")
    index_name = "vector_index"

    vector_store = MongoDBAtlasVectorSearch(
        embedding=embedding_model,
        collection=vectors_collection,
        index_name=index_name,
    )

    return vector_store.max_marginal_relevance_search(query, K=1)