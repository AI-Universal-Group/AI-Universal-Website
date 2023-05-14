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

# Databases

"""
Database for storing site data such as user accounts, user settings, site logs, errors, etc.
"""
site_data_db = client["site_data"]

"""
Database for storing user logs such as logins and signups.
Data includes ip addresses, times, etc.
"""
user_logs_db = client["user_logs"]

# Collections

"""
Collection for storing user data such as username and password.
"""
users_collection = site_data_db["users"]

"""
Collection for storing user settings such as theme and language preferences.
"""
settings_collection = site_data_db["settings"]

"""
Collection for storing page load logs
"""
page_loads_collection = site_data_db["page_loads"]

"""
Collection for storing user logins such as times and ip addresses.
"""
logins_collection = user_logs_db["logins"]

"""
Collection for storing user signups such as times and ip addresses.
"""
signups_collection = user_logs_db["signups"]
