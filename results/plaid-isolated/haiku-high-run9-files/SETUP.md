# Plaid Link Integration Setup Guide

This project integrates Plaid Link for secure bank account connections in Python.

## Prerequisites

- Python 3.9+
- pip package manager
- A Plaid account with API credentials

## Step 1: Create Plaid Account & Get API Keys

1. Sign up at [Plaid Dashboard](https://dashboard.plaid.com)
2. Navigate to **Team Settings** → **Keys**
3. Copy your:
   - **Client ID**
   - **Sandbox Secret** (for development)

## Step 2: Set Up Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Add your Plaid credentials to `.env`:
   ```
   PLAID_CLIENT_ID=your_client_id_here
   PLAID_SECRET=your_sandbox_secret_here
   ```

3. **Important:** Never commit `.env` to version control!

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Run the Application

```bash
python app.py
```

The Flask server will start on `http://localhost:5000`

## API Endpoints

### 1. Create Link Token
**POST** `/api/create-link-token`

Creates a Plaid Link token to initiate the account connection flow.

**Request:**
```json
{
  "user_id": "user-123",
  "products": ["auth", "transactions"]
}
```

**Response:**
```json
{
  "link_token": "link-sandbox-abc123..."
}
```

### 2. Exchange Token
**POST** `/api/exchange-token`

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
  "item_id": "item-abc123..."
}
```

### 3. Webhook Endpoint
**POST** `/api/webhook`

Handles Plaid webhook notifications for transaction updates and account events.

**Webhook Setup:**
1. Go to Plaid Dashboard → **Settings** → **Webhooks**
2. Add your webhook URL: `https://your-domain.com/api/webhook`
3. Plaid will send signed webhook events to this endpoint

### 4. Health Check
**GET** `/health`

Simple health check endpoint.

## Security Features

### Token Verification
- **`plaid-link-verify`** validates all Link requests
- **`@verifier.protect`** decorator protects sensitive endpoints
- Prevents unauthorized token exchanges

### Webhook Signature Validation
- All webhooks are verified using your Plaid secret
- Invalid signatures are rejected automatically

## Testing with Plaid Sandbox

Use Plaid's test credentials when prompted in Link:

**Test Bank:**
- Username: `user_good`
- Password: `pass_good`

See [Plaid Test Credentials](https://plaid.com/docs/sandbox/overview/#sandbox-test-credentials) for more test accounts.

## Production Deployment

When moving to production:

1. Update environment variables with **Production** credentials
2. Change Plaid environment:
   ```python
   host=plaid.Environment.Production
   ```
3. Enable SSL/HTTPS for webhook endpoints
4. Store credentials in secure environment variables (not .env files)
5. Add proper error logging and monitoring

## Troubleshooting

### "Missing environment variables" error
- Ensure `.env` file exists with valid credentials
- Run: `source .env` to load variables

### "Invalid public token" error
- Token may have expired (valid for 30 minutes)
- Verify user completed Link flow successfully
- Check token is from same Plaid environment (sandbox vs production)

### Webhook not receiving events
- Verify webhook URL is publicly accessible
- Check Plaid Dashboard webhook logs for errors
- Ensure signature validation isn't rejecting valid requests

## Next Steps

1. Implement proper database storage for access tokens
2. Add transaction fetching using access tokens
3. Set up webhook processing for account updates
4. Implement user authentication for your app
5. Add error handling and logging

## Resources

- [Plaid Documentation](https://plaid.com/docs)
- [Link Flow Guide](https://plaid.com/docs/link/web)
- [API Reference](https://plaid.com/docs/api/overview)
- [Test Credentials](https://plaid.com/docs/sandbox/overview/#sandbox-test-credentials)
