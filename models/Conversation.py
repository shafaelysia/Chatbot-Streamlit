from datetime import datetime
from services.db import get_collection

class Message:
    def __init__(self, prompt=None, response=None, timestamp=None):
        self.prompt = prompt
        self.response = response
        self.timestamp = timestamp

    def to_dict(self):
        return {
            "prompt": self.prompt,
            "response": self.response,
            "timestamp": self.timestamp
        }

class Conversation:
    def __init__(self, _id=None, user_id=None, title=None, messages=None, created_at=None, updated_at=None):
        self._id = _id
        self.user_id = user_id
        self.title = title
        self.messages = [Message(**message) for message in messages] if messages else []
        self.created_at = created_at if created_at else datetime.datetime.utcnow()
        self.updated_at = updated_at if updated_at else datetime.datetime.utcnow()

    def to_dict(self):
        return {
            "_id": self._id,
            "userId": self.user_id,
            "title": self.title,
            "messages": [message.to_dict() for message in self.messages],
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
    def get_one_chat(cls, criteria):
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
    def get_all_chat_titles(cls, criteria):
        try:
            conversations_collection = get_collection("conversations")
            conversations_data = conversations_collection.find(criteria, {"title": 1, "_id": 0})
            return [conversation_data["title"] for conversation_data in conversations_data]
        except Exception as e:
            raise Exception("Failed to get chat titles!") from e

    @classmethod
    def update_message(cls, criteria, new_data):
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