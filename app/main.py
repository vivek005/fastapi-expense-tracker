from fastapi import FastAPI, HTTPException, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from . import schemas, crud, database
from .auth import hash_password, verify_password, create_access_token
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Mount static files (HTML/CSS/JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def startup_event():
    database.init_db()

@app.get("/")
def read_index():
    return FileResponse('static/index.html')

# --- AUTHENTICATION ROUTES ---

from fastapi import FastAPI, HTTPException, Form, Depends
from fastapi.responses import JSONResponse # Add this import

# ... (rest of your imports and setup)

@app.post("/signup")
def signup(username: str = Form(...), password: str = Form(...)):
    conn = database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            # Use JSONResponse for specific errors to avoid the catch-all
            return JSONResponse(status_code=400, content={"detail": "Username already taken"})
        
        hashed_pw = hash_password(password)
        cursor.execute("INSERT INTO users (username, hashed_password) VALUES (?, ?)", 
                       (username, hashed_pw))
        conn.commit()
        return {"message": "User created successfully!"}
    except Exception as e:
        logger.error(f"Signup error: {e}")
        return JSONResponse(status_code=500, content={"detail": "Error creating user"})
    finally:
        conn.close()

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    conn = database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user or not verify_password(password, user['hashed_password']):
            # If user is not found or password is wrong, return 401 directly
            return JSONResponse(status_code=401, content={"detail": "Invalid username or password"})
        
        access_token = create_access_token(data={"sub": user['username'], "id": user['id']})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Login error: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error during login"})
    finally:
        conn.close()

# --- EXISTING EXPENSE ROUTES ---

@app.post("/expenses/", response_model=schemas.ExpenseResponse)
def create_expense(expense: schemas.ExpenseCreate):
    try:
        return crud.create_expense_in_db(expense)
    except Exception as e:
        logger.error(f"Failed to create expense: {e}")
        raise HTTPException(status_code=500, detail="Could not save expense")

@app.get("/expenses/", response_model=list[schemas.ExpenseResponse])
async def list_expenses():
    try:
        return crud.get_all_expenses()
    except Exception as e:
        logger.error(f"Failed to fetch expenses: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/expenses/total")
def get_total_spent():
    try:
        total = crud.get_total_spent_from_db()
        return {"total_spent": total}
    except Exception as e:
        logger.error(f"Failed to calculate total: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving total")

@app.get("/expenses/categories")
def get_categories_report():
    try:
        return crud.get_category_report_from_db()
    except Exception as e:
        logger.error(f"Failed to generate category report: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving report")

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    try:
        return crud.delete_expense_from_db(expense_id)
    except Exception as e:
        logger.error(f"Failed to delete expense {expense_id}: {e}")
        raise HTTPException(status_code=500, detail="Could not delete expense")