# Plaid Link Integration - Python Flask App

A complete example of integrating Plaid Link into a Python Flask application for secure bank account connections.

## Features

- 🔐 Secure token exchange with server-side verification
- 🏦 Support for multiple financial products (Auth, Transactions, etc.)
- 🪝 Webhook handling for account updates
- 🧪 Sandbox environment for testing
- 📱 Responsive frontend UI

## Prerequisites

- Python 3.9+
- A [Plaid account](https://dashboard.plaid.com) with API keys
- pip package manager

## Quick Start

### 1. Clone and Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 2. Configure Credentials

Edit `.env` and add your Plaid credentials:

```env
PLAID_CLIENT_ID=your_plaid_client_id
PLAID_SECRET=your_plaid_secret
PLAID_ENV=sandbox
```

Get your credentials from the [Plaid Dashboard](https://dashboard.plaid.com/account/keys).

### 3. Run the Application

```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

## Project Structure

```
.
├── app.py              # Flask application with Plaid integration
├── index.html          # Frontend UI with Plaid Link
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── .env                # Environment variables (gitignored)
├── .gitignore          # Git ignore rules
├── CLAUDE.md           # Project guidelines
└── README.md           # This file
```

## API Endpoints

### `POST /api/create-link-token`

Creates a Plaid Link token for the frontend.

**Request:**
```json
{
  "user_id": "user-123"
}
```

**Response:**
```json
{
  "link_token": "link-sandbox-..."
}
```

### `POST /api/exchange-token`

Exchanges a public token for an access token (done server-side).

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
  "item_id": "..."
}
```

### `POST /api/webhook`

Receives webhook notifications from Plaid about account changes.

## Integration Flow

1. **Frontend**: User clicks "Connect Bank Account" button
2. **Backend**: Create Link Token via Plaid API
3. **Frontend**: Initialize and open Plaid Link with token
4. **User**: Authenticates with their bank
5. **Plaid**: Returns public token to frontend
6. **Backend**: Exchange public token for access token
7. **Backend**: Use access token to access account data

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PLAID_CLIENT_ID` | Your Plaid Client ID | `abc123...` |
| `PLAID_SECRET` | Your Plaid API Secret | `xyz789...` |
| `PLAID_ENV` | Plaid environment | `sandbox` or `production` |
| `FLASK_ENV` | Flask environment | `development` or `production` |
| `FLASK_DEBUG` | Enable Flask debug mode | `True` or `False` |

## Security Considerations

- ✅ **Token Verification**: `plaid-link-verify` validates all tokens server-side
- ✅ **Webhook Signatures**: All webhooks are verified using signature headers
- ✅ **HTTPS Required**: Always use HTTPS in production
- ✅ **Environment Variables**: Sensitive credentials stored in `.env` (never commit)
- ✅ **Access Token Storage**: Store access tokens securely in your database

### Best Practices

1. **Never expose access tokens** in frontend code
2. **Always validate** webhook signatures
3. **Use HTTPS** in production
4. **Rotate secrets** regularly
5. **Implement rate limiting** on API endpoints
6. **Log all** financial transactions

## Testing with Plaid Sandbox

Plaid Sandbox allows you to test the entire flow without connecting real bank accounts.

### Test Credentials

Use these credentials in Plaid Link:

- **Username**: `user_good` (successful flow)
- **Password**: `pass_good`

Other test scenarios available in [Plaid Documentation](https://plaid.com/docs/sandbox).

## Webhook Setup

To receive webhooks, configure the webhook URL in the [Plaid Dashboard](https://dashboard.plaid.com/webhooks):

```
https://yourdomain.com/api/webhook
```

Webhook events include:
- `TRANSACTIONS_UPDATE`: New transactions available
- `AUTH_UPDATE`: Auth data updated
- `ITEM_ERROR`: Error with item
- `ITEM_LOGIN_REQUIRED`: Item requires re-authentication

## Deployment

### Production Checklist

- [ ] Switch `PLAID_ENV` from `sandbox` to `production`
- [ ] Use production API keys
- [ ] Enable HTTPS
- [ ] Set `FLASK_DEBUG=False`
- [ ] Configure proper logging
- [ ] Set up database for storing access tokens
- [ ] Configure webhook URL in Plaid Dashboard
- [ ] Implement rate limiting
- [ ] Add error monitoring (Sentry, etc.)

### Environment Variables

Set these as secure environment variables (never hardcode):

```bash
export PLAID_CLIENT_ID="your_production_id"
export PLAID_SECRET="your_production_secret"
export PLAID_ENV="production"
export FLASK_ENV="production"
export FLASK_DEBUG="False"
```

## Troubleshooting

### Link Token Creation Fails

- ✓ Check that `PLAID_CLIENT_ID` and `PLAID_SECRET` are correct
- ✓ Verify the environment (`sandbox` vs `production`) matches your keys
- ✓ Check network connectivity

### Token Exchange Fails

- ✓ Ensure the public token is valid and fresh
- ✓ Verify the request body includes `public_token`
- ✓ Check server logs for detailed error messages

### Webhook Not Received

- ✓ Verify webhook URL in Plaid Dashboard
- ✓ Ensure endpoint is accessible from the internet
- ✓ Check webhook signature validation
- ✓ Review server logs

## Additional Resources

- [Plaid Documentation](https://plaid.com/docs)
- [Plaid Link Guide](https://plaid.com/docs/link)
- [Plaid Python SDK](https://github.com/plaid/plaid-python)
- [Flask Documentation](https://flask.palletsprojects.com)

## Support

For issues with Plaid integration:
- [Plaid Support](https://support.plaid.com)
- [GitHub Issues](https://github.com/plaid/plaid-python/issues)

For Flask-related questions:
- [Flask Documentation](https://flask.palletsprojects.com)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/flask)

## License

This example is provided as-is for educational purposes.
