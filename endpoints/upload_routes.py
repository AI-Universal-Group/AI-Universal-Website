"""
(C) Zach Lagden 2023 All Rights Reserved.
This code may not be used, copied, distributed, or reproduced in part or in whole
for commercial or personal purposes without the express written consent of the owner. 
"""

import os

import requests
from dotenv import load_dotenv
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

from .helpers import users_collection

load_dotenv()

# reCAPTCHA Secret Key
RECAPTCHA_SECRET_KEY = os.getenv("recaptcha_secret_key")

# Upload Folder

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "uploads/images"
)

blueprint = Blueprint("upload_routes", __name__, url_prefix="/upload")


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


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {
        "png",
        "jpg",
        "jpeg",
        "pdf",
    }


# Routes


@blueprint.route("/upload", methods=["POST"])
def upload_file():
    uploaded_file = request.files["file"]
    if uploaded_file.filename == "":
        return "No file selected!"

    if not allowed_file(uploaded_file.filename):
        return "Invalid file type!"

    filename = secure_filename(uploaded_file.filename)
    uploaded_file.save(os.path.join(UPLOAD_FOLDER, filename))

    return "File successfully uploaded!"
