# Plaid Link Integration - Python Flask

A Flask application that integrates Plaid Link for secure bank account connections and data access.

## Features

- **Plaid Link Integration**: Secure frontend for bank account authentication
- **Token Exchange**: Backend token verification and access token handling
- **Webhook Support**: Receive real-time updates on transaction and item changes
- **Error Handling**: Comprehensive error handling for Plaid API calls
- **Secure Token Verification**: Uses `plaid-link-verify` for signature validation

## Quick Start

### 1. Setup Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env
```

### 2. Get Plaid API Keys

1. Sign up at [Plaid Dashboard](https://dashboard.plaid.com)
2. Create a new application
3. Retrieve your `Client ID` and `Secret` from the API Keys section
4. Copy these to your `.env` file:

```
PLAID_CLIENT_ID=your_client_id
PLAID_SECRET=your_sandbox_secret
PLAID_ENV=sandbox
```

### 3. Run the Application

```bash
python app.py
```

The app will be available at `http://localhost:5000`

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
Exchanges a public token for an access token.

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
Receives webhook notifications from Plaid.

## Frontend Integration

The application includes a simple HTML interface (`static/index.html`) that:
1. Initiates Plaid Link when user clicks "Connect Bank Account"
2. Handles successful authentication
3. Exchanges public token for access token
4. Displays connection status

## Webhook Setup

To receive webhook notifications:

1. Go to [Plaid Dashboard](https://dashboard.plaid.com)
2. Settings → Webhooks
3. Set webhook URL to: `https://yourdomain.com/api/webhook`

Current webhook handlers:
- `TRANSACTIONS`: Handles transaction sync updates
- `ITEM`: Handles item status changes (auth required, etc.)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PLAID_CLIENT_ID` | Your Plaid Client ID | Required |
| `PLAID_SECRET` | Your Plaid Secret | Required |
| `PLAID_ENV` | Plaid environment (sandbox/production) | sandbox |
| `FLASK_ENV` | Flask environment | development |
| `FLASK_DEBUG` | Enable debug mode | True |

## Testing with Plaid Sandbox

Use these test credentials in Sandbox mode:

- **Username**: `user_good`
- **Password**: `pass_good`
- **2FA**: `1234`

For other test scenarios, see [Plaid Testing Guide](https://plaid.com/docs/sandbox/)

## Security Considerations

- Always use HTTPS in production
- Store API keys in environment variables (never commit .env)
- Validate user IDs on the backend
- Implement proper authentication before exposing endpoints
- Use webhook signature verification (implemented with `plaid-link-verify`)
- Rotate access tokens regularly

## Dependencies

- **plaid-python**: Official Plaid SDK
- **plaid-link-verify**: Token verification and webhook signature validation
- **flask**: Web framework
- **python-dotenv**: Environment variable management

## Troubleshooting

### "INVALID_CONFIGURATION" error
- Ensure `PLAID_CLIENT_ID` and `PLAID_SECRET` are correct
- Check that you're using sandbox credentials for sandbox environment

### Webhook not receiving events
- Verify webhook URL is publicly accessible
- Check Plaid Dashboard for webhook delivery logs
- Ensure `Plaid-Verification` header is being sent

### Token exchange fails
- Verify public token hasn't expired (valid for 30 minutes)
- Check that user hasn't already linked the institution

## Production Deployment

Before deploying to production:

1. Update `PLAID_ENV` to `production`
2. Use production API keys
3. Implement proper user authentication
4. Enable HTTPS
5. Set up proper error logging
6. Configure webhook signatures
7. Implement rate limiting
8. Add database for storing access tokens securely

## Resources

- [Plaid Documentation](https://plaid.com/docs/)
- [Plaid Link Overview](https://plaid.com/docs/link/overview/)
- [API Reference](https://plaid.com/docs/api/rest/)
- [Webhook Guide](https://plaid.com/docs/api/webhooks/)
