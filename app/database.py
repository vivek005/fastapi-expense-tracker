import os
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL", "expenses.db")

def get_connection():
    # If the URL starts with 'postgres', use PostgreSQL
    if DB_URL.startswith("postgres://") or DB_URL.startswith("postgresql://"):
        conn = psycopg2.connect(DB_URL, sslmode='require')
        return conn
    else:
        # Otherwise, fall back to local SQLite
        conn = sqlite3.connect(DB_URL)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # SQL syntax is almost identical for our needs
    users_sql = '''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL
        )
    '''
    expenses_sql = '''
        CREATE TABLE IF NOT EXISTS expenses (
            id SERIAL PRIMARY KEY,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            notes TEXT,
            date TEXT NOT NULL,
            owner_id INTEGER REFERENCES users(id) ON DELETE CASCADE
        )
    '''
    # For SQLite compatibility in local testing
    if not (DB_URL.startswith("postgres")):
        users_sql = users_sql.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
        expenses_sql = expenses_sql.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
        expenses_sql = expenses_sql.replace("owner_id INTEGER REFERENCES users(id)", "owner_id INTEGER, FOREIGN KEY(owner_id) REFERENCES users(id)")

    cursor.execute(users_sql)
    cursor.execute(expenses_sql)
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Persistent Database Initialized!")