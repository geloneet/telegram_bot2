# bot/services/db_service.py
import sqlite3

DB_PATH = "bot.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            credits INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def get_credits(user_id: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT credits FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def add_user_if_not_exists(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, credits) VALUES (?, 0)", (user_id,))
    conn.commit()
    conn.close()

def update_credits(user_id: int, new_amount: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET credits = ? WHERE user_id = ?", (new_amount, user_id))
    conn.commit()
    conn.close()

def add_credits(user_id: int, amount: int):
    current = get_credits(user_id)
    update_credits(user_id, current + amount)

def deduct_credit(user_id: int, amount: int = 1) -> bool:
    current = get_credits(user_id)
    if current >= amount:
        update_credits(user_id, current - amount)
        return True
    return False