from typing import List
import logging
from openai.error import ServiceUnavailableError
from semantic_search.semantic_search.config import get_use_fallback
from semantic_search.semantic_search.external_services.openai import gpt_query, gpt_query_json

from semantic_search.semantic_search.external_services.replicate import replicate_query


def run_completion(prompt: str, return_json: bool = False):
    try:
        if get_use_fallback():
            return replicate_query(prompt)
        else:
            return gpt_query_json(prompt) if return_json else gpt_query(prompt)
    except ServiceUnavailableError:
        logging.debug("Open AI service unavailable, using fallback model")
        return replicate_query(prompt)
    except Exception as e:
        logging.error("Error running completion: %s", e, exc_info=True)
        raise e


def summarize_thread(thread_messages: List[str]) -> str:
    text = "\n".join(thread_messages)
    return run_completion(
        "Summarize the following conversation and include channel information and usernames and actual names of the "
        "author of the message: " + text
    )
