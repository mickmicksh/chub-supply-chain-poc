# Plaid Link Integration - Python Flask App

A complete example of integrating Plaid Link into a Python Flask application for secure bank account connections.

## 📋 Features

- **Plaid Link Integration**: User-friendly bank account connection flow
- **Token Exchange**: Secure public token to access token exchange
- **Webhook Handling**: Real-time updates for transactions and item events
- **Security**: Built-in webhook signature verification with `plaid-link-verify`
- **Error Handling**: Comprehensive error handling and logging

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file and add your Plaid credentials
cp .env.example .env
# Edit .env with your Plaid API keys
```

### 2. Get Plaid Credentials

1. Sign up at [Plaid Dashboard](https://dashboard.plaid.com)
2. Navigate to "Team settings" → "Keys"
3. Copy your `client_id` and `secret` (Sandbox environment)
4. Add them to your `.env` file:

```
PLAID_CLIENT_ID=your_client_id
PLAID_SECRET=your_sandbox_secret
```

### 3. Run the App

```bash
python app.py
```

The app will start at `http://localhost:5000`

### 4. Test with Plaid's Test Credentials

Open `http://localhost:5000/index.html` in your browser and click "Connect Bank Account".

Use these test credentials in Plaid Link:
- **Username**: `user_good`
- **Password**: `pass_good`
- **2FA Code**: `123456`

## 📁 Project Structure

```
.
├── app.py                 # Flask backend with Plaid integration
├── index.html            # Frontend UI with Plaid Link
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── CLAUDE.md            # Project guidelines
└── README.md            # This file
```

## 🔌 API Endpoints

### POST `/api/create-link-token`
Creates a Plaid Link token for initializing the frontend flow.

**Request:**
```json
{
  "user_id": "user-123"
}
```

**Response:**
```json
{
  "link_token": "link-sandbox-abc123...",
  "expiration": "2026-03-30T14:30:00Z"
}
```

### POST `/api/exchange-token`
Exchanges a public token from Plaid Link for an access token.

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
  "item_id": "item-123abc"
}
```

### POST `/api/webhook`
Handles Plaid webhook events (requires HTTPS in production).

**Event Types:**
- `TRANSACTIONS`: New transactions available
- `ITEM`: Item changes (errors, consent expiration, etc.)

### GET `/health`
Health check endpoint.

## 🔐 Security Features

- **Webhook Signature Verification**: All webhooks are verified using `plaid-link-verify`
- **Environment Variables**: Sensitive credentials are not hardcoded
- **PII Protection**: Never log or store public tokens
- **HTTPS Required**: Webhooks must use HTTPS in production

## 📚 API Reference

### Initialize Plaid Link (Frontend)

```javascript
const handler = Plaid.create({
    token: link_token,
    onSuccess: (publicToken, metadata) => {
        // Send publicToken to backend for exchange
    },
    onExit: (err, metadata) => {
        // Handle user exit
    },
    onEvent: (eventName, metadata) => {
        // Track events
    },
});

handler.open();
```

### Exchange Token (Backend)

```python
exchange_request = ItemPublicTokenExchangeRequest(
    public_token=public_token
)
response = client.item_public_token_exchange(exchange_request)
access_token = response.access_token
item_id = response.item_id
```

## 🧪 Testing

### Test with Sandbox Credentials
The app runs in Sandbox mode by default. Use Plaid's test credentials above.

### Test Webhook Handling
Plaid will send test webhooks when you make changes in the dashboard. Check your Flask logs for webhook events.

## 📖 Documentation

- [Plaid Link Documentation](https://plaid.com/docs/link)
- [Plaid Python SDK](https://github.com/plaid/plaid-python)
- [plaid-link-verify Package](https://pypi.org/project/plaid-link-verify/)

## 🔄 Production Deployment

Before deploying to production:

1. **Switch to Production Keys**: Update `.env` with production Plaid credentials
2. **Update Host**: Change `plaid.Environment.Sandbox` to `plaid.Environment.Production`
3. **Enable HTTPS**: Webhooks require HTTPS
4. **Set Webhook URL**: Configure webhook URL in Plaid dashboard
5. **Implement Database**: Store `access_tokens` and `item_ids` securely
6. **Add Authentication**: Implement user authentication
7. **Error Monitoring**: Set up error tracking (e.g., Sentry)

## 🐛 Troubleshooting

### "Plaid Link Token Expired"
Link tokens expire after 1 hour. Generate a new one before opening Plaid Link.

### "Authentication Failed"
Check that your `PLAID_CLIENT_ID` and `PLAID_SECRET` are correct and match your environment (Sandbox vs Production).

### "Webhook Signature Verification Failed"
Ensure your `PLAID_SECRET` in `.env` matches the one in the Plaid dashboard.

## 📝 License

This project is provided as an example. See Plaid's terms of service for API usage.
