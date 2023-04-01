"""
Copyright (c) Zach Lagden 2023
All Rights Reserved.
"""
import os

import openai
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
from flask_restful import Api
from flask_socketio import SocketIO
from pymongo import MongoClient
from werkzeug.debug import DebuggedApplication

from flask_session import Session

from endpoints import users

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

client = MongoClient(os.getenv("mongodb"), connect=False)
user_data_db = client["user_data"]
users_collection = user_data_db["users"]
settings_collection = user_data_db["settings"]
user_information_collection = user_data_db["user_information"]


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


api.add_resource(users.UserManagementResource(), "/api/v1/user")

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000)
