"""
(C) Zach Lagden 2023 All Rights Reserved.
This code may not be used, copied, distributed, or reproduced in part or in whole
for commercial or personal purposes without the express written consent of the owner. 
"""

import hashlib

from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, request, session
from flask_restful import Resource, Api, reqparse
from flask_pymongo import PyMongo

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("mongodb")

mongo = PyMongo(app)

api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument("username", type=str)
parser.add_argument("password", type=str)
parser.add_argument("logout", type=bool, default=False)
parser.add_argument("phone_number", type=str)
parser.add_argument("email", type=str)
parser.add_argument("new_username", type=str)
parser.add_argument("new_password", type=str)


def is_authenticated(session_user):
    """
    Determine if a user is authenticated or not.

    Args:
    - session_user: The current user's session.

    Returns:
    - True if the user is authenticated; False otherwise.
    """

    return bool(session_user)


class UserManagement(Resource):
    """
    Class handling creation, update and removal of users.
    """

    def get(self):
        """
        Retrieve user data for authenticated user.

        Returns:
        - JSON object containing user information if user is authenticated.
        """
        session_user = session.get("user")
        if not is_authenticated(session_user):
            response = make_response(
                jsonify({"message": "401 Unauthorized", "ok": False}), 401
            )
            return response

        user_data_to_return = {
            "uuid": str(session_user["uuid"]),
            "username": session_user["username"],
            "email": session_user["email"],
            "phone_number": session_user["phone_number"],
        }

        response = make_response(
            jsonify({"data": user_data_to_return, "ok": True}), 200
        )
        return response

    def post(self):
        """
        Log in a user.

        Returns:
        - JSON object containing authenticated user's data.
        """
        args = parser.parse_args()
        username = args["username"]
        password = args["password"]
        logout = args["logout"]

        if logout:
            session.pop("user", None)
            response = make_response(jsonify({"message": "Logged out."}), 200)
            return response

        if not username or not password:
            response = make_response(
                jsonify(
                    {
                        "message": "400 Bad Request: Missing username or password header.",
                        "ok": False,
                    }
                ),
                400,
            )
            return response

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        found_user = mongo.db.users.find_one(
            {"username": username, "password": hashed_password}
        )

        if not found_user:
            response = make_response(
                jsonify(
                    {
                        "message": "401 Unauthorized: Incorrect username or password.",
                        "ok": False,
                    }
                ),
                401,
            )
            return response

        session["user"] = {
            "uuid": str(found_user["_id"]),
            "username": found_user["username"],
            "email": found_user["email"],
            "phone_number": found_user["phone_number"],
        }
        response = make_response(jsonify({"data": session["user"], "ok": True}), 200)
        return response

    def put(self):
        """
        Create a new user.

        Returns:
        - JSON object containing the newly created user's data.
        """
        args = parser.parse_args()
        username = args["username"]
        password = args["password"]
        phone_number = args["phone_number"]
        email = args["email"]

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        existing_user = mongo.db.users.find_one(
            {
                "$or": [
                    {"username": username},
                    {"email": email},
                    {"phone_number": phone_number},
                ]
            }
        )

        if existing_user:
            response = make_response(
                jsonify(
                    {
                        "message": "409 Conflict: User with same credentials already exists.",
                        "ok": False,
                    }
                ),
                409,
            )
            return response

        new_user = {
            "username": username,
            "password": hashed_password,
            "phone_number": phone_number,
            "email": email,
        }

        result = mongo.db.users.insert_one(new_user)
        session["user"] = {
            "uuid": str(result.inserted_id),
            "username": username,
            "email": email,
            "phone_number": phone_number,
        }

        response = make_response(jsonify({"data": session["user"], "ok": True}), 201)
        return response

    def patch(self):
        """
        Update a user's data.

        Returns:
        - JSON object containing updated user data.
        """
        args = parser.parse_args()
        current_password = args["password"]
        new_username = args["new_username"]
        new_password = args["new_password"]

        session_user = session.get("user")
        if not is_authenticated(session_user):
            response = make_response(
                jsonify({"message": "401 Unauthorized", "ok": False}), 401
            )
            return response

        uid = ObjectId(session_user["uuid"])
        user_info = mongo.db.users.find_one({"_id": uid})
        stored_password = user_info["password"]

        if not any([new_username, new_password]):
            response = make_response(
                jsonify(
                    {
                        "message": "400 Bad Request: Headers 'new_username' and or 'new_password'"
                        "are required and cannot be empty.",
                        "ok": False,
                    }
                ),
                400,
            )
            return response

        if not current_password:
            response = make_response(
                jsonify(
                    {
                        "message": "400 Bad Request: 'password' is required and cannot be empty.",
                        "ok": False,
                    }
                ),
                400,
            )
            return response

        if hashlib.sha256(current_password.encode()).hexdigest() != stored_password:
            response = make_response(
                jsonify(
                    {"message": "401 Unauthorized: Incorrect password.", "ok": False}
                ),
                401,
            )
            return response

        update_query = {}
        if new_username:
            update_query["username"] = new_username

        if new_password:
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
            update_query["password"] = hashed_password

        mongo.db.users.update_one({"_id": uid}, {"$set": update_query})

        session_user.update(update_query)
        session["user"] = session_user

        response = make_response(
            jsonify({"message": "User data updated successfully.", "ok": True}), 200
        )
        return response

    def delete(self):
        """
        Delete a user.
        Returns:
        - JSON object containing message of successful user removal.
        """
        session_user = session.get("user")
        if not is_authenticated(session_user):
            response = make_response(
                jsonify({"message": "401 Unauthorized", "ok": False}), 401
            )
            return response

        uid = ObjectId(session_user["uuid"])
        mongo.db.users.delete_one({"_id": uid})
        session.pop("user", None)

        response = make_response(
            jsonify({"message": "User deleted successfully.", "ok": True}), 200
        )
        return response


def user_management_resource():
    """
    Function returning an instance of UserManagement class.
    """
    return UserManagement
