import logging
import copy
from typing import List, Dict
from .external_services.pinecone import get_pinecone_index
from .external_services.openai import create_embeddings, gpt_summarize_thread
import datetime
from .external_services.slack_api import fetch_thread_messages, fetch_channel_messages, is_thread, \
    is_actual_message, \
    slack_names_map, filter_messages, load_previous_messages, load_subsequent_messages


class Embedding:
    def __init__(self, channel_id, id, text, ts, thread_ts=None, author_id=None):
        self.channel_id = channel_id
        self.id = id
        self.text = text
        self.ts = ts
        self.thread_ts = thread_ts
        self.author_id = author_id

    def replace_names(self, names_map: Dict[str, str]) -> 'Embedding':
        embedding = copy.copy(self)
        for (user_id, user_name) in names_map.items():
            embedding.text = embedding.text.replace(f"<@{user_id}>", user_name)
        embedding.text = f"{names_map[self.author_id]}: {embedding.text}" \
            if self.author_id in names_map else embedding.text
        return embedding

    def add_datetime_to_text(self) -> 'Embedding':
        embedding = copy.copy(self)
        dt = datetime.datetime.fromtimestamp(int(float(self.ts)))
        embedding.text = f"{dt.isoformat()} {embedding.text}"
        return embedding

    def __str__(self):
        return str({
            'channel_id': self.channel_id,
            'id': self.id,
            'text': self.text,
            'ts': self.ts,
            'thread_ts': self.thread_ts,
            'author_id': self.author_id,
        })

    def add_adjacent_messages_context(self, context_messages: List['Embedding']) -> 'Embedding':
        embedding = copy.copy(self)
        prefix = "".join([f"{emb.text}\n\n" for emb in filter(None, context_messages)])
        embedding.text = f"{prefix}{embedding.text}"
        return embedding

    def add_header(self, header: 'Embedding') -> 'Embedding':
        embedding = copy.copy(self)
        embedding.text = f"Thread: {header.text}\n\n{embedding.text}"
        return embedding

    def convert_to_summary(self, summary: str) -> 'Embedding':
        embedding = copy.copy(self)
        embedding.id = f"{embedding.id}-summary"
        embedding.text = (f"Thread: {embedding.text}\n"
                          f"Thread summary: {summary}")
        return embedding

    def to_metadata(self) -> Dict[str, str]:
        metadata = {
            'channel_id': self.channel_id,
            'text': self.text,
            'ts': self.ts,
            'version': 1,
        }
        if self.thread_ts is not None:
            metadata['thread_ts'] = self.thread_ts
        if self.author_id is not None:
            metadata['author_id'] = self.author_id
        return metadata


def slack_message_to_embedding(channel_id: str, message: dict) -> Embedding:
    return Embedding(
        channel_id,
        f"{channel_id}-{message['ts']}",
        message['text'],
        message['ts'],
        message.get('thread_ts'),
        message.get('user'),
    )


def generate_embeddings(channel_id: str, messages: List[dict]) -> List[Embedding]:
    return list(map(lambda message: slack_message_to_embedding(channel_id, message), messages))


def replace_ids_with_names(embeddings: List[Embedding], team_id: str) -> List[Embedding]:
    names_map = slack_names_map(team_id)
    return [embedding.replace_names(names_map) for embedding in embeddings]


def enrich_with_adjacent_messages(embeddings: List[Embedding]) -> List[Embedding]:
    updated_embeddings = []
    for i in range(len(embeddings)):
        first_context_embedding = embeddings[i - 2] if i - 2 >= 0 else None
        second_context_embedding = embeddings[i - 1] if i - 1 >= 0 else None
        updated_embeddings.append(embeddings[i].add_adjacent_messages_context([
            first_context_embedding,
            second_context_embedding
        ]))
    return updated_embeddings


def enrich_with_datetime(embeddings: List[Embedding]) -> List[Embedding]:
    return [embedding.add_datetime_to_text() for embedding in embeddings]


def attach_header(embeddings: List[Embedding], header: Embedding) -> List[Embedding]:
    part_with_header = embeddings[:2]
    part_without_header = embeddings[2:]
    return part_with_header + [embedding.add_header(header) for embedding in part_without_header]


