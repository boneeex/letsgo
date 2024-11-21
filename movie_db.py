import psycopg2
import os
from psycopg2.extras import DictCursor

DB_HOST = os.getenv('DB_HOST', '')
DB_NAME = os.getenv('DB_NAME', "")
DB_USER = os.getenv('DB_USER', "")
DB_PASS = os.getenv('DB_PASS', "")

def get_connection():
    return psycopg2.connect(dbname=DB_NAME,
                            user=DB_USER,
                            password=DB_PASS, 
                            host=DB_HOST, 
                            cursor_factory=DictCursor,
                            port=5432)

def create_table():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS movies(
                    movie_id SERIAL PRIMARY KEY,
                    movie_name VARCHAR(15) NOT NULL,
                    img_url VARCHAR NOT NULL
                );
            """)
            conn.commit()

if __name__ == "__main__":
    create_table()