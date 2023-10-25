import logging
import random
import time

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

