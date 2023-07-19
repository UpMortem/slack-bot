import json
import os
from urllib.request import Request, urlopen
import requests

BASE_URL = os.environ["API_BASE_URL"]
SHARED_SECRET = os.environ["API_SHARED_SECRET"]


def get_team_data(team_id):
    url = f"{BASE_URL}/api/organization/get_team_data/{team_id}"
    headers = {"X-Shared-Secret": SHARED_SECRET}
    response = requests.get(url=url, headers=headers, timeout=30)
    data = response.json()
    if (data.get("error") is not None):
        raise Exception(data["error"])
    return {
        "openai_key": data["openai_key"],
        "slack_bot_token": data["slack_bot_token"],
        "has_reached_request_limit": data["has_reached_request_limit"],
        "owner_email": data["owner_email"],
    }


def revoke_token(team_id):
    url = f"{BASE_URL}/api/slack/revoke_token"
    headers = {"X-Shared-Secret": os.environ["API_SHARED_SECRET"]}
    # make post request with team id and token as data
    print("revoking tokens for team: " + str(team_id))
    response = requests.post(
        url=url,
        headers=headers,
        json={
            "team_id": team_id,
        },
        timeout=30
    )
    data = response.json()
    if (data.get("error") is not None):
        raise Exception(data["error"])
    return

def increment_request_count(team_id):
    url = f"{BASE_URL}/api/slack/increment_request_count"
    headers = {
        "X-Shared-Secret": SHARED_SECRET,
        "Content-Type": "application/json",
    }
    response = requests.post(
        url=url,
        headers=headers,
        json={
            "team_id": team_id,
        },
        timeout=30
    )
    data = response.json()
    if (data.get("error") is not None):
        raise Exception(data["error"])
    return
