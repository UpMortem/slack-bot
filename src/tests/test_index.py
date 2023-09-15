import unittest

from index import flask_app

class IndexTestCase(unittest.TestCase):
class IndexTestCase(unittest.TestCase):
    def setUp(self):
        self.app = flask_app
        self.client = self.app.test_client()

    def tearDown(self):
        pass

    def test_slack_events_route(self):
        response = self.client.post("/slack/events")
        self.assertEqual(response.status_code, 200)

    def test_app_installed_route(self):
        response = self.client.post("/slack/app-installed")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
