"""
Copyright (c) Zach Lagden 2023
All Rights Reserved.
"""
import hashlib
import json
import os

import openai
from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import (
    Flask,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    session,
)
from flask_minify import Minify
from flask_restful import Api, Resource
from flask_socketio import SocketIO
from pymongo import MongoClient
from werkzeug.debug import DebuggedApplication

from flask_session import Session

load_dotenv()

SESSION_COOKIE_NAME = "wrld"
SESSION_TYPE = "filesystem"
GPT_PROMPTS_FOLDER = "prompts"

openai.api_key = "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"

app = Flask(__name__)
app.config.from_object(__name__)

app.debug = True
app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

Session(app)
api = Api(app)
Minify(app=app, html=True, js=True, cssless=True)
socketio = SocketIO(app)

client = MongoClient(os.getenv("mongodb"))
user_data_db = client["user_data"]
users_collection = user_data_db["users"]
settings_collection = user_data_db["settings"]
user_information_collection = user_data_db["user_information"]


class UserManagment(Resource):
    """
    API endpoint for user db managegment
    """

    def get(self):
        """
        The get function for the UserManagement endpoint.
        """
        if "user" not in session:
            return make_response(
                jsonify({"ok": False, "code": 401, "error": "401 Unauthorized"}), 401
            )

        found_user = users_collection.find_one(
            {"username": session["user"]["username"]}
        )

        user_data_to_return = {
            "uuid": str(found_user["_id"]),
            "username": found_user["username"],
            "email": found_user["email"],
            "phone_number": found_user["phone_number"],
        }

        return jsonify({"ok": True, "code": 200, "data": user_data_to_return})

    def post(self):
        """
        The post function for the UserManagement endpoint.
        """
        username = request.headers.get("username")
        password = request.headers.get("password")
        logout = request.headers.get("logout")

        if logout == "true":
            session.pop("user", None)
            return make_response(
                jsonify({"ok": True, "code": 200, "message": "Logged out."}), 200
            )

        if (not username or not password) and not logout:
            return make_response(
                jsonify(
                    {
                        "ok": False,
                        "code": 400,
                        "error": "400 Bad Request: Missing username or password header.",
                    }
                ),
                400,
            )

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        found_user = users_collection.find_one(
            {"username": username, "password": hashed_password}
        )

        if not found_user:
            return make_response(
                jsonify(
                    {
                        "ok": False,
                        "code": 401,
                        "error": "401 Unauthorized: Incorrect username or password.",
                    }
                ),
                401,
            )

        session["user"] = {
            "uuid": str(found_user["_id"]),
            "username": found_user["username"],
        }
        return jsonify({"ok": True, "code": 200, "data": session["user"]})

    def put(self):
        """
        The put function for the UserManagement endpoint.
        """
        username = request.headers.get("username")
        password = request.headers.get("password")
        phone_number = request.headers.get("phone_number")
        email = request.headers.get("email")

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        existing_user = users_collection.find_one({"username": username})
        if existing_user:
            return make_response(
                jsonify(
                    {
                        "ok": False,
                        "code": 409,
                        "error": "Username already exists in the database.",
                    }
                ),
                409,
            )

        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            return make_response(
                jsonify(
                    {
                        "ok": False,
                        "code": 409,
                        "error": "Email already exists in the database.",
                    }
                ),
                409,
            )

        existing_user = users_collection.find_one({"phone_number": phone_number})
        if existing_user:
            return make_response(
                jsonify(
                    {
                        "ok": False,
                        "code": 409,
                        "error": "Phone number already exists in the database.",
                    }
                ),
                409,
            )

        new_user = {
            "username": username,
            "password": hashed_password,
            "phone_number": phone_number,
            "email": email,
        }

        result = users_collection.insert_one(new_user)
        session["user"] = {"uuid": str(result.inserted_id), "username": username}

        return make_response(
            jsonify(
                {
                    "ok": True,
                    "code": 201,
                    "data": {"username": username, "uuid": str(result.inserted_id)},
                }
            ),
            201,
        )

    def patch(self):
        """
        The patch function for the UserManagement endpoint.
        """

        if "user" in session:
            uid = session["user"]["uuid"]
            current_password = request.headers.get("password")
            new_username = request.headers.get("new_username")
            new_password = request.headers.get("new_password")

            if not any([new_username, new_password]):
                return make_response(
                    jsonify(
                        {
                            "ok": False,
                            "code": 400,
                            "error": "Bad Request: Headers 'new_username' and or 'new_password'"
                            "are required and cannot be empty.",
                        }
                    ),
                    400,
                )

            if not current_password:
                return make_response(
                    jsonify(
                        {
                            "ok": False,
                            "code": 400,
                            "error": "Bad Request: 'password' is required and cannot be empty.",
                        }
                    ),
                    400,
                )

            user_info = users_collection.find_one({"_id": ObjectId(uid)})
            stored_password = user_info["password"]

            if hashlib.sha256(current_password.encode()).hexdigest() == stored_password:
                if new_username is not None and len(new_username) > 0:
                    users_collection.update_one(
                        {"_id": ObjectId(uid)}, {"$set": {"username": new_username}}
                    )
                if new_password is not None and len(new_password) > 0:
                    users_collection.update_one(
                        {"_id": ObjectId(uid)},
                        {
                            "$set": {
                                "password": hashlib.sha256(
                                    new_password.encode()
                                ).hexdigest()
                            }
                        },
                    )
                session["user"]["username"] = new_username

                return make_response(
                    jsonify(
                        {
                            "ok": True,
                            "code": 200,
                            "message": "User data updated successfully.",
                        }
                    ),
                    200,
                )

            return make_response(
                jsonify(
                    {
                        "ok": False,
                        "code": 401,
                        "error": "Unauthorized: Incorrect password.",
                    }
                ),
                401,
            )

        return make_response(
            jsonify({"ok": False, "code": 401, "error": "Unauthorized"}), 401
        )

    def delete(self):
        """
        The delete function for the UserManagement endpoint.
        """
        if "user" in session:
            print(session)
            uid = session["user"]["uuid"]
            users_collection.delete_one({"_id": ObjectId(uid)})

            session.pop("user", None)

            return make_response(
                jsonify(
                    {"ok": True, "code": 200, "message": "User deleted successfully."}
                ),
                200,
            )

        return make_response(
            jsonify({"ok": False, "code": 401, "error": "Unauthorized"}), 401
        )


