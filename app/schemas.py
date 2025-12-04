
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional


class ExpenseCreate(BaseModel):
amount: float = Field(..., gt=0)
category: str
note: Optional[str] = None
created_at: Optional[datetime] = None
user: Optional[str] = "default_user"
share_id: Optional[str] = None


class ExpenseOut(ExpenseCreate):
id: int
created_at: datetime


class Config:
orm_mode = True


class BudgetCreate(BaseModel):
category: str
year: int
month: int
amount: float = Field(..., gt=0)
user: Optional[str] = "default_user"
alert_threshold: Optional[float] = None


class BudgetOut(BudgetCreate):
id: int


class Config:
orm_mode = True


class ReportItem(BaseModel):
category: str
spent: float
budget: Optional[float]
percent_used: Optional[float]
---


## File: app/crud.py


```python
"""Simple CRUD helpers using SQLAlchemy ORM."""
from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime
import calendar




def create_expense(db: Session, exp: schemas.ExpenseCreate):
e = models.Expense(
amount=exp.amount,
category=exp.category,
note=exp.note,
user=exp.user,
share_id=exp.share_id,
created_at=exp.created_at
)
db.add(e)
db.commit()
db.refresh(e)
return e




def create_or_update_budget(db: Session, b: schemas.BudgetCreate):
q = db.query(models.Budget).filter_by(category=b.category, year=b.year, month=b.month, user=b.user)
obj = q.first()
if obj:
obj.amount = b.amount
obj.alert_threshold = b.alert_threshold
else:
obj = models.Budget(**b.dict())
db.add(obj)
db.commit()
db.refresh(obj)
return obj




def total_spent_month(db: Session, year: int, month: int, user: str = "default_user"):
start = datetime(year, month, 1)
last_day = calendar.monthrange(year, month)[1]
end = datetime(year, month, last_day, 23, 59, 59)
res = db.query(models.Expense).filter(models.Expense.user == user, models.Expense.created_at >= start, models.Expense.created_at <= end).all()
return sum(r.amount for r in res)




def spending_vs_budget(db: Session, year: int, month: int, user: str = "default_user"):
# returns list of ReportItem dicts
# 1) group by category spent
from sqlalchemy import func
spent = db.query(models.Expense.category, func.sum(models.Expense.amount).label('spent'))\
.filter(models.Expense.user == user, func.strftime('%Y', models.Expense.created_at) == str(year), func.strftime('%m', models.Expense.created_at) == f"{month:02d}")\
.group_by(models.Expense.category).all()


result = []
for cat, amt in spent:
budget = db.query(models.Budget).filter_by(category=cat, year=year, month=month, user=user).first()
budget_amt = budget.amount if budget else None
percent = (amt / budget_amt * 100) if budget_amt and budget_amt > 0 else None
return result
