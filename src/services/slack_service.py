from slack_bolt import App
import time
import os
import re
from services.openai_service import respond_to_user
from lib.retry import retry
from .api_service import get_key, increment_request_count, revoke_token
import traceback
import sys
# grabs the credentials from .env directly
slack_app = App()


users_map = {}


def send_message(channel: str, thread_ts: str, text: str, slack_bot_token: str):
    response = retry(
        lambda: slack_app.client.chat_postMessage(
            token=slack_bot_token,
            channel=channel,
            text=text,
            thread_ts=thread_ts,
        )
    )
    return response["ts"]


def update_message(channel: str, thread_ts: str, ts: str, text: str, slack_bot_token: str):
    response = retry(
        lambda: slack_app.client.chat_update(
            token=slack_bot_token,
            channel=channel,
            ts=ts,
            thread_ts=thread_ts,
            text=text
        )
    )
    return response["ts"]


def delete_message(channel: str, ts: str, slack_bot_token: str):
    response = retry(lambda: slack_app.client.chat_delete(
        token=slack_bot_token,
        channel=channel, ts=ts
    ))
    return response["ts"]


def get_thread_messages(channel: str, thread_ts: str, slack_bot_token: str):
    try:
        return retry(
            lambda: slack_app.client.conversations_replies(
                token=slack_bot_token,
                channel=channel,
                ts=thread_ts,
                include_all_metadata=True,
            )["messages"]
        )
    except Exception as e:
        print(e)


def get_thread_messages_with_usernames_json(channel: str, thread_ts: str, slack_bot_token: str):
    thread_messages = get_thread_messages(channel, thread_ts, slack_bot_token)
    messages_arr = [
        {
            "role": "user" if m.get("bot_id") is None else "assistant",
            "content": m["text"] + ". " + (get_user_name(m["user"], slack_bot_token) if m.get("bot_id") is None else ""),
            "name": re.sub(r"\s", "_", get_user_name(m["user"], slack_bot_token)) if m.get("bot_id") is None else "Haly",
        } for m in thread_messages
    ]
    return messages_arr


def find_user_by_id(user_id: str, slack_bot_token: str):
    try:
        return retry(lambda: slack_app.client.users_info(token=slack_bot_token, user=user_id))
    except Exception as e:
        print(e)


def get_user_name(user_id: str, slack_bot_token: str):
    if user_id not in users_map:
        user = find_user_by_id(user_id, slack_bot_token)
        users_map[user_id] = user["user"]["profile"]["real_name"]
    return users_map[user_id].capitalize()


def find_bot_id(payload):
    for auth in payload["authorizations"]:
        # Check if the current authorization is a bot
        if auth["is_bot"]:
            return auth["user_id"]

    return None


def get_sender(payload):
    return payload.get("event").get("user")


def handle_token_revoked(payload):
    team_id = payload.get("team_id")
    try:
        revoke_token(team_id)
    except Exception as error:
        print(error)
    return


def process_event_payload(payload):
    event = payload.get("event")
    event_type = event.get("type")
    if (event_type == "tokens_revoked"):
        handle_token_revoked(payload)
        return
    sender = get_sender(payload)
    if sender is None:
        print("sender not found")
        return

    bot_id = find_bot_id(payload)
    if not bot_id:
        print("botId not found")
        return

    if sender == bot_id:
        return

    channel = event.get("channel")
    text = event.get("text")
    thread_ts = event.get("thread_ts")
    ts = event.get("ts")
    team_id = event.get("team")
    user = event.get("user")
    try:
        keys = get_key(team_id)
        thread_to_reply = thread_ts
        if thread_ts != ts:
            thread_to_reply = ts

        msg_ts = send_message(
            channel,
            thread_to_reply,
            "*Thinking...*",
            keys["slack_bot_token"]
        )

        username = get_user_name(user, keys["slack_bot_token"])
        messages = [{
            "role": "user",
            "content": text + ". " + username,
            "name": re.sub(r"\s", "_", username),
        }]
        if thread_ts:
            messages = (
                get_thread_messages_with_usernames_json(
                    channel,
                    thread_ts,
                    keys["slack_bot_token"]
                )
                or messages
            )

        start_time = time.perf_counter()
        response = respond_to_user(messages, keys["openai_key"])
        increment_request_count(team_id)
        end_time = time.perf_counter()
        print(f"response generated in {round(end_time - start_time, 2)}s")

        return update_message(channel, thread_to_reply, msg_ts, response, keys["slack_bot_token"])
    except Exception as error:
        # Improve error handling
        print(error)
        etype, value, tb = sys.exc_info()
        print(traceback.print_exception(etype, value, tb))
        return
