"""
(C) Zach Lagden 2023 All Rights Reserved.
This code may not be used, copied, distributed, or reproduced in part or in whole
for commercial or personal purposes without the express written consent of the owner. 
"""

import hashlib
import os

from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import session
from flask_restful import Resource, reqparse
from .helpers import users_collection

load_dotenv()

users_collection.create_index("username", unique=True)

parser = reqparse.RequestParser()
parser.add_argument("model", type=str)
parser.add_argument("prompt", type=str)


def is_authenticated(session_user):
    return True if session_user else False


class AiPrompts(Resource):
    def get(self):
        if not is_authenticated(session.get("user")):
            return {"message": "401 Unauthorized"}, 401


def AiPromptsResource():
    return AiPrompts
