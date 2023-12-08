from pgvector.psycopg2 import register_vector
import psycopg2

from ..config import get_postgres_host, get_postgres_port, get_postgres_database, get_postgres_user, get_postgres_password

conn = None
try:
    conn = psycopg2.connect(
        host=get_postgres_host(),
        database=get_postgres_database(),
        user=get_postgres_user(),
        password=get_postgres_password(),
        port=get_postgres_port())

    cur = conn.cursor()

    cur.execute('CREATE EXTENSION IF NOT EXISTS vector')
    register_vector(cur)

    # cur.execute('DROP TABLE IF EXISTS embedding')
    cur.execute('CREATE TABLE IF NOT EXISTS embedding (id bigserial PRIMARY KEY, namespace text, chunk_id text, metadata text, values vector)')

    conn.commit()
except (Exception, psycopg2.DatabaseError) as error:
    print(error)


def get_postgres_cursor():
    return cur


def postgres_commit():
    if conn is not None:
        conn.commit()

def postgres_excute(postgres_cursor):
    if conn is not None:
        postgres_cursor.excute(postgres_cursor)