from datetime import datetime, timezone
from tools.db import get_collection

class Conversation:
    _id: str
    user_id: str
    title: str
    session_id: str
    created_at: datetime
    updated_at: datetime

    def __init__(self, _id = None, user_id = None, title = None, session_id = None, created_at = None, updated_at = None):
        """Initializes a new Conversation instance."""
        self._id = _id
        self.user_id = user_id
        self.title = title
        self.session_id = session_id
        self.created_at = created_at if created_at else datetime.now(timezone.utc)
        self.updated_at = updated_at if updated_at else datetime.now(timezone.utc)

    def to_dict(self):
        """Converts the Conversation instance to a dictionary."""
        return {
            "_id": self._id,
            "user_id": self.user_id,
            "title": self.title,
            "session_id": self.session_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def get_collection(cls):
        """Retrieves the MongoDB collection for conversations."""
        return get_collection("conversations")

    @classmethod
    def create(cls, conversation_data):
        """Creates a new conversation in the database."""
        try:
            conversations_collection = cls.get_collection()
            if conversations_collection.find_one({"$or": [{"session_id": conversation_data["session_id"]}]}):
                return False, "Chat session already exists!"

            new_conversation = cls(**conversation_data)
            new_conversation_dict = new_conversation.to_dict()

            conversations_collection.insert_one(new_conversation_dict)
            return True, None
        except Exception as e:
            print(f"Error during conversation creation: {e}")
            return False, e

    @classmethod
    def get_one(cls, criteria):
        """Retrieves one conversation from the database based on given criteria."""
        try:
            conversations_collection = cls.get_collection()
            conversation_data = conversations_collection.find_one(criteria)
            if conversation_data:
                return cls(**conversation_data).to_dict()
            else:
                return None
        except Exception as e:
            raise Exception("Failed to get chat!") from e

    @classmethod
    def get_user_chats(cls, criteria):
        """Retrieves all user's conversations from the database based on given criteria."""
        try:
            conversations_collection = cls.get_collection()
            conversations_data = conversations_collection.find(criteria).sort("updated_at", -1)
            return [cls(**conversation).to_dict() for conversation in conversations_data]
        except Exception as e:
            raise Exception(f"Failed to get all user's chats! Error: {e}") from e

    @classmethod
    def update_title(cls, criteria, title):
        """Updates a conversations' title in the database based on given criteria."""
        try:
            conversations_collection = cls.get_collection()
            result = conversations_collection.update_one(criteria, {"$set": {"title": title}})
            return result.modified_count > 0
        except Exception as e:
            raise Exception("Failed to update chat!") from e

    @classmethod
    def update_updated_at(cls, criteria):
        """Updates a conversations' updated_at in the database based on given criteria."""
        try:
            conversations_collection = cls.get_collection()
            result = conversations_collection.update_one(criteria, {"$set": {"updated_at": datetime.now(timezone.utc)}})
            return result.modified_count > 0
        except Exception as e:
            raise Exception("Failed to update chat!") from e

    @classmethod
    def delete(cls, criteria):
        """Deletes a conversation in the database based on given criteria."""
        try:
            conversations_collection = cls.get_collection()
            result = conversations_collection.delete_one(criteria)
            return result.deleted_count > 0
        except Exception as e:
            raise Exception("Failed to delete chat!") from e