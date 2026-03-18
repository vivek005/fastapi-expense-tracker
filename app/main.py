from fastapi import FastAPI, HTTPException, Form, Depends, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from . import schemas, crud, database
from .auth import hash_password, verify_password, create_access_token, get_user_from_token
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def startup_event():
    database.init_db()

@app.get("/")
def read_index():
    return FileResponse('static/index.html')

# --- SECURITY HELPER ---

def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    return get_user_from_token(token)

# --- AUTHENTICATION ---

@app.post("/signup")
def signup(username: str = Form(...), password: str = Form(...)):
    conn = database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return JSONResponse(status_code=400, content={"detail": "Username taken"})
        cursor.execute("INSERT INTO users (username, hashed_password) VALUES (?, ?)", 
                       (username, hash_password(password)))
        conn.commit()
        return {"message": "Success"}
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
            return JSONResponse(status_code=401, content={"detail": "Invalid credentials"})
        token = create_access_token(data={"sub": user['username'], "id": user['id']})
        return {"access_token": token, "token_type": "bearer"}
    finally:
        conn.close()

# --- EXPENSES ---

@app.post("/expenses/", response_model=schemas.ExpenseResponse)
def create_expense(expense: schemas.ExpenseCreate, user=Depends(get_current_user)):
    if not user: raise HTTPException(status_code=401)
    return crud.create_expense_in_db(expense, owner_id=user["id"])

@app.get("/expenses/")
async def list_expenses(user=Depends(get_current_user)):
    if not user: return []
    return crud.get_all_expenses(owner_id=user["id"])

@app.get("/expenses/total")
def get_total_spent(user=Depends(get_current_user)):
    if not user: return {"total_spent": 0}
    return {"total_spent": crud.get_total_spent_from_db(owner_id=user["id"])}

@app.get("/expenses/categories")
def get_categories_report(user=Depends(get_current_user)):
    if not user: return []
    return crud.get_category_report_from_db(owner_id=user["id"])

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, user=Depends(get_current_user)):
    if not user: raise HTTPException(status_code=401)
    return crud.delete_expense_from_db(expense_id, owner_id=user["id"])