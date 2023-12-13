import json
import logging
import time
import uuid
from datetime import date
from .external_services.openai import create_embedding, query_chat_gpt_forcing_json
from .external_services.vector_databases.vector_instance import get_db_instance

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
    return list(links)


def smart_query(namespace, query, username: str):
    smart_query_start_time = time.perf_counter()
    trace_id = uuid.uuid4()
    logging.info(f"Executing Smart Query: {query}, trace_id = {trace_id}")

    create_embedding_start_time = time.perf_counter()
    query_vector = create_embedding(query)
    create_embedding_time = time.perf_counter() - create_embedding_start_time
    logging.info(f"Smart Query: embedding created in {round(create_embedding_time, 2)}s, "
                 f"trace_id = {trace_id}")

    db_search_start_time = time.perf_counter()
    query_matches = get_db_instance().select(query_vector)

    db_search_time = time.perf_counter() - db_search_start_time
    logging.info(f"Smart Query: Postgre search finished in {round(db_search_time, 2)}s, "
                 f"trace_id = {trace_id}")

    gpt_request_start_time = time.perf_counter()
    messages_for_gpt = [
        {
            "id": qm["id"],
            "text": qm["metadata"]["text_without_context"]
            if "text_without_context" in qm["metadata"]
            else qm["metadata"]["text"]
        }
        for qm in query_matches
    ]   
    prompt = (f"Act as a Smart Search Engine that can logically infer an answer to the given query. "
              f"Be aware of today's date: {str(date.today())} and use it in your conclusions.\n\n"
              "Here is a list of Slack messages in JSON:\n"
              f"{json.dumps(messages_for_gpt)}\n\n"
              f"{username} is looking for an answer to the following search query: {query}\n\n"
              "Give an answer to the query based off the given messages. Only use the messages that are relevant and "
              "don't make up any answers. Prefer more recent messages.\n"
              "Strictly follow the policies below and don't include wrongs messages.\n"
              "Be as clear and short as possible and don't use any introductionary words. Omit phrases like, "
              "\"Based on the messages found.\" Exclude search queries and questions from the messages. Rely on "
              "positive statements.\n\n"
              "The output MUST be a valid JSON object (don't include any surrounding text) with "
              "the following schema:\n"
              "{\n"
              "   \"messages_explain\": \"List out all message objects from the JSON above that relate to the query."
              "Describe how each message in this list relates to the query in detail. Use a separate field for that. "
              "Exclude search queries and Haly/Haly Master mentions from this list. Rely on positive statements. "
              "Make sure you include correct JSON objects.\",\n"
              "   \"explain\": \"Think through the messages in the messages_explain field above and infer the "
              "answer to the query. Use strong deduction and explain the conclusion. Be as concise as possible.\",\n"
              "   \"answer\": \"Based on the explain and messages_explain fields, generate a short and concise "
              "answer to the query for the end user. Don't include any IDs or other service information.\",\n"
              "   \"messages\": [ From the messages_explain field pick top 1 or 2 messages that were used to infer "
              "the answer in the explain field and write their IDs in this array ]\n"
              "}")

    gpt_response = None
    try:
        gpt_response = query_chat_gpt_forcing_json(prompt)
        result = json.loads(gpt_response)
        gpt_request_time = time.perf_counter() - gpt_request_start_time
        total_time = time.perf_counter() - smart_query_start_time
        logging.info(
            f"Smart Query: Request to ChatGPT took {round(gpt_request_time, 2)}s, "
            f"trace_id = {trace_id}"
        )
        logging.info(
            f"Smart Query Completed in {round(total_time, 2)}s, trace_id = {trace_id}"
        )
        used_messages = list(
            filter(
                lambda match: match["id"]
                in result["messages"], query_matches
            )
        )
        return result['answer'], build_links_list(namespace, used_messages)
    except Exception as e:
        gpt_request_time = time.perf_counter() - gpt_request_start_time
        total_time = time.perf_counter() - smart_query_start_time
        logging.info(
            f"Smart Query: Request to ChatGPT or response decoding failed {e} "
            f"{round(gpt_request_time, 2)}s, trace_id = {trace_id}"
        )
        logging.info(
            f"Smart Query Completed in {round(total_time, 2)}s, trace_id = {trace_id}"
        )
        return f"Error occurred:\n{e}\n\nRaw GPT response:\n{gpt_response}"
