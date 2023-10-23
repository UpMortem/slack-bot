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
    prompt = ("I have a list of Slack messages in JSON:\n"
              f"{json.dumps(messages_for_gpt)}\n\n"
              f"I have the following search query from a Slack user: {query}\n\n"
              "Act as a smart search engine that can infer an answer to the given query"
              " based on the given information chunks. "
              "Give an answer to the query based off the given messages. Only use the messages that are relevant and "
              "don't make up any answers. Prefer more recent messages.\n"
              "Be as clear and short as possible and don't use any introductionary words. Omit phrases like, "
              "\"Based on the messages found.\"\n\n"
              "The output should be a JSON object with the following schema:\n"
              "{\n"
              "   \"answer\": \"A string with the answer to the query\",\n"
              "   \"messages\": [] - an array of IDs (from the JSON given above) from the messages that were used to "
              "build the answer to the query. Include maximum 5 IDs of the most relevant messages. Re-iterate multiple "
              "times and make sure the IDs in this list correspond to the actual messages that were used to build the "
              "answer. Sort the IDs according to the value of the related message in the conclusion of the answer, "
              "from the most valuable to the least valuable.\n"
              "}")

    stage_start_time = time.perf_counter()
    result = json.loads(gpt_query(prompt))
    logging.info(f"Smart Query: Request to ChatGPT took {round(time.perf_counter() - stage_start_time, 2)}s")

    used_messages = list(filter(lambda match: match["id"] in result["messages"], query_matches))

    return f"{result['answer']}{build_links_list(namespace, used_messages)}"
