import streamlit as st
from pymongo.mongo_client import MongoClient

def get_db_conn():
    """Returns a MongoDB client connection."""
    MONGODB_ATLAS_CLUSTER_URI = st.secrets.mongo.MONGODB_ATLAS_CLUSTER_URI
    return MongoClient(MONGODB_ATLAS_CLUSTER_URI)

def get_collection(collection_name):
    """Returns a MongoDB collection."""
    client = get_db_conn()
    db = client.get_database("chatbot_db")
    return db.get_collection(collection_name)