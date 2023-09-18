import unittest
from unittest.mock import patch

from services.slack_service import handle_app_mention


class SlackServiceTest(unittest.TestCase):
    @patch("services.slack_service.get_team_data")
    @patch("services.slack_service.respond_to_user")
    def test_handle_app_mention(self, mock_respond_to_user, mock_get_team_data):
        # Mock the necessary dependencies
        mock_respond_to_user.return_value = "Test response"
        mock_get_team_data.return_value = {
            "slack_bot_token": "test_token",
            "openai_key": "test_key",
        }

        # Call the function under test
        result = handle_app_mention(
            {
                "channel": "test_channel",
                "text": "test_text",
                "thread_ts": "test_thread_ts",
                "ts": "test_ts",
                "team": "test_team",
                "user": "test_user",
            },
            lambda channel, thread_ts, text, slack_bot_token: None,
        )

        # Assert the result
        self.assertEqual(result, "Test response")
