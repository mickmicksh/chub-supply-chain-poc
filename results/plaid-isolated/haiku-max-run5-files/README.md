# Plaid Link Python Integration

A complete Flask-based implementation for integrating Plaid Link into your Python application for secure bank account connections.

## Features

✅ **Plaid Link Integration** - Client-side account linking UI
✅ **Token Exchange** - Secure public-to-access token conversion
✅ **Webhook Handling** - Signature-verified event processing
✅ **Error Handling** - Comprehensive exception management
✅ **Sandbox Testing** - Ready for development with Plaid Sandbox

## Prerequisites

- Python 3.9+
- A [Plaid account](https://dashboard.plaid.com) with API credentials
- pip package manager

## Setup Instructions

### 1. Clone Environment Variables

```bash
cp .env.example .env
```

Then update `.env` with your Plaid credentials:

```bash
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_secret_here
PLAID_ENV=sandbox  # or 'production'
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Development Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### POST `/api/create-link-token`

Create a Plaid Link token for client-side linking.

**Request Body:**
```json
{
  "user_id": "unique_user_identifier",
  "products": ["auth", "transactions"],
  "country_codes": ["US"]
}
```

**Response:**
```json
{
  "link_token": "link-sandbox-xxx",
  "expiration": "2024-01-01T12:00:00Z"
}
```

### POST `/api/exchange-token`

Exchange a public token for an access token.

**Request Body:**
```json
{
  "public_token": "public-sandbox-xxx"
}
```

**Response:**
```json
{
  "access_token": "access-sandbox-xxx",
  "item_id": "item-123"
}
```

### POST `/api/webhook`

Webhook endpoint for Plaid events (automatic signature verification).

**Supported Events:**
- `TRANSACTIONS` - Transaction updates
- `ITEM` - Item/account updates

## Testing with the Web Interface

Open `http://localhost:5000` in your browser to test the full flow:

1. Click "Connect Bank Account"
2. Use Plaid Sandbox credentials to simulate account linking
3. View the resulting access token and item ID

## Plaid Sandbox Test Credentials

When using Plaid Sandbox:

- **Username:** any value (e.g., `user_good`)
- **Password:** `pass_good`
- **2FA:** `1234` (when prompted)

Full list of test credentials: https://plaid.com/docs/sandbox/

## Project Structure

```
.
├── app.py              # Flask application with Plaid integration
├── index.html          # Web UI for testing
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment configuration
├── README.md           # This file
└── CLAUDE.md           # Project guidelines
```

## Security Considerations

- **Always use HTTPS in production** - Plaid requires secure connections
- **Webhook signature verification** - All incoming webhooks are verified using `plaid-link-verify`
- **Token protection** - Access tokens should be stored securely server-side
- **Environment variables** - Never commit `.env` files with real credentials

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PLAID_CLIENT_ID` | Yes | - | Your Plaid Client ID |
| `PLAID_SECRET` | Yes | - | Your Plaid Secret Key |
| `PLAID_ENV` | No | `sandbox` | Plaid environment (sandbox or production) |
| `PORT` | No | `5000` | Server port |
| `DEBUG` | No | `False` | Flask debug mode |

## Troubleshooting

### "PLAID_CLIENT_ID and PLAID_SECRET must be set"

Make sure you've created a `.env` file and set your credentials:
```bash
cp .env.example .env
# Edit .env with your credentials
```

### Link token creation fails

- Verify your credentials are correct
- Check that you're using the correct Plaid environment (sandbox vs production)
- Ensure `plaid-link-verify` is installed

### Webhook signature verification fails

- Confirm the `PLAID_SECRET` is the same in your `.env` and Plaid dashboard
- Ensure the webhook is being called with the correct `Plaid-Verification` header

## Next Steps

1. **Add Database** - Store access tokens and user-account mappings
2. **Implement Accounts API** - Retrieve account details
3. **Implement Transactions API** - Fetch and sync transactions
4. **Add Auth** - Secure user endpoints with authentication
5. **Deploy to Production** - Switch to production Plaid credentials

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `plaid-python` | 26.0.0 | Official Plaid Python SDK |
| `plaid-link-verify` | 1.0.2 | Token verification and webhook validation |
| `flask` | 3.0.0 | Web framework |
| `python-dotenv` | 1.0.0 | Environment variable management |

## Support

- [Plaid Documentation](https://plaid.com/docs/)
- [Plaid Link Guide](https://plaid.com/docs/link/)
- [Webhook Events](https://plaid.com/docs/api/webhooks/)
