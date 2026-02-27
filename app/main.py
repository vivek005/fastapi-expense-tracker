from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from . import schemas, crud, database
import logging

# Configure logging to show time and error level
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

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
    try:
        return crud.create_expense_in_db(expense)
    except Exception as e:
        logger.error(f"Failed to create expense: {e}")
        raise HTTPException(status_code=500, detail="Could not save expense")

@app.get("/expenses/", response_model=list[schemas.ExpenseResponse])
async def list_expenses():
    try:
        # We call the CRUD function inside the try block
        return crud.get_all_expenses()
    except Exception as e:
        # This logs the actual error to your terminal for debugging
        logger.error(f"Failed to fetch expenses: {e}")
        # This sends a professional response back to the frontend
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

