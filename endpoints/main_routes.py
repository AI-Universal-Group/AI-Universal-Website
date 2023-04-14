"""
(C) Zach Lagden 2023 All Rights Reserved.
This code may not be used, copied, distributed, or reproduced in part or in whole
for commercial or personal purposes without the express written consent of the owner. 
"""

import os
import requests
import hashlib

from dotenv import load_dotenv
from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_pymongo import PyMongo

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get("mongodb")
mongo = PyMongo(app)

# reCAPTCHA Secret Key
RECAPTCHA_SECRET_KEY = os.getenv("recaptcha_secret_key")

blueprint = Blueprint("main_routes", __name__, url_prefix="/")

# Helper Functions


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

    found_user = mongo.db.users.find_one(
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


# Routes


@blueprint.route("/")
def home_route():
    """
    This function generates homepage.

    Args:
        None

    Returns:
        Renders homepage.
    """

    return render_template("pages/home.html", user=get_user_data(session))


@blueprint.route("/login", methods=["GET", "POST"])
def login_route():
    """
    This function is to login user provided the credentials are correct.

    Args:
        None

    Returns:
        Redirects to homepage on successful login.
        Renders login page on GET request.
    """

    if "user" in session:
        return redirect(url_for("app_routes.app_route"))

    if request.method == "POST":
        # Verify reCAPTCHA token
        if not verify_recaptcha(request.form.get("g-recaptcha-response")):
            # reCAPTCHA verification failed
            flash("reCAPTCHA verification failed. Please try again.", "error")
            return redirect(url_for("main_routes.login_route"))

        # Validate form data
        username = request.form.get("username")
        password = request.form.get("password")

        if not all([username, password]):
            flash("Both username and password are required.", "error")
            return redirect(url_for("main_routes.login_route"))

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        found_user = mongo.db.users.find_one(
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
            return redirect(url_for("main_routes.home_route"))

        flash("Invalid username or password.", "error")

    return render_template("pages/login.html", user=get_user_data(session))


@blueprint.route("/signup", methods=["GET", "POST"])
def signup_route():
    """
    This function is to register a new user provided the credentials are valid.

    Args:
        None

    Returns:
        Redirects to homepage on successful registration.
        Renders signup page on GET request.
    """

    if "user" in session:
        return redirect(url_for("app_routes.app_route"))

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
                flash("Username or email is already taken.", "error")
                return render_template("pages/signup.html", user=get_user_data(session))

            new_user = {
                "username": username,
                "email": email,
                "phone_number": phone_number,
                "password": hashed_password,
            }
            inserted_user = mongo.db.users.insert_one(new_user)
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
            return redirect(url_for("app_routes.onboarding_route"))

        except Exception as e:
            flash(
                f"An error occurred while creating your account. Error message: {str(e)}",
                "error",
            )
            return render_template("pages/signup.html", user=get_user_data(session))

    return render_template("pages/signup.html", user=get_user_data(session))
