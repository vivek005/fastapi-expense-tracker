import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
DB_FILE = os.getenv("DATABASE_URL", "expenses.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON") # Required for private links
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    # 1. Create Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL
        )
    ''')
    # 2. Create Expenses Table with owner_id
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            notes TEXT,
            date TEXT NOT NULL,
            owner_id INTEGER,
            FOREIGN KEY (owner_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Database ready: Users and Expenses tables initialized!")