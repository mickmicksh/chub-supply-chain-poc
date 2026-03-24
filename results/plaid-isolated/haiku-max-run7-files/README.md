# Plaid Link Bank Account Integration

A Flask-based Python application for integrating Plaid Link to enable secure bank account connections.

## Features

- 🔐 Secure bank account authentication via Plaid Link
- 💳 Support for multiple financial products (Auth, Transactions)
- 🪝 Webhook handling for real-time account updates
- 🛡️ Token verification with `plaid-link-verify`
- 🧪 Sandbox environment support for testing

## Prerequisites

- Python 3.9+
- A [Plaid account](https://dashboard.plaid.com) with API credentials
- pip package manager

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and add your Plaid credentials:

```bash
cp .env.example .env
```

Edit `.env` with your Plaid credentials:

```env
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_secret_here
PLAID_ENV=sandbox
```

You can find your API credentials in the [Plaid Dashboard](https://dashboard.plaid.com/team/keys).

### 3. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## API Endpoints

### Create Link Token
**POST** `/api/create-link-token`

Creates a Plaid Link token that initializes the Plaid Link flow.

Request:
```json
{
  "user_id": "unique_user_identifier"
}
```

Response:
```json
{
  "link_token": "link-sandbox-...",
  "expiration": "2026-03-24T14:30:00Z"
}
```

### Exchange Token
**POST** `/api/exchange-token`

Exchanges a public token (from Plaid Link) for an access token.

Request:
```json
{
  "public_token": "public-sandbox-..."
}
```

Response:
```json
{
  "access_token": "access-sandbox-...",
  "item_id": "item-123456"
}
```

### Webhook Handler
**POST** `/api/webhook`

Handles Plaid webhook events. Configure this URL in your Plaid Dashboard under Settings → Webhooks.

## Testing

### Using the Web Interface

1. Start the application: `python app.py`
2. Open `http://localhost:5000/static/index.html` in your browser
3. Click "Connect Bank Account"
4. Use Plaid's test credentials:
   - Username: `user_good`
   - Password: `pass_good`

### Using cURL

Create a link token:
```bash
curl -X POST http://localhost:5000/api/create-link-token \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user"}'
```

Exchange a token:
```bash
curl -X POST http://localhost:5000/api/exchange-token \
  -H "Content-Type: application/json" \
  -d '{"public_token": "public-sandbox-..."}'
```

## Production Deployment

Before deploying to production:

1. **Update Environment**: Change `PLAID_ENV` to `production`
2. **Use Production Credentials**: Replace sandbox API keys with production keys
3. **Configure Webhook**: Set your webhook URL in Plaid Dashboard
4. **Enable HTTPS**: Use SSL/TLS for all connections
5. **Use a Production Server**: Deploy with gunicorn or similar instead of Flask's development server

Example with gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Error Handling

The application includes comprehensive error handling:

- **ApiException**: Plaid API errors are caught and logged
- **Webhook Verification**: Invalid signatures are rejected with 401 status
- **Missing Parameters**: Request validation returns 400 errors
- **General Errors**: Unexpected errors return 500 responses

All errors are logged for debugging purposes.

## Webhook Events

The application handles two main webhook types:

### TRANSACTIONS
Triggered when transaction data is available or updated.

### ITEM
Triggered when item status changes (e.g., login required, new accounts linked).

## Security Notes

- **Never commit `.env` files** with real credentials
- **Protect your Plaid Secret** - keep it server-side only
- **Validate all webhook signatures** using `plaid-link-verify`
- **Use HTTPS in production** for all communications
- **Implement rate limiting** for production deployments

## Documentation

For more information, see:
- [Plaid Link Documentation](https://plaid.com/docs/link/)
- [Plaid Python SDK](https://github.com/plaid/plaid-python)
- [Plaid API Reference](https://plaid.com/docs/api/)

## License

This project is provided as-is for integration purposes.
