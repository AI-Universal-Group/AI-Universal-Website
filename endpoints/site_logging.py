import hashlib
import datetime
from dotenv import load_dotenv
from flask import jsonify, make_response, request, session
from flask_restful import Resource, reqparse
from .helpers import page_loads_collection

load_dotenv()

parser = reqparse.RequestParser()
parser.add_argument("ip", type=str, default=None)
parser.add_argument("page", type=str, default=None)
parser.add_argument("user_agent", type=str, default=None)
parser.add_argument("browser", type=str, default=None)
parser.add_argument("referrer", type=str, default=None)
parser.add_argument("language", type=str, default=None)
parser.add_argument("screen_width", type=int, default=None)
parser.add_argument("screen_height", type=int, default=None)


class SiteLogging(Resource):
    """
    Class handling logging of events on the website to the database.
    """

    def post(self):
        args = parser.parse_args()

        ip = args["ip"]
        page = args["page"]
        user_agent = args["user_agent"]
        browser = args["browser"]
        referrer = args["referrer"]
        language = args["language"]
        screen_width = args["screen_width"]
        screen_height = args["screen_height"]

        # Get a hash of the session ID
        session_id = hashlib.sha256(session.sid.encode()).hexdigest()

        # Create a new document for the page load event
        page_load = {
            "session_id": session_id,
            "ip": ip,
            "page": page,
            "time": datetime.datetime.now(),
            "user_agent": user_agent,
            "browser": browser,
            "referrer": referrer,
            "language": language,
            "screen_width": screen_width,
            "screen_height": screen_height,
        }

        # Insert the document into the page_loads_collection
        page_loads_collection.insert_one(page_load)

        return make_response(jsonify({"message": "Page load event logged."}), 200)


def site_logging_resource():
    """
    Function returning an instance of SiteLogging class.
    """
    return SiteLogging
