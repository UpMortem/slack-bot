import os
import sys
import unittest

from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler

from lib.guards import shared_secret_guard

sys.path.append("src")

flask_app = Flask(__name__)
handler = SlackRequestHandler(app=flask_app)


def handle_app_installed(request):
    return "App installed", 200


@shared_secret_guard(test_mode=flask_app.config["TESTING"])
def app_installed_route():
    return handle_app_installed(request)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    if flask_app.config["TESTING"]:
        return "OK", 200
    return handler.handle(request)


@flask_app.cli.command()
def test():
    """Run the unit tests."""
    tests = unittest.TestLoader().discover("src/tests", pattern="test*.py")
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


if __name__ == "__main__":
    flask_app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
