import os
from flask import Flask
from slack_bolt.adapter.flask import SlackRequestHandler
from routes.slack_router import slack_router
from services.slack_service import slack_app

handler = SlackRequestHandler(slack_app)

flask_app = Flask("Haly")
flask_app.register_blueprint(slack_router, url_prefix="/slack")

if __name__ == "__main__":
    flask_app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))