import sqlite3
from datetime import datetime

DB_NAME = "expense.db"  # ✅ Ensure consistent usage

def init_db() -> None:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Create Users Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    # Create Expenses Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            category TEXT NOT NULL,
            amount INTEGER NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')

    # Create Monthly Limit Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS monthly_limit (
            username TEXT PRIMARY KEY,
            limit_amount INTEGER NOT NULL,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')

    conn.commit()
    conn.close()

def register_user(name: str, email: str, password: str) -> bool:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT 1 FROM users WHERE email = ?", (email,))
    if c.fetchone():
        conn.close()
        return False  # Email already registered

    username = email.split("@")[0]
    c.execute(
        "INSERT INTO users (username, name, email, password) VALUES (?, ?, ?, ?)", 
        (username, name, email, password)
    )
    conn.commit()
    conn.close()
    return True

def login_user(email: str, password: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT username, name FROM users WHERE email=? AND password=?", (email, password))
    user = c.fetchone()
    conn.close()
    return user  # Returns (username, name) or None

def add_expense(username: str, category: str, amount: int, description: str) -> None:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d")
    c.execute('''
        INSERT INTO expenses (username, category, amount, description, date) 
        VALUES (?, ?, ?, ?, ?)
    ''', (username, category, amount, description, date))
    conn.commit()
    conn.close()

def get_expenses(username: str):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT category, amount, description, date FROM expenses WHERE username = ?", (username,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_monthly_limit(username: str) -> int:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT limit_amount FROM monthly_limit WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

def set_monthly_limit(username: str, limit: int) -> None:
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO monthly_limit (username, limit_amount)
        VALUES (?, ?)
        ON CONFLICT(username) DO UPDATE SET limit_amount=excluded.limit_amount
    ''', (username, limit))
    conn.commit()
    conn.close()