def index_messages(channel_id, messages, start_from, pinecone_index, pinecone_namespace):
    total_messages = len(messages)

    logging.info("Replacing User IDs with User Names in the messages")
    embeddings = generate_embeddings(channel_id, messages)
    embeddings = replace_ids_with_names(embeddings, team_id=pinecone_namespace)
    embeddings = enrich_with_datetime(embeddings)
    embeddings_without_context = embeddings
    embeddings = enrich_with_adjacent_messages(embeddings)

    logging.info("Preparing messages for embedding")
    messages_for_embedding = []

    for (counter, (message, embedding)) in list(enumerate(zip(messages, embeddings)))[start_from:]:
        if is_thread(message):
            logging.info(
                f"{counter + 1}/{total_messages} Appending thread messages for {message['ts']} : {message['thread_ts']}")
            thread_messages = filter_messages(fetch_thread_messages(channel_id, message["thread_ts"]))
            thread_embeddings = generate_embeddings(channel_id, thread_messages)
            thread_embeddings = replace_ids_with_names(thread_embeddings, team_id=pinecone_namespace)
            thread_embeddings = enrich_with_datetime(thread_embeddings)
            thread_header = thread_embeddings[0]
            raw_messages_for_summary = list(map(lambda e: e.text, thread_embeddings))

            additional_context_embeddings = [
                embeddings_without_context[counter - 2] if counter >= 2 else None,
                embeddings_without_context[counter - 1] if counter >= 1 else None,
            ]
            additional_context_embeddings = list(filter(None, additional_context_embeddings))
            thread_embeddings = additional_context_embeddings + thread_embeddings
            thread_embeddings = enrich_with_adjacent_messages(thread_embeddings)[len(additional_context_embeddings):]
            thread_embeddings = attach_header(thread_embeddings, thread_header)
            messages_for_embedding += thread_embeddings
            logging.info(f"  - Appended {str(len(thread_messages))} thread messages")

            try:
                logging.info(f"  - Summarizing thread {message['thread_ts']}")
                summary = gpt_summarize_thread(raw_messages_for_summary)
                messages_for_embedding.append(thread_header.convert_to_summary(summary))
            except:
                logging.info(f"  - Failed to summarize - {message['thread_ts']}")
        elif is_actual_message(message):
            logging.info(f"{counter + 1}/{total_messages} Appending regular message {message['ts']}")
            messages_for_embedding.append(embedding)

    logging.info(f"Generated {str(len(messages_for_embedding))} messages for embedding")
    messages_for_embedding = list(filter(lambda emb_t: len(emb_t.text) != 0, messages_for_embedding))
    logging.info(f"Removed empty messages, {str(len(messages_for_embedding))} messages left")

    insert_pinecone_embeddings(messages_for_embedding, pinecone_index, pinecone_namespace)


def index_whole_channel(pinecone_namespace, channel_id):
    logging.info(f"Fetching all messages from {channel_id} channel")
    messages = list(reversed(fetch_channel_messages(channel_id)))
    logging.info(f"Loaded {str(len(messages))} messages")

    messages = filter_messages(messages)
    total_messages = len(messages)
    logging.info(f"Filtering out service messages, left {str(total_messages)} messages")

    index_messages(channel_id, messages, 0, get_pinecone_index(), pinecone_namespace)


def insert_pinecone_embeddings(messages_for_embedding: List[Embedding], pinecone_index, pinecone_namespace):
    logging.info("Starting embeddings creation for the generated messages")
    chunk_size = 30  # for OpenAI
    embedding_chunks = [messages_for_embedding[i:i + chunk_size] for i in
                        range(0, len(messages_for_embedding), chunk_size)]
    counter = 0
    for chunk in embedding_chunks:
        logging.info(f"Inserting a chunk of Pinecone embeddings: [{counter} - {counter + len(chunk) - 1}]")
        counter += len(chunk)
        try:
            embeddings = create_embeddings([embedding_message.text for embedding_message in chunk])
            items = []

            for i in range(len(chunk)):
                items.append({
                    'id': chunk[i].id,
                    'values': embeddings[i],
                    'metadata': chunk[i].to_metadata()
                })

            pinecone_index.upsert(
                vectors=items,
                namespace=pinecone_namespace
            )
        except:
            logging.exception("Couldn't insert embeddings")


