import json
from threading import Thread
from typing import Callable
import time
import os
import re
from slack_bolt import App, Say, BoltContext
from services.openai_service import respond_to_user
from lib.retry import retry
from .api_service import get_team_data, increment_request_count, revoke_token
import logging

DAILY_MESSAGE_LIMIT = 10

# grabs the credentials from .env directly
slack_app = App()

logging.basicConfig(level=os.environ["LOG_LEVEL"])

users_map = {}

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

def no_bot_messages(message) -> bool:
    return message.get("bot_id") is None if message else True

def no_message_changed(event) -> bool:
    return event.get("subtype") != "message_changed" and event.get("edited") is None


#########################################
# Event Handlers
#########################################

@slack_app.event("tokens_revoked")
def handle_tokens_revoked(body, logger):
    team_id = body.get("team_id")
    try:
        revoke_token(team_id)
    except Exception as error:
        print(error)
    return

@slack_app.event(event={"type": re.compile("(message)|(app_mention)"), "subtype": None},  matchers=[no_bot_messages, no_message_changed])
def handle_app_mention(event, say):
    channel = event.get("channel")
    text = event.get("text")
    thread_ts = event.get("thread_ts")
    ts = event.get("ts")
    team_id = event.get("team")
    user = event.get("user")
    try:
        # Check if message is already in a thread, if it is, reply to that thread, else reply to the message in a new thread
        thread_to_reply = ts if thread_ts != ts else thread_ts

        # Get neccessary keys
        team_data = get_team_data(team_id)
        slack_bot_token = team_data["slack_bot_token"]
        openAi_key = team_data["openai_key"] if team_data["openai_key"] else os.environ["OPENAI_API_KEY"]

        # Check quota
        if team_data["has_reached_request_limit"] == True:
            say(
                channel=channel,
                thread_ts=thread_to_reply,
                text=f"It appears you've exceeded the usage limit. To continue enjoying our services without interruption, kindly get in touch with your organization's administrator on {team_data['owner_email']} and request for a subscription upgrade.",
                token=slack_bot_token
            )
            return

        # Send 'thinking' message while we process the request
        response = say(
            channel=channel,
            thread_ts=thread_to_reply,
            text="Thinking...",
            token=slack_bot_token
        )
        msg_ts = response["ts"]
        
        # Get messages in thread
        username = get_user_name(user, slack_bot_token)
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
                    slack_bot_token
                )
                or messages
            )

        start_time = time.perf_counter()
        response = respond_to_user(messages, openAi_key)
        end_time = time.perf_counter()
        print(f"response generated in {round(end_time - start_time, 2)}s")

        # Increment request count in a new Thread
        Thread(target=increment_request_count, args=(team_id,)).start()
        
        return update_message(channel, thread_to_reply, msg_ts, response, slack_bot_token)
    except Exception as error:
        # Improve error handling
        print(error)
        return


# Respond to the App Home opened event
@slack_app.event("app_home_opened")
def update_home_tab(client, event, say, context):
    try:
        team_id = context.get("team_id")
        team_data = get_team_data(team_id)
        current_user = event["user"]
        owner_user = team_data["owner_slack_id"]

        # print(json.dumps(event, indent=4))
        # Get the user's plan information (Replace this with your logic to fetch the user's plan)
        request_count = team_data["request_count"]
        product_name = team_data["product_name"]
        has_free_plan = product_name == "Free plan"

        # Row 1: Current Plan and Upgrade Button
        current_plan_section = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{product_name}* ",
            },
        }
        if has_free_plan and current_user == owner_user:
            current_plan_section["accessory"] = {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Upgrade",
                },
                "url": "https://billing.upmortem.com/pricing",
                "action_id": "upgrade_plan",

            }

        # Info section
        info_section = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "I'm Haly, your friendly Slack chatbot. I'm here to help you with any questions or problems you might have. I'm an expert in everything, so feel free to ask me anything. I'm a good listener and always ready to assist you. Just type your question or request, and I'll do my best to provide you with the information you need. You can direct message me or add me to a public channel. Just tag me to talk with me with @Haly.",
            },
        }

        row1_blocks = [
            current_plan_section,
            {
                "type": "divider"
            },
            info_section,
            {
                "type": "divider"
            },
        ]
        if has_free_plan:
            # Messages count section
            messages_section = {
                "type": "context",
                "elements" : [
                    {
                        "type": "mrkdwn",
                        "text": f"`{request_count * '█'}{(DAILY_MESSAGE_LIMIT - request_count) * '⁢ ⁢'}`    *{request_count}/{DAILY_MESSAGE_LIMIT} daily messages used*",
                    },
                ]
            }
            row1_blocks.append(messages_section)

        go_to_dashboard_button = {
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": "🌐 Go to Dashboard",
                "emoji": True
            },
            "action_id": "go_to_dashboard",
            "url": "https://billing.upmortem.com",
        }
        contact_support_button = {
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": "✉️ Contact support",
                "emoji": True
            },
            "action_id": "email_support",
            "url": "mailto:support@upmortem.com",
        }
        elements = [
            contact_support_button
        ]
        if current_user == owner_user:
            elements.insert(0, go_to_dashboard_button)

        row2_blocks = [
            {
                "type": "actions",
                "elements": elements
            }
        ]

        # Combine both rows into the Home Tab view
        home_tab_content = {
            "type": "home",
            "blocks": [*row1_blocks, *row2_blocks],
        }

        # Publish the updated Home Tab view
        client.views_publish(user_id=event["user"], view=home_tab_content, token=team_data["slack_bot_token"])

    except Exception as e:
        print("Error publishing home tab view:", e)

@slack_app.action("go_to_dashboard")
def handle_some_action(ack, body, logger):
    ack()
    logger.debug(body)

@slack_app.action("email_support")
def handle_some_action(ack, body, logger):
    ack()
    logger.debug(body)

@slack_app.action("upgrade_plan")
def handle_some_action(ack, body, logger):
    ack()
    logger.debug(body)

@slack_app.event("message")
def handle_message_events(body, logger):
    logger.debug(body)

@slack_app.event("app_mention")
def handle_message_events(body, logger):
    logger.debug(body)

@slack_app.event("app_uninstalled")
def handle_app_uninstalled_events(body, logger):
    logger.debug(body)
