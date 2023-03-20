# Sort the imports
import hashlib
import os

from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, request, session, url_for, render_template, redirect
from flask_minify import Minify
from flask_restful import Api, Resource
from flask_session import Session
from pymongo import MongoClient

# Load Env
load_dotenv()

# Configuration

users_file = "users.json"

# Flask Configuration
SESSION_COOKIE_NAME = 'wrld'
SESSION_TYPE = 'filesystem'

# Init Flask
app = Flask(__name__)
app.config.from_object(__name__)

# Init Flask Extensions
Session(app)
api = Api(app)
Minify(
    app=app,
    html=True,
    js=True,
    cssless=True
)

# MongoDB Configuration
client = MongoClient(os.getenv("mongodb"))
db = client["mydatabase"]
users_collection = db["users"]

# Api

# The UserManagement is a class that inherits from the Resource class.
class UserManagment(Resource):
    # The get method returns information about the current logged in user, if logged in, otherwise returns a 401 error.
    def get(self):
        if 'user' not in session:
            return make_response(jsonify({
                "ok": False,
                "code": 401,
                "error": "401 Unauthorized"
            }), 401)

        # Use the username to retrieve the user from the users collection in MongoDB
        found_user = users_collection.find_one({"username": session['user']['username']})

        user_data_to_return = {
            "uuid": str(found_user["_id"]),
            "username": found_user["username"],
            "email": found_user["email"],
            "phone_number": found_user["phone_number"]
        }

        return jsonify({
            "ok": True,
            "code": 200,
            "data": user_data_to_return
        })

    # The post method receives a username, password and logout parameters in the headers. It either logs out user from session or creates/verifies username/password and adds it to the users' file.
    def post(self):
        username = request.headers.get("username")
        password = request.headers.get("password")
        logout = request.headers.get("logout")

        if logout == "true":
            session.pop('user', None)
            return make_response(jsonify({
                    "ok": True,
                    "code": 200,
                    "message": "Logged out."
                }), 200)

        elif (not username or not password) and not logout:
            return make_response(jsonify({
                "ok": False,
                "code": 400,
                "error": "400 Bad Request: Missing username or password header."
            }), 400)

        # Hashes the password with SHA256 algorithm
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Find the user with matching username and hashed password, using the `find_one()` method of the `users_collection`
        found_user = users_collection.find_one({"username": username, "password": hashed_password})

        if not found_user:
            return make_response(jsonify({
                "ok": False,
                "code": 401,
                "error": "401 Unauthorized: Incorrect username or password."
            }), 401)

        # Store the found user in the session
        session['user'] = {
            "uuid": str(found_user["_id"]),
            "username": found_user["username"]
        }
        return jsonify({
            "ok": True,
            "code": 200,
            "data": session['user']
        })

    # The put method receives a username and password and adds this new user to the users' file after checking unique entry.
    def put(self):
        username = request.headers.get("username")
        password = request.headers.get("password")
        phone_number = request.headers.get("phone_number")
        email = request.headers.get("email")

        # Hashes the password with SHA256 algorithm.
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # check whether username already exists in the database
        existing_user = users_collection.find_one({"username": username})
        if existing_user:
            return make_response(jsonify({
                "ok": False,
                "code": 409,
                "error": "Username already exists in the database."
            }), 409)

        # check whether email already exists in the database
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            return make_response(jsonify({
                "ok": False,
                "code": 409,
                "error": "Email already exists in the database."
            }), 409)

        # check whether phone number already exists in the database
        existing_user = users_collection.find_one({"phone_number": phone_number})
        if existing_user:
            return make_response(jsonify({
                "ok": False,
                "code": 409,
                "error": "Phone number already exists in the database."
            }), 409)

        # Create a new user document with the given username and hashed password
        new_user = {"username": username, "password": hashed_password, "phone_number": phone_number, "email": email}

        # Insert the new document into the users collection, and store the assigned `_id` in the session.
        result = users_collection.insert_one(new_user)
        session['user'] = {
            "uuid": str(result.inserted_id),
            "username": username
        }

        # Return success message with created user credentials.
        return make_response(jsonify({
            "ok": True,
            "code": 201,
            "data": {
                "username": username,
                "uuid": str(result.inserted_id)
            }
        }), 201)

    # The following function updates the information of a user including their username and password
    def patch(self):
        # Checks whether the session is associated with a user.
        if 'user' in session:
            uid = session['user']['uuid'] # Gets the unique identifier from session data for the user.
            current_password = request.headers.get("password") # Fetches the user's current password from the header.
            new_username = request.headers.get("new_username") # Fetches the updated username, if provided, from the header. 
            new_password = request.headers.get("new_password") # Fetches the updated password, if provided, from the header.
            
            # Error handling, if either the new username or password entered are empty or not provided.
            if not any([new_username, new_password]):
                return make_response(jsonify({
                    "ok": False,
                    "code": 400,
                    "error": "Bad Request: Headers 'new_username' and or 'new_password' are required and cannot be empty."
                }), 400)
            
            if not current_password:
                return make_response(jsonify({
                    "ok": False,
                    "code": 400,
                    "error": "Bad Request: 'password' is required and cannot be empty."
                }), 400)
                
            user_info = users_collection.find_one({"_id": ObjectId(uid)}) # Gets the particular user info using the UID.
            stored_password = user_info['password'] # Fetches the user's saved password from user_info.
            
            # Authentication check -- If the user has entered the correct current password.
            if hashlib.sha256(current_password.encode()).hexdigest() == stored_password:
                # Updates the user's information if new values are provided.
                if new_username is not None and len(new_username) > 0:
                    users_collection.update_one({"_id": ObjectId(uid)}, {"$set": {"username": new_username}})
                if new_password is not None and len(new_password) > 0:
                    users_collection.update_one({"_id": ObjectId(uid)}, {"$set": {"password": hashlib.sha256(new_password.encode()).hexdigest()}})
                session['user']['username'] = new_username # Update the username inside the session object.
                # Return success message if all the above conditions are met & changes have been made successfully
                return make_response(jsonify({
                    "ok": True,
                    "code": 200,
                    "message": "User data updated successfully."
                }), 200)
            else:
                # Return failure message if the given credentials don't match the saved user information.
                return make_response(jsonify({
                    "ok": False,
                    "code": 401,
                    "error": "Unauthorized: Incorrect password."
                }), 401)
        else:
            # Return error message if no active session is detected.
            return make_response(jsonify({
                "ok": False,
                "code": 401,
                "error": "Unauthorized"
            }), 401)
    

    # The following function deletes the user data from the system.
    def delete(self):
        if 'user' in session:
            print(session)
            uid = session['user']['uuid'] # Acquiring the UUID of the user if they are logged in & have an existing session.
            users_collection.delete_one({'_id': ObjectId(uid)}) # Removes the user entry corresponding to the given UUID.
            
            session.pop('user', None) # Destroys the active session.
            # Returns JSON response indicating successful deletion.
            return make_response(jsonify({
                "ok": True,
                "code": 200,
                "message": "User deleted successfully."
            }), 200)
        else:
            # Returns error message if no active session is detected.
            return make_response(jsonify({
                "ok": False,
                "code": 401,
                "error": "Unauthorized"
            }), 401)

