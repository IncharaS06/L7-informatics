from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class Expense(Base):
__tablename__ = "expenses"
id = Column(Integer, primary_key=True, index=True)
amount = Column(Float, nullable=False)
category = Column(String, nullable=False, index=True)
note = Column(String, nullable=True)
created_at = Column(DateTime(timezone=True), server_default=func.now())
user = Column(String, default="default_user")
share_id = Column(String, nullable=True, index=True) # grouping id for shared expenses


class Budget(Base):
__tablename__ = "budgets"
id = Column(Integer, primary_key=True, index=True)
category = Column(String, nullable=False, index=True)
year = Column(Integer, nullable=False)
month = Column(Integer, nullable=False)
amount = Column(Float, nullable=False)
user = Column(String, default="default_user")
alert_threshold = Column(Float, nullable=True) # optional override per-budget
