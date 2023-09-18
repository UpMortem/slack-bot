import os

from flask import Flask, request

flask_app = Flask(__name__)


def shared_secret_guard(func):
    # Add logic to check shared secret
    pass


def handle_app_installed(request):
    # Add logic to handle app installed route
    pass


@flask_app.route("/slack/app-installed", methods=["POST"])
@shared_secret_guard
def app_installed_route():
    return handle_app_installed(request)


if __name__ == "__main__":
    flask_app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
