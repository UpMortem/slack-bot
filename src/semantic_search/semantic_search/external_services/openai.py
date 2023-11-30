from typing import List, Any
import openai
from retry import retry
from ..config import get_openai_key

openai.api_key = get_openai_key()


@retry(delay=2, backoff=2, tries=5)
def create_embedding(text):
    model = "text-embedding-ada-002"
    text = text.replace("\n", " ")
    return openai.Embedding.create(input=[text], model=model)['data'][0]['embedding']


@retry(delay=2, backoff=2, tries=5)
def create_embeddings(texts: List[str]) -> List[Any]:
    model = "text-embedding-ada-002"
    texts = list(map(lambda text: text.replace("\n", " "), texts))  # explain why we need this
    embeddings = openai.Embedding.create(input=texts, model=model)
    return list(map(lambda e: e.embedding, embeddings['data']))


@retry(delay=2, backoff=2, tries=5)
def query_chat_gpt_forcing_json(query: str) -> str:
    summary = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": query}],
        response_format={"type": "json_object"},
    )
    return summary.choices[0].message.content.strip()


@retry(delay=2, backoff=2, tries=5)
def query_chat_gpt(query: str) -> str:
    summary = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": query}],
    )
    return summary.choices[0].message.content.strip()


@retry(delay=2, backoff=2, tries=5)
def query_chat_gpt_3_5(query: str) -> str:
    summary = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": query}],
    )
    return summary.choices[0].message.content.strip()


def summarize_thread_with_chat_gpt(thread_messages: List[str]) -> str:
    text = "\n".join(thread_messages)
    return query_chat_gpt(
        "Summarize the following conversation and include channel information and usernames and actual names of the "
        "author of the message: " + text
    )


def summarize_thread_with_chat_gpt_3_5(thread_messages: List[str]) -> str:
    text = "\n".join(thread_messages)
    return query_chat_gpt_3_5(
        "Summarize the following conversation and include channel information and usernames and actual names of the "
        "author of the message: " + text
    )
