"""
Flask Server for the AI Universal Website.

(C) Zach Lagden 2023 All Rights Reserved.
This code may not be used, copied, distributed, or reproduced in part or in whole
for commercial or personal purposes without the express written consent of the owner. 
"""

import os
import requests
import hashlib

import openai
from dotenv import load_dotenv
from endpoints import users
from flask import Flask, redirect, render_template, request, session, flash, url_for
from flask_minify import Minify
from flask_restful import Api
from pymongo import MongoClient
from flask_session import Session

load_dotenv()

# Folder Location
GPT_PROMPTS_FOLDER = "prompts"

# reCAPTCHA Secret Key
RECAPTCHA_SECRET_KEY = os.getenv("recaptcha_secret_key")

# OpenAI API Key
openai.api_key = os.getenv("openai")

app = Flask(__name__)

# Flask Configurations
flask_config = {
    "SESSION_COOKIE_NAME": "wrld",
    "SESSION_TYPE": "filesystem",
}
app.config.from_mapping(flask_config)
Session(app)
api = Api(app)

# Minifying HTML, CSS and JS files
Minify(app=app, html=True, js=True, cssless=True)

# MongoDB Connection
client = MongoClient(os.getenv("mongodb"), connect=False)
user_data_db = client["user_data"]
users_collection = user_data_db["users"]
settings_collection = user_data_db["settings"]
user_information_collection = user_data_db["user_information"]


def get_user_data(route_session):
    """
    This function returns user data if user exists else None.

    Args:
    route_session: session object

    Returns:
    dictionary consisting of user data
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


def verify_recaptcha(response):
    """
    Verify reCAPTCHA token and returns True if valid, False otherwise.

    Args:
    response: google recaptcha response

    Returns:
    boolean (True/False)
    """

    params = {"secret": RECAPTCHA_SECRET_KEY, "response": response}
    response = requests.post(
        "https://www.google.com/recaptcha/api/siteverify", params=params
    )
    return response.json().get("success", False)


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    This function is to login user provided the credentials are correct.

    Args:
    None

    Returns:
    Redirects to homepage on successful login.
    Renders login page on GET request.
    """

    if "user" in session:
        return redirect("/")

    if request.method == "POST":
        # Verify reCAPTCHA token
        if not verify_recaptcha(request.form.get("g-recaptcha-response-login")):
            # reCAPTCHA verification failed
            flash("reCAPTCHA verification failed. Please try again.", "error")
            return redirect(url_for("login"))

        # Validate form data
        username = request.form.get("username")
        password = request.form.get("password")

        if not all([username, password]):
            flash("Both username and password are required.", "error")
            return redirect(url_for("login"))

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        found_user = users_collection.find_one(
            {"username": username, "password": hashed_password}
        )

        if found_user:
            session["user"] = {
                "uuid": str(found_user["_id"]),
                "username": found_user["username"],
                "email": found_user["email"],
                "phone_number": found_user["phone_number"],
            }

            # Redirect to homepage on successful login
            return redirect(url_for("home_route"))

        flash("Invalid username or password.", "error")

    return render_template("pages/login.html", user=get_user_data(session))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    This function is to register a new user provided the credentials are valid.

    Args:
    None

    Returns:
    Redirects to homepage on successful registration.
    Renders signup page on GET request.
    """

    if "user" in session:
        return redirect("/")

    if request.method == "POST":
        # Verify reCAPTCHA token
        if not verify_recaptcha(request.form.get("g-recaptcha-response")):
            # reCAPTCHA verification failed
            flash("reCAPTCHA verification failed. Please try again.", "error")
            return render_template("pages/signup.html", user=get_user_data(session))

        # Validate form data
        username = request.form.get("username")
        email = request.form.get("email")
        phone_number = request.form.get("phone-number")
        password = request.form.get("password")

        if not all([username, email, phone_number, password]):
            flash("All fields are required.", "error")
            return render_template("pages/signup.html", user=get_user_data(session))

        # Hash password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Create user in database
        try:
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
                flash("Username or email is already taken.", "error")
                return render_template("pages/signup.html", user=get_user_data(session))

            new_user = {
                "username": username,
                "email": email,
                "phone_number": phone_number,
                "password": hashed_password,
            }
            inserted_user = users_collection.insert_one(new_user)
            if not inserted_user:
                flash(
                    "An error occurred while creating your account. Please try again.",
                    "error",
                )
                return render_template("pages/signup.html", user=get_user_data(session))

            # Login user and redirect to homepage
            session["user"] = {
                "uuid": str(inserted_user.inserted_id),
                "username": username,
                "email": email,
                "phone_number": phone_number,
            }
            flash("Your account has been created successfully!", "info")
            return redirect(url_for("home_route"))

        except Exception as e:
            flash(
                f"An error occurred while creating your account. Error message: {str(e)}",
                "error",
            )
            return render_template("pages/signup.html", user=get_user_data(session))

    return render_template("pages/signup.html", user=get_user_data(session))


@app.route("/ai")
def ai_test_route():
    """
    This function generates page for AI testing.

    Args:
    None

    Returns:
    Renders page for AI testing.
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
    This function generates homepage.

    Args:
    None

    Returns:
    Renders homepage.
    """

    return render_template("pages/home.html", user=get_user_data(session))


@app.route("/learn-more")
def learn_more_route():
    """
    This function generates learn more page.

    Args:
    None

    Returns:
    Renders learn more page.
    """

    return render_template("pages/learn_more.html", user=get_user_data(session))


@app.route("/policy/<string:policy_name>")
def policy_route(policy_name):
    """
    This function routes to various policies.

    Args:
    policy_name: string argument consisting of policy name

    Returns:
    Renders respective policy page.
    """

    return render_template(f"policies/{policy_name}.html", user=get_user_data(session))


@app.route("/onboarding")
def onboarding_route():
    """
    This function generates onboarding page.

    Args:
    None

    Returns:
    Renders onboarding page.
    """

    return render_template("pages/onboarding.html", user=get_user_data(session))


@app.route("/credits")
def credits_route():
    """
    This function generates credits page.

    Args:
    None

    Returns:
    Renders credits page.
    """

    return render_template("pages/credits.html", user=get_user_data(session))


api.add_resource(users.user_management_resource(), "/api/v1/user")

if __name__ == "__main__":
    app.run(port=5000, debug=True)
