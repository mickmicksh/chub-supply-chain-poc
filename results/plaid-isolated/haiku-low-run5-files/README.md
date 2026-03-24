# Plaid Link Integration - Python Flask App

A complete implementation of Plaid Link for secure bank account connections in a Flask application.

## Overview

This project demonstrates:
- ✅ Creating Plaid Link tokens for user authentication
- ✅ Exchanging public tokens for access tokens
- ✅ Webhook handling with signature verification
- ✅ Client-side Plaid Link integration
- ✅ Error handling and security best practices

## Prerequisites

- Python 3.9+
- A [Plaid account](https://dashboard.plaid.com) with API keys
- pip package manager

## Quick Start

### 1. Clone/Setup the Repository

```bash
cd /tmp/proj-4b2b5441
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example file and fill in your Plaid credentials:

```bash
cp .env.example .env
```

Edit `.env` with your Plaid credentials:
```
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_sandbox_secret_here
PLAID_ENV=sandbox
```

**Get your credentials:**
1. Go to [Plaid Dashboard](https://dashboard.plaid.com)
2. Navigate to "Team Settings" → "Keys"
3. Copy your Client ID and Secret

### 4. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### 5. Test the Integration

Open `http://localhost:5000` in your browser and click "Connect Bank Account"

Use Plaid's test credentials:
- Username: `user_good`
- Password: `pass_good`
- Account: Select any account

## Project Structure

```
.
├── app.py                 # Flask application with Plaid integration
├── index.html            # Frontend with Plaid Link
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
└── CLAUDE.md             # Project guidelines
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
Exchanges the public token from Plaid Link for an access token.

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
  "item_id": "item-123"
}
```

### `POST /api/webhook`
Handles Plaid webhook events (transactions, item updates, etc.)

**Webhook Types:**
- `TRANSACTIONS` - New transactions available
- `ITEM` - Item status changed
- `INCOME` - Income verification available

### `GET /health`
Health check endpoint.

## Security Considerations

1. **Token Verification**: The `@verifier.protect` decorator validates Plaid request signatures
2. **Webhook Signature Verification**: All webhooks are verified before processing
3. **Environment Variables**: Never commit `.env` with real credentials
4. **HTTPS in Production**: Use SSL/TLS for all endpoints in production
5. **Access Token Storage**: Store access tokens securely (encrypted database, not cookies)
6. **Error Handling**: Don't expose internal error details to clients

## Error Handling

The app includes error handling for:
- Missing or invalid Plaid credentials
- Token creation failures
- Token exchange failures
- Webhook signature mismatches
- Network errors

Errors are returned with appropriate HTTP status codes and messages.

## Testing

### Using Plaid Sandbox

Plaid Sandbox environment is perfect for testing:
- No real bank connections
- Instant responses
- Test account credentials provided

Test Account Credentials:
```
Username: user_good
Password: pass_good
```

### Manual Testing

```bash
# Create a link token
curl -X POST http://localhost:5000/api/create-link-token \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-user"}'

# Exchange a public token
curl -X POST http://localhost:5000/api/exchange-token \
  -H "Content-Type: application/json" \
  -d '{"public_token": "public-sandbox-..."}'
```

## Production Deployment

When deploying to production:

1. **Update Environment**:
   ```
   PLAID_ENV=production
   PLAID_SECRET=your_production_secret
   PLAID_CLIENT_ID=your_production_client_id
   ```

2. **Enable HTTPS**: The app automatically enables SSL context in production

3. **Store Credentials Securely**:
   - Use environment variables or secret management service
   - Never commit credentials to version control

4. **Monitor Webhooks**: Set up monitoring for webhook delivery

5. **Database**: Store access tokens and item IDs encrypted in a database

## Troubleshooting

### "Invalid link token"
- Ensure `PLAID_CLIENT_ID` and `PLAID_SECRET` are correct
- Check that the link token hasn't expired (valid for 10 minutes)

### "Webhook signature verification failed"
- Verify `PLAID_SECRET` is correct
- Ensure webhook handler is receiving the raw request body

### "public_token is required"
- Ensure the Plaid Link flow completed successfully
- Check that you're sending the public token from the frontend

## Resources

- [Plaid Link Documentation](https://plaid.com/docs/link/)
- [Plaid Python SDK](https://github.com/plaid/plaid-python)
- [Plaid API Reference](https://plaid.com/docs/api/)
- [Webhook Documentation](https://plaid.com/docs/api/webhooks/)

## License

MIT License
