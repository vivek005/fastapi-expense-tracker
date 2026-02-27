import sqlite3
import os
from dotenv import load_dotenv

# 1. Load variables from .env as soon as the file is read
load_dotenv()

# 2. Assign DB_FILE using environment variables with a fallback default
DB_FILE = os.getenv("DATABASE_URL", "expenses.db")

def get_connection():
    """Establishes a connection to the SQLite database with Row support."""
    conn = sqlite3.connect(DB_FILE)
    # Access data by name (row['amount']) instead of index (row[0])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            notes TEXT,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Database initialized and table created!")