from .database import get_connection

def create_expense_in_db(expense, owner_id):
    conn = get_connection()
    cursor = conn.cursor()
    # Ensure owner_id is included in the INSERT
    query = "INSERT INTO expenses (amount, category, notes, date, owner_id) VALUES (?, ?, ?, ?, ?)"
    cursor.execute(query, (expense.amount, expense.category, expense.notes, str(expense.date), owner_id))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {**expense.dict(), "id": new_id, "owner_id": owner_id}

def get_all_expenses(owner_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE owner_id = ?", (owner_id,))
    rows = cursor.fetchall()
    expenses = [dict(row) for row in rows]
    conn.close()
    return expenses

def get_total_spent_from_db(owner_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM expenses WHERE owner_id = ?", (owner_id,))
    result = cursor.fetchone()
    total = result[0] if result[0] else 0
    conn.close()
    return total    

def get_category_report_from_db(owner_id):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT category, SUM(amount) as total FROM expenses WHERE owner_id = ? GROUP BY category"
    cursor.execute(query, (owner_id,))
    rows = cursor.fetchall()
    report = [dict(row) for row in rows]
    conn.close() 
    return report

def delete_expense_from_db(expense_id: int, owner_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    # Security check: only delete if it belongs to this user
    cursor.execute("DELETE FROM expenses WHERE id = ? AND owner_id = ?", (expense_id, owner_id))
    conn.commit()
    conn.close()
    return {"message": "Success"}