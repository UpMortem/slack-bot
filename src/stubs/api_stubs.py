import os
team_data_stub = {
    "openai_key": os.environ["OPENAI_API_KEY"],
    "slack_bot_token": os.environ["SLACK_BOT_TOKEN"],
    "has_reached_request_limit": False,
    "owner_email": "test@haly.com",
    "owner_slack_id": os.environ["SLACK_USER_ID"],
    "request_count": 0,
    "product_name": "test",
}
