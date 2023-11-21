import requests

from ..config import get_api_base_url, get_api_shared_secret, is_standalone, get_openai_key, get_slack_token, \
    get_slack_user_id


def get_team_data_stub():
    return {
        "openai_key": get_openai_key(),
        "slack_bot_token": get_slack_token(),
        "has_reached_request_limit": False,
        "owner_email": "test@haly.com",
        "owner_slack_id": get_slack_user_id(),
        "request_count": 0,
        "product_name": "test",
    }


def get_team_data(team_id):
    """
    Makes a call to the internal API to retrieve the team data.
    This function is currently duplicated in src/services/api_service.
    """
    if is_standalone():
        return get_team_data_stub()
    url = f"{get_api_base_url()}/api/organization/get_team_data/{team_id}"
    headers = {"X-Shared-Secret": get_api_shared_secret()}
    response = requests.get(url=url, headers=headers, timeout=30)
    data = response.json()
    if data.get("error") is not None:
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
