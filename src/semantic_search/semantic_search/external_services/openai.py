import math
import re
from typing import List, Any
import openai
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
    texts = list(map(lambda text: text.replace("\n", " "), texts))  # explain why we need this
    embeddings = openai.Embedding.create(input=texts, model=model)
    return list(map(lambda e: e.embedding, embeddings['data']))


@retry(delay=3, backoff=2, tries=8)
def gpt_query(query: str) -> str:
    max_tokens = 3300 - estimate_tokens_number(query)
    completion = openai.Completion.create(model="gpt-3.5-turbo-instruct", prompt=query, max_tokens=max_tokens)
    return completion.choices[0].text.strip()


def estimate_tokens_number(text: str) -> int:
    words = re.findall(r'\b\w+\b', text)
    return math.ceil(sum(map(lambda w: len(w) / 2, words)))


@retry(delay=3, backoff=2, tries=8)
def gpt_summarize_thread(thread_messages: List[str]) -> str:
    text = "\n".join(thread_messages)
    return gpt_query(
        "Summarize the following conversation and include channel information and usernames and actual names of the "
        "author of the message: " + text
    )
