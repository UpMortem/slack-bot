from typing import List
import logging
from openai.error import ServiceUnavailableError
from semantic_search.semantic_search.external_services.openai import gpt_query

from semantic_search.semantic_search.external_services.replicate import replicate_query


def run_completion(prompt: str):
    try:
        return gpt_query(prompt)
    except ServiceUnavailableError:
        logging.debug(f"Open AI service unavailable, using fallback model")
        return replicate_query(prompt)


def summarize_thread(thread_messages: List[str]) -> str:
    text = "\n".join(thread_messages)
    return run_completion(
        "Summarize the following conversation and include channel information and usernames and actual names of the "
        "author of the message: " + text
    )
