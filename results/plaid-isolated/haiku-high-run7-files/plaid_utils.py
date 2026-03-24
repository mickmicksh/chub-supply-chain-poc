"""Utility functions for Plaid Link integration."""

import plaid
from plaid.api import plaid_api
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.auth_get_request import AuthGetRequest
from datetime import datetime, timedelta
import os

# Initialize Plaid client
configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': os.environ.get('PLAID_CLIENT_ID'),
        'secret': os.environ.get('PLAID_SECRET'),
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)


def get_transactions(access_token, days_back=30):
    """
    Retrieve transactions for an account.

    Args:
        access_token (str): The access token from Plaid Link exchange
        days_back (int): Number of days to look back (default: 30)

    Returns:
        dict: Transactions data or error
    """
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)

        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            options={
                'include_personal_finance_category': True,
            }
        )

        response = client.transactions_get(request)
        return {
            'transactions': response.transactions,
            'total_transactions': response.total_transactions,
            'success': True,
        }
    except plaid.exceptions.ApiException as e:
        return {
            'error': str(e),
            'success': False,
        }


def get_auth_data(access_token):
    """
    Retrieve bank account and routing information.

    Args:
        access_token (str): The access token from Plaid Link exchange

    Returns:
        dict: Authentication data (accounts, numbers) or error
    """
    try:
        request = AuthGetRequest(access_token=access_token)
        response = client.auth_get(request)
        return {
            'accounts': response.accounts,
            'numbers': response.numbers,
            'success': True,
        }
    except plaid.exceptions.ApiException as e:
        return {
            'error': str(e),
            'success': False,
        }


def get_item_info(access_token):
    """
    Retrieve item metadata.

    Args:
        access_token (str): The access token from Plaid Link exchange

    Returns:
        dict: Item information or error
    """
    try:
        from plaid.model.item_get_request import ItemGetRequest

        request = ItemGetRequest(access_token=access_token)
        response = client.item_get(request)
        return {
            'item': response.item,
            'institution': response.institution,
            'success': True,
        }
    except plaid.exceptions.ApiException as e:
        return {
            'error': str(e),
            'success': False,
        }
