from typing import List, Any
import openai
from openai.error import TryAgain, Timeout, RateLimitError, APIConnectionError, APIError
from retry import retry

from ..config import get_openai_key

openai.api_key = get_openai_key()


@retry(delay=3, backoff=2, tries=8)
def create_embedding(text):
    model = "text-embedding-ada-002"
    text = text.replace("\n", " ")
    return openai.Embedding.create(input=[text], model=model)['data'][0]['embedding']


@retry(delay=3, backoff=2, tries=8)
def create_embeddings(texts: List[str]) -> List[Any]:
    model = "text-embedding-ada-002"
    # explain why we need this
    texts = list(map(lambda text: text.replace("\n", " "), texts))
    embeddings = openai.Embedding.create(input=texts, model=model)
    return list(map(lambda e: e.embedding, embeddings['data']))


@retry(exceptions=[TryAgain, Timeout, RateLimitError, APIConnectionError, APIError], delay=3, backoff=2, tries=8)
def gpt_query_json(query: str) -> str:
    summary = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": query}],
        response_format={"type": "json_object"},
    )
    return summary.choices[0].message.content.strip()


@retry(delay=3, backoff=2, tries=8)
def gpt_query(query: str) -> str:
    summary = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": query}],
    )
    return summary.choices[0].message.content.strip()


@retry(delay=3, backoff=2, tries=8)
def gpt_summarize_thread(thread_messages: List[str]) -> str:
    text = "\n".join(thread_messages)
    return gpt_query(
        "Summarize the following conversation and include channel information and usernames and actual names of the "
        "author of the message: " + text
    )
