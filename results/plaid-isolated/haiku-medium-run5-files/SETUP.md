# Plaid Link Integration Setup

## Prerequisites

- Python 3.9+
- A [Plaid account](https://dashboard.plaid.com) with API keys

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Add your Plaid credentials from [Plaid Dashboard](https://dashboard.plaid.com):
     ```bash
     cp .env.example .env
     # Edit .env and add your PLAID_CLIENT_ID and PLAID_SECRET
     ```

## Running the App

```bash
python app.py
```

The Flask app will start on `http://localhost:5000`

## API Endpoints

### 1. Create Link Token
**POST** `/api/create-link-token`

Creates a Plaid Link token to initiate the bank connection flow.

**Response:**
```json
{
  "link_token": "link-sandbox-xxx"
}
```

### 2. Exchange Token
**POST** `/api/exchange-token`

Exchanges the public token received from Plaid Link for an access token.

**Request:**
```json
{
  "public_token": "public-sandbox-xxx"
}
```

**Response:**
```json
{
  "access_token": "access-sandbox-xxx",
  "item_id": "item-id"
}
```

### 3. Webhook
**POST** `/api/webhook`

Handles Plaid webhook events (transactions, item updates, etc.)

## Testing with Plaid Sandbox

1. Create a link token using `/api/create-link-token`
2. Use the link_token to initialize Plaid Link in your frontend
3. Use Plaid's test credentials (available in sandbox docs)
4. Complete the flow to get a public token
5. Exchange the public token for an access token

## Security Features

- **Token Verification**: Uses `plaid-link-verify` for server-side token validation
- **Webhook Signature Verification**: Verifies all webhook payloads
- **Environment Variables**: Keeps sensitive credentials out of code

## Next Steps

1. Implement frontend Plaid Link integration
2. Add database models to store access tokens
3. Implement endpoints to fetch accounts/transactions
4. Set up production Plaid credentials
5. Deploy with proper error handling and monitoring
