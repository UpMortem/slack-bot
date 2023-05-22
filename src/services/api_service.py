# make request to localhost:6060/api/organization/get_key with X-Shared-Secret header
import os

import requests

BASE_URL = os.environ["API_BASE_URL"]

def get_key(team_id):
    url = f"{BASE_URL}/api/organization/get_key/{team_id}"
    headers = {"X-Shared-Secret": os.environ["API_SHARED_SECRET"]}
    response = requests.get(url=url, headers=headers, timeout=30)
    return response.json()["key"]
