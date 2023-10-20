import json
import logging
import os
from flask import Flask, request, jsonify
from .external_services.pinecone import get_pinecone_index
from .google_tasks import queue_task
from .load_messages import index_messages
from .external_services.slack_api import load_previous_messages_with_pointer

logging.basicConfig(level=os.environ["LOG_LEVEL"])
app = Flask("SemanticSearchIndex")
BULK_SIZE = 50


@app.route('/handle_task', methods=['POST'])
def handle_task():
    try:
        logging.info(f"Processing task with payload: {request.data.decode('utf-8')}")
        payload = json.loads(request.data.decode('utf-8'))
        task_id = payload['task_id']
        iteration_number = payload['iteration_number']
        namespace = payload['namespace']
        channel_id = payload['channel_id']
        last_message_id = payload['last_message_id']
        [messages, next_last_message] = load_previous_messages_with_pointer(channel_id, last_message_id, BULK_SIZE)
        logging.info(f"Task: {task_id}, Iteration Number: {iteration_number}")
        logging.info(f"Task: {task_id}, Number of Actual Messages: {len(messages)}")
        start_from = 0 if next_last_message is None else 2
        index_messages(channel_id, messages, start_from, get_pinecone_index(), namespace)
        if next_last_message is not None:
            queue_task({
                'task_id': task_id,
                'iteration_number': iteration_number + 1,
                'namespace': namespace,
                'channel_id': channel_id,
                'last_message_id': next_last_message,
            })
        return jsonify({'status': 'success'}), 200

    except ValueError as ve:
        logging.error("An error occurred while handling a task: %s", ve, exc_info=True)
        return jsonify({'status': 'unauthenticated'}), 401


def start():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
