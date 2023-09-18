import unittest
from unittest.mock import patch

from src.services import openai_service


class TestOpenAIService(unittest.TestCase):
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"})
    def test_run_completion(self):
        slack_messages = [{"role": "user", "content": "Hello"}]
        model = "gpt-3.5-turbo"
        openai_key = "test_key"
        system_prompt = "This is a test."
        team_id = "test_team"

        result = openai_service.run_completion(
            slack_messages, model, openai_key, system_prompt, team_id
        )
        self.assertIsInstance(result, str)

    # Add more test methods for other functions in the openai_service module
