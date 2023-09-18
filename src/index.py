import logging
import os
import unittest

from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler

from lib.guards import shared_secret_guard
from services.slack_service import handle_app_installed, slack_app

logging.basicConfig(level=os.environ["LOG_LEVEL"])


flask_app = Flask("Haly")
handler = SlackRequestHandler(slack_app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


@flask_app.route("/slack/app-installed", methods=["POST"])
@shared_secret_guard
def app_installed_route():
    return handle_app_installed(request)


@flask_app.cli.command()
def test():
    """Run the tests."""
    tests = unittest.TestLoader().discover("src/tests", pattern="test_*.py")
    result = unittest.TextTestRunner().run(tests)
    if result.wasSuccessful():
        return 0
    return 1


if __name__ == "__main__":
    flask_app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
