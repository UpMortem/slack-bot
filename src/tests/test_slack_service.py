import unittest
from unittest.mock import patch


class TestSlackService(unittest.TestCase):
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"})
    def test_update_message(self):
        # Call the function with test inputs
        # Assert that it produces the expected output
        pass

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"})
    def test_delete_message(self):
        # Call the function with test inputs
        # Assert that it produces the expected output
        pass

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"})
    def test_get_thread_messages(self):
        # Call the function with test inputs
        # Assert that it produces the expected output
        pass

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"})
    def test_get_thread_messages_with_usernames_json(self):
        # Call the function with test inputs
        # Assert that it produces the expected output
        pass

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"})
    def test_find_user_by_id(self):
        # Call the function with test inputs
        # Assert that it produces the expected output
        pass

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"})
    def test_get_user_name(self):
        # Call the function with test inputs
        # Assert that it produces the expected output
        pass


if __name__ == "__main__":
    unittest.main()
