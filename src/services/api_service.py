import json
import logging
import os
from urllib.request import Request, urlopen
import requests
from stubs.api_stubs import team_data_stub

BASE_URL = os.environ["API_BASE_URL"]
SHARED_SECRET = os.environ["API_SHARED_SECRET"]
STANDALONE = os.environ["STANDALONE"] == "true"


def get_team_data(team_id):
    """
    Makes a call to the internal API to retrieve the team data.
    This function is currently duplicated in src/semantic_search/semantic_search/external_services/internal_api.
    """
    if STANDALONE:
        return team_data_stub
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
        "owner_slack_id": data["owner_slack_id"],
        "request_count": data["request_count"],
        "product_name": data["product_name"],
    }


def revoke_token(team_id):
    if STANDALONE:
        return
    url = f"{BASE_URL}/api/slack/revoke_token"
    headers = {"X-Shared-Secret": os.environ["API_SHARED_SECRET"]}
    # make post request with team id and token as data
    logging.debug("revoking tokens for team: " + str(team_id))
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
    if STANDALONE:
        return
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


def get_team_subscription(team_id):
    url = f"{BASE_URL}/api/organization/stripe_subscription_by_slack_team_id/{team_id}"
    headers = {"X-Shared-Secret": SHARED_SECRET}
    response = requests.get(url=url, headers=headers, timeout=30)
    data = response.json()
    if data.get("error") is not None:
        raise Exception(data["error"])
    return {
        "product_name": data["product_name"],
        "product_id": data["product_id"],
        "semantic_search_enabled": data["semantic_search_enabled"],
    }


def send_prompt_subscription_notifications(detections, channel, thread_ts, ts, team_id):
    url = f"{BASE_URL}/api/prompt_subscriptions/notification"
    headers = {"X-Shared-Secret": SHARED_SECRET}
    response = requests.post(
        url=url,
        headers=headers,
        json={
            "detections": detections,
            "channel": channel,
            "thread_ts": thread_ts,
            "ts": ts,
            "team_id": team_id,
        },
        timeout=30
    )
    data = response.json()
    if data.get("error") is not None:
        raise Exception(data["error"])
    return


def get_user_subscriptions(user_id, team_id):
    url = f"{BASE_URL}/api/prompt_subscriptions/{team_id}/{user_id}"
    headers = {"X-Shared-Secret": SHARED_SECRET}
    response = requests.get(url=url, headers=headers, timeout=30)
    data = response.json()
    if data.get("error") is not None:
        raise Exception(data["error"])
    return data["subscriptions"]


def delete_subscription(subscription_id, slack_team_id, slack_user_id):
    url = f"{BASE_URL}/api/prompt_subscriptions/default/delete"
    data = {
        "subscription_id": subscription_id,
        "slack_team_id": slack_team_id,
        "slack_user_id": slack_user_id,
    }
    headers = {"X-Shared-Secret": SHARED_SECRET}
    response = requests.post(
        url=url,
        headers=headers,
        json=data,
        timeout=30
    )
    data = response.json()
    if data.get("error") is not None:
        raise Exception(data["error"])
    return data["success"]


def add_subscription(subscription_id, slack_team_id, slack_user_id):
    url = f"{BASE_URL}/api/prompt_subscriptions/default/add"
    data = {
        "subscription_id": subscription_id,
        "slack_team_id": slack_team_id,
        "slack_user_id": slack_user_id,
    }
    headers = {"X-Shared-Secret": SHARED_SECRET}
    response = requests.post(
        url=url,
        headers=headers,
        json=data,
        timeout=30
    )
    data = response.json()
    if data.get("error") is not None:
        raise Exception(data["error"])
    return data["success"]


# @todo cache results
def is_smart_search_available(team_id):
    subscription = get_team_subscription(team_id)
    return subscription["semantic_search_enabled"] is True
