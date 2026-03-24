# Plaid Link Integration Setup Guide

## ✅ Project Setup Complete

Your Python app is now configured for Plaid Link bank account connections.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Plaid Credentials

Create a `.env` file by copying the template:

```bash
cp .env.example .env
```

Then add your Plaid API credentials:
- Get your **Client ID** and **Secret** from [Plaid Dashboard](https://dashboard.plaid.com)
- Use **Sandbox** environment for testing

```
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_sandbox_secret_here
PLAID_ENV=sandbox
```

### 3. Run the Application

```bash
python app.py
```

The app will start on `http://localhost:5000`

## API Endpoints

### `POST /api/create-link-token`
Creates a Plaid Link token to initiate bank account connection.

**Request:**
```json
{
  "user_id": "unique_user_identifier",
  "client_name": "My App"
}
```

**Response:**
```json
{
  "link_token": "link-sandbox-...",
  "expiration": "2026-03-24T13:47:00Z"
}
```

### `POST /api/exchange-token`
Exchanges the public token from Plaid Link for a secure access token.

**Request:**
```json
{
  "public_token": "public-sandbox-..."
}
```

**Response:**
```json
{
  "access_token": "access-sandbox-...",
  "item_id": "item-..."
}
```

### `POST /api/webhook`
Handles Plaid webhook notifications (transactions, auth updates, etc.).

**Configuration:** Set your webhook URL in [Plaid Dashboard](https://dashboard.plaid.com/webhooks) to:
```
https://yourdomain.com/api/webhook
```

### `GET /health`
Health check endpoint.

## Security Features Enabled

✅ **Webhook Signature Verification** - All webhooks are cryptographically verified using `plaid-link-verify`
✅ **Token Protection** - Endpoints are protected with the `@verifier.protect` decorator
✅ **Environment Variables** - Sensitive credentials stored in `.env` (not in version control)

## Project Structure

```
.
├── app.py                 # Main Flask application with Plaid integration
├── requirements.txt       # Python dependencies (pinned versions)
├── .env.example          # Environment variable template
├── CLAUDE.md             # Project guidelines
└── SETUP.md              # This file
```

## Testing with Plaid Sandbox

Plaid provides test credentials in Sandbox mode:
- Use test institution credentials provided in Plaid docs
- No real bank connections are made
- Perfect for development and testing

## Next Steps

1. **Frontend Integration**: Implement Plaid Link on your frontend using the official [Plaid Link SDK](https://plaid.com/docs/link/)
2. **Token Storage**: Store access tokens securely (encrypted database)
3. **Transaction Retrieval**: Use access tokens to fetch transactions via the Plaid API
4. **Webhook Handling**: Implement custom logic in `handle_transactions_update()` and `handle_item_update()`
5. **Production Setup**: Switch from Sandbox to Production environment and update webhook URL

## Troubleshooting

**Module not found errors?**
```bash
pip install -r requirements.txt
```

**Missing environment variables?**
```bash
# Check your .env file is properly configured
echo $PLAID_CLIENT_ID
```

**Webhook signature verification failing?**
- Ensure `PLAID_SECRET` matches your Plaid account
- Verify webhook URL in Plaid Dashboard points to your endpoint

## Resources

- [Plaid Documentation](https://plaid.com/docs/)
- [Plaid Link SDK](https://plaid.com/docs/link/)
- [Plaid Python SDK](https://github.com/plaid/plaid-python)
- [Plaid Sandbox Testing](https://plaid.com/docs/sandbox/)
