"""
Flask Server for the AI Universal Website.

(C) Zach Lagden 2023 All Rights Reserved.
This code may not be used, copied, distributed, or reproduced in part or in whole
for commercial or personal purposes without the express written consent of the owner. 
"""


import os

import openai
from dotenv import load_dotenv
from endpoints import users
from flask import Flask, redirect, render_template, request, session
from flask_minify import Minify
from flask_restful import Api
from pymongo import MongoClient

from flask_session import Session

# * Initialize Flask/Flask Extensions and Configurations

load_dotenv()

GPT_PROMPTS_FOLDER = "prompts"

openai.api_key = os.getenv("openai")

app = Flask(__name__)

flask_config = {
    "SESSION_COOKIE_NAME": "wrld",
    "SESSION_TYPE": "filesystem",
}

app.config.from_mapping(flask_config)

Session(app)
api = Api(app)
Minify(app=app, html=True, js=True, cssless=True)

# * Initialize MongoDB Connection

client = MongoClient(os.getenv("mongodb"), connect=False)
user_data_db = client["user_data"]
users_collection = user_data_db["users"]
settings_collection = user_data_db["settings"]
user_information_collection = user_data_db["user_information"]


# * Define flask routes


def get_user_data(route_session):
    """
    This function takes a session object as input, checks if there exists a 'user' key in it,
    finds the corresponding user in the users_collection using the username,
    and returns a dictionary with the user's unique identifier, username, email, and phone number.

    :param session: dictionary containing user session data.
    :return: dictionary containing uuid, username, email, and phone number of the found user.
    """
    if "user" not in route_session:
        return None

    found_user = users_collection.find_one(
        {"username": route_session["user"]["username"]}
    )

    return {
        "uuid": str(found_user["_id"]),
        "username": found_user["username"],
        "email": found_user["email"],
        "phone_number": found_user["phone_number"],
    }


@app.route("/login")
def login():
    """
    This function renders the login page with GET request.
    """

    if "user" in session:
        return redirect("/")

    return render_template("pages/login.html", user=get_user_data(session))


@app.route("/ai")
def ai_test_route():
    """
    This function renders the AI chatbot page that allows authenticated users to communicate with
    OpenAI GPT-3 API and send/receive messages in real-time.
    """
    if "user" not in session:
        return redirect("/")

    return render_template(
        "pages/ai.html",
        user=get_user_data(session),
        user_data={"credits": 69, "subscription_data": "Valid Subscription"},
    )


@app.route("/")
def home_route():
    """
    This function renders the homepage for authenticated/unauthenticated users.
    """
    return render_template("pages/home.html", user=get_user_data(session))


@app.route("/learn-more")
def learn_more_route():
    """
    This function renders the learn more page for authenticated/unauthenticated users.
    """
    return render_template("pages/learn_more.html", user=get_user_data(session))


@app.route("/policy/<string:policy_name>")
def policy_route(policy_name):
    """
    This function renders the policy page for authenticated/unauthenticated users.

    It takes a policy name as a parameter.
    """
    return render_template(f"policies/{policy_name}.html", user=get_user_data(session))


@app.route("/onboarding")
def onboarding_route():
    """
    This function renders the onboarding page for authenticated/unauthenticated users.
    """
    return render_template("pages/onboarding.html", user=get_user_data(session))


# * Define API routes

api.add_resource(users.user_management_resource(), "/api/v1/user")


# * Run flask socketio server

if __name__ == "__main__":
    app.run(port=5000, debug=True)
