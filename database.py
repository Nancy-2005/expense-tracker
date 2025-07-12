import sqlite3
from datetime import datetime

DB_NAME = "expense.db"  # ✅ Use the same DB everywhere

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            category TEXT,
            amount INTEGER,
            description TEXT,
            date TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS monthly_limit (
            username TEXT PRIMARY KEY,
            limit_amount INTEGER
        )
    ''')

    conn.commit()
    conn.close()

def register_user(name, email, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    if c.fetchone():
        conn.close()
        return False

    username = email.split("@")[0]
    c.execute("INSERT INTO users (username, name, email, password) VALUES (?, ?, ?, ?)", 
              (username, name, email, password))
    conn.commit()
    conn.close()
    return True

def login_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT username, name FROM users WHERE email=? AND password=?", (email, password))
    user = c.fetchone()
    conn.close()
    return user

def add_expense(username, category, amount, description):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d")
    c.execute("INSERT INTO expenses (username, category, amount, description, date) VALUES (?, ?, ?, ?, ?)",
              (username, category, amount, description, date))
    conn.commit()
    conn.close()

def get_expenses(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT category, amount, description, date FROM expenses WHERE username = ?", (username,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_monthly_limit(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS monthly_limit (username TEXT PRIMARY KEY, limit_amount INTEGER)")
    c.execute("SELECT limit_amount FROM monthly_limit WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

def set_monthly_limit(username, limit):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS monthly_limit (username TEXT PRIMARY KEY, limit_amount INTEGER)")
    c.execute("REPLACE INTO monthly_limit (username, limit_amount) VALUES (?, ?)", (username, limit))
    conn.commit()
    conn.close()
