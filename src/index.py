import os
import logging
from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler
from lib.guards import shared_secret_guard
from services.slack_service import slack_app, handle_app_installed

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


if __name__ == "__main__":
    flask_app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
