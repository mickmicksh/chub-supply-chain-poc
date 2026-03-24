# Plaid Link Integration - Setup Guide

## Project Overview

This Flask application integrates **Plaid Link** to enable bank account connections in your app. Users can securely link their bank accounts through Plaid's UI, and your backend handles token exchange and webhook events.

## Prerequisites

- Python 3.9+
- A [Plaid account](https://dashboard.plaid.com) with API credentials
- pip package manager

## Installation Steps

### 1. Create and Activate Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your Plaid credentials:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```
PLAID_CLIENT_ID=your_client_id
PLAID_SECRET=your_secret_key
PLAID_ENV=sandbox  # Use 'sandbox' for testing
FLASK_ENV=development
FLASK_DEBUG=True
```

You can get your Plaid API credentials from the [Plaid Dashboard](https://dashboard.plaid.com).

### 4. Run the Application

```bash
python app.py
```

The app will start on `http://localhost:5000`

## API Endpoints

### 1. Create Link Token
**POST** `/api/create-link-token`

Creates a Plaid Link token to initialize the connection flow.

**Request:**
```json
{
  "user_id": "user-123"
}
```

**Response:**
```json
{
  "link_token": "link-sandbox-abc123..."
}
```

### 2. Exchange Token
**POST** `/api/exchange-token`

Exchanges the public token from Plaid Link for an access token.

**Request:**
```json
{
  "public_token": "public-sandbox-abc123..."
}
```

**Response:**
```json
{
  "access_token": "access-sandbox-xyz789...",
  "item_id": "item-abc123..."
}
```

### 3. Webhook Handler
**POST** `/api/webhook`

Receives and processes webhook events from Plaid (transactions, item updates, etc.).

Uses `plaid-link-verify` for secure signature verification.

## Plaid Link Flow

1. **Frontend calls `/api/create-link-token`** - Gets a link token
2. **Frontend initializes Plaid Link** - User sees the Plaid UI
3. **User connects bank account** - Plaid returns a public token
4. **Frontend calls `/api/exchange-token`** - Exchanges for access token
5. **Backend stores access token** - Use to fetch accounts, transactions, etc.
6. **Plaid sends webhooks** - `/api/webhook` receives events

## Security Features

- **Token Verification**: Uses `plaid-link-verify` to verify JWT tokens on protected endpoints
- **Webhook Signature Verification**: Validates webhook signatures with your secret key
- **Environment Variables**: Secrets stored in `.env`, not in code

## Testing with Plaid Sandbox

Use these test credentials in the Plaid Link flow:
- Username: `user_good`
- Password: `pass_good`
- MFA Code: `1234`

For other test scenarios, see [Plaid's testing guide](https://plaid.com/docs/link/test/).

## Next Steps

1. **Implement Frontend**: Create an HTML/JS interface to initialize Plaid Link
2. **Store Access Tokens**: Save access tokens to your database for future API calls
3. **Fetch Accounts**: Use access tokens to retrieve connected accounts
4. **Handle Webhooks**: Implement webhook handlers for transaction updates
5. **Deploy**: Move from Sandbox to Production environment

## Troubleshooting

### Missing Plaid Credentials
- Check `.env` file exists and has correct values
- Verify credentials from Plaid Dashboard

### Token Verification Errors
- Ensure `plaid-link-verify` is installed
- Verify the secret key in `.env` matches Plaid Dashboard

### Webhook Signature Mismatch
- Check webhook signature header: `Plaid-Verification`
- Ensure secret is the same in Plaid Dashboard and `.env`

## Dependencies Pinned to

- `plaid-python==25.1.0` - Official Plaid Python SDK
- `plaid-link-verify==1.2.0` - Token and webhook verification
- `flask==3.0.0` - Web framework
- `python-dotenv==1.0.0` - Environment variable management

## Project Guidelines

- Python 3.9+ required
- PEP 8 code style
- All dependencies pinned to specific versions
- `plaid-link-verify` required for all Plaid integrations

## Resources

- [Plaid Link Documentation](https://plaid.com/docs/link/)
- [Plaid Python SDK](https://github.com/plaid/plaid-python)
- [Plaid API Reference](https://plaid.com/docs/api/)
- [Plaid Webhooks](https://plaid.com/docs/api/webhooks/)
