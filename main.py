"""
(C) Zach Lagden 2023 All Rights Reserved.
This code may not be used, copied, distributed, or reproduced in part or in whole
for commercial or personal purposes without the express written consent of the owner. 
"""

import os

import openai
from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, session, url_for
from flask_assets import Environment
from flask_discord import DiscordOAuth2Session, Unauthorized, requires_authorization
from flask_minify import Minify
from flask_restful import Api
from flask_session import Session

from assets import *
from endpoints import app_routes, main_routes, settings_routes, site_logging, users
from internal.database import client, users_collection
from internal.helpers import get_user_data

load_dotenv()

# Configuration

GPT_PROMPTS_FOLDER = os.getenv("gpt_prompts_folder")  # Folder Location
RECAPTCHA_SECRET_KEY = os.getenv("recaptcha_secret_key")  # reCAPTCHA Secret Key
openai.api_key = os.getenv("openai")  # OpenAI API Key

# Register the flask application

app = Flask(__name__)

# Flask Blueprint Configurations
app.register_blueprint(main_routes.blueprint)
app.register_blueprint(app_routes.blueprint)
app.register_blueprint(settings_routes.blueprint)

# Flask Configuration
flask_config = {
    "MAX_CONTENT_LENGTH": 10 * 1024 * 1024,  # 10mb
    "CACHE": True,  # Set flask asset cacheing to True
    "SESSION_COOKIE_NAME": "wrld",
    "SESSION_PERMANENT": False,
    "SESSION_TYPE": "mongodb",
    "SESSION_MONGODB": client,
    "SESSION_MONGODB_DB": "site_data",
    "SESSION_MONGODB_COLLECTION": "sessions",
    "DISCORD_CLIENT_ID": os.getenv("DISCORD_CLIENT_ID"),
    "DISCORD_CLIENT_SECRET": os.getenv("DISCORD_CLIENT_SECRET"),
    "DISCORD_REDIRECT_URI": os.getenv("DISCORD_REDIRECT_URI"),
    "DISCORD_BOT_TOKEN": os.getenv("DISCORD_BOT_TOKEN"),
    "DISCORD_GUILD_ID": os.getenv("DISCORD_GUILD_ID"),
    "DISCORD_GUILD_INVITE": os.getenv("DISCORD_GUILD_INVITE"),
}
app.secret_key = os.getenv("flask_secret")
app.config.from_mapping(flask_config)

# Flask Extensions
Session(app)
api = Api(app)
assets = Environment(app)

# Minifying HTML, CSS and JS files
Minify(app=app, html=True, js=True, cssless=True)

# Register JavaScript bundles
assets.register("base_js", base_js)
assets.register("home_js", home_js)
assets.register("learn_more_js", learn_more_js)
assets.register("login_signup_js", login_signup_js)
assets.register("onboarding_js", onboarding_js)
assets.register("credits_js", credits_js)

# Register CSS bundles
assets.register("base_css", base_css)
assets.register("home_css", home_css)
assets.register("learn_more_css", learn_more_css)
assets.register("login_signup_css", login_signup_css)
assets.register("onboarding_css", onboarding_css)
assets.register("credits_css", credits_css)

discord = DiscordOAuth2Session(app)


@app.route("/base")
def base():
    return render_template("base.html")


@app.route("/discord/login")
def discord_login_route():
    """
    Discord OAuth2 login route
    """
    return discord.create_session()


@app.route("/discord/callback")
def discord_callback_route():
    """
    Discord OAuth2 callback route
    """
    discord.callback()
    return redirect(url_for("discord_link_route"))


@app.errorhandler(Unauthorized)
def discord_redirect_unauthorized(error):
    """
    Redirect to Discord login if not authorized
    """
    print(f"Redirecting user to discord login due to unauth error: {error}")
    return redirect(url_for("discord_login_route"))


@app.route("/discord/link")
@requires_authorization
def discord_link_route():
    """
    Route for linking a Discord account to a user's profile
    """
    user = get_user_data(session)
    discord_user = discord.fetch_user()

    if not user:
        return render_template(
            "pages/discord/link.html", not_logged_in=True, discord_user=discord_user
        )

    if "discord_id" in user:
        return render_template(
            "pages/discord/link.html", already_linked=True, discord_user=discord_user
        )
    users_collection.update_one(
        {"_id": ObjectId(user["uuid"])},
        {"$set": {"discord_id": str(discord_user.id)}},
    )

    guild_id = app.config["DISCORD_GUILD_ID"]
    response = discord_user.add_to_guild(guild_id)

    if response:
        join_success = True
    elif response == {}:
        join_success = None
    else:
        join_success = False

    return render_template(
        "pages/discord/link.html",
        link_success=True,
        join_success=join_success,
        discord_user=discord_user,
        discord_guild_invite=app.config["DISCORD_GUILD_INVITE"],
    )


@app.route("/discord/unlink")
@requires_authorization
def discord_unlink_route():
    """
    Route for unlinking a Discord account from a user's profile
    """
    user = get_user_data(session)
    discord_user = discord.fetch_user()

    if not user:
        return render_template(
            "pages/discord/unlink.html", not_logged_in=True, discord_user=discord_user
        )

    if "discord_id" not in user:
        return render_template(
            "pages/discord/unlink.html", not_linked=True, discord_user=discord_user
        )
    users_collection.update_one(
        {"_id": ObjectId(user["uuid"])},
        {"$unset": {"discord_id": ""}},
    )

    return render_template(
        "pages/discord/unlink.html",
        unlink_success=True,
        discord_user=discord_user,
    )


# Define API routes
api.add_resource(users.user_management_resource(), "/api/v1/user")
api.add_resource(site_logging.site_logging_resource(), "/api/v1/log_page_load")


if __name__ == "__main__":
    os.environ[
        "OAUTHLIB_INSECURE_TRANSPORT"
    ] = "true"  #! Only in development environment.
    app.run(port=5000, debug=True)
