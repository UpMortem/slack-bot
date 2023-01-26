from flask import jsonify
import time
from services.slack_service import (
    send_message,
    get_thread_messages,
    get_thread_messages_with_usernames,
)
from services.openai_service import respond_to_user
from threading import Thread

# POST /slack/events
def post_event(request):
    if request.get("type") == "url_verification":
        return request.get("challenge")

    Thread(target=process_event_payload, args=(request,)).start()
    return jsonify({"message": "success"}), 200


def find_bot_id(payload):
    for auth in payload["authorizations"]:
        # Check if the current authorization is a bot
        if auth["is_bot"]:
            return auth["user_id"]

    return None


def process_event_payload(payload):
    event = payload.get("event")
    channel = event.get("channel")
    text = event.get("text")
    thread_ts = event.get("thread_ts")
    ts = event.get("ts")
    bot_id = find_bot_id(payload)
    if not bot_id:
        print("botId not found")
        return
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
        response = response + f"\n\n\n_response generated in {round(end_time - start_time, 2)}s_ :hourglass:"

        return send_message(channel, thread_to_reply, response)
    except Exception as error:
        # Improve error handling
        print(error)
        return
