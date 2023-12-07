import datetime as dt
import logging
import time
from typing import Optional
from retry import retry
from slack_sdk.errors import SlackApiError
from slack_sdk import WebClient

from .internal_api import get_team_data
from ..config import CONTEXT_LENGTH

slack_names = {}

clients = {}


def get_client(team_id: str):
    if team_id not in clients:
        clients[team_id] = _create_new_client(team_id)
        return clients[team_id][0]
    (client, exp) = clients[team_id]
    if exp > dt.datetime.now():
        return client
    clients[team_id] = _create_new_client(team_id)
    return clients[team_id][0]


def _create_new_client(team_id: str):
    team_data = get_team_data(team_id)
    client = WebClient(token=team_data["slack_bot_token"])
    return client, dt.datetime.now() + dt.timedelta(days=1)


@retry(delay=5, backoff=2, tries=8)
def fetch_thread_messages(team_id, channel_id, thread_ts):
    try:
        return get_client(team_id).conversations_replies(channel=channel_id, ts=thread_ts)["messages"]
    except SlackApiError as e:
        logging.error("Error fetching thread replies: %s", e, exc_info=True)


@retry(delay=5, backoff=2, tries=8)
def fetch_channel_messages(team_id, channel_id):
    messages = []
    client = get_client(team_id)
    try:
        response = client.conversations_history(channel=channel_id, include_all_metadata=True)
        while response["ok"]:
            messages += response["messages"]
            if response["has_more"]:
                time.sleep(1)
                response = client.conversations_history(channel=channel_id,
                                                                  cursor=response["response_metadata"]["next_cursor"])
            else:
                break
    except SlackApiError as e:
        logging.error("Error fetching channel messages: %s", e, exc_info=True)
    return messages


@retry(delay=5, backoff=2, tries=8)
def fetch_several_messages_before(team_id, channel_id, message_id, number_of_messages):
    messages = []
    try:
        response = get_client(team_id).conversations_history(channel=channel_id, latest=message_id,
                                                          limit=number_of_messages, include_all_metadata=True,
                                                          inclusive=True)
        if response["ok"]:
            messages += response["messages"]
    except SlackApiError as e:
        logging.error("Error fetching conversations history: %s", e, exc_info=True)
    return list(reversed(messages))


@retry(delay=5, backoff=2, tries=8)
def fetch_several_messages_after(team_id, channel_id, message_id, number_of_messages):
    messages = []
    try:
        response = get_client(team_id).conversations_history(channel=channel_id, oldest=message_id,
                                                          limit=number_of_messages, include_all_metadata=True,
                                                          inclusive=True)
        if response["ok"]:
            messages += response["messages"]
    except SlackApiError as e:
        logging.error("Error fetching conversations history: %s", e, exc_info=True)
    return list(reversed(messages))


def is_thread(message):
    return "thread_ts" in message


def is_actual_message(message):
    return ('subtype' not in message) and ('bot_id' not in message)


def filter_messages(messages):
    return list(filter(lambda message: is_actual_message(message), messages))


@retry(delay=5, backoff=2, tries=8)
def slack_names_map(team_id):
    global slack_names

    if team_id not in slack_names:
        slack_names[team_id] = {}
        users = get_client(team_id).users_list(team_id=team_id)

        for user in users['members']:
            display_name = user['profile']['display_name']
            slack_names[team_id][user['id']] = display_name if len(display_name) > 0 else user['profile']['real_name']

    return slack_names[team_id]


def load_previous_messages(team_id: str, channel_id: str, last_message_id: str, number: int):
    result = load_previous_messages_with_pointer(team_id, channel_id, last_message_id, number)
    messages = result[0][-number:]
    return messages


def load_subsequent_messages(team_id: str, channel_id: str, first_message_id: str, number: int):
    (messages, ) = load_subsequent_messages_with_pointer(team_id, channel_id, first_message_id, number)
    return messages[:number]


def load_previous_messages_with_pointer(team_id: str, channel_id: str, last_message_id: str, minimum_number: int,
                                        bulk_size: Optional[int] = None):
    if bulk_size is None:
        bulk_size = minimum_number
    messages = fetch_several_messages_before(team_id, channel_id, last_message_id, bulk_size)
    actual_messages = filter_messages(messages)
    if len(messages) < bulk_size:
        return [actual_messages, None, 0]
    if len(actual_messages) < minimum_number:
        return load_previous_messages_with_pointer(team_id, channel_id, last_message_id, minimum_number, bulk_size * 2)
    context_tail = actual_messages[:CONTEXT_LENGTH - 1]
    return [actual_messages, context_tail[-1]['ts'], len(context_tail)]


def load_subsequent_messages_with_pointer(team_id: str, channel_id: str, first_message_id: str, minimum_number: int,
                                          bulk_size: Optional[int] = None):
    if bulk_size is None:
        bulk_size = minimum_number
    messages = fetch_several_messages_after(team_id, channel_id, first_message_id, bulk_size)
    actual_messages = filter_messages(messages)
    if len(messages) < bulk_size:
        return [actual_messages, None]
    if len(actual_messages) < minimum_number:
        return load_subsequent_messages_with_pointer(team_id, channel_id, first_message_id, minimum_number, bulk_size * 2)
    return [actual_messages, None]
