# Plaid Link Integration - Python App

This is a Flask application that integrates Plaid Link for secure bank account connections.

## Features

- 🏦 Secure bank account linking with Plaid Link
- 🔐 Server-side token verification with plaid-link-verify
- 📱 Responsive web interface
- 🔗 Public token exchange for access tokens
- 📊 Webhook handling for transaction updates
- 🧪 Works with Plaid Sandbox for testing

## Prerequisites

- Python 3.9+
- A [Plaid account](https://dashboard.plaid.com) with API keys
- pip package manager

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your Plaid credentials:

```bash
cp .env.example .env
```

Edit `.env` with your credentials from [Plaid Dashboard](https://dashboard.plaid.com):

```
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_sandbox_secret_here
```

### 3. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## API Endpoints

### `POST /api/create-link-token`
Creates a Link token to initialize the Plaid Link flow.

**Response:**
```json
{
  "link_token": "link-sandbox-abc123..."
}
```

### `POST /api/exchange-token`
Exchanges a public token for an access token after user completes Link flow.

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
  "item_id": "item-id-xyz..."
}
```

### `POST /api/webhook`
Receives webhook events from Plaid (e.g., transaction updates).

**Requires:** `Plaid-Verification` header for signature verification

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── static/
│   └── index.html        # Frontend for Plaid Link
└── README.md             # This file
```

## Frontend Flow

1. User clicks "Connect Bank Account" button
2. Frontend calls `/api/create-link-token` to get a link token
3. Plaid Link opens with the token
4. User selects and connects their bank account
5. Plaid returns a public token
6. Frontend calls `/api/exchange-token` with the public token
7. Backend exchanges it for an access token
8. Access token is ready for API calls

## Testing

### Using Plaid Sandbox

Use these test credentials in Plaid Link:
- **Username:** `user_good`
- **Password:** `pass_good`

This allows you to test the full flow without using real bank credentials.

### With curl

```bash
# Create a link token
curl -X POST http://localhost:5000/api/create-link-token \
  -H "Content-Type: application/json"

# Exchange a public token (replace with actual token from Link flow)
curl -X POST http://localhost:5000/api/exchange-token \
  -H "Content-Type: application/json" \
  -d '{"public_token": "public-sandbox-..."}'
```

## Security Notes

- Always use the `plaid-link-verify` library to verify webhook signatures
- Store access tokens securely in your database (encrypted)
- Never expose your `PLAID_SECRET` in client-side code
- Use HTTPS in production
- Implement proper error handling and logging

## Next Steps

1. **Store Access Tokens:** Save access tokens in your database for later use
2. **Fetch Transactions:** Use access tokens to retrieve transaction data
3. **Handle Webhooks:** Process transaction update webhooks
4. **Deploy:** Move to production environment when ready

## Documentation

For more information, refer to:
- [Plaid API Documentation](https://plaid.com/docs/)
- [Plaid Link Documentation](https://plaid.com/docs/link/)
- [Python SDK Reference](https://plaid.com/docs/api/libraries/)

## Troubleshooting

### "Invalid client_id" or "Invalid secret"
- Check that your credentials in `.env` match your Plaid dashboard

### "Link token expired"
- Link tokens expire after 15 minutes; create a new one if needed

### Webhook signature verification fails
- Ensure the webhook secret matches your Plaid settings
- Check that the `Plaid-Verification` header is being passed correctly

## License

This project is provided as-is for integration with Plaid services.
