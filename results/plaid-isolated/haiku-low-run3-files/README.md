# Plaid Link Integration - Python Flask App

A complete implementation of Plaid Link for bank account connections in Python. This project demonstrates secure token exchange, webhook handling, and production-ready patterns.

## Features

- ✅ Plaid Link UI integration
- ✅ Secure public token exchange for access tokens
- ✅ Webhook signature verification
- ✅ Transaction and item update webhooks
- ✅ Error handling and validation
- ✅ Sandbox/Development/Production environment support

## Prerequisites

- Python 3.9+
- A [Plaid account](https://dashboard.plaid.com) (free tier available)
- pip and virtual environment

## Setup Instructions

### 1. Create and Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file and update with your Plaid credentials:

```bash
cp .env.example .env
```

Edit `.env` and add your Plaid API credentials from [https://dashboard.plaid.com](https://dashboard.plaid.com):

```
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_secret_here
PLAID_ENV=Sandbox
FLASK_ENV=development
```

**Important:** Never commit `.env` to version control. It's already in `.gitignore`.

## Running the Application

Start the Flask development server:

```bash
python app.py
```

The app will be available at `http://localhost:5000`

Open `index.html` in your browser (or serve it through the Flask app) to test the integration.

## API Endpoints

### 1. Create Link Token
```
POST /api/create-link-token
Content-Type: application/json

{
    "user_id": "user-123"
}

Response:
{
    "link_token": "link-sandbox-...",
    "expiration": "2026-03-24T13:31:00Z"
}
```

### 2. Exchange Token
```
POST /api/exchange-token
Content-Type: application/json

{
    "public_token": "public_key_sandbox_..."
}

Response:
{
    "access_token": "access-sandbox-...",
    "item_id": "Xxxxxxxxxxxxxxxxx"
}
```

### 3. Webhook Endpoint
```
POST /api/webhook

Plaid will POST updates about linked accounts to this endpoint.
Webhook signature is verified using plaid-link-verify.
```

## Testing in Sandbox

1. Start the app: `python app.py`
2. Open `index.html` in your browser
3. Click "Connect Bank Account"
4. Use Plaid's test credentials:
   - Username: `user_good`
   - Password: `pass_good`

See [Plaid Sandbox Documentation](https://plaid.com/docs/sandbox/) for more test accounts.

## Production Deployment

Before deploying to production:

1. **Switch to Production Environment:**
   ```
   PLAID_ENV=Production
   ```

2. **Update Plaid Credentials:**
   - Use your production API keys from Plaid dashboard

3. **Enable Webhook Verification:**
   - Verify all webhook signatures with `plaid-link-verify`
   - Set up webhook endpoint in Plaid dashboard

4. **Security Checklist:**
   - [ ] HTTPS enabled
   - [ ] Environment variables properly configured
   - [ ] Webhook signature verification enabled
   - [ ] CORS properly configured (if frontend is on different domain)
   - [ ] Access tokens stored securely (encrypted in database)
   - [ ] Rate limiting enabled
   - [ ] Error handling doesn't leak sensitive information

## Project Structure

```
.
├── app.py                 # Flask application with Plaid integration
├── index.html            # Frontend with Plaid Link UI
├── requirements.txt      # Python dependencies (pinned versions)
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
├── CLAUDE.md            # Project guidelines
└── README.md            # This file
```

## Security Notes

- The `plaid-link-verify` package validates webhook signatures to ensure they're from Plaid
- Never hardcode API credentials in your code
- Use HTTPS in production
- Access tokens should be stored securely (encrypted in database)
- The `@verifier.protect` decorator validates request signatures on protected endpoints

## Troubleshooting

### "Invalid Link Token"
- Ensure your Plaid API keys are correct in `.env`
- Check that the link token hasn't expired (expires in 1 hour)
- Verify you're using the correct environment (Sandbox vs Production)

### "Webhook Verification Failed"
- Ensure `PLAID_SECRET` in your webhook handler matches your environment
- Check that Plaid webhook endpoint is configured correctly in dashboard

### "Token Exchange Failed"
- Verify the public token is fresh (tokens are single-use)
- Check API key permissions in Plaid dashboard
- Ensure required products (auth, transactions) are enabled

## Documentation

- [Plaid Link Documentation](https://plaid.com/docs/link/web/)
- [Plaid Python SDK](https://github.com/plaid/plaid-python)
- [Plaid Webhooks](https://plaid.com/docs/api/webhooks/)

## License

MIT
