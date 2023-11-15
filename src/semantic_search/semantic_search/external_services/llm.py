import logging
from openai.error import ServiceUnavailableError
from semantic_search.semantic_search.external_services.openai import gpt_query

from semantic_search.semantic_search.external_services.replicate import replicate_query


def run_completion(prompt: str):
    try:
        gpt_query(prompt)
    except ServiceUnavailableError:
        logging.debug(f"Open AI service unavailable, using fallback model")
        return replicate_query(prompt)
