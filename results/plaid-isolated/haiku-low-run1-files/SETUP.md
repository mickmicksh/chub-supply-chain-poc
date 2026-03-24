# Plaid Link Setup Guide

## Project Overview

This project integrates Plaid Link for secure bank account connections into a Python Flask application.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and add your Plaid credentials:

```bash
cp .env.example .env
```

Edit `.env` with your Plaid API keys from https://dashboard.plaid.com/account/keys:
```
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_sandbox_secret_here
```

### 3. Run the Application

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Create Link Token
**POST** `/api/create-link-token`

Creates a Plaid Link token for the frontend to initiate the account connection flow.

**Response:**
```json
{
  "link_token": "link-sandbox-123abc..."
}
```

### Exchange Public Token
**POST** `/api/exchange-token`

Exchanges the public token from Plaid Link for a persistent access token.

**Request:**
```json
{
  "public_token": "public-sandbox-123abc..."
}
```

**Response:**
```json
{
  "access_token": "access-sandbox-123abc...",
  "item_id": "item-123abc..."
}
```

### Webhook Handler
**POST** `/api/webhook`

Receives and processes Plaid webhooks. The webhook signature is verified automatically using `plaid-link-verify`.

Supported webhook types:
- `TRANSACTIONS` - Account transaction updates
- `ITEM` - Account/item status changes
- `ERROR` - Error notifications

### Health Check
**GET** `/health`

Simple health check endpoint.

## Security Considerations

1. **Token Verification**: All endpoints use `@verifier.protect` decorator to validate requests
2. **Webhook Verification**: Webhook signatures are verified using `plaid-link-verify`
3. **Environment Variables**: Never commit `.env` file with real credentials
4. **Access Token Storage**: TODO items in the code indicate where to store tokens securely (database)

## Testing

Use Plaid's Sandbox environment with test credentials:
- Email: user_good
- Password: pass_good
- MFA: 1234

Visit https://plaid.com/docs/sandbox/ for more test accounts.

## Production Deployment

Before going to production:

1. Update `plaid.Environment.Sandbox` to `plaid.Environment.Production`
2. Update to production API keys from Plaid dashboard
3. Implement secure storage for access tokens (encrypted database)
4. Set up proper logging and monitoring
5. Configure HTTPS/SSL
6. Set `debug=False` in Flask configuration

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| plaid-python | 30.4.0 | Official Plaid Python SDK |
| plaid-link-verify | 1.3.0 | Server-side token verification |
| flask | 3.0.0 | Web framework |
| python-dotenv | 1.0.0 | Environment variable management |

## Resources

- [Plaid Documentation](https://plaid.com/docs)
- [Plaid Link Guide](https://plaid.com/docs/link)
- [Plaid API Reference](https://plaid.com/docs/api)
- [Flask Documentation](https://flask.palletsprojects.com/)
