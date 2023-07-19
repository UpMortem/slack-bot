# from flask import jsonify
# from threading import Thread
# from services.slack_service import (
#   process_event_payload
# )

# # POST /slack/events
# def post_event(request):
#     if request.get("type") == "url_verification":
#         return request.get("challenge")

#     Thread(target=process_event_payload, args=(request,)).start()
#     return jsonify({"message": "success"}), 200
