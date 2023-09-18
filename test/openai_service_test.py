import unittest
from unittest.mock import patch

from src.services import openai_service


class MockMessage:
    def __init__(self, content):
        self.content = content


class MockChoices:
    def __init__(self, message):
        self.message = message


class OpenAIServiceTest(unittest.TestCase):
    @patch("src.services.openai_service.openai")
    def test_run_completion(self, mock_openai):
        # Mock the openai.ChatCompletion.create method
        mock_openai.ChatCompletion.create.return_value = MockChoices(
            message=MockMessage(content="Test response")
        )

        # Call the run_completion method with test data
        response = openai_service.run_completion(
            [{"role": "user", "content": "Test message"}], "test_key", "gpt-3.5-turbo"
        )

        # Assert that the response is correct
        self.assertEqual(response, "Test response")

        # Assert that the openai.ChatCompletion.create method was called with the correct arguments
        mock_openai.ChatCompletion.create.assert_called_once_with(
            model="gpt-3.5-turbo",
            temperature=0.7,
            messages=[
                {"role": "system", "content": openai_service.base_prompt},
                {"role": "user", "content": "Test message"},
            ],
        )


if __name__ == "__main__":
    unittest.main()
