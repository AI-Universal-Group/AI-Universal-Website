"""
(C) Zach Lagden 2023 All Rights Reserved.
This code may not be used, copied, distributed, or reproduced in part or in whole
for commercial or personal purposes without the express written consent of the owner. 
"""

import os
import requests
import hashlib
import json
import datetime

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
from .helpers import users_collection, signups_collection, logins_collection

load_dotenv()

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

    found_user = users_collection.find_one(
        {"username": route_session["user"]["username"]}
    )

    return {
        "uuid": str(found_user["_id"]),
        "username": found_user["username"],
        "email": found_user["email"],
        "phone_number": found_user["phone_number"],
    }


def get_client_ip(request):
    """
    Get the client's IP address from the request object.

    Args:
    request: request object

    Returns:
    string consisting of the client's IP address
    """
    if "X-Forwarded-For" in request.headers:
        return request.headers["X-Forwarded-For"].split(",")[0].strip()
    return request.remote_addr


def verify_recaptcha(response):
    """
    Verify reCAPTCHA token and returns True if valid, False otherwise.

    Args:
    response: google recaptcha response

    Returns:
    boolean (True/False)
    """
    print(RECAPTCHA_SECRET_KEY)
    params = {"secret": RECAPTCHA_SECRET_KEY, "response": response}
    response = requests.post(
        "https://www.google.com/recaptcha/api/siteverify", params=params
    )
    print(response.json())
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

    return render_template("landing/home.html", user=get_user_data(session))


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
        print(request.form)
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

            # Log login data
            ip_address = get_client_ip(request)
            logins_collection.insert_one(
                {
                    "user_id": str(found_user["_id"]),
                    "ip_address": ip_address,
                    "timestamp": datetime.datetime.utcnow(),
                }
            )

            # Redirect to homepage on successful login
            return redirect(url_for("main_routes.home_route"))

        flash("Invalid username or password.", "error")

    return render_template("landing/login.html", user=get_user_data(session))


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
            return render_template("landing/signup.html", user=get_user_data(session))

        # Validate form data
        username = request.form.get("username")
        email = request.form.get("email")
        phone_number = request.form.get("phone-number")
        password = request.form.get("password")

        if not all([username, email, phone_number, password]):
            flash("All fields are required.", "error")
            return render_template("landing/signup.html", user=get_user_data(session))

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
                return render_template(
                    "landing/signup.html", user=get_user_data(session)
                )

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
                return render_template(
                    "landing/signup.html", user=get_user_data(session)
                )

            else:
                # Login user and redirect to homepage
                session["user"] = {
                    "uuid": str(inserted_user.inserted_id),
                    "username": username,
                    "email": email,
                    "phone_number": phone_number,
                }

                # Log signup data
                ip_address = get_client_ip(request)
                response = requests.get(f"http://ip-api.com/json/{ip_address}")
                region_data = response.json()
                signups_collection.insert_one(
                    {
                        "user_id": str(inserted_user.inserted_id),
                        "ip_address": ip_address,
                        "timestamp": datetime.datetime.utcnow(),
                        "region_data": json.dumps(region_data),
                    }
                )

                flash("Your account has been created successfully!", "info")
                return redirect(url_for("app_routes.onboarding_route"))

        except Exception as e:
            flash(
                f"An error occurred while creating your account. Error message: {str(e)}",
                "error",
            )
            return render_template("landing/signup.html", user=get_user_data(session))

    return render_template("landing/signup.html", user=get_user_data(session))


@blueprint.route("/learn-more")
def learn_more_route():
    """
    This function generates learn more page.

    Args:
    None

    Returns:
    Renders learn more page.
    """

    return render_template("landing/learn_more.html", user=get_user_data(session))


@blueprint.route("/policy/<string:policy_name>")
def policy_route(policy_name):
    """
    This function routes to various policies.

    Args:
    policy_name: string argument consisting of policy name

    Returns:
    Renders respective policy page.
    """

    allowed_urls = ["cookies", "privacy", "terms_of_service"]

    if policy_name not in allowed_urls:
        return "404 - Page not found", 404  # TODO: create 404 page

    return render_template(
        f"landing/policies/{policy_name}.html", user=get_user_data(session)
    )


@blueprint.route("/credits")
def credits_route():
    """
    This function generates credits page.

    Args:
    None

    Returns:
    Renders credits page.
    """

    return render_template("landing/credits.html", user=get_user_data(session))
