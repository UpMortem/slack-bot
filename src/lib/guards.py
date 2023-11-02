from functools import wraps
from http import HTTPStatus
import os
import time

from flask import abort, jsonify, request

unauthorized_error = {
    "message": "Requires authentication"
}

def time_tracker(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(
            f"Function '{func.__name__}' took {elapsed_time:.4f} seconds to execute.")
        return result

    return wrapper

def shared_secret_guard(function):
    @wraps(function)
    def decorator(*args, **kwargs):
        secret = get_secret_from_request()
        if secret != os.environ["API_SHARED_SECRET"]:
            json_abort(HTTPStatus.UNAUTHORIZED, unauthorized_error)
            return None
        return function(*args, **kwargs)

    return decorator

def get_secret_from_request():
    secret = request.headers.get("X-Shared-Secret", None)
    if not secret:
        json_abort(HTTPStatus.UNAUTHORIZED, unauthorized_error)
        return None
    return secret

def json_abort(status_code, data=None):
    response = jsonify(data)
    response.status_code = status_code
    abort(response)
