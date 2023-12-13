import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

CONTEXT_LENGTH = 5


def get_openai_key() -> str:
    return os.environ.get('OPENAI_API_KEY')


def get_slack_token() -> str:
    return os.environ.get('SLACK_BOT_TOKEN')


def get_slack_user_id() -> str:
    return os.environ.get('SLACK_USER_ID')


def get_pinecone_key() -> str:
    return os.environ.get('PINECONE_KEY')


def get_pinecone_environment() -> str:
    return os.environ.get('PINECONE_ENVIRONMENT')


def get_pinecone_index_name() -> str:
    return os.environ.get('PINECONE_INDEX')


def index_service_endpoint() -> Optional[str]:
    return os.environ.get('INDEX_SERVICE_ENDPOINT')


def get_google_tasks_service_account() -> str:
    return os.environ.get('GOOGLE_TASKS_SERVICE_ACCOUNT')


def get_google_tasks_queue_path() -> str:
    return os.environ.get('GOOGLE_TASKS_QUEUE_PATH')


def get_api_base_url() -> str:
    return os.environ.get('API_BASE_URL')


def get_api_shared_secret() -> str:
    return os.environ.get('API_SHARED_SECRET')


def is_standalone() -> bool:
    return os.environ.get('STANDALONE') == 'true'

def get_postgres_host()-> str :
    return os.environ.get('POSTGRES_HOST')

def get_postgres_port()-> str :
    return os.environ.get('POSTGRES_PORT')

def get_postgres_database()-> str :
    return os.environ.get('POSTGRES_DATABASE')

def get_postgres_user()-> str :
    return os.environ.get('POSTGRES_USER')

def get_postgres_password()-> str :
    return os.environ.get('POSTGRES_PASSWORD')
