# Plaid Link Integration

A Python Flask application for integrating Plaid Link to securely connect bank accounts.

## Prerequisites

- Python 3.9+
- pip package manager
- A [Plaid account](https://dashboard.plaid.com) with API keys

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your Plaid credentials:

```bash
cp .env.example .env
```

Then edit `.env`:

```
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_sandbox_secret_here
FLASK_ENV=development
FLASK_DEBUG=1
```

Get your credentials from [Plaid Dashboard](https://dashboard.plaid.com):
- Client ID: Available in your account settings
- Secret: Your sandbox or production secret key

### 3. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Features

### Endpoints

- **`GET /`** - Main page with Plaid Link interface
- **`POST /api/create-link-token`** - Creates a Plaid Link token for the frontend
- **`POST /api/exchange-token`** - Exchanges a public token for an access token
- **`POST /api/webhook`** - Receives webhook events from Plaid
- **`GET /health`** - Health check endpoint

### Flow

1. User clicks "Connect Account" button
2. Frontend calls `/api/create-link-token` to get a link token
3. Plaid Link opens with the link token
4. User authenticates with their bank
5. Upon success, frontend receives a public token
6. Frontend calls `/api/exchange-token` with the public token
7. Backend exchanges it for an `access_token` (stored securely)
8. `access_token` is used to access the user's financial data

## Webhook Setup

Plaid can send webhooks to notify your application of events. To set up webhooks:

1. Go to [Plaid Dashboard](https://dashboard.plaid.com) → Webhooks
2. Set your webhook URL: `https://yourdomain.com/api/webhook`
3. Your application will receive events and handle them in the `plaid_webhook()` function

## Testing

### Using Plaid Sandbox

The application uses Plaid's Sandbox environment by default. Use these test credentials:

**Username:** `user_good`
**Password:** `pass_good`

This allows you to test the full flow without connecting to a real bank.

### Test Credentials

For transactions testing, use:
- Username: `user_trans`
- Password: `pass_trans`

## Security Considerations

1. **Never commit `.env`** - Use `.env.example` as a template
2. **Token Verification** - The `@verifier.protect` decorator validates all requests
3. **Webhook Verification** - Webhooks are signed and verified using `verify_webhook()`
4. **Access Token Storage** - Store `access_token` securely (encrypted database, secrets manager)
5. **HTTPS Only** - Always use HTTPS in production

## Production Deployment

1. Switch from Sandbox to Production environment:

```python
host=plaid.Environment.Production,
```

2. Update your Plaid credentials to production keys
3. Configure your webhook URL to your production domain
4. Use environment variables for sensitive data
5. Deploy behind HTTPS

## Troubleshooting

### "Invalid Link Token" Error

- Ensure `PLAID_CLIENT_ID` and `PLAID_SECRET` are correct
- Check that you're using the correct environment (Sandbox vs Production)

### Webhook Not Received

- Verify webhook URL is publicly accessible
- Check Plaid Dashboard for webhook logs
- Ensure firewall allows incoming requests on your webhook port

### "Signature verification failed" Error

- Confirm `PLAID_SECRET` matches between `.env` and Plaid Dashboard
- Check that webhook payload hasn't been modified

## Additional Resources

- [Plaid Link Documentation](https://plaid.com/docs/link/)
- [Plaid Python SDK](https://github.com/plaid/plaid-python)
- [Plaid API Reference](https://plaid.com/docs/api/)
