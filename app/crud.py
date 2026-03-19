from .database import get_connection, get_p

p = get_p()

def create_expense_in_db(expense, owner_id):
    conn = get_connection()
    cursor = conn.cursor()
    p = get_p()
    clean_category = expense.category.strip().capitalize()
    
    # Check if we are on Postgres to use RETURNING
    query = f"INSERT INTO expenses (amount, category, notes, date, owner_id) VALUES ({p}, {p}, {p}, {p}, {p})"
    if p == "%s": query += " RETURNING id"
    
    cursor.execute(query, (expense.amount, clean_category, expense.notes, str(expense.date), owner_id))
    
    if p == "%s":
        new_id = cursor.fetchone()['id']
    else:
        new_id = cursor.lastrowid
        
    conn.commit()
    conn.close()
    return {**expense.dict(), "id": new_id, "owner_id": owner_id, "category": clean_category}

def get_all_expenses(owner_id):
    conn = get_connection()
    cursor = conn.cursor()
    p = get_p()
    cursor.execute(f"SELECT * FROM expenses WHERE owner_id = {p}", (owner_id,))
    rows = cursor.fetchall()
    expenses = [dict(row) for row in rows]
    conn.close()
    return expenses

def get_total_spent_from_db(owner_id):
    conn = get_connection()
    cursor = conn.cursor()
    p = get_p()
    cursor.execute(f"SELECT SUM(amount) as total_sum FROM expenses WHERE owner_id = {p}", (owner_id,))
    result = cursor.fetchone()
    total = (result['total_sum'] if isinstance(result, dict) else result[0]) or 0
    conn.close()
    return total    

def get_category_report_from_db(owner_id):
    conn = get_connection()
    cursor = conn.cursor()
    p = get_p()
    query = f"SELECT category, SUM(amount) as total FROM expenses WHERE owner_id = {p} GROUP BY category"
    cursor.execute(query, (owner_id,))
    rows = cursor.fetchall()
    report = [dict(row) for row in rows]
    conn.close() 
    return report

def delete_expense_from_db(expense_id: int, owner_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    p = get_p()
    cursor.execute(f"DELETE FROM expenses WHERE id = {p} AND owner_id = {p}", (expense_id, owner_id))
    conn.commit()
    conn.close()
    return {"message": "Success"}

