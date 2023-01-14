from slack_bolt import App
import os

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


def command(text: str):
    return "You said: " + text
