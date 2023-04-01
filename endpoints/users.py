import hashlib
import os

from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import session
from flask_restful import Resource, reqparse
from pymongo import MongoClient

load_dotenv()

client = MongoClient(os.getenv("mongodb"), connect=False)
user_data_db = client["user_data"]
users_collection = user_data_db["users"]
settings_collection = user_data_db["settings"]
user_information_collection = user_data_db["user_information"]

users_collection.create_index("username", unique=True)

parser = reqparse.RequestParser()
parser.add_argument("username", type=str)
parser.add_argument("password", type=str)
parser.add_argument("logout", type=bool, default=False)
parser.add_argument("phone_number", type=str)
parser.add_argument("email", type=str)
parser.add_argument("new_username", type=str)
parser.add_argument("new_password", type=str)


def is_authenticated(session_user):
    return True if session_user else False


class UserManagement(Resource):
    def get(self):
        session_user = session.get("user")
        if not is_authenticated(session_user):
            return {"message": "401 Unauthorized"}, 401

        user_data_to_return = {
            "uuid": str(session_user["uuid"]),
            "username": session_user["username"],
            "email": session_user["email"],
            "phone_number": session_user["phone_number"],
        }

        return {"data": user_data_to_return}, 200

    def post(self):
        args = parser.parse_args()
        username = args["username"]
        password = args["password"]
        logout = args["logout"]

        if logout:
            session.pop("user", None)
            return {"message": "Logged out."}, 200

        if not username or not password:
            return {
                "message": "400 Bad Request: Missing username or password header."
            }, 400

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        found_user = users_collection.find_one(
            {"username": username, "password": hashed_password}
        )

        if not found_user:
            return {"message": "401 Unauthorized: Incorrect username or password."}, 401

        session["user"] = {
            "uuid": str(found_user["_id"]),
            "username": found_user["username"],
            "email": found_user["email"],
            "phone_number": found_user["phone_number"],
        }
        return {"data": session["user"]}, 200

    def put(self):
        args = parser.parse_args()
        username = args["username"]
        password = args["password"]
        phone_number = args["phone_number"]
        email = args["email"]

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        existing_user = users_collection.find_one(
            {
                "$or": [
                    {"username": username},
                    {"email": email},
                    {"phone_number": phone_number},
                ]
            }
        )

        if existing_user:
            return {
                "message": "409 Conflict: User with same credentials already exists."
            }, 409

        new_user = {
            "username": username,
            "password": hashed_password,
            "phone_number": phone_number,
            "email": email,
        }

        result = users_collection.insert_one(new_user)
        session["user"] = {
            "uuid": str(result.inserted_id),
            "username": username,
            "email": email,
            "phone_number": phone_number,
        }

        return {"data": session["user"]}, 201

    def patch(self):
        args = parser.parse_args()
        current_password = args["password"]
        new_username = args["new_username"]
        new_password = args["new_password"]

        session_user = session.get("user")
        if not is_authenticated(session_user):
            return {"message": "401 Unauthorized"}, 401

        uid = ObjectId(session_user["uuid"])
        user_info = users_collection.find_one({"_id": uid})
        stored_password = user_info["password"]

        if not any([new_username, new_password]):
            return {
                "message": "400 Bad Request: Headers 'new_username' and or 'new_password'"
                "are required and cannot be empty."
            }, 400

        if not current_password:
            return {
                "message": "400 Bad Request: 'password' is required and cannot be empty."
            }, 400

        if hashlib.sha256(current_password.encode()).hexdigest() != stored_password:
            return {"message": "401 Unauthorized: Incorrect password."}, 401

        update_query = {}
        if new_username:
            update_query["username"] = new_username

        if new_password:
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
            update_query["password"] = hashed_password

        users_collection.update_one({"_id": uid}, {"$set": update_query})

        session_user.update(update_query)
        session["user"] = session_user

        return {"message": "User data updated successfully."}, 200

    def delete(self):
        session_user = session.get("user")
        if not is_authenticated(session_user):
            return {"message": "401 Unauthorized"}, 401

        uid = ObjectId(session_user["uuid"])
        users_collection.delete_one({"_id": uid})
        session.pop("user", None)

        return {"message": "User deleted successfully."}, 200


def UserManagementResource():
    return UserManagement
