from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from . import schemas, crud, database

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def startup_event():
    database.init_db()

@app.get("/")
def read_index():
    return FileResponse('static/index.html')

@app.post("/expenses/", response_model=schemas.ExpenseResponse)
def create_expense(expense: schemas.ExpenseCreate):
    return crud.create_expense_in_db(expense)

@app.get("/expenses/", response_model=list[schemas.ExpenseResponse])
def list_expenses():
    return crud.get_all_expenses()

@app.get("/expenses/total")
def get_total_spent():
    total = crud.get_total_spent_from_db()
    return {"total_spent": total}

@app.get("/expenses/categories")
def get_categories_report():
    return crud.get_category_report_from_db()

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    return crud.delete_expense_from_db(expense_id)

