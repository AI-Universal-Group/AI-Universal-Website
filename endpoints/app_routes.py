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
from pymongo import MongoClient

load_dotenv()

# MongoDB Connection
client = MongoClient(os.getenv("mongodb"), connect=False)
user_data_db = client["user_data"]
users_collection = user_data_db["users"]
settings_collection = user_data_db["settings"]
user_information_collection = user_data_db["user_information"]

# reCAPTCHA Secret Key
RECAPTCHA_SECRET_KEY = os.getenv("recaptcha_secret_key")

blueprint = Blueprint("app_routes", __name__, url_prefix="/app")


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


@blueprint.route("/onboarding")
def onboarding_route():
    """
    This function generates onboarding page.

    Args:
    None

    Returns:
    Renders onboarding page.
    """

    if "user" not in session:
        return redirect(url_for("main_routes.login_route"))

    return render_template("pages/onboarding.html", user=get_user_data(session))