@socketio.on("client-connect")
def client_connect(data):
    print("Connected to client: " + data["id"])


@socketio.on("ai-prompt")
def connect(prompt):
    with open(
        os.path.abspath(os.path.join(GPT_PROMPTS_FOLDER, "Language GPT Model.json"))
    ) as f:
        message_data = json.loads(f.read())
        f.close()

    messages = [
        {"role": "system", "content": message_data["system"]},
    ]

    for msg in message_data["training"]:
        messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append(
        {
            "role": "user",
            "content": f"Provide an answer for the following prompt:\n{prompt}",
        }
    )

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)

    choice = response["choices"][0]  # first choice
    if choice["finish_reason"] != "stop":
        return False, Exception(
            f"Gpt Stop Error- {choice['finish_reason']} - Gpt stopped while generating your response, this is usually a one time thing so please try again."
        )

    elif choice["finish_reason"] == "stop":
        message_response = choice["message"]["content"]

    output = {
        "id": response["id"],
        "raw": message_response,
        "formatted": str(message_response),
    }

    socketio.emit("ai-output", output["formatted"], room=request.sid)


@app.route("/")
def index():
    """
    Index endpoint for the website frontend.
    """
    if "user" not in session:
        return render_template("pages/home.html", user=None)

    found_user = users_collection.find_one({"username": session["user"]["username"]})

    user_data = {
        "uuid": str(found_user["_id"]),
        "username": found_user["username"],
        "email": found_user["email"],
        "phone_number": found_user["phone_number"],
    }
    return render_template("pages/home.html", user=user_data)


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Login endpoint for the website frontend.
    """
    if request.method == "POST":
        email = request.form.get("email").strip().lower()
        password = request.form.get("password").strip()

        if (email or password) == "":
            return render_template(
                "pages/login.html",
                error=True,
                message="Fields cannot be left blank",
                fields=(email, password),
            )

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        found_user = users_collection.find_one(
            {"username": email, "password": hashed_password}
        )

        found_user = users_collection.find_one(
            {"email": email, "password": hashed_password}
        )

        if not found_user:
            return render_template(
                "pages/login.html",
                error=True,
                message="Email or password incorrect.",
                fields=(email, password),
            )

        session["user"] = {
            "uuid": str(found_user["_id"]),
            "username": found_user["username"],
        }

        return redirect("/")

    if "user" not in session:
        return render_template("pages/login.html")

    return redirect("/")


@app.route("/signup")
def signup():
    """
    Signup endpoint for the website frontend.
    """
    if "user" not in session:
        return render_template("pages/signup.html")

    return redirect("/")


@app.route("/ai")
def ai():
    """
    Test Ai endpoint for the website frontend.
    """
    if "user" not in session:
        return render_template("pages/ai.html", user=None)

    found_user = users_collection.find_one({"username": session["user"]["username"]})

    user_data = {
        "uuid": str(found_user["_id"]),
        "username": found_user["username"],
        "email": found_user["email"],
        "phone_number": found_user["phone_number"],
    }

    return render_template(
        "pages/ai.html",
        user=user_data,
        user_data={"credits": 69, "subscription_data": "Valid Subscription"},
    )


api.add_resource(UserManagment, "/api/v1/user")

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000)
