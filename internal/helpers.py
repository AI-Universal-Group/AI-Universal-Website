from flask import Flask, session
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os
import requests

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
load_dotenv()

# MongoDB Connection
app.config["MONGO_URI"] = os.getenv("MONGODB_URI")
mongo = PyMongo(app)
users_collection = mongo.db.users
settings_collection = mongo.db.settings
user_information_collection = mongo.db.user_information

# reCAPTCHA Secret Key
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")


def get_user_data():
    """
    This function returns user data if user exists else None.

    Returns:
    dictionary consisting of user data
    """

    if "user" not in session:
        return None

    found_user = users_collection.find_one({"username": session["user"]["username"]})

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
