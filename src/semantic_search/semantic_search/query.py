import json
import logging
import time
from .external_services.pinecone import get_pinecone_index
from .external_services.openai import create_embedding, gpt_query


def build_links_list(namespace: str, matches) -> str:
    if namespace != 'T03QUQ2NFQC':
        return ""
    links = map(lambda match: f"https://upmortemworkspace.slack.com/archives/{match['metadata']['channel_id']}"
                              f"/p{match['metadata']['ts'].replace('.', '')}", matches)
    return "\n" + "\n".join(links)


def smart_query(namespace, query):
    logging.info(f"Executing Smart Query: {query}")

    stage_start_time = time.perf_counter()
    query_vector = create_embedding(query)
    logging.info(f"Smart Query: embedding created in {round(time.perf_counter() - stage_start_time, 2)}s")

    stage_start_time = time.perf_counter()
    query_results = get_pinecone_index().query(
        queries=[query_vector],
        top_k=30,
        namespace=namespace,
        include_values=False,
        includeMetadata=True
    )
    logging.info(f"Smart Query: Pinecone search finished in {round(time.perf_counter() - stage_start_time, 2)}s")
    query_matches = query_results['results'][0]['matches']

    messages_for_gpt = [{"id": qm["id"], "text": qm["metadata"]["text"]} for qm in query_matches]
    prompt = ("I have a list of messages in JSON:\n"
              f"{json.dumps(messages_for_gpt)}\n\n"
              f"I have the following search query: {query}\n\n"
              "Give an answer to the query based off the given messages. Only use the messages that are relevant and "
              "don't make up any answers. Prefer more recent messages.\n"
              "Be as clear and short as possible and don't use any introductionary words.\n\n"
              "The output should be a JSON object with the following schema:\n"
              "{\n"
              "   \"answer\": \"A string with the answer to the query\",\n"
              "   \"messages\": [] - an array of IDs (from the JSON given above) from the messages that were used to "
              "build the answer to the query. Include maximum 3 IDs of the most relevant messages.\n"
              "}")

    stage_start_time = time.perf_counter()
    result = json.loads(gpt_query(prompt))
    logging.info(f"Smart Query: Request to ChatGPT took {round(time.perf_counter() - stage_start_time, 2)}s")

    used_messages = list(filter(lambda match: match["id"] in result["messages"], query_matches))

    return f"{result['answer']}{build_links_list(namespace, used_messages)}"
