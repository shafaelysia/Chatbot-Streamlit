from datetime import datetime, timezone
from tools.db import get_collection

class Conversation:
    def __init__(self, _id=None, user_id=None, title=None, session_id=None, created_at=None, updated_at=None):
        self._id = _id
        self.user_id = user_id
        self.title = title
        self.session_id = session_id
        self.created_at = created_at if created_at else datetime.now(timezone.utc)
        self.updated_at = updated_at if updated_at else datetime.now(timezone.utc)

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
            conversations_collection = get_collection("conversations")
            if conversations_collection.find_one({"$or": [{"session_id": conversation_data["session_id"]}]}):
                return False, "Chat session already exists!"

            new_conversation = cls(**conversation_data)
            new_conversation_dict = new_conversation.to_dict()
            new_conversation_dict.pop("_id", None)

            result = conversations_collection.insert_one(new_conversation_dict)
            return result.inserted_id, None
        except Exception as e:
            print(f"Error during conversation creation: {e}")
            return False, e

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
    def update_title(cls, criteria, title):
        try:
            conversations_collection = get_collection("conversations")
            conversations_collection.update_one(criteria, {"$set": {"title": title}})
        except Exception as e:
            raise Exception("Failed to update chat!") from e

    @classmethod
    def update_updated_at(cls, criteria):
        try:
            conversations_collection = get_collection("conversations")
            conversations_collection.update_one(criteria, {"$set": {"updated_at": datetime.now(timezone.utc)}})
        except Exception as e:
            raise Exception("Failed to update chat!") from e

    @classmethod
    def delete(cls, criteria):
        try:
            conversations_collection = get_collection("conversations")
            conversations_collection.delete_one(criteria)
        except Exception as e:
            raise Exception("Failed to delete chat!") from e