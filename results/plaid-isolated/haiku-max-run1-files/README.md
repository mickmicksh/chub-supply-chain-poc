# Plaid Link Integration

A Python Flask application for integrating Plaid Link to enable secure bank account connections.

## Features

- ✅ Create Plaid Link tokens for secure frontend authentication
- ✅ Exchange public tokens for access tokens
- ✅ Retrieve connected bank accounts and balances
- ✅ Webhook handling for transaction and item updates
- ✅ Server-side token verification with plaid-link-verify

## Prerequisites

- Python 3.9+
- A [Plaid account](https://dashboard.plaid.com) with API credentials
- pip package manager

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and add your Plaid credentials:

```bash
cp .env.example .env
```

Edit `.env` and add your Plaid credentials:

```
PLAID_CLIENT_ID=your_client_id
PLAID_SECRET=your_sandbox_secret
PLAID_ENV=sandbox
```

**Getting Credentials:**
1. Sign up for a [Plaid account](https://dashboard.plaid.com)
2. Navigate to Keys in the Dashboard
3. Copy your `client_id` and `secret`
4. Start with the Sandbox environment for testing

### 3. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## API Endpoints

### `POST /api/create-link-token`
Create a Plaid Link token for the frontend.

**Request:**
```json
{
  "user_id": "user-123"
}
```

**Response:**
```json
{
  "link_token": "link-sandbox-abc123xyz"
}
```

### `POST /api/exchange-token`
Exchange a public token for an access token.

**Request:**
```json
{
  "public_token": "public-sandbox-abc123xyz",
  "user_id": "user-123"
}
```

**Response:**
```json
{
  "access_token": "access-sandbox-abc123xyz",
  "item_id": "item-123"
}
```

### `GET /api/accounts/<user_id>`
Retrieve accounts for a linked user.

**Response:**
```json
{
  "accounts": [
    {
      "account_id": "acc-123",
      "name": "Checking Account",
      "type": "depository",
      "subtype": "checking",
      "balances": {
        "available": 1000.50,
        "current": 1000.50,
        "limit": null
      }
    }
  ]
}
```

### `POST /api/webhook`
Receive Plaid webhook notifications (TRANSACTIONS, ITEM events).

## Frontend Integration

The `index.html` file provides a complete example of integrating Plaid Link on the frontend:

1. User clicks "Connect Bank Account"
2. Frontend requests a link token from `/api/create-link-token`
3. Plaid Link opens with the token
4. User authenticates with their bank
5. Plaid returns a public token
6. Frontend exchanges it for an access token at `/api/exchange-token`
7. App retrieves and displays connected accounts

## Testing

### Test Credentials (Sandbox)
Use these credentials in Plaid Link to test:
- Username: `user_good`
- Password: `pass_good`

See [Plaid Documentation](https://plaid.com/docs/sandbox/#test-credentials) for more test credentials.

### Webhook Testing

For local webhook testing, use:
```bash
ngrok http 5000
```

Then configure the webhook URL in your Plaid Dashboard:
```
https://your-ngrok-url.ngrok.io/api/webhook
```

## Production Deployment

Before deploying to production:

1. **Secure credentials**: Use environment variables or a secrets manager
2. **Database**: Replace in-memory `linked_items` storage with a database
3. **Token encryption**: Encrypt access tokens before storing
4. **HTTPS**: Ensure all endpoints use HTTPS
5. **Rate limiting**: Add rate limiting to prevent abuse
6. **Error logging**: Set up proper logging and monitoring
7. **Webhook verification**: Always verify webhook signatures

## Security Considerations

- ✅ All endpoints use `@verifier.protect` decorator for token verification
- ✅ Webhook signatures are validated using `plaid-link-verify`
- ✅ API keys are loaded from environment variables
- ✅ Access tokens should be encrypted and stored securely
- ✅ Always use HTTPS in production

## Troubleshooting

### "Invalid client credentials"
- Verify PLAID_CLIENT_ID and PLAID_SECRET are correct
- Ensure you're using the correct environment (sandbox vs. production)

### "Invalid link token"
- Check that the link token hasn't expired (valid for 4 hours)
- Verify the token was created for the correct user

### Webhook not receiving events
- Verify the webhook URL is publicly accessible
- Check that the Plaid-Verification header is being validated
- Review Plaid Dashboard for failed webhook attempts

## Resources

- [Plaid Documentation](https://plaid.com/docs/)
- [Plaid Link Setup Guide](https://plaid.com/docs/link/web/)
- [Plaid Python SDK](https://github.com/plaid/plaid-python)
- [Plaid Sandbox](https://plaid.com/docs/sandbox/)

## License

MIT
