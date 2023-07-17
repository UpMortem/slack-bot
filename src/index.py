import logging
import time
import os
from logging import Logger
from flask import Flask, g, request
from slack_bolt.adapter.flask import SlackRequestHandler
from routes.slack_router import slack_router
from services.slack_service import slack_app

handler = SlackRequestHandler(slack_app)

flask_app = Flask("Haly")
flask_app.register_blueprint(slack_router, url_prefix="/slack")

##########################################
# Config logger
##########################################
logging.basicConfig(level=logging.INFO)
flask_app.logger: Logger

@flask_app.before_request
def before_request():
    g.start_time = time.perf_counter()
    g.route = request.path

@flask_app.after_request
def after_request(response):
    end_time = time.perf_counter()
    processing_time = end_time - g.start_time

    flask_app.logger.info(f"Route: {g.route}, Request processed in {processing_time} seconds")

    return response

if __name__ == "__main__":
    flask_app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), threaded=True)
