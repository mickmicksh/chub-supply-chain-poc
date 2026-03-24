# Plaid Link Integration - Python Flask App

A complete Flask application for integrating Plaid Link to handle bank account connections securely.

## Features

- ✅ **Link Token Creation** - Initialize Plaid Link with unique tokens
- ✅ **Token Exchange** - Exchange public tokens for access tokens
- ✅ **Webhook Verification** - Secure webhook signature validation
- ✅ **Error Handling** - Comprehensive error handling and logging
- ✅ **Environment Configuration** - Secure credential management

## Prerequisites

- Python 3.9+
- Plaid account with API credentials (get them at https://dashboard.plaid.com)
- pip package manager

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and add your Plaid credentials:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_secret_here
PLAID_ENV=sandbox
FLASK_ENV=development
```

### 3. Run the Application

```bash
python app.py
```

The app will start on `http://localhost:5000`

## API Endpoints

### `POST /api/create-link-token`
Create a Link token to initialize the Plaid Link flow

**Request:**
```json
{
  "user_id": "user-123"
}
```

**Response:**
```json
{
  "link_token": "link-production-...",
  "expiration": "2026-03-24T13:35:00Z"
}
```

### `POST /api/exchange-token`
Exchange a public token for an access token after user connects their account

**Request:**
```json
{
  "public_token": "public-production-..."
}
```

**Response:**
```json
{
  "access_token": "access-production-...",
  "item_id": "..."
}
```

### `POST /api/webhook`
Receive Plaid webhook events for account and transaction updates

**Headers:**
- `Plaid-Verification`: Webhook signature for verification

## Testing

### Using the Web UI

1. Open `http://localhost:5000` in your browser
2. Click "Connect Bank Account"
3. Use Plaid's test credentials:
   - Username: `user_good`
   - Password: `pass_good`
   - 2FA: `1234`

### Using cURL

```bash
# Create link token
curl -X POST http://localhost:5000/api/create-link-token \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user-123"}'

# Exchange token (after user connects via Plaid Link)
curl -X POST http://localhost:5000/api/exchange-token \
  -H "Content-Type: application/json" \
  -d '{"public_token":"public_token_from_plaid_link"}'
```

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── index.html            # Web UI for testing
├── README.md             # This file
└── CLAUDE.md             # Project guidelines
```

## Security Considerations

- **Token Verification**: All webhooks are verified using HMAC signatures
- **Environment Variables**: API credentials are stored in `.env` (never commit this file)
- **Error Handling**: Sensitive error details are not exposed to clients
- **HTTPS**: Use HTTPS in production environments
- **Access Tokens**: Store access tokens securely in your database

## Dependencies

| Package | Purpose |
|---------|---------|
| `flask` | Web framework |
| `plaid-python` | Official Plaid Python SDK |
| `plaid-link-verify` | Server-side token verification |
| `python-dotenv` | Environment variable management |

## Webhook Events

The webhook endpoint handles:
- **TRANSACTIONS** - Account transaction updates
- **ITEM** - Item status changes (e.g., login required)

Customize `handle_transactions_update()` and `handle_item_update()` functions to implement your business logic.

## Production Deployment

1. Set `PLAID_ENV=production` in your environment
2. Use HTTPS with valid SSL certificates
3. Store credentials securely (use secrets management)
4. Configure proper logging and monitoring
5. Set `FLASK_ENV=production`
6. Use a production WSGI server (e.g., Gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Documentation

- [Plaid Link Documentation](https://plaid.com/docs/link/)
- [Plaid API Reference](https://plaid.com/docs/api/)
- [Webhooks Guide](https://plaid.com/docs/api/webhooks/)

## License

MIT
