# Plaid Link Integration

A Python Flask application for integrating Plaid Link to enable secure bank account connections.

## Quick Start

### 1. Prerequisites

- Python 3.9+
- A [Plaid account](https://dashboard.plaid.com) with API keys
- pip

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Copy `.env.example` to `.env` and add your Plaid credentials:

```bash
cp .env.example .env
```

Edit `.env` with your Plaid API credentials:
```
PLAID_CLIENT_ID=your_client_id
PLAID_SECRET=your_sandbox_secret
FLASK_ENV=development
```

### 4. Run the Server

```bash
python app.py
```

The server will start at `http://localhost:5000`

### 5. Test the Integration

Open `plaid_client_example.html` in your browser (or serve it from the Flask app), then click "Connect Bank Account" to test the integration.

## API Endpoints

### `POST /api/create-link-token`
Creates a Plaid Link token for initiating the account connection flow.

**Request:**
```json
{
    "client_user_id": "user-123"
}
```

**Response:**
```json
{
    "link_token": "link-sandbox-..."
}
```

### `POST /api/exchange-token`
Exchanges a public token for an access token after user completes Link flow.

**Request:**
```json
{
    "public_token": "public-token-from-link"
}
```

**Response:**
```json
{
    "access_token": "access-sandbox-...",
    "item_id": "item_id"
}
```

### `POST /api/webhook`
Receives and processes webhooks from Plaid. Signature verification is automatic.

**Webhook Types:**
- `TRANSACTIONS` - Transaction update events
- `ITEM` - Item update events

## Testing with Sandbox

The application is configured to use Plaid's Sandbox environment for testing. You can use Plaid's test credentials:

- Username: `user_good`
- Password: `pass_good`
- Verification code: `1234`

## Security Features

- **Token Verification**: Uses `plaid-link-verify` for secure token handling
- **Webhook Signature Validation**: Automatically verifies incoming webhook signatures
- **Decorator Protection**: API endpoints are protected with `@verifier.protect` decorator
- **Environment Variables**: Sensitive credentials stored in `.env` (not in version control)

## Error Handling

The application includes comprehensive error handling for:
- Invalid API requests
- Missing required fields
- Plaid API errors
- Webhook verification failures

## Production Deployment

Before deploying to production:

1. Switch from Sandbox to Production environment in `app.py`:
   ```python
   host=plaid.Environment.Production
   ```

2. Update `.env` with production API keys

3. Set `FLASK_ENV=production`

4. Ensure webhook endpoint is publicly accessible and registered in Plaid dashboard

5. Use a production WSGI server (e.g., Gunicorn):
   ```bash
   gunicorn app:app --workers 4 --bind 0.0.0.0:5000
   ```

## Next Steps

1. Implement `handle_transactions_update()` and `handle_item_update()` functions
2. Store access tokens securely in your database
3. Integrate with your user authentication system
4. Add additional Plaid products (investments, liabilities, etc.)

## Support

For more information:
- [Plaid Documentation](https://plaid.com/docs)
- [Plaid Link Guide](https://plaid.com/docs/link/)
- [Plaid Python SDK](https://github.com/plaid/plaid-python)
