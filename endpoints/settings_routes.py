"""
(C) Zach Lagden 2023 All Rights Reserved.
This code may not be used, copied, distributed, or reproduced in part or in whole
for commercial or personal purposes without the express written consent of the owner. 
"""

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

blueprint = Blueprint("settings_routes", __name__, url_prefix="/settings")


@blueprint.route("/")
def settings_route():
    user = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "01234567890",
        "subscription": {
            "type": "Gold",
            "next_billing_date": "2023-05-12",
            "last_billing_date": "2023-04-12",
            "credit": 100.00,
        },
    }

    if "user" not in session:
        return redirect(url_for("main_routes.home_route"))

    return render_template("app/settings/account.html", user=user)


@blueprint.route("subscription")
def settings_subscription_route():
    user = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "01234567890",
        "subscription": {
            "type": "Gold",
            "next_billing_date": "2023-05-12",
            "last_billing_date": "2023-04-12",
            "credit": 100.00,
        },
    }
    return render_template("app/settings/subscription.html", user=user)


@blueprint.route("/advanced")
def settings_advanced_route():
    user = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "01234567890",
        "subscription": {
            "type": "Gold",
            "next_billing_date": "2023-05-12",
            "last_billing_date": "2023-04-12",
            "credit": 100.00,
        },
    }
    return render_template("app/settings/advanced.html", user=user)
