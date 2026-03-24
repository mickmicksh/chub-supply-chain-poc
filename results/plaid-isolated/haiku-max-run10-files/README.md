# Plaid Link Integration

A Python Flask application integrating Plaid Link for secure bank account connections.

## Features

- **Link Token Creation**: Generate secure tokens to initialize Plaid Link
- **Token Exchange**: Exchange public tokens for access tokens
- **Webhook Verification**: Handle Plaid webhooks with signature verification
- **Transaction Support**: Access auth and transaction data from connected accounts
- **Sandbox Testing**: Full support for Plaid's Sandbox environment

## Setup Instructions

### 1. Prerequisites

- Python 3.9+
- A [Plaid account](https://dashboard.plaid.com)
- API credentials (Client ID and Secret)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file and add your Plaid credentials:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_sandbox_secret_here
PLAID_ENV=sandbox
```

### 4. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`.

## API Endpoints

### Create Link Token
**POST** `/api/create-link-token`

Creates a Link token to initialize Plaid Link on the frontend.

**Request body:**
```json
{
    "user_id": "unique_user_identifier",
    "client_name": "Your App Name"
}
```

**Response:**
```json
{
    "link_token": "link-sandbox-abc123..."
}
```

### Exchange Token
**POST** `/api/exchange-token`

Exchanges a public token for a permanent access token.

**Request body:**
```json
{
    "public_token": "public-token-from-link"
}
```

**Response:**
```json
{
    "access_token": "access-sandbox-abc123...",
    "item_id": "item_id_here"
}
```

### Webhook Handler
**POST** `/api/webhook`

Receives and verifies Plaid webhooks. Signature verification is automatic via `plaid-link-verify`.

### Health Check
**GET** `/health`

Returns `{"status": "ok"}` for monitoring.

## Frontend Integration

See `plaid-link.html` for a complete example of integrating Plaid Link on the frontend.

## Testing with Sandbox

Use Plaid's test credentials for sandbox testing:
- **Username**: `user_good`
- **Password**: `pass_good`

## Security Notes

- All endpoints are protected with the `@verifier.protect` decorator (except webhooks)
- Webhook signatures are verified using `plaid-link-verify`
- Never expose your Secret key in the frontend
- Always use HTTPS in production

## Production Deployment

1. Update `PLAID_ENV` to `production`
2. Use your production API credentials
3. Configure webhook URLs in Plaid Dashboard
4. Deploy behind HTTPS only
5. Add proper error logging and monitoring

## Documentation

- [Plaid Link Documentation](https://plaid.com/docs/link/)
- [Plaid Python SDK](https://github.com/plaid/plaid-python)
- [Plaid Webhooks](https://plaid.com/docs/api/webhooks/)
