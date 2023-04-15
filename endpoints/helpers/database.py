"""
This module provides a connection to MongoDB and relevant collections for user data.

(C) Zach Lagden 2023 All Rights Reserved.
This code may not be used, copied, distributed, or reproduced in part or in whole
for commercial or personal purposes without the express written consent of the owner. 
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

client = MongoClient(os.getenv("mongodb"), connect=False)
user_data_db = client["user_data"]

"""
Collection for storing user data such as username and password.
"""
users_collection = user_data_db["users"]

"""
Collection for storing user settings such as theme and language preferences.
"""
settings_collection = user_data_db["settings"]

"""
Collection for storing additional user information such as name, email, and phone number.
"""
user_information_collection = user_data_db["user_information"]
