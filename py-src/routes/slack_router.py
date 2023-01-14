from flask import Blueprint, request
from controllers.slack_controller import post_event, post_command

slack_router = Blueprint("slack_router", __name__)


@slack_router.route("/events", methods=["POST"])
def events():
    return post_event(request.get_json())


@slack_router.route("/command/:commandName", methods=["POST"])
def command(command_name):
    post_command(command_name)
