import json
import logging
import os
from flask import Flask, request, jsonify
from .config import get_google_tasks_service_account
from .google_tasks import queue_task
from .load_messages import index_messages
from .external_services.slack_api import load_previous_messages_with_pointer
import google.auth.transport.requests
import google.oauth2.id_token

logging.basicConfig(level=os.environ["LOG_LEVEL"])
app = Flask("SemanticSearchIndex")
BULK_SIZE = 20


@app.route('/handle_task', methods=['POST'])
def handle_task():
    id_token = request.headers.get('Authorization').split(' ').pop()
    if not id_token:
        return jsonify({'message': 'No token found'}), 401

    try:
        request_adapter = google.auth.transport.requests.Request()
        decoded_token = google.oauth2.id_token.verify_oauth2_token(
            id_token, request_adapter
        )
        if decoded_token['email'] != get_google_tasks_service_account():
            return jsonify({'status': 'unauthenticated'}), 401
    except Exception as e:
        logging.error("Handle Task Auth Error: %s", e, exc_info=True)
        return jsonify({'status': 'unauthenticated'}), 401

    try:
        logging.info(f"Processing task with payload: {request.data.decode('utf-8')}")
        payload = json.loads(request.data.decode('utf-8'))
        task_id = payload['task_id']
        iteration_number = payload['iteration_number']
        namespace = payload['namespace']
        channel_id = payload['channel_id']
        last_message_id = payload['last_message_id']
        [messages, next_last_message, start_from] = load_previous_messages_with_pointer(namespace, channel_id, last_message_id, BULK_SIZE)
        logging.info(f"Task: {task_id}, Iteration Number: {iteration_number}")
        logging.info(f"Task: {task_id}, Number of Actual Messages: {len(messages)}")
        index_messages(channel_id, messages, start_from, namespace)
        if next_last_message is not None:
            queue_task({
                'task_id': task_id,
                'iteration_number': iteration_number + 1,
                'namespace': namespace,
                'channel_id': channel_id,
                'last_message_id': next_last_message,
            })
        return jsonify({'status': 'success'}), 200

    except Exception as e:
        logging.error("Handle Task Error: %s", e, exc_info=True)
        return jsonify({'status': 'error'}), 500
