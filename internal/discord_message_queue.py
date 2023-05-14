"""
(C) Zach Lagden 2023 All Rights Reserved.
This code may not be used, copied, distributed, or reproduced in part or in whole
for commercial or personal purposes without the express written consent of the owner. 
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

client = MongoClient(os.getenv("mongodb"), connect=False)
