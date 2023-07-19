import os
import logging
from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler
from services.slack_service import slack_app

logging.basicConfig(level=logging.DEBUG)

flask_app = Flask("Haly")
handler = SlackRequestHandler(slack_app)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


if __name__ == "__main__":
    flask_app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))