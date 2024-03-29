import threading
import time
import os
import re
from slack_bolt import App
from lib.split_string import split_string_into_chunks
from semantic_search.semantic_search.google_tasks import trigger_indexation
from semantic_search.semantic_search.load_messages import handle_message_update_and_reindex
from semantic_search.semantic_search.query import smart_query
from services.openai_service import respond_to_user
from lib.retry import retry
from services.api_service import get_team_data, increment_request_count, revoke_token, is_smart_search_available
import logging

DAILY_MESSAGE_LIMIT = 10
MESSAGE_LENGTH_LIMIT = 2500
HOME_TAB_MESSAGE = ":wave: Hi there! I'm Haly, your friendly Slack chatbot! I'm here to assist you with any questions or problems you may have. With my expertise in a wide range of topics, feel free to ask me anything!\n\
I'm not just a good listener, but also ready to help you out. Just type in your question or request, and I'll do my best to provide you with the information you need.\n\
You can reach out to me by direct messaging me or by adding me to a public channel. Just tag me using @Haly to start a conversation. Let's get chatting!"
WELCOME_MESSAGE = "Hello everyone! I'm Haly, your friendly chatbot. I'm here to help you with anything you need. Just mention my name (@Haly) and ask your question, and I'll do my best to assist you. Looking forward to chatting with you all! 😊"

# grabs the credentials from .env directly
slack_app = App()

logging.basicConfig(level=os.environ["LOG_LEVEL"])

users_map = {}


def update_message(channel: str, thread_ts: str, ts: str, text: str, slack_bot_token: str, blocks=None):
    response = retry(
        lambda: slack_app.client.chat_update(
            token=slack_bot_token,
            channel=channel,
            ts=ts,
            thread_ts=thread_ts,
            text=text,
            blocks=blocks,
            unfurl_links=True,
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


def is_direct_message(event) -> bool:
    return event.get("channel_type") == "im"


#########################################
# Event Handlers
#########################################

@slack_app.event("tokens_revoked")
def handle_tokens_revoked(body, logger):
    team_id = body.get("team_id")
    if len(body.get("event").get("tokens").get("bot")) > 0:
        try:
            revoke_token(team_id)
        except Exception as error:
            logging.error(error, exc_info=True)
    return


@slack_app.event(event={"type": re.compile("(app_mention)"), "subtype": None},  matchers=[no_bot_messages, no_message_changed])
def handle_message_to_bot(event, say):
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
            if team_data["product_name"] == "Free plan":
                limit_reached_message = f"It appears you've exceeded the usage limit. To continue enjoying our services without interruption, kindly get in touch with your organization's administrator on {team_data['owner_email']} and request for a subscription upgrade."
            else:
                limit_reached_message = f"It appears you've exceeded the usage limit. Contact support at support@haly.ai to increase your usage limit."
            say(
                channel=channel,
                thread_ts=thread_to_reply,
                text=limit_reached_message,
                token=slack_bot_token
            )
            logging.info(
                f"Organization {team_id} has exceeded the usage limit")
            return

        # Send 'thinking' message while we process the request
        response = say(
            channel=channel,
            thread_ts=thread_to_reply,
            text="Thinking...",
            token=slack_bot_token,
            unfurl_links=True,
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

        smart_search_available = is_smart_search_available(team_id)
        start_time = time.perf_counter()

        search_pattern = r'^<\@\w+>\s+search\s+(.+)$'

        match = re.search(search_pattern, text)
        if match and smart_search_available:
            search_query = match.group(1)
            response, messages_links = smart_query(
                team_id, search_query, username)
        else:
            response = respond_to_user(messages, openAi_key, team_id)
            messages_links = []

        end_time = time.perf_counter()
        logging.info(
            f"response generated in {round(end_time - start_time, 2)}s"
        )

        # Split message because Slack doesn't allow long messages
        if (len(response) > MESSAGE_LENGTH_LIMIT):
            chunks = split_string_into_chunks(response, MESSAGE_LENGTH_LIMIT)
            update_message(
                channel, thread_to_reply, msg_ts, chunks[0], slack_bot_token
            )
            for chunk in chunks[1:]:
                say(
                    channel=channel,
                    thread_ts=thread_to_reply,
                    text=chunk,
                    token=slack_bot_token
                )
        else:
            update_message(
                channel, thread_to_reply, msg_ts, response, slack_bot_token
            )

        # Send links used in Semantic Search as a new Message
        if len(messages_links) > 0:
            say(
                channel=channel,
                thread_ts=thread_to_reply,
                text="",
                blocks=reply_blocks(message="", links=messages_links),
                token=slack_bot_token
            )

        # Increment request count
        try:
            increment_request_count(team_id)
        except Exception as error:
            logging.error(error)

    except Exception as error:
        # Improve error handling
        logging.error(error, exc_info=True)
        return


@slack_app.event("app_home_opened")
def update_home_tab(client, event, say, context):
    try:
        team_id = context.get("team_id")
        team_data = get_team_data(team_id)
        if (event["tab"] == "home" and event["view"] is None):
            say(
                text=HOME_TAB_MESSAGE,
                token=team_data["slack_bot_token"]
            )
        current_user = event["user"]
        owner_user = team_data["owner_slack_id"]

        request_count = team_data["request_count"]
        product_name = team_data["product_name"]
        has_free_plan = product_name == "Free plan"

        # Row 1: Current Plan and Upgrade Button
        current_plan_section = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"✅ *{product_name}* ",
            },
        }
        if has_free_plan and current_user == owner_user:
            current_plan_section["accessory"] = {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Upgrade",
                },
                "url": "https://billing.haly.ai/pricing",
                "action_id": "upgrade_plan",

            }

        # Info section
        info_section = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "👋 I'm Haly, your friendly Slack chatbot. I'm here to help you with any questions or problems you might have. I'm an expert in everything, so feel free to ask me anything. I'm a good listener and always ready to assist you. Just type your question or request, and I'll do my best to provide you with the information you need. You can direct message me or add me to a public channel. Just tag me to talk with me with @Haly.",
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
                "elements": [
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
            "url": "https://billing.haly.ai",
        }
        contact_support_button = {
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": "✉️ Contact support",
                "emoji": True
            },
            "action_id": "email_support",
            "url": "https://www.haly.ai/support",
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
        client.views_publish(
            user_id=event["user"], view=home_tab_content, token=team_data["slack_bot_token"])

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


