import psycopg2
from psycopg2.extras import DictCursor
from config import DB_NAME, DB_HOST, DB_PASS, DB_USER

def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        cursor_factory=DictCursor,
        port=5432
    )

def create_table():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS achievments(
                    ach_id SERIAL PRIMARY KEY,
                    ach_name VARCHAR(15) UNIQUE NOT NULL,
                    condition VARCHAR(100)
                );
            """)
            conn.commit()

if __name__ == "__main__":
    create_table()