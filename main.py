"""
Copyright (c) Zach Lagden 2023
All Rights Reserved.
"""
import hashlib
import json
import os

import openai
from dotenv import load_dotenv
from endpoints import users
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
from flask_restful import Api
from flask_socketio import SocketIO
from pymongo import MongoClient
from werkzeug.debug import DebuggedApplication

from flask_session import Session

# * Initialize Flask/Flask Extensions and Configurations

load_dotenv()

SESSION_COOKIE_NAME = "wrld"
SESSION_TYPE = "filesystem"
GPT_PROMPTS_FOLDER = "prompts"

openai.api_key = "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"

app = Flask(__name__)
app.config.from_object(__name__)

#! Remove when actually deploying
app.debug = True
app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

Session(app)
api = Api(app)
Minify(app=app, html=True, js=True, cssless=True)
socketio = SocketIO(app)

# * Initialize MongoDB Connection

client = MongoClient(os.getenv("mongodb"), connect=False)
user_data_db = client["user_data"]
users_collection = user_data_db["users"]
settings_collection = user_data_db["settings"]
user_information_collection = user_data_db["user_information"]

# * Define socketio events


@socketio.on("client-connect")
def handle_client_connect(data):
    print(f"Client connected: {data['id']}")


@socketio.on("ai-prompt")
def handle_ai_prompt(prompt):
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
            "content": f"Provide a response for the following message:\n{prompt}",
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


# * Define flask routes


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        found_user = users_collection.find_one(
            {"username": username, "password": hashed_password}
        )
        if not found_user:
            found_user = users_collection.find_one(
                {"email": username, "password": hashed_password}
            )

        if not found_user:
            fields = (username, password)
            error = True
            message = "Invalid username or password."
            return render_template(
                "pages/login.html", error=error, username=username, message=message
            )
        else:
            session["user"] = {
                "uuid": str(found_user["_id"]),
                "username": found_user["username"],
                "email": found_user["email"],
                "phone_number": found_user["phone_number"],
            }
            return redirect("/")
    else:
        return render_template("pages/login.html")


@app.route("/signup")
def signup():
    if "user" not in session:
        return render_template("pages/signup.html")

    return redirect("/")


@app.route("/ai")
def ai():
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


@app.route("/")
def home():
    if "user" not in session:
        return render_template("pages/home.html", user=None)

    found_user = users_collection.find_one({"username": session["user"]["username"]})

    user_data = {
        "uuid": str(found_user["_id"]),
        "username": found_user["username"],
        "email": found_user["email"],
        "phone_number": found_user["phone_number"],
    }

    return render_template(
        "pages/home.html",
        user=user_data,
        user_data={"credits": 69, "subscription_data": "Valid Subscription"},
    )


# * Define API routes

api.add_resource(users.UserManagementResource(), "/api/v1/user")

# * Run flask socketio server

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000)
