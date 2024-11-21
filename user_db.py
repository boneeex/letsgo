import psycopg2
import os
from psycopg2.extras import DictCursor
from datetime import datetime, timedelta
import jwt
import asyncpg

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
                CREATE TABLE IF NOT EXISTS users(
                    user_id SERIAL PRIMARY KEY,
                    username VARCHAR(15) UNIQUE NOT NULL,
                    password_hash VARCHAR(15) NOT NULL,
                    ac_creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP,
                    points INTEGER,
                    quizes_done VARCHAR,
                    ach_done VARCHAR,
                    likes INTEGER,
                    dislikes INTEGER,
                    films_watched INTEGER,
                    streak_days INTEGER
                );
            """)
            conn.commit()

def user_register(username, password_hash):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users(username, password_hash)
                VALUES(%s, %s)
            """, (username, password_hash))
            conn.commit()
            if cursor.fetchall:
                return True
            else:
                return False
            

def user_login(username, password_hash):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM users
                WHERE username = %s AND password_hash = %s
            """, (username, password_hash))
            return cursor.fetchone()

def get_user(username):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM users
                WHERE user_id = %s
            """, (username,))
            return cursor.fetchall()
        
def update_last_activity(username):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT last_activity FROM users WHERE username = %s", (username,))
            last_activity = DictCursor(cursor.fetchone())["last_activity"]
            check_streak = datetime.now() - last_activity 
            if check_streak > timedelta(days=1):
                cursor.execute("""
                    UPDATE users
                    SET streak_days = 0
                    WHERE username = %s
                """, ( username,))
            else:
                cursor.execute("""
                    UPDATE users
                    SET streak_days = streak_days + 1
                    WHERE username = %s
                """, (username,))
            conn.commit()
            cursor.execute("""
                UPDATE users
                SET last_activity = CURRENT_TIMESTAMP
                WHERE username = %s
            """, (username,))
            conn.commit()


def top_by_days_streak():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM users
                ORDER BY streak_days DESC
            """)
            return DictCursor.fetchall()

def update_points(username, points):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE users
                SET points = %s
                WHERE username = %s
            """, (points, username,))
            conn.commit()

def top_by_points():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM users
                ORDER BY points DESC
            """)
            return DictCursor.fetchall()

secret_key = "sekret_key"

def create_jwt(payload: dict) -> str:
    payload['exp'] = datetime.utcnow() + timedelta(hours=3)
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token


def jwt_token_payload(token: str) -> dict | bool:
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except:
        return False


async def check_jwt_token(jwt_token: str) -> bool | dict:
    if jwt_token_payload(jwt_token):
        conn = await asyncpg.connect(user='postgres', password='postgres', database='me2me', host='localhost', port='5432')
        user_id = jwt_token_payload(jwt_token)['user_id']
        user = await conn.fetchrow('select * from users where user_id = $1', user_id)
        user = dict(user)
        jwt_token = create_jwt(payload={'user_id': user_id})
        return jwt_token
    return False


if __name__ == "__main__":
    create_table()