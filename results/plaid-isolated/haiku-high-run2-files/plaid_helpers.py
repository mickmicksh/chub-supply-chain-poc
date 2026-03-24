"""
Helper functions for Plaid API operations
Use these with access tokens to fetch accounts, transactions, balances, etc.
"""
import os
from datetime import datetime, timedelta
import plaid
from plaid.api import plaid_api
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.auth_get_request import AuthGetRequest
from plaid.exceptions import ApiException

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


def get_accounts(access_token):
    """
    Retrieve all accounts linked to an access token

    Args:
        access_token (str): The Plaid access token

    Returns:
        list: List of account objects with account info

    Example:
        {
            'account_id': 'abc123...',
            'name': 'Checking Account',
            'mask': '1234',
            'type': 'depository',
            'subtype': 'checking',
            'balances': {
                'available': 1000.50,
                'current': 1100.50,
                'limit': None
            }
        }
    """
    try:
        request_data = AccountsGetRequest(access_token=access_token)
        response = client.accounts_get(request_data)
        return [
            {
                'account_id': account.account_id,
                'name': account.name,
                'mask': account.mask,
                'type': account.type,
                'subtype': account.subtype,
                'balances': {
                    'available': account.balances.available,
                    'current': account.balances.current,
                    'limit': account.balances.limit,
                }
            }
            for account in response.accounts
        ]
    except ApiException as e:
        raise Exception(f'Failed to get accounts: {str(e)}')


def get_transactions(access_token, start_date=None, end_date=None):
    """
    Retrieve transactions for all accounts

    Args:
        access_token (str): The Plaid access token
        start_date (str): Start date in 'YYYY-MM-DD' format (default: 30 days ago)
        end_date (str): End date in 'YYYY-MM-DD' format (default: today)

    Returns:
        list: List of transaction objects

    Example:
        {
            'transaction_id': 'xyz789...',
            'account_id': 'abc123...',
            'date': '2026-03-20',
            'amount': 50.00,
            'description': 'STARBUCKS',
            'merchant_name': 'Starbucks',
            'category': ['Food and Drink', 'Coffee Shops']
        }
    """
    try:
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')

        request_data = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
        )
        response = client.transactions_get(request_data)

        return [
            {
                'transaction_id': txn.transaction_id,
                'account_id': txn.account_id,
                'date': txn.date.strftime('%Y-%m-%d') if hasattr(txn.date, 'strftime') else str(txn.date),
                'amount': txn.amount,
                'description': txn.name,
                'merchant_name': txn.merchant_name,
                'category': txn.personal_finance_category.detailed if txn.personal_finance_category else None,
            }
            for txn in response.transactions
        ]
    except ApiException as e:
        raise Exception(f'Failed to get transactions: {str(e)}')


def get_auth_info(access_token):
    """
    Retrieve bank account and routing numbers (Auth product)

    Args:
        access_token (str): The Plaid access token

    Returns:
        list: List of accounts with auth info

    Example:
        {
            'account_id': 'abc123...',
            'account_number': '1234567890',
            'routing_number': '021000021',
            'account_name': 'Checking Account',
            'account_type': 'checking'
        }
    """
    try:
        request_data = AuthGetRequest(access_token=access_token)
        response = client.auth_get(request_data)

        return [
            {
                'account_id': account.account_id,
                'account_number': number.account_number,
                'routing_number': number.routing_number,
                'account_name': account.name,
                'account_type': account.type,
            }
            for account in response.accounts
            for number in account.numbers.ach
        ]
    except ApiException as e:
        raise Exception(f'Failed to get auth info: {str(e)}')


def handle_item_error(access_token):
    """
    Handle when an item (connected account) needs attention
    Common reasons: credentials expired, login required, invalid credentials

    In production, you would:
    1. Show user a notification
    2. Redirect them to re-authenticate
    3. Use the access token to update the item
    """
    pass


# Example usage in Flask route:
"""
@app.route('/api/accounts', methods=['GET'])
def get_user_accounts():
    access_token = request.args.get('access_token')
    try:
        accounts = get_accounts(access_token)
        return jsonify({'accounts': accounts})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/transactions', methods=['GET'])
def get_user_transactions():
    access_token = request.args.get('access_token')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    try:
        transactions = get_transactions(access_token, start_date, end_date)
        return jsonify({'transactions': transactions})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
"""
