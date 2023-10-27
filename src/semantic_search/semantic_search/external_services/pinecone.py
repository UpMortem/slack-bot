import logging

import pinecone
from ..config import get_pinecone_key, get_pinecone_environment, get_pinecone_index_name

pinecone.init(api_key=get_pinecone_key(), environment=get_pinecone_environment(), log_level="debug")
logging.getLogger("pinecone").setLevel("DEBUG")
logging.getLogger("urllib3").setLevel("DEBUG")
logging.getLogger("pinecone.core.client").setLevel("DEBUG")
logging.getLogger("pinecone.core.client.rest").setLevel("DEBUG")


def get_pinecone_index() -> 'pinecone.Index':
    return pinecone.Index(get_pinecone_index_name())
