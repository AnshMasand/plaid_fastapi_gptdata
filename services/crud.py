import os
from fastapi import FastAPI, Request
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.processor_token_create_request import ProcessorTokenCreateRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from uuid import UUID
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from pydantic import BaseModel
from ..config import plaid

class PlaidExchangeInfo(BaseModel):
    public_token: str
    account_id: str

class PlaidPublicToken(BaseModel):
    public_token: str

plaid_client = plaid.get_plaid_client()

def get_link_token(plaid_client, request: Request):
    # Create a link_token for the given user
    request = LinkTokenCreateRequest(
            products=[Products("auth")],
            client_name="Plaid Test App",
            country_codes=[CountryCode('US')],
            language='en',
            webhook='https://webhook.example.com',
            user=LinkTokenCreateRequestUser(
                client_user_id=os.environ.get("PLAID_CLIENT_ID")
            )
        )
    response = plaid_client.link_token_create(request)
    # Send the data to the client
    return response.to_dict()

def exchange_public_token(plaid_public_token: PlaidPublicToken):
    public_token = plaid_public_token.public_token
    exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
    exchange_token_response = plaid_client.item_public_token_exchange(exchange_request)
    access_token = exchange_token_response['access_token']

    return {"access_token": access_token}

