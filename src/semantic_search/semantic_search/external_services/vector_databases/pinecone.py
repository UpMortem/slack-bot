import pinecone
from .vector_database import VectorDatabase
from ...config import get_pinecone_key, get_pinecone_environment, get_pinecone_index_name

class Pinecone(VectorDatabase): 
    def __init__(self):
        pinecone.init(api_key=get_pinecone_key(), environment=get_pinecone_environment())

    # overriding abstract method 
    def insert(self, embeddings, chunk, namespace):
        items = []

        for i in range(len(chunk)):
            items.append({
                'id': chunk[i].id,
                'values': embeddings[i],
                'metadata': chunk[i].to_metadata()
            })

        self.get_pinecone_index().upsert(
            vectors=items,
            namespace=namespace
        )
  
    # overriding abstract method 
    def delete(self, ids, namespace):
        self.get_pinecone_index().delete(ids=ids, namespace=namespace)

    # overriding abstract method 
    def select(self, query_vector, namespace):
        query_results = self.get_pinecone_index().query(
            queries=[query_vector],
            top_k=50,
            namespace=namespace,
            include_values=False,
            includeMetadata=True
        )
        return query_results['results'][0]['matches']

    def get_pinecone_index() -> 'pinecone.Index':
        return pinecone.Index(get_pinecone_index_name())

