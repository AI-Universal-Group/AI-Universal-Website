"""
(C) Zach Lagden 2023 All Rights Reserved.
This code may not be used, copied, distributed, or reproduced in part or in whole
for commercial or personal purposes without the express written consent of the owner. 
"""

import os

import openai
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, flash, url_for
from flask_minify import Minify
from flask_pymongo import PyMongo
from flask_restful import Api
from flask_session import Session

from internal.helpers import get_user_data
from endpoints import users, app_routes, main_routes, settings_routes

load_dotenv()

# Folder Location
GPT_PROMPTS_FOLDER = "prompts"

# reCAPTCHA Secret Key
RECAPTCHA_SECRET_KEY = os.getenv("recaptcha_secret_key")

# OpenAI API Key
openai.api_key = os.getenv("openai")

app = Flask(__name__)

# Flask Blueprint Configurations
app.register_blueprint(main_routes.blueprint)
app.register_blueprint(app_routes.blueprint)
app.register_blueprint(settings_routes.blueprint)

# Flask Configurations
flask_config = {
    "SESSION_COOKIE_NAME": "wrld",
    "SESSION_TYPE": "filesystem",
}
app.config.from_mapping(flask_config)

# Flask Extensions
Session(app)
api = Api(app)
mongo = PyMongo(app)

# Minifying HTML, CSS and JS files
Minify(app=app, html=True, js=True, cssless=True)


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


api.add_resource(users.user_management_resource(mongo), "/api/v1/user")

if __name__ == "__main__":
    app.run(port=5000, debug=True)
