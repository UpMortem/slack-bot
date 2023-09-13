import json
from uuid import uuid4

from google.cloud import tasks_v2

from .config import index_service_endpoint
from .load_messages import index_whole_channel


def create_http_task_with_token(
        project: str,
        location: str,
        queue: str,
        url: str,
        payload: bytes,
) -> tasks_v2.Task:
    client = tasks_v2.CloudTasksClient()
    # noinspection PyTypeChecker
    task = tasks_v2.Task(
        http_request=tasks_v2.HttpRequest(
            http_method=tasks_v2.HttpMethod.POST,
            url=url,
            body=payload,
        ),
    )

    # noinspection PyTypeChecker
    return client.create_task(
        tasks_v2.CreateTaskRequest(
            parent=client.queue_path(project, location, queue),
            task=task,
        )
    )


def trigger_indexation(namespace, channel_id):
    if index_service_endpoint() is None:
        return index_whole_channel(namespace, channel_id)

    return queue_task(
        create_index_task_payload(namespace, channel_id)
    )


def queue_task(payload):
    create_http_task_with_token(
        'develop-up',
        'us-central1',
        'semantic-search-index',
        index_service_endpoint(),
        bytes(json.dumps(payload), 'utf-8'),
    )


def create_index_task_payload(namespace, channel_id, last_message_id=None):
    return {
        'task_id': str(uuid4()),
        'iteration_number': 1,
        'namespace': namespace,
        'channel_id': channel_id,
        'last_message_id': last_message_id,
    }
