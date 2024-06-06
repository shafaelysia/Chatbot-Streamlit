import streamlit as st
from pymongo.mongo_client import MongoClient

def get_db_conn():
    MONGODB_ATLAS_CLUSTER_URI = st.secrets.mongo.MONGODB_ATLAS_CLUSTER_URI
    return MongoClient(MONGODB_ATLAS_CLUSTER_URI)

def get_collection(collection_name):
    client = get_db_conn()
    db = client.get_database("chatbot_db")
    return db.get_collection(collection_name)

# def initialize_db():
#     db = get_db()

#     db.users.create_index("username", unique=True)
#     db.messages.create_index([("user_id", 1), ("timestamp", -1)])

#     if db.users.count_documents({}) == 0:
#         db.users.insert_many([
#             {"username": "admin", "password": "adminpass", "role": "admin"},
#             {"username": "user", "password": "userpass", "role": "user"}
#         ])