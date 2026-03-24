# Plaid Link Integration - Python Flask App

A complete Plaid Link integration setup for connecting bank accounts in Python using Flask. This project includes server-side token verification, webhook handling, and a frontend example.

## Features

- ✅ Plaid Link token creation
- ✅ Public token exchange for access tokens
- ✅ Server-side webhook verification using `plaid-link-verify`
- ✅ Transaction and item webhook handlers
- ✅ Sandbox and production environment support
- ✅ Flask REST API
- ✅ Frontend HTML example

## Prerequisites

- Python 3.9+
- [Plaid account](https://dashboard.plaid.com) with API keys
- pip

## Setup

### 1. Clone or create the project

```bash
cd your-project-directory
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and add your Plaid credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```
PLAID_CLIENT_ID=your_client_id
PLAID_SECRET=your_secret_key
PLAID_ENV=sandbox
```

Get your credentials from [Plaid Dashboard](https://dashboard.plaid.com/account/keys).

### 5. Run the application

```bash
python app.py
```

The app will start at `http://localhost:5000`

## API Endpoints

### `GET /health`
Health check endpoint

**Response:**
```json
{ "status": "ok" }
```

### `POST /api/create-link-token`
Create a Link token for the frontend Plaid Link flow

**Request:**
```json
{}
```

**Response:**
```json
{
  "link_token": "link-sandbox-abc123..."
}
```

### `POST /api/exchange-token`
Exchange a public token for an access token

**Request:**
```json
{
  "public_token": "public-sandbox-abc123..."
}
```

**Response:**
```json
{
  "access_token": "access-sandbox-abc123...",
  "item_id": "item-123..."
}
```

### `POST /api/webhook`
Webhook endpoint for Plaid events (transactions, item updates, etc.)

**Webhook Types Handled:**
- `TRANSACTIONS`: New transactions or transaction updates
- `ITEM`: Item events (new logins, password changes)

## Frontend Integration

Open `index.html` in your browser or serve it from your Flask app:

```python
@app.route('/')
def index():
    return send_file('index.html')
```

The frontend will:
1. Create a Link token by calling `/api/create-link-token`
2. Open Plaid Link modal for user
3. Exchange the public token via `/api/exchange-token`
4. Display connection status

## Testing

### With Plaid Sandbox

1. Use test credentials from [Plaid Sandbox Docs](https://plaid.com/docs/sandbox/)
2. Test username: `user_good`
3. Test password: `pass_good`

### Using cURL

```bash
# Create link token
curl -X POST http://localhost:5000/api/create-link-token \
  -H "Content-Type: application/json"

# Exchange token (replace with actual public token)
curl -X POST http://localhost:5000/api/exchange-token \
  -H "Content-Type: application/json" \
  -d '{"public_token":"public-sandbox-xxx"}'
```

## Security Notes

- **Webhook Verification**: All webhooks are verified using `plaid-link-verify`
- **Environment Variables**: Never commit `.env` file (included in `.gitignore`)
- **Access Tokens**: Treat as secrets and store securely (database with encryption)
- **HTTPS in Production**: Use HTTPS URLs for all Plaid endpoints in production

## Error Handling

The app includes comprehensive error handling:
- Invalid credentials → 400 Bad Request
- Missing parameters → 400 Bad Request
- Webhook verification failures → 400 Bad Request
- Server errors → 500 Internal Server Error

## Next Steps

1. **Database Integration**: Store access tokens and item IDs securely
2. **User Authentication**: Link access tokens to user accounts
3. **Transaction Sync**: Fetch and store transactions from Plaid
4. **Webhook Processing**: Implement custom logic in webhook handlers
5. **Deployment**: Deploy to production with proper environment configuration

## Documentation

- [Plaid Link Docs](https://plaid.com/docs/link/)
- [Plaid Python SDK](https://github.com/plaid/plaid-python)
- [Plaid Webhooks](https://plaid.com/docs/api/webhooks/)

## Support

For issues or questions:
- Check Plaid [Status Page](https://plaid.com/status)
- Review error messages in Flask logs
- Consult [Plaid Community](https://community.plaid.com/)

## License

MIT
