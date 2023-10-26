import pinecone
from ..config import get_pinecone_key, get_pinecone_environment, get_pinecone_index_name

pinecone.init(api_key=get_pinecone_key(), environment=get_pinecone_environment())


def get_pinecone_index() -> 'pinecone.Index':
    return pinecone.Index(get_pinecone_index_name())
