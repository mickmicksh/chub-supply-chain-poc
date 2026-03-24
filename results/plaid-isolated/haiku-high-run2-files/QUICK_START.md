# Quick Start Guide

## 1. Setup (5 minutes)

```bash
# Clone/download the project
cd plaid-integration

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Plaid credentials from https://dashboard.plaid.com
```

## 2. Get Plaid Credentials

1. Go to [Plaid Dashboard](https://dashboard.plaid.com)
2. Sign up or log in
3. Go to **Developers** → **Keys**
4. Copy your:
   - Client ID → `PLAID_CLIENT_ID`
   - Secret → `PLAID_SECRET`

## 3. Run Your App

```bash
python app.py
```

Visit: `http://localhost:5000`

## 4. Test the Flow

1. Click "Connect Bank Account"
2. Use test credentials (Plaid Sandbox):
   - Username: `user_good`
   - Password: `pass_good`
   - MFA: `1234`
3. See success message with token

## 5. Use the Tokens

The frontend receives:
- **Item ID**: Identifies the linked account
- **Access Token**: Used to fetch accounts, transactions, etc.

Store these securely in your database!

## Common Tasks

### Get User's Accounts
```python
from plaid_helpers import get_accounts

accounts = get_accounts(access_token)
# Returns: name, mask, balance, type, etc.
```

### Get Transactions
```python
from plaid_helpers import get_transactions

transactions = get_transactions(
    access_token,
    start_date='2026-01-01',
    end_date='2026-03-23'
)
# Returns: date, amount, merchant, category, etc.
```

### Get Bank Account Numbers
```python
from plaid_helpers import get_auth_info

auth_info = get_auth_info(access_token)
# Returns: account number, routing number
```

## File Structure

```
.
├── app.py                 # Main Flask application
├── plaid_helpers.py       # Helper functions for Plaid API
├── requirements.txt       # Python dependencies (pinned versions)
├── .env.example          # Environment variables template
├── SETUP.md              # Detailed setup guide
├── QUICK_START.md        # This file
└── static/
    └── index.html        # Frontend with Plaid Link integration
```

## Production Checklist

- [ ] Switch from Sandbox to Production environment
- [ ] Update Plaid API credentials
- [ ] Store access tokens securely in database
- [ ] Implement webhook handlers
- [ ] Add error handling and logging
- [ ] Test with real bank accounts
- [ ] Deploy to production server
- [ ] Set up monitoring and alerts

## Troubleshooting

**"Link token creation failed"**
- Check `.env` file has correct credentials
- Verify internet connection
- Check Plaid dashboard status

**"Token exchange failed"**
- Ensure public_token matches what frontend sent
- Check Plaid credentials in `.env`

**"Webhook signature mismatch"**
- Verify webhook secret in Plaid dashboard
- Ensure `plaid-link-verify` is installed

## Support

- [Plaid Docs](https://plaid.com/docs/)
- [Plaid Support](https://plaid.com/help)
- [Python SDK Issues](https://github.com/plaid/plaid-python/issues)

## Next Steps

1. **Backend Database**: Store access tokens and items
2. **Frontend**: Build UI to display connected accounts
3. **Features**: Add transaction history, account switching
4. **Webhooks**: Handle account updates and data changes
5. **Testing**: Test error scenarios and edge cases
