import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL", "expenses.db")

def get_connection():
    if DB_URL.startswith("postgres://") or DB_URL.startswith("postgresql://"):
        # Fix for Render: ensure the URL starts with 'postgresql://'
        conn_url = DB_URL.replace("postgres://", "postgresql://", 1)
        # RealDictCursor allows reading rows as dictionaries
        return psycopg2.connect(conn_url, sslmode='require', cursor_factory=RealDictCursor)
    else:
        conn = sqlite3.connect(DB_URL)
        conn.row_factory = sqlite3.Row
        return conn

# NEW: This helper automatically picks '?' for local and '%s' for Render
def get_p():
    return "%s" if "postgres" in DB_URL else "?"

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    users_sql = 'CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username TEXT UNIQUE NOT NULL, hashed_password TEXT NOT NULL)'
    expenses_sql = 'CREATE TABLE IF NOT EXISTS expenses (id SERIAL PRIMARY KEY, amount REAL NOT NULL, category TEXT NOT NULL, notes TEXT, date TEXT NOT NULL, owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE)'
    
    if "postgres" not in DB_URL:
        users_sql = users_sql.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
        expenses_sql = expenses_sql.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")

    cursor.execute(users_sql)
    cursor.execute(expenses_sql)
    conn.commit()
    cursor.close()
    conn.close()