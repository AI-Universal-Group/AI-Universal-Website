"""
(C) Zach Lagden 2023 All Rights Reserved.
This code may not be used, copied, distributed, or reproduced in part or in whole
for commercial or personal purposes without the express written consent of the owner. 
"""

import os

import openai
from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_discord import DiscordOAuth2Session, Unauthorized, requires_authorization
from flask_minify import Minify
from flask_restful import Api

from endpoints import app_routes, main_routes, settings_routes, users
from flask_session import Session
from internal.database import users_collection
from internal.helpers import get_user_data

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

# Minifying HTML, CSS and JS files
Minify(app=app, html=True, js=True, cssless=True)

# Discord Routes

discord = DiscordOAuth2Session(app)


@app.route("/discord/login")
def discord_login_route():
    return discord.create_session()


@app.route("/discord/callback")
def discord_callback_route():
    discord.callback()
    return redirect(url_for("discord_link_route"))


@app.errorhandler(Unauthorized)
def discord_redirect_unauthorized(e):
    return redirect(url_for("discord_login_route"))


@app.route("/discord/link")
@requires_authorization
def discord_link_route():
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
    else:
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


# Define API routes
api.add_resource(users.user_management_resource(), "/api/v1/user")

# Run if running as a script
if __name__ == "__main__":
    os.environ[
        "OAUTHLIB_INSECURE_TRANSPORT"
    ] = "true"  #! Only in development environment.
    app.run(port=5000, debug=True)
