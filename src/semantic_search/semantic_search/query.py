import logging
import time
from .external_services.pinecone import get_pinecone_index
from .external_services.openai import create_embedding, gpt_query


def smart_query(namespace, query):
    logging.info(f"Executing Smart Query: {query}")

    stage_start_time = time.perf_counter()
    query_vector = create_embedding(query)
    logging.info(f"Smart Query: embedding created in {round(stage_start_time - time.perf_counter(), 2)}s")

    stage_start_time = time.perf_counter()
    query_results = get_pinecone_index().query(
        queries=[query_vector],
        top_k=30,
        namespace=namespace,
        include_values=False,
        includeMetadata=True
    )
    logging.info(f"Smart Query: Pinecone search finished in {round(stage_start_time - time.perf_counter(), 2)}s")
    query_matches = query_results['results'][0]['matches']

    messages_for_filtering = ["<MSG_ID>" + qm['id'] + '</MSG_ID><MSG>' + qm['metadata']['text'] + "<MSG>" for qm in
                              query_matches]
    filter_query = (f"I have a list of messages in the following format: <MSG_ID>Message ID</MSG_ID>"
                    f"<MSG>Message Text</MSG>. Give me the list of IDs of all messages that are definitely related"
                    f" to the following search query or may contain an answer to the question in it: \"{query}\". Do not include any explanations, only provide"
                    f" a list of IDs separated by comma. Prefer more recent messages. Here is the list of messages:")
    filter_query += "\n" + "\n".join(messages_for_filtering)

    stage_start_time = time.perf_counter()
    filter_response = gpt_query(filter_query)
    logging.info(f"Smart Query: ChatGPT filtered messages in {round(stage_start_time - time.perf_counter(), 2)}s")

    filtered_matches = list(filter(lambda m: m['id'] in filter_response, query_matches))
    filtered_messages_text = "\n".join([qm['metadata']['text'] for qm in filtered_matches])

    summarize_answer_query = (f"Summarize the answer the the following search query: \"{query}\" based off the "
                              f"information in the found messages: {filtered_messages_text}. Use messages that are "
                              f"relevant to the query, but don't include anything about that in your answer. Also give "
                              f"me an explanation of why each of the included messages is relevant.")
    stage_start_time = time.perf_counter()
    response = gpt_query(summarize_answer_query)
    logging.info(f"Smart Query: ChatGPT summarized the answer in {round(stage_start_time - time.perf_counter(), 2)}s")
    return response
