from slack_bolt import App
from routes.slack_router import slack_router
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask
from services.slack_service import slack_app

flask_app = Flask("Haly")
handler = SlackRequestHandler(slack_app)
flask_app.register_blueprint(slack_router)
