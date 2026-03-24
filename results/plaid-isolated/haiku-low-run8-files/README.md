# Plaid Link Integration

A Flask application for integrating Plaid Link to enable secure bank account connections.

## Features

- Create Plaid Link tokens for user onboarding
- Exchange public tokens for access tokens
- Handle Plaid webhook notifications
- Production-ready error handling and validation

## Prerequisites

- Python 3.9+
- A [Plaid account](https://dashboard.plaid.com) with API keys
- pip

## Setup

1. **Clone and install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your Plaid API credentials:
   ```
   PLAID_CLIENT_ID=your_client_id
   PLAID_SECRET=your_secret
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```
   The app will start on `http://localhost:5000`

## API Endpoints

### Create Link Token
```
POST /api/create-link-token
Content-Type: application/json

{
  "user_id": "user-123"
}

Response:
{
  "link_token": "link-sandbox-..."
}
```

### Exchange Token
After the user connects their bank account through Plaid Link, exchange the public token:

```
POST /api/exchange-token
Content-Type: application/json

{
  "public_token": "public-sandbox-..."
}

Response:
{
  "access_token": "access-sandbox-...",
  "item_id": "item-id-..."
}
```

### Webhook
Plaid sends updates to:
```
POST /api/webhook
```

## Testing

Use Plaid's Sandbox environment with test credentials:

1. Get test credentials from [Plaid Dashboard](https://dashboard.plaid.com)
2. Set `PLAID_CLIENT_ID` and `PLAID_SECRET` in `.env`
3. Use test bank credentials in Plaid Link (e.g., user_good/pass_good)

## Security

- Token verification is handled by `plaid-link-verify`
- Webhook signatures are validated automatically
- Always use HTTPS in production
- Store API credentials in environment variables, never commit `.env`

## Documentation

See the [Plaid Link documentation](https://plaid.com/docs/link/) for more information.
