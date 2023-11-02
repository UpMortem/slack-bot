from fastapi import FastAPI, Request, BackgroundTasks
from pydantic import BaseModel
import os
import logging
from slack_bolt.adapter.fastapi import SlackRequestHandler
from slack_bolt import App
from fastapi.responses import JSONResponse
from semantic_search.semantic_search.query import smart_query
from services.slack_service import slack_app, handle_app_installed


# Configuration and Logging
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
logging.basicConfig(level=LOG_LEVEL)

# Initialize FastAPI app and Slack Bolt App
api = FastAPI()
app_handler = SlackRequestHandler(slack_app)

# Routes
@api.post("/slack/events")
async def slack_events_endpoint(req: Request):
    return await app_handler.handle(req)

@api.post("/slack/app-installed")
async def app_installed_route(req: Request):
    handle_app_installed(req)
    return JSONResponse(content={"message": "App installed successfully"})

# Pydantic model for smart query requests
class SmartQueryRequest(BaseModel):
    query: str
    name: str
@api.post("/test-smart-query")
async def test_smart_query(req: SmartQueryRequest):
    # Using Pydantic model for automatic request parsing and validation
    # ... code for smart query ...
    return {"response": smart_query("T03QUQ2NFQC", req.query, req.name)}


# Running the application with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
