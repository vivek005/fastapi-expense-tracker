from fastapi import FastAPI
from .database import init_db, get_connection
from pydantic import BaseModel, Field
from datetime import date

# This is your Pydantic Model
class ExpenseCreate(BaseModel):
    amount: float = Field(gt=0, description="The amount must be greater than zero")
    category: str = Field(min_length=3, max_length=20)
    notes: str = "No notes provided" # Default value
    date: date # This automatically validates YYYY-MM-DD strings

app = FastAPI()

# This runs the database initialization when you start the server
@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def home():
    return {"status": "Success", "message": "FastAPI is running with SQLite!"}

@app.post("/expenses/")
def create_expense(expense: ExpenseCreate):
    # 1. Open the connection
    conn = get_connection()
    cursor = conn.cursor()
    
    # 2. Write the SQL command
    # Notice the '?'—these are placeholders to prevent SQL Injection (Security!)
    query = """
        INSERT INTO expenses (amount, category, notes, date) 
        VALUES (?, ?, ?, ?)
    """
    
    # 3. Execute with the validated data from Pydantic
    cursor.execute(query, (
        expense.amount, 
        expense.category, 
        expense.notes, 
        str(expense.date) # We convert the date object to a string for SQLite
    ))
    
    # 4. Save and Close
    conn.commit()
    conn.close()
    
    return {"message": "Expense saved successfully!", "data": expense}
    
@app.get("/expenses/")
def list_expenses():
    # 1. Get the connection
    conn = get_connection()
    cursor = conn.cursor()
    
    # 2. Run the Select query
    cursor.execute("SELECT * FROM expenses")
    
    # 3. Fetch all records
    rows = cursor.fetchall()
    
    # 4. Convert rows to a list of dictionaries
    # Remember 'conn.row_factory = sqlite3.Row'? 
    # That makes this conversion very easy.
    expenses = []
    for row in rows:
        expenses.append(dict(row))
    
    conn.close()
    return expenses

@app.get("/expenses/total")
def get_total_spent():
    conn = get_connection()
    cursor = conn.cursor()
    
    # SQL math: SUM(amount) adds up the whole column
    cursor.execute("SELECT SUM(amount) FROM expenses")
    
    # fetchone() gives us the single result of the math
    result = cursor.fetchone()
    
    # The result comes back as a Row, so we grab the first value
    total = result[0] if result[0] else 0
    
    conn.close()
    return {"total_spent": total}