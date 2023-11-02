from functools import wraps
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
import os
import time

unauthorized_error = {
    "message": "Requires authentication"
}

def time_tracker(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = await func(*args, **kwargs)  # Assuming this can be an async function
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"Function '{func.__name__}' took {elapsed_time:.4f} seconds to execute.")
        return result
    return wrapper

def shared_secret_guard(request: Request):
    secret = get_secret_from_request(request)
    if secret != os.environ["API_SHARED_SECRET"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=unauthorized_error)

    # If the secret matches, simply return True or some other success indicator
    return True

def get_secret_from_request(request: Request):
    secret = request.headers.get("X-Shared-Secret")
    if not secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=unauthorized_error)
    return secret