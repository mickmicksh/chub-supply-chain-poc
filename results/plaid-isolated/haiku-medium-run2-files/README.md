# Plaid Link Integration

A Flask application for seamless bank account connections using Plaid Link.

## Features

- **Link Token Generation**: Create Link tokens for the Plaid Link flow
- **Token Exchange**: Exchange public tokens for access tokens
- **Webhook Handling**: Process Plaid webhook events with signature verification
- **Error Handling**: Comprehensive error handling and logging

## Prerequisites

- Python 3.9+
- A [Plaid account](https://dashboard.plaid.com) with API keys
- pip package manager

## Setup

### 1. Clone and Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your Plaid credentials
# PLAID_CLIENT_ID=your_client_id
# PLAID_SECRET=your_sandbox_secret
# PLAID_ENVIRONMENT=sandbox
```

### 3. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## API Endpoints

### Create Link Token
**POST** `/api/create-link-token`

Creates a Link token for initiating the Plaid Link flow.

Request:
```json
{
    "user_id": "user-123",
    "products": ["auth", "transactions"],
    "country_codes": ["US"]
}
```

Response:
```json
{
    "link_token": "link-sandbox-..."
}
```

### Exchange Token
**POST** `/api/exchange-token`

Exchanges a public token for an access token after user connects their bank account.

Request:
```json
{
    "public_token": "public-sandbox-...",
    "user_id": "user-123"
}
```

Response:
```json
{
    "access_token": "access-sandbox-...",
    "item_id": "..."
}
```

### Webhook Handler
**POST** `/api/webhook`

Receives and processes Plaid webhook events. Signature verification is performed automatically.

### Health Check
**GET** `/health`

Returns application health status.

## Testing

### 1. Create a Link Token

```bash
curl -X POST http://localhost:5000/api/create-link-token \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "products": ["auth", "transactions"],
    "country_codes": ["US"]
  }'
```

### 2. Use Test Credentials in Plaid Link

Open the returned `link_token` in your web application and use Plaid's sandbox credentials:
- Username: `user_good`
- Password: `pass_good`
- Account: Select any account

### 3. Exchange the Public Token

After successfully connecting an account in Plaid Link, exchange the public token:

```bash
curl -X POST http://localhost:5000/api/exchange-token \
  -H "Content-Type: application/json" \
  -d '{
    "public_token": "public-sandbox-...",
    "user_id": "user-123"
  }'
```

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── .gitignore            # Git ignore rules
├── CLAUDE.md             # Project guidelines
└── README.md             # This file
```

## Security

- **Webhook Verification**: All webhooks are verified using `plaid-link-verify`
- **Token Protection**: The `@verifier.protect` decorator validates request signatures
- **Environment Variables**: Sensitive credentials are stored in `.env` (not committed to git)

## Troubleshooting

### "Invalid client_id or secret"
- Verify `PLAID_CLIENT_ID` and `PLAID_SECRET` are correctly set in `.env`
- Ensure you're using sandbox credentials for testing

### "Webhook signature verification failed"
- Verify `PLAID_SECRET` is correct
- Check that the webhook is coming from Plaid's servers

### "Link token creation failed"
- Ensure your Plaid account is active
- Verify products are supported in your Plaid plan

## Next Steps

1. **Frontend Integration**: Add Plaid Link SDK to your web/mobile app
2. **Transaction Sync**: Implement transaction fetching using the access token
3. **Webhook Processing**: Extend webhook handlers for your use case
4. **Production Deployment**: Switch `PLAID_ENVIRONMENT` to `production` and use production keys

## Documentation

- [Plaid API Reference](https://plaid.com/docs)
- [Plaid Link Integration Guide](https://plaid.com/docs/link)
- [Python SDK Documentation](https://github.com/plaid/plaid-python)

## Support

For issues or questions:
1. Check the [Plaid documentation](https://plaid.com/docs)
2. Review logs in the console output
3. Contact Plaid support via your dashboard
