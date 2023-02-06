from flask import jsonify
from services.slack_service import (
  process_event_payload
)
from threading import Thread

# POST /slack/events
def post_event(request):
    if request.get("type") == "url_verification":
        return request.get("challenge")

    print(request)
    Thread(target=process_event_payload, args=(request,)).start()
    return jsonify({"message": "success"}), 200
