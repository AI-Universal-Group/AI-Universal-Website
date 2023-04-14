"""
(C) Zach Lagden 2023 All Rights Reserved.
This code may not be used, copied, distributed, or reproduced in part or in whole
for commercial or personal purposes without the express written consent of the owner.
"""

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_pymongo import pymongo

blueprint = Blueprint("settings_routes", __name__, url_prefix="/settings")

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
collection = db["users"]


@blueprint.route("/")
def settings_route():
    if "user" not in session:
        return redirect(url_for("main_routes.home_route"))

    user = collection.find_one({"email": session["user"]["email"]})

    return render_template("pages/settings/account.html", user=user)


@blueprint.route("subscription")
def settings_subscription_route():
    if "user" not in session:
        return redirect(url_for("main_routes.home_route"))

    user = collection.find_one({"email": session["user"]["email"]})

    return render_template("pages/settings/subscription.html", user=user)


@blueprint.route("/advanced")
def settings_advanced_route():
    if "user" not in session:
        return redirect(url_for("main_routes.home_route"))

    user = collection.find_one({"email": session["user"]["email"]})

    return render_template("pages/settings/advanced.html", user=user)
