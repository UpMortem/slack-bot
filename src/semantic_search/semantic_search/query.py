import json
import logging
import time
from .external_services.pinecone import get_pinecone_index
from .external_services.openai import create_embedding, gpt_query


def build_slack_message_link(workspace_name, channel_id, message_timestamp, thread_timestamp=None):
    base_url = f"https://{workspace_name}.slack.com/archives/{channel_id}/"

    message_link_timestamp = message_timestamp.replace('.', '')
    if thread_timestamp:
        return f"{base_url}p{message_link_timestamp}?thread_ts={thread_timestamp}&cid={channel_id}"

    return f"{base_url}p{message_link_timestamp}"


def build_links_list(namespace: str, matches) -> str:
    if namespace != 'T03QUQ2NFQC':
        return ""
    links = map(lambda match: build_slack_message_link(
        "upmortemworkspace",
        match['metadata']['channel_id'],
        match['metadata']['ts'],
        match['metadata'].get('thread_ts')
    ), matches)
    return "\n" + "\n".join(links)


def smart_query(namespace, query):
    logging.info(f"Executing Smart Query: {query}")

    stage_start_time = time.perf_counter()
    query_vector = create_embedding(query)
    logging.info(f"Smart Query: embedding created in {round(time.perf_counter() - stage_start_time, 2)}s")

    stage_start_time = time.perf_counter()
    query_results = get_pinecone_index().query(
        queries=[query_vector],
        top_k=50,
        namespace=namespace,
        include_values=False,
        includeMetadata=True
    )
    logging.info(f"Smart Query: Pinecone search finished in {round(time.perf_counter() - stage_start_time, 2)}s")
    query_matches = query_results['results'][0]['matches']

    messages_for_gpt = [{"id": qm["id"], "text": qm["metadata"]["text"]} for qm in query_matches]
    prompt = ("Act as a Smart Search Engine that can logically infer an answer to the given query.\n\n"
              "Here is a list of Slack messages in JSON:\n"
              f"{json.dumps(messages_for_gpt)}\n\n"
              f"A Slack user is looking for an answer to the following search query: {query}\n\n"
              "Give an answer to the query based off the given messages. Only use the messages that are relevant and "
              "don't make up any answers. Prefer more recent messages.\n"
              "Strictly follow the policies below and don't include wrongs messages.\n"
              "Be as clear and short as possible and don't use any introductionary words. Omit phrases like, "
              "\"Based on the messages found.\" Exclude search queries and questions from the messages. Rely on "
              "positive statements.\n\n"
              "The output should be a JSON object with the following schema:\n"
              "{\n"
              "   \"messages_explain\": \"List out all message objects from the JSON above that relate to the query."
              "Describe how each message in this list relates to the query in detail. Use a separate field for that. "
              "Exclude search queries and Haly/Haly Master mentions from this list. Rely on positive statements.\",\n"
              "   \"explain\": \"Think through the messages in the messages_explain field above and infer the "
              "answer to the query. Use strong deduction and explain the conclusion. Be as concise as possible.\",\n"
              "   \"answer\": \"Based on the explain and messages_explain fields, generate a short and concise "
              "answer to the query for the end user. Don't include any IDs or other service information.\",\n"
              "   \"messages\": [ From the messages_explain field, pick top 1 messages in which the last part of the "
              "message text helped to infer the answer and write their ids in this array ]\n"
              "}")

    stage_start_time = time.perf_counter()
    result = json.loads(gpt_query(prompt))
    logging.info(f"Smart Query: Request to ChatGPT took {round(time.perf_counter() - stage_start_time, 2)}s")

    used_messages = list(filter(lambda match: match["id"] in result["messages"], query_matches))

    return f"{result['answer']}{build_links_list(namespace, used_messages)}"
