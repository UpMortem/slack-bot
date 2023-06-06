import os

import requests

BASE_URL = os.environ["API_BASE_URL"]

def get_key(team_id):
    url = f"{BASE_URL}/api/organization/get_key/{team_id}"
    headers = {"X-Shared-Secret": os.environ["API_SHARED_SECRET"]}
    response = requests.get(url=url, headers=headers, timeout=30)
    data = response.json()
    if (data.get("error") is not None):
        raise Exception(data["error"])
    return {"openai_key": data["openai_key"], "slack_bot_token": data["slack_bot_token"]}