def delete_pinecone_embedding(embeddings: list[Embedding], pinecone_index, pinecone_namespace):
    ids = list(map(lambda emb: emb.id, embeddings))
    logging.info(f"Deleting embeddings for {str(ids)}")
    pinecone_index.delete(ids=ids, namespace=pinecone_namespace)


def handle_message_update_and_reindex(body):
    event = body['event']
    team_id = body['team_id']
    message = None
    if 'subtype' in event and event['subtype'] == 'message_deleted':
        # processing a message deletion
        channel_id = event['channel']
        message = event['previous_message']
        embedding = slack_message_to_embedding(channel_id, message)
        delete_pinecone_embedding([embedding], get_pinecone_index(), team_id)
        if message.get('thread_ts') is not None:
            # just reindex the whole thread
            index_messages(channel_id, load_previous_messages(channel_id, message.get('thread_ts'), 1), 0, get_pinecone_index(), team_id)
            return
        message_ts = message['ts']
        messages_for_reindex = load_previous_messages(channel_id, message_ts, 2) + load_subsequent_messages(channel_id, message_ts, 2)
        # reindex surrounding messages
        index_messages(channel_id, messages_for_reindex, 2, get_pinecone_index(), team_id)
        return
    if 'subtype' in event and event['subtype'] == 'message_changed':
        # processing a message update
        channel_id = event['channel']
        message = event['previous_message']
        if message.get('thread_ts') is not None:
            # just reindex the whole thread
            index_messages(channel_id, load_previous_messages(channel_id, message.get('thread_ts'), 1), 0, get_pinecone_index(), team_id)
            return
        message_ts = message['ts']
        messages_for_reindex = load_previous_messages(channel_id, message_ts, 3) + load_subsequent_messages(channel_id, message_ts, 3)[1:]
        # reindex surrounding messages
        index_messages(channel_id, messages_for_reindex, 2, get_pinecone_index(), team_id)
        return
    if 'subtype' not in event:
        message = event
    if message is None:
        return
    # processing a new message
    message_id = message['ts']
    thread_ts = message.get('thread_ts')
    channel_id = event['channel']
    if not is_actual_message(message):
        return
    embeddings = generate_embedding_for_message(team_id, channel_id, message_id, thread_ts)
    insert_pinecone_embeddings(
        embeddings,
        get_pinecone_index(),
        team_id
    )


def generate_embedding_for_message(team_id, channel_id, message_id, thread_ts) -> List['Embedding']:
    if thread_ts is not None:
        # should be improved
        thread_messages = fetch_thread_messages(channel_id, thread_ts)
        thread_messages = filter_messages(thread_messages)
        thread_head = thread_messages[0]
        head_embedding = generate_embeddings(channel_id, [thread_head])[0]

        message_index = None
        for i, message in enumerate(thread_messages):
            if message['ts'] == message_id:
                message_index = i
                break

        if message_index is None:
            return []
        messages = thread_messages[:message_index + 1]
        additional_messages = [] if len(messages) > 2 else load_previous_messages(channel_id, thread_head['ts'], 4 - len(messages))[:-1]
        embeddings = generate_embeddings(channel_id, additional_messages) + generate_embeddings(channel_id, messages)
        embeddings = replace_ids_with_names(embeddings, team_id)
        embeddings = enrich_with_datetime(embeddings)
        embeddings = enrich_with_adjacent_messages(embeddings)[len(additional_messages):]
        embeddings = attach_header(embeddings, head_embedding)
        return embeddings[-1:]

    embeddings = generate_embeddings(channel_id, load_previous_messages(channel_id, message_id, 3))
    embeddings = replace_ids_with_names(embeddings, team_id)
    embeddings = enrich_with_datetime(embeddings)
    embeddings = enrich_with_adjacent_messages(embeddings)
    return embeddings[-1:]
