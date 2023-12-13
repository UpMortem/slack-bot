from pgvector.psycopg2 import register_vector
import psycopg2
from .vector_database import VectorDatabase
import json
import numpy as np

from ...config import get_postgres_host, get_postgres_port, get_postgres_database, get_postgres_user, get_postgres_password

class Postgres(VectorDatabase): 
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                host=get_postgres_host(),
                database=get_postgres_database(),
                user=get_postgres_user(),
                password=get_postgres_password(),
                port=get_postgres_port())
            
            self.cur = self.conn.cursor()
            
            self.cur.execute('CREATE EXTENSION IF NOT EXISTS vector')
            register_vector(self.cur)

            self.cur.execute('CREATE TABLE IF NOT EXISTS embedding (id bigserial PRIMARY KEY, namespace text, chunk_id text, metadata text, values vector)')
            self.conn.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    # overriding abstract method 
    def insert(self, embeddings, chunk, namespace):
        for i in range(len(chunk)):
            metadata = json.dumps(chunk[i].to_metadata())
            self.cur.execute('INSERT INTO embedding (namespace, chunk_id, metadata, values) VALUES (%s, %s, %s, %s)', (namespace, chunk[i].id, metadata, embeddings[i]))
        
        self.conn.commit()
  
    # overriding abstract method 
    def delete(self, ids, namespace):
        self.cur.execute('DELETE FROM embedding WHERE chunk_id IN (%s) AND namespace=%s',(ids, namespace))
        self.conn.commit()

    # overriding abstract method 
    def select(self, query_vector):
        self.cur.execute('SELECT * FROM embedding ORDER BY values <-> %s LIMIT 50', (np.array(query_vector),))
        embeddings = self.cur.fetchall()
        output = [dict(id=chunk_id, metadata=json.loads(metadata)) for id, namespace, chunk_id, metadata, values in embeddings]
        return output


