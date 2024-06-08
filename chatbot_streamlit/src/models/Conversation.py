from datetime import datetime
from services.db import get_collection
from utils.helpers import generate_session_id

class Conversation:
    def __init__(self, _id=None, user_id=None, title=None, session_id=None, created_at=None, updated_at=None):
        self._id = _id
        self.user_id = user_id
        self.title = title
        self.session_id = session_id if session_id else generate_session_id()
        self.created_at = created_at if created_at else datetime.datetime.utcnow()
        self.updated_at = updated_at if updated_at else datetime.datetime.utcnow()

    def to_dict(self):
        return {
            "_id": self._id,
            "user_id": self.user_id,
            "title": self.title,
            "session_id": self.session_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def create(cls, conversation_data):
        try:
            new_conversation = cls(**conversation_data)
            conversations_collection = get_collection("conversations")
            result = conversations_collection.insert_one(new_conversation.to_dict())
            return result.inserted_id
        except Exception as e:
            raise Exception("Failed to create new chat!") from e

    @classmethod
    def get_one(cls, criteria):
        try:
            conversations_collection = get_collection("conversations")
            conversation_data = conversations_collection.find_one(criteria)
            if conversation_data:
                return cls(**conversation_data)
            else:
                return None
        except Exception as e:
            raise Exception("Failed to get chat!") from e

    @classmethod
    def get_user_chats(cls, criteria):
        try:
            conversations_collection = get_collection("conversations")
            return conversations_collection.find(criteria)
        except Exception as e:
            raise Exception("Failed to get all user's chats!") from e

    @classmethod
    def get_all_with_history(cls):
        pass

    @classmethod
    def update(cls, criteria, new_data):
        try:
            conversations_collection = get_collection("conversations")
            conversations_collection.update_one(criteria, {"$set": new_data})
        except Exception as e:
            raise Exception("Failed to update chat!") from e

    @classmethod
    def delete(cls, criteria):
        try:
            conversations_collection = get_collection("conversations")
            conversations_collection.delete_one(criteria)
        except Exception as e:
            raise Exception("Failed to delete chat!") from e