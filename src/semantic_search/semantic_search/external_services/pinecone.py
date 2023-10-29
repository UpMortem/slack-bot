import logging

import pinecone

from ..https_requests import send_https_request
from ..config import get_pinecone_key, get_pinecone_environment, get_pinecone_index_name

pinecone.init(api_key=get_pinecone_key(), environment=get_pinecone_environment(), log_level="debug")
logging.getLogger("pinecone").setLevel("DEBUG")
logging.getLogger("urllib3").setLevel("DEBUG")
logging.getLogger("pinecone.core.client").setLevel("DEBUG")
logging.getLogger("pinecone.core.client.rest").setLevel("DEBUG")


def get_pinecone_index() -> 'pinecone.Index':
    return pinecone.Index(get_pinecone_index_name())


def query_index(query_vector, top_k, namespace, include_values, include_metadata, trace_id):
    host = f"{get_pinecone_index_name()}-0ddc4d6.svc.{get_pinecone_environment()}.pinecone.io"
    path = "/query"
    headers = {
        "content-type": "application/json",
        "api-key": get_pinecone_key(),
        "accept": "application/json",
    }
    data = {
        "vector": query_vector,
        "top_k": top_k,
        "includeMetadata": include_metadata,
        "includeValues": include_values,
        "namespace": namespace,
    }
    return send_https_request(host, path, data, headers, trace_id)
