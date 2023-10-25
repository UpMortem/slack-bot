import logging
import random
import time
import requests
import json

import pinecone
from ..config import get_pinecone_key, get_pinecone_environment, get_pinecone_index_name

pinecone.init(api_key=get_pinecone_key(), environment=get_pinecone_environment())


def get_pinecone_index() -> 'pinecone.Index':
    return pinecone.Index(get_pinecone_index_name())


def test_pinecone_request():
    vector = [random.random() * 2 - 1 for _ in range(1536)]
    start = time.perf_counter_ns()
    results = get_pinecone_index().query(vector, top_k=50, namespace="T03QUQ2NFQC", include_metadata=True,
                                         include_values=False)
    finish = time.perf_counter_ns()

    logging.info(
        f"Pinecone query test: executed in {((finish - start) / 10**9):.3f}s "
        f"with {len(results['matches'])} matches"
    )

    return {
        "time": (finish - start) / 10**9,
        "matches": len(results['matches']),
    }


def custom_pinecone_query(query_vector, namespace, top_k):
    url = f"https://semantic-search-prod-0ddc4d6.svc.us-central1-gcp.pinecone.io/query"

    headers = {
        "content-type": "application/json",
        "api-key": get_pinecone_key(),
        "accept": "application/json",
    }

    body = {
        "vector": query_vector,
        "top_k": top_k,
        "includeMetadata": True,
        "includeValues": False,
        "namespace": namespace,
    }

    # Send the POST request
    response = requests.post(url, headers=headers, data=json.dumps(body))

    # Check for a valid response
    response.raise_for_status()

    print(response.status_code)
    print(f"--{response.text}--")
    # Parse and return the response
    response_data = response.json()
    return response_data

