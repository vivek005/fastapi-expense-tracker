from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date

class ExpenseBase(BaseModel):
    # Field helps add metadata and extra validation
    notes: str = Field(..., min_length=2, max_length=50, description="What did you buy?")
    amount: float = Field(..., gt=0, description="Amount must be greater than zero")
    category: str = Field(default="Misc", min_length=2)
    date: date

    # Custom validator: This is "Mastery" level logic
    @field_validator('amount')
    @classmethod
    def amount_must_be_realistic(cls, v: float) -> float:
        if v > 1000000:
            raise ValueError('Amount seems too high. Please verify.')
        return v

class ExpenseCreate(ExpenseBase):
    pass # This is used when creating a new expense

class ExpenseResponse(ExpenseBase):
    id: int # The response includes the database ID

    class Config:
        from_attributes = True # This allows compatibility with database objects