from pgvector.psycopg2 import register_vector
import psycopg2

from ..config import get_postgre_host, get_postgre_port, get_postgre_database, get_postgre_user, get_postgre_password

conn = None
try:
    conn = psycopg2.connect(
        host=get_postgre_host(),
        database=get_postgre_database(),
        user=get_postgre_user(),
        password=get_postgre_password(),
        port=get_postgre_port())

    cur = conn.cursor()

    cur.execute('CREATE EXTENSION IF NOT EXISTS vector')
    register_vector(cur)

    # cur.execute('DROP TABLE IF EXISTS embedding')
    cur.execute('CREATE TABLE IF NOT EXISTS embedding (id bigserial PRIMARY KEY, namespace text, chunk_id text, metadata text, values vector)')

    conn.commit()
except (Exception, psycopg2.DatabaseError) as error:
    print(error)


def get_postgre_cursor():
    return cur


def postgre_commit():
    if conn is not None:
        conn.commit()

def postgre_excute(postgre_cursor):
    if conn is not None:
        postgre_cursor.excute(postgre_cursor)