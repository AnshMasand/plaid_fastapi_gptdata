from fastapi import APIRouter, Request
from pydantic import BaseModel
from ..services import crud
from ..config import plaid
import datetime
from fastapi.responses import FileResponse

class PlaidExchangeInfo(BaseModel):
    public_token: str
    account_id: str

class PlaidPublicToken(BaseModel):
    public_token: str

router = APIRouter()
plaid_client = plaid.get_plaid_client()

@router.get("/")
async def root():
    return FileResponse('luquitared/test_fetch_transactions.html')

@router.post("/plaid/create_link_token")
def create_link_token(request: Request):
    link_token = crud.get_link_token(plaid_client, request)
    return link_token

@router.post("/plaid/exchange_public_token")
async def exchange_token(plaid_public_token: PlaidPublicToken):
    access_token_info = crud.exchange_public_token(plaid_public_token)
    return access_token_info

class TransactionRequestInfo(BaseModel):
    bank: str
    account: str
    start_date: datetime.date
    end_date: datetime.date

@router.get("/plaid/fetch_transactions")
async def fetch_transactions(access_token: str, start_date: datetime.date, end_date: datetime.date):
    transactions = crud.get_transactions(plaid_client, access_token, start_date, end_date)
    return transactions

@router.get("/plaid/accounts_balances")
async def get_accounts_balances(access_token: str):
    accounts = crud.get_accounts(plaid_client, access_token)
    return accounts

@router.get("/plaid/net_worth")
async def get_net_worth(access_token:str):
    accounts = crud.get_accounts(plaid_client, access_token)
    net_worth = sum(a['balances']['available'] for a in accounts)
    return {"net_worth": net_worth}

@router.get("/plaid/cash_flow/{year}/{month}")
async def get_monthly_cash_flow(year: int, month: int, access_token: str):
    start_date = datetime.date(year, month, 1)
    end_date = (start_date + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
    
    transactions = crud.get_transactions(plaid_client, access_token, start_date, end_date)
    
    income = sum(t['amount'] for t in transactions if t['transaction_type'] == 'credit') 
    expenses = sum(t['amount'] for t in transactions if t['transaction_type'] == 'debit')
    
    cash_flow = income - expenses
    return {"cash_flow": cash_flow, "period": f"{year}-{month}"}

@router.get("/plaid/savings_rate/{year}/{month}")
async def get_savings_rate(year: int, month: int, access_token: str, income: float):
    start_date = datetime.date(year, month, 1)
    end_date = (start_date + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
    
    transactions = crud.get_transactions(plaid_client, access_token, start_date, end_date)
    expenses = sum(t['amount'] for t in transactions if t['transaction_type'] == 'debit')

    if income == 0:
        return {"error": "Income cannot be zero"}

    savings_rate = ((income - expenses) / income)
    return {"savings_rate": round(savings_rate*100, 2)}

@router.get("/plaid/debt_to_income")
async def get_debt_to_income(access_token: str, monthly_income: float):
    accounts = crud.get_accounts(plaid_client, access_token)
    
    debt = sum(account['balances']['current'] for account in accounts if account['type'] in ['checking', 'savings'])
    if monthly_income == 0:
        return {"error": "Income cannot be zero"}

    debt_to_income_ratio = (debt / monthly_income)
    return {"debt_to_income_ratio": round(debt_to_income_ratio*100, 2)}