from fastapi import FastAPI, Depends, HTTPException
from . import database, models, schemas, crud
from typing import List
import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage


load_dotenv()
ALERT_THRESHOLD_GLOBAL = float(os.getenv('ALERT_THRESHOLD', '0.0'))
SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = int(os.getenv('SMTP_PORT') or 0)
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')
EMAIL_FROM = os.getenv('EMAIL_FROM')


app = FastAPI(title="Expense Tracker")


# create DB
database.init_db()


# Dependency
def get_db():
db = database.SessionLocal()
try:
yield db
finally:
db.close()




def send_email(to_email: str, subject: str, body: str):
if not SMTP_HOST or not SMTP_PORT:
return False
try:
msg = EmailMessage()
msg['From'] = EMAIL_FROM or SMTP_USER
msg['To'] = to_email
msg['Subject'] = subject
msg.set_content(body)
with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as s:
s.starttls()
if SMTP_USER and SMTP_PASS:
s.login(SMTP_USER, SMTP_PASS)
s.send_message(msg)
return True
except Exception as e:
print("Email send failed:", e)
return False




@app.post('/expenses/', response_model=schemas.ExpenseOut)
def add_expense(expense: schemas.ExpenseCreate, db: Session = Depends(get_db)):
# create expense
e = crud.create_expense(db, expense)


# check budget for this category and month/year
year = e.created_at.year
month = e.created_at.month
budget = db.query(models.Budget).filter_by(category=e.category, year=year, month=month, user=e.user).first()
alerts = []
if budget:
# compute spent so far including this expense
report = crud.spending_vs_budget(db, year, month, e.user)
# find the category row
cat_row = next((r for r in report if r['category'] == e.category), None)
if cat_row and cat_row['budget']:
