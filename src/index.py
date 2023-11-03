import hashlib
import hmac
import os
import logging
import re
import time

from pydantic import BaseModel
from lib.guards import shared_secret_guard
from semantic_search.semantic_search.external_services import openai
from semantic_search.semantic_search.query import smart_query
from semantic_search.semantic_search.config import get_slack_signing_secret
from services.slack_service import handle_app_mention, no_bot_messages, no_message_changed, handle_app_installed
from fastapi import BackgroundTasks, FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
import time
import hmac
import hashlib

logging.basicConfig(level=os.environ["LOG_LEVEL"])

app = FastAPI()

SLACK_SIGNING_SECRET = get_slack_signing_secret()

async def verify_slack_request(request: Request) -> bool:
    request_body = await request.body()
    timestamp = request.headers.get('X-Slack-Request-Timestamp')
    if abs(time.time() - float(timestamp)) > 60 * 5:
        return False
    
    slack_signature = request.headers.get('X-Slack-Signature')
    sig_basestring = f"v0:{timestamp}:{request_body.decode('utf-8')}"
    my_signature = 'v0=' + hmac.new(
        SLACK_SIGNING_SECRET.encode('utf-8'),
        sig_basestring.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(my_signature, slack_signature)

@app.post("/slack/events")
async def slack_events(request: Request, background_tasks: BackgroundTasks):
    if not await verify_slack_request(request):
        raise HTTPException(status_code=403, detail="Verification failed")

    event_data = await request.json()
    
    # Slack URL verification challenge
    if event_data.get("type") == "url_verification":
        return JSONResponse({"challenge": event_data.get("challenge")})
    
    # Immediately acknowledge Slack event
    if event_data.get("type") == "event_callback":
        # Asynchronous processing of the event
        background_tasks.add_task(handle_event, event_data["event"])
        return Response(status_code=200)

    return Response(status_code=200)

async def handle_event(event: dict):
    event_type = event.get("type")
    event_subtype = event.get("subtype")

    # Check if the event type is 'app_mention' and there's no subtype
    if re.match(r"app_mention", event_type) and not event_subtype:
        # Now apply your custom matchers
        # if no_bot_messages(event) and no_message_changed(event):
        handle_app_mention(event)
            # pass
    pass

@app.post("/slack/app-installed")
async def app_installed_route(req: Request):
    handle_app_installed(req)
    return JSONResponse(content={"message": "App installed successfully"})

# Pydantic model for smart query requests
class SmartQueryRequest(BaseModel):
    query: str
    name: str
@app.post("/test-smart-query")
async def test_smart_query(req: SmartQueryRequest):
    # Using Pydantic model for automatic request parsing and validation
    # ... code for smart query ...
    return {"response": smart_query("T03QUQ2NFQC", req.query, req.name)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
