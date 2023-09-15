import unittest
from unittest.mock import patch

from lib.guards import shared_secret_guard
from src.index import flask_app


class IndexTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.headers = {"Authorization": "Bearer test_token"}

    def setUp(self):
        self.app = flask_app
        self.client = self.app.test_client()
        self.patcher = patch.object(shared_secret_guard, return_value=True)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_slack_events_route(self):
        response = self.client.post("/slack/events", headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_app_installed_route(self):
        response = self.client.post("/slack/app-installed", headers=self.headers)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
