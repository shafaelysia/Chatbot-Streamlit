from datetime import datetime, timezone
from tools.db import get_collection
from utils.helpers import hash_password

class User:
    def __init__(self, _id=None, username=None, email=None, password=None, first_name=None, last_name=None, picture_path=None, role=None, is_admin=False, created_at=None, updated_at=None, is_active=None, last_login=None):
        self._id = _id
        self.username = username
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.picture_path = picture_path
        self.role = role
        self.is_admin = is_admin
        self.created_at = created_at if created_at else datetime.now(timezone.utc)
        self.updated_at = updated_at if updated_at else datetime.now(timezone.utc)
        self.is_active = is_active
        self.last_login = last_login

    def to_dict(self):
        return {
            "_id": self._id,
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "picture_path": self.picture_path,
            "role": self.role,
            "is_admin": self.is_admin,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_active": self.is_active,
            "last_login": self.last_login
        }

    @classmethod
    def create(cls, user_data):
        try:
            users_collection = get_collection("users")
            if users_collection.find_one({"$or": [{"username": user_data["username"]}, {"email": user_data["email"]}]}):
                return False, "Username or email already exists"

            hashed_password = hash_password(user_data["password"])
            user_data["password"] = hashed_password
            user_data["created_at"] = datetime.now(timezone.utc)
            user_data["updated_at"] = datetime.now(timezone.utc)
            user_data["is_active"] = False
            user_data["last_login"] = None

            result = users_collection.insert_one(user_data)
            return result.inserted_id, None
        except Exception as e:
            print(f"Error during user creation: {e}")
            return False, e

    @classmethod
    def get_one(cls, criteria):
        try:
            users_collection = get_collection("users")
            user_data = users_collection.find_one(criteria)
            if user_data:
                return cls(**user_data).to_dict()
            else:
                return None
        except Exception as e:
            raise Exception("Failed to get user!") from e

    @classmethod
    def get_all(cls):
        try:
            users_collection = get_collection("users")
            users_data = users_collection.find()
            return [cls(**user_data).to_dict() for user_data in users_data]
        except Exception as e:
            raise Exception("Failed to get all users!") from e


    @classmethod
    def update(cls, criteria, new_data):
        try:
            users_collection = get_collection("users")
            return users_collection.update_one(criteria, {"$set": new_data})
        except Exception as e:
            raise Exception("Failed to update user!") from e

    @classmethod
    def partial_update(cls, criteria, new_data):
        try:
            users_collection = get_collection("users")
            users_collection.update_one(criteria, {"$set": new_data})
        except Exception as e:
            raise Exception("Failed to update user!") from e

    @classmethod
    def delete(cls, criteria):
        try:
            users_collection = get_collection("users")
            users_collection.delete_one(criteria)
        except Exception as e:
            raise Exception("Failed to delete user!") from e
