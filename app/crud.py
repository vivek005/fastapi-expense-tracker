from .database import get_connection

def create_expense_in_db(expense):
    conn = get_connection()
    cursor = conn.cursor()
    query = "INSERT INTO expenses (amount, category, notes, date) VALUES (?, ?, ?, ?)"
    cursor.execute(query, (expense.amount, expense.category, expense.notes, str(expense.date)))
    new_id = cursor.lastrowid # Get the ID of the new record
    conn.commit()
    conn.close()
    return {**expense.dict(), "id": new_id}

def get_all_expenses():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    # This turns database rows into Python dictionaries
    expenses = [dict(row) for row in rows]
    conn.close()
    return expenses

def get_total_spent_from_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM expenses")
    result = cursor.fetchone()
    total = result[0] if result[0] else 0
    conn.close()
    return total    

def get_category_report_from_db():
    conn = get_connection() # Open the connection here
    cursor = conn.cursor()
    query = """
        SELECT category, SUM(amount) as total 
        FROM expenses 
        GROUP BY category
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    report = [dict(row) for row in rows]
    conn.close() 
    return report

def delete_expense_from_db(expense_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()
    return {"message": "Success"}


