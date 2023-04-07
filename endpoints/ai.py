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
parser.add_argument("model", type=str)
parser.add_argument("prompt", type=str)


def is_authenticated(session_user):
    return True if session_user else False


class AiPrompts(Resource):
    def get(self):
        if not is_authenticated(session.get("user")):
            return {"message": "401 Unauthorized"}, 401


def AiPromptsResource():
    return AiPrompts
