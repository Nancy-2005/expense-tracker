import sqlite3

DB_NAME = "users.db"

import sqlite3

def init_db():
    conn = sqlite3.connect("expenses.db")
    c = conn.cursor()
    
    # ✅ Create 'users' table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # ✅ Create 'expenses' table
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            username TEXT,
            category TEXT,
            amount INTEGER,
            description TEXT,
            date TEXT
        )
    ''')

    # ✅ Create 'monthly_limit' table (quote "limit")
    c.execute('''
        CREATE TABLE IF NOT EXISTS monthly_limit (
            username TEXT PRIMARY KEY,
            "limit" INTEGER
        )
    ''')

    conn.commit()
    conn.close()




def login_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT email, name FROM users WHERE email = ? AND password = ?", (email, password))
    result = c.fetchone()
    conn.close()
    return result 
def register_user(name, email, password):
    conn = sqlite3.connect("expenses.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    if c.fetchone():
        conn.close()
        return False

    username = email.split("@")[0]  # or generate a unique username
    c.execute("INSERT INTO users (username, name, email, password) VALUES (?, ?, ?, ?)", 
              (username, name, email, password))
    conn.commit()
    conn.close()
    return True

 # (email, name) or None

def add_expense(username, category, amount, description):
    from datetime import datetime
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        category TEXT,
        amount INTEGER,
        description TEXT,
        date TEXT
    )''')
    date = datetime.now().strftime("%Y-%m-%d")
    c.execute("INSERT INTO expenses (username, category, amount, description, date) VALUES (?, ?, ?, ?, ?)",
              (username, category, amount, description, date))
    conn.commit()
    conn.close()


# In database.py
def get_expenses(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT category, amount, description, date FROM expenses WHERE username = ?", (username,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_monthly_limit(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS limits (username TEXT PRIMARY KEY, monthly_limit INTEGER)")
    c.execute("SELECT monthly_limit FROM limits WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

def set_monthly_limit(username, limit):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS limits (username TEXT PRIMARY KEY, monthly_limit INTEGER)")
    c.execute("REPLACE INTO limits (username, monthly_limit) VALUES (?, ?)", (username, limit))
    conn.commit()
    conn.close()



