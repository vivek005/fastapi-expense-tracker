from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from . import schemas, crud
from .database import init_db


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def startup_event():
    init_db()

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
    return{"total_spent": total}


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    crud.delete_expense_by_id(expense_id)
    return {"message": "Deleted successfully"}