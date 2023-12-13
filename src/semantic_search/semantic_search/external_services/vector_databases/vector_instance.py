from ...config import get_postgres_host, get_pinecone_environment
from .postgres import Postgres
from .pinecone import Pinecone

postgres_instance = None
pinecone_instance = None

def get_db_instance():
    global postgres_instance, pinecone_instance
    if get_postgres_host():
        if postgres_instance is None:
            postgres_instance = Postgres()
        return postgres_instance
    else:
        if pinecone_instance is None:
            pinecone_instance = Pinecone()
        return pinecone_instance