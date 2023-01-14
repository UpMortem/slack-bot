from flask import jsonify
from services.slack_service import (
    send_message,
    get_thread_messages,
    get_thread_messages_with_usernames,
)
from services.openai_service import (
    respond_to_user,
    get_conversation_summary,
)
from threading import Thread


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
        response = respond_to_user(messages)
        return send_message(channel, thread_to_reply, response)
    except Exception as error:
        print(error)
        return


def post_event(request):
    if request.get("type") == "url_verification":
        return request.get("challenge")
    Thread(target=process_event_payload, args=(request,)).start()
    return jsonify({"message": "success"}), 200


def post_command(request):
    command = request.params.get("commandName")

    try:
        if command == "test":
            return jsonify({"message": "This is a test command"}), 200
        else:
            return (
                jsonify(
                    {
                        "error": f"Sorry, I don't know how to handle the command '{command}'"
                    }
                ),
                200,
            )
    except Exception as error:
        print(error)
        return jsonify({"error": "An error occurred while processing the request"}), 500


def get_thread_summary(channel_id, thread_ts):
    thread_messages = get_thread_messages(channel_id, thread_ts)
    summary = get_conversation_summary(thread_messages)

    return summary


def find_bot_id(payload):
    bot = next((auth for auth in payload["authorizations"] if auth["is_bot"]), None)
    return bot["user_id"]
