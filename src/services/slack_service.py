from slack_bolt import App
import time
import os
from services.openai_service import respond_to_user

# grabs the credentials from .env directly
slack_app = App()
users_map = {}

def send_message(channel: str, thread_ts: str, text: str):
    try:
        slack_app.client.chat_postMessage(
            token=os.environ["SLACK_BOT_TOKEN"],
            channel=channel,
            text=text,
            thread_ts=thread_ts,
        )
    except Exception as e:
        print(e)


def get_thread_messages(channel: str, thread_ts: str):
    try:
        result = slack_app.client.conversations_replies(
            token=os.environ["SLACK_BOT_TOKEN"],
            channel=channel,
            ts=thread_ts,
            include_all_metadata=True,
        )
        return result["messages"]
    except Exception as e:
        print(e)


def get_thread_messages_with_usernames(channel: str, thread_ts: str, bot_id: str):
    thread_messages = get_thread_messages(channel, thread_ts)
    messages_arr = [
        f"HALY: {m['text']}"
        if m.get("bot_id")
        else f"{get_username(m['user'])}: {m['text'].replace(f'<@{bot_id}>', '').strip()}"
        for m in thread_messages
    ]
    return "\n".join(messages_arr)


def find_user_by_id(user_id: str):
    try:
        return slack_app.client.users_info(user=user_id)
    except Exception as e:
        print(e)


def get_username(user_id: str):
    if user_id not in users_map:
        user = find_user_by_id(user_id)
        users_map[user_id] = user["user"]["name"]
    return users_map[user_id]

def find_bot_id(payload):
    for auth in payload["authorizations"]:
        # Check if the current authorization is a bot
        if auth["is_bot"]:
            return auth["user_id"]

    return None

def get_sender(payload):
    return payload.get("event").get("user")


def process_event_payload(payload):
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

    event = payload.get("event")
    channel = event.get("channel")
    text = event.get("text")
    thread_ts = event.get("thread_ts")
    ts = event.get("ts")

    try:
        thread_to_reply = thread_ts
        if thread_ts != ts:
            thread_to_reply = ts
        messages = f"USER: {text.replace(f'<@{bot_id}>','').strip()}"
        if thread_ts:
            messages = (
                get_thread_messages_with_usernames(channel, thread_ts, bot_id)
                or messages
            )

        start_time = time.perf_counter()
        response = respond_to_user(messages)
        end_time = time.perf_counter()
        print(f"response generated in {round(end_time - start_time, 2)}s")

        return send_message(channel, thread_to_reply, response)
    except Exception as error:
        # Improve error handling
        print(error)
        return
