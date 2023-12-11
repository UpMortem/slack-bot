from abc import ABC, abstractmethod 

class VectorDatabase(ABC): 
    @abstractmethod
    def insert(self, embeddings, chunk, namespace):
        pass

    @abstractmethod
    def delete(self, ids, namespace):
        pass

    @abstractmethod
    def select(self, query_vector):
        pass