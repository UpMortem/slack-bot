import unittest
from unittest.mock import patch

from src.services.api_service import (
    get_team_data,
    increment_request_count,
    revoke_token,
)


class APIServiceTest(unittest.TestCase):
    @patch("src.services.api_service.os")
    def test_get_team_data(self, mock_os):
        # Mock the behavior of os.environ.get to return a test value
        mock_os.environ.get.return_value = "test_value"

        # Call the function under test
        result = get_team_data("team_id")

        # Assert that the result is as expected
        self.assertEqual(result, "test_value")

    @patch("src.services.api_service.logging")
    def test_increment_request_count(self, mock_logging):
        # Call the function under test
        increment_request_count("team_id")

        # Assert that the logging function was called with the expected arguments
        mock_logging.info.assert_called_with(
            "Incrementing request count for team team_id"
        )

    @patch("src.services.api_service.logging")
    def test_revoke_token(self, mock_logging):
        # Call the function under test
        revoke_token("team_id")

        # Assert that the logging function was called with the expected arguments
        mock_logging.info.assert_called_with("Revoking token for team team_id")


if __name__ == "__main__":
    unittest.main()
