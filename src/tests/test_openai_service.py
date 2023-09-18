import unittest
import unittest.mock

from src.services import openai_service


class TestOpenAIService(unittest.TestCase):
    @unittest.mock.patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"})
    def test_run_completion(self):
        # Call the function with test inputs
        result = openai_service.run_completion([], "test_model", "test_key")
        # Use assert methods to check if the function is working as expected
        self.assertIsInstance(result, str)

    @unittest.mock.patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"})
    def test_respond_to_user(self):
        result = openai_service.respond_to_user([], "test_key", "test_team_id")
        self.assertIsInstance(result, str)

    def test_rough_num_tokens_from_messages(self):
        result = openai_service.rough_num_tokens_from_messages([])
        self.assertIsInstance(result, int)

    @unittest.mock.patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"})
    def test_summarize_conversation(self):
        result = openai_service.summarize_conversation([], "test_key")
        self.assertIsInstance(result, str)

    def test_chunk_messages(self):
        result = openai_service.chunk_messages([], 10000)
        self.assertIsInstance(result, list)


if __name__ == "__main__":
    unittest.main()