# Website

@app.route('/')
def index():
    if 'user' not in session:
        return render_template('pages/home.html', user=None)

    # Use the username to retrieve the user from the users collection in MongoDB
    found_user = users_collection.find_one({"username": session['user']['username']})

    user_data = {
        "uuid": str(found_user["_id"]),
        "username": found_user["username"],
        "email": found_user["email"],
        "phone_number": found_user["phone_number"]
    }
    return render_template('pages/home.html', user=user_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Grab username and password from POST form data
        email = request.form.get("email")
        password = request.form.get("password")

        # Hashes the password with SHA256 algorithm
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Find the user with matching username and hashed password, using the `find_one()` method of the `users_collection`
        found_user = users_collection.find_one({"username": email, "password": hashed_password})

        # Find the user with matching email and hashed password, using the `find_one()` method of the `users_collection`
        found_user = users_collection.find_one({"email": email, "password": hashed_password})

        if not found_user:
            error = "Could not find an account with that username"
            return render_template('pages/login.html', error=error)

        # Store the found user in the session
        session['user'] = {
            "uuid": str(found_user["_id"]),
            "username": found_user["username"]
        }

        return redirect('/')

    if 'user' not in session:
        return render_template('pages/login.html')

    return redirect('/')

@app.route('/signup')
def signup():
    if 'user' not in session:
        return render_template('pages/signup.html')

    return redirect('/')

api.add_resource(UserManagment, '/api/v1/user')

if __name__ == "__main__":
    app.run(debug=True, port=5000)
