import pytest

from services.slack_service import (
    find_user_by_id,
    get_thread_messages_with_usernames_json,
    get_user_name,
)


def test_get_thread_messages_with_usernames_json():
    # Call the function with some input
    result = get_thread_messages_with_usernames_json(
        "channel", "thread_ts", "slack_bot_token"
    )
    # Assert that the output is as expected
    pytest.asser(result, list)


def test_find_user_by_id():
    # Call the function with some input
    result = find_user_by_id("user_id", "slack_bot_token")
    # Assert that the output is as expected
    pytest.asser(result, dict)


def test_get_user_name():
    # Call the function with some input
    result = get_user_name("user_id", "slack_bot_token")
    # Assert that the output is as expected
    pytest.asser(result, str)
