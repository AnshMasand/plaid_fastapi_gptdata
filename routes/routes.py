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