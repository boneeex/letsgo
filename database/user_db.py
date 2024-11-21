import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime, timedelta
from jose import jwt
from config import DB_NAME, DB_HOST, DB_PASS, DB_USER, SECRET_KEY


def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        cursor_factory=DictCursor,
        port=5432
    )

# Создание таблицы пользователей
def create_table():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id SERIAL PRIMARY KEY,
                    username VARCHAR(15) UNIQUE NOT NULL,
                    password VARCHAR(15) NOT NULL,
                    ac_creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP,
                    points INTEGER DEFAULT 0,
                    quizes_done VARCHAR DEFAULT '',
                    ach_done VARCHAR DEFAULT '',
                    likes INTEGER DEFAULT 0,
                    dislikes INTEGER DEFAULT 0,
                    films_watched INTEGER DEFAULT 0,
                    streak_days INTEGER DEFAULT 0
                );
            """)
            conn.commit()

# Регистрация пользователя
def user_register(username, password):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (username, password)
                VALUES (%s, %s) RETURNING user_id
            """, (username, password))
            conn.commit()
            user_id = cursor.fetchone()
            return {"user_id": user_id}

# Авторизация пользователя
def user_login(username, password):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM users
                WHERE username = %s AND password = %s
            """, (username, password))
            return cursor.fetchone()

# Получение информации о пользователе
def get_user_by_username(username):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM users
                WHERE username = %s
            """, (username,))
            return cursor.fetchone()
        
def get_user_by_id(user_id):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT * FROM users
                WHERE user_id = %s
            """, (user_id,))
            return cursor.fetchone()

# Обновление последней активности
def update_last_activity(username):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT last_activity FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            last_activity = result['last_activity'] if result else None

            if last_activity is None:
                cursor.execute("""
                    UPDATE users
                    SET streak_days = 0,
                        last_activity = CURRENT_TIMESTAMP
                    WHERE username = %s
                """, (username,))
            else:
                # Вычисляем разницу времени
                check_streak = datetime.now() - last_activity
                if check_streak > timedelta(days=1):
                    cursor.execute("""
                        UPDATE users
                        SET streak_days = 0
                        WHERE username = %s
                    """, (username,))
                else:
                    cursor.execute("""
                        UPDATE users
                        SET streak_days = streak_days + 1
                        WHERE username = %s
                    """, (username,))
                # Обновляем last_activity
                cursor.execute("""
                    UPDATE users
                    SET last_activity = CURRENT_TIMESTAMP
                    WHERE username = %s
                """, (username,))
            conn.commit()


# Топ пользователей по серии дней
def top_by_days_streak():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT username, streak_days
                FROM users
                ORDER BY streak_days DESC
            """)
            return cursor.fetchall()

# Обновление очков пользователя
def update_points(username, points):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE users
                SET points = %s
                WHERE username = %s
            """, (points, username,))
            conn.commit()

# Топ пользователей по очкам
def top_by_points():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT username, points
                FROM users
                ORDER BY points DESC
            """)
            return cursor.fetchall()

# Создание JWT токена
def create_jwt(payload: dict) -> str:
    payload['exp'] = datetime.utcnow() + timedelta(hours=3)
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Проверка JWT токена
def jwt_token_payload(token: str) -> dict | bool:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except:
        return False

async def check_jwt_token(jwt_token: str):
    try:
        payload = jwt_token_payload(jwt_token)
        if not payload:
            return False
        user_id = payload["user_id"]
        user = get_user_by_id(int(user_id))
        if user:
            new_token = create_jwt({"user_id": user_id})
            return new_token
        return False
    except Exception as e:
        return False
