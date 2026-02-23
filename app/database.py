import sqlite3

DB_FILE = "expenses.db"

def get_connection():
    # Connects to the SQLite file (creates it if missing)
    conn = sqlite3.connect(DB_FILE)
    # This allows us to access data by name (row['amount']) instead of index (row[0])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    # Create the expenses table
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