# Plaid Link Bank Account Integration

This project integrates Plaid Link into a Python Flask application to enable secure bank account connections.

## Prerequisites

- Python 3.9+
- A [Plaid account](https://dashboard.plaid.com) with API credentials
- pip package manager

## Setup Instructions

### 1. Clone and Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and fill in your Plaid credentials:

```bash
cp .env.example .env
```

Edit `.env` and add your Plaid API credentials:

```
PLAID_CLIENT_ID=your_client_id_from_dashboard
PLAID_SECRET=your_sandbox_secret_from_dashboard
SECRET_KEY=your-secret-key-for-flask
```

**Get your credentials from:** https://dashboard.plaid.com/account/keys

### 3. Run the Application

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### POST `/api/create-link-token`
Creates a Link token to initialize the Plaid Link modal.

**Request:**
```json
{
    "user_id": "user-123"
}
```

**Response:**
```json
{
    "link_token": "link-sandbox-...",
    "expiration": "2026-03-24T13:49:00Z"
}
```

### POST `/api/exchange-token`
Exchanges a public token from Plaid Link for an access token.

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
    "item_id": "item-id-123"
}
```

### POST `/api/webhook`
Receives webhook events from Plaid (transactions updates, auth changes, etc.)

Plaid will send POST requests to this endpoint with signed payloads.

### GET `/health`
Health check endpoint to verify the server is running.

## Frontend Integration

See `frontend_example.html` for a complete example of how to:
1. Initialize Plaid Link
2. Create a link token by calling your backend
3. Handle the link flow completion
4. Exchange the public token for an access token

## Key Components

- **app.py** - Flask backend with Plaid API integration
- **requirements.txt** - Python package dependencies (pinned versions)
- **.env** - Environment variables (create from .env.example)
- **frontend_example.html** - Client-side Plaid Link integration example

## Security Notes

1. **Never expose your Plaid Secret** - Keep it in environment variables
2. **Store access tokens securely** - Use encrypted database storage
3. **Verify webhook signatures** - The `plaid-link-verify` package handles this
4. **Use HTTPS in production** - Required for webhook signature verification

## Testing

1. Use Plaid's test credentials when in Sandbox mode
2. Test credentials are provided in the Plaid Dashboard under "Account > Sandbox Credentials"
3. Popular test bank: "Bank of America" with credentials:
   - Username: `user_good`
   - Password: `pass_good`

## Webhook Setup (Production)

1. Go to https://dashboard.plaid.com/webhooks
2. Add your webhook URL: `https://yourdomain.com/api/webhook`
3. The webhook handler will verify Plaid's signature automatically

## Troubleshooting

### "Missing required environment variables"
Make sure you've created `.env` from `.env.example` and added your Plaid credentials.

### "Link token creation failed"
Check that your Plaid Client ID and Secret are correct and valid for your environment (Sandbox vs Production).

### "Invalid webhook signature"
Ensure you're using the correct Plaid Secret in the `plaid-link-verify` initialization.

## Next Steps

1. Set up database models to store user bank connections
2. Implement endpoints to fetch transactions using stored access tokens
3. Set up proper webhook handling for transaction updates
4. Move to Production environment when ready

## Resources

- [Plaid Link Documentation](https://plaid.com/docs/link/)
- [Plaid Python SDK](https://github.com/plaid/plaid-python)
- [Plaid API Reference](https://plaid.com/docs/api/)
