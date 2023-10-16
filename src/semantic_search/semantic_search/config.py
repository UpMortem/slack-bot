import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def get_openai_key() -> str:
    return os.environ.get('OPENAI_KEY')


def get_slack_token() -> str:
    return os.environ.get('SLACK_TOKEN')


def get_pinecone_key() -> str:
    return os.environ.get('PINECONE_KEY')


def get_pinecone_environment() -> str:
    return "asia-southeast1-gcp-free"


def get_pinecone_index_name() -> str:
    return os.environ.get('PINECONE_INDEX')


def index_service_endpoint() -> Optional[str]:
    return os.environ.get('INDEX_SERVICE_ENDPOINT')