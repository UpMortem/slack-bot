import json
from typing import Optional
from uuid import uuid4

from google.cloud import tasks_v2

from .config import index_service_endpoint, get_google_tasks_service_account, get_google_tasks_queue_path
from .load_messages import index_whole_channel


def create_http_task_with_token(
        url: str,
        payload: bytes,
        queue_path: Optional[str]
) -> tasks_v2.Task:
    client = tasks_v2.CloudTasksClient()
    # noinspection PyTypeChecker
    task = tasks_v2.Task(
        http_request=tasks_v2.HttpRequest(
            http_method=tasks_v2.HttpMethod.POST,
            url=url,
            oidc_token=tasks_v2.OidcToken(
                service_account_email=get_google_tasks_service_account(),
            ),
            body=payload,
        ),
    )

    if queue_path is None:
        queue_path = "projects/develop-up/locations/us-central1/queues/semantic-search-index"

    # noinspection PyTypeChecker
    return client.create_task(
        tasks_v2.CreateTaskRequest(
            parent=queue_path,
            task=task,
        ),
        timeout=30,
    )


def trigger_indexation(namespace, channel_id):
    if index_service_endpoint() is None:
        return index_whole_channel(namespace, channel_id)

    return queue_task(
        create_index_task_payload(namespace, channel_id)
    )


def queue_task(payload):
    create_http_task_with_token(
        index_service_endpoint(),
        bytes(json.dumps(payload), 'utf-8'),
        get_google_tasks_queue_path(),
    )


def create_index_task_payload(namespace, channel_id, last_message_id=None):
    return {
        'task_id': str(uuid4()),
        'iteration_number': 1,
        'namespace': namespace,
        'channel_id': channel_id,
        'last_message_id': last_message_id,
    }