@slack_app.action(re.compile("link_to_expert\w*"))
def handle_some_action(ack, body, logger):
    ack()
    logger.debug(body)


@slack_app.action("upgrade_plan")
def handle_some_action(ack, body, logger):
    ack()
    logger.debug(body)


@slack_app.event("message")
def hande_message_events(body, event, say, logger):
    # DM's to haly
    if is_direct_message(event) and no_message_changed(event) and event.get("bot_id") is None:
        return handle_message_to_bot(event, say)
    else:
        threading.Thread(
            target=handle_semantic_search_update, args=[body]
        ).start()
    logger.debug(body)


def handle_semantic_search_update(body):
    if not is_smart_search_available(body['team_id']):
        return None
    return handle_message_update_and_reindex(body)


@slack_app.event("app_mention")
def handle_message_events(body, logger):
    logger.debug(body)


@slack_app.event("app_uninstalled")
def handle_app_uninstalled_events(body, logger):
    logger.debug(body)


def handle_app_installed(request):
    try:
        team_id = request.form.get("team_id")
        team_data = get_team_data(team_id)
        if team_data["slack_bot_token"] is None:
            logging.info(
                f"App installed but no token found for team {team_id}")
        conversation_list = retry(
            lambda: slack_app.client.conversations_list(
                token=team_data["slack_bot_token"],
                types="public_channel",
                exclude_archived=True,
                limit=10
            )
        )
        # send message to general channel
        for conversation in conversation_list["channels"]:
            if conversation["is_general"]:
                retry(
                    lambda: slack_app.client.conversations_join(
                        token=team_data["slack_bot_token"],
                        channel=conversation["id"]
                    )
                )
                retry(
                    lambda: slack_app.client.chat_postMessage(
                        token=team_data["slack_bot_token"],
                        channel=conversation["id"],
                        text=WELCOME_MESSAGE
                    )
                )
        return "OK"
    except Exception as e:
        logging.error(e, exc_info=True)
        return "Error handling app installation", 500


@slack_app.event("member_joined_channel")
def handle_member_joined(event, body, logger, context):
    team_id = body['team_id']
    invited_user_id = event['user']
    bot_id = context['bot_user_id']
    if invited_user_id != bot_id:
        return
    if not is_smart_search_available(team_id):
        return
    logger.info("Haly was added to a channel, trigger indexing here.")
    trigger_indexation(context['team_id'], context['channel_id'])


def reply_blocks(message, links=[], experts=[]):
    link_sections = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Messages used to generate this response:* " + " ".join([f"<{link}|[{index + 1}]>" for index, link in enumerate(links)]),
            }
        }
    ] if len(links) > 0 else []

    experts = [
        {
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": expert["name"],
            },
            "url": expert["url"],
            "action_id": f"link_to_expert_{expert['name']}"
        } for expert in experts
    ]

    experts_section = [
        {
            "type": "divider"
        },
        {
            "type": "rich_text",
            "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [
                            {
                                "type": "text",
                                "text": "Possible Subject Matter Experts",
                                "style": {
                                    "bold": True
                                }
                            }
                        ]
                    }
            ]
        },
        {
            "type": "actions",
            "elements": [*experts]
        }
    ] if len(experts) > 0 else []

    text_section = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": message
            }
        },
    ] if len(message) > 0 else []

    return [
        *text_section,
        *experts_section,
        *link_sections,
    ]
