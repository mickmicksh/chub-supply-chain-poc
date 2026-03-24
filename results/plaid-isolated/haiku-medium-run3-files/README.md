# Plaid Link Integration - Python Flask App

This project integrates Plaid Link for secure bank account connections in your Python application.

## Quick Start

### 1. Setup Environment Variables

Copy the `.env.example` file to `.env` and fill in your Plaid credentials:

```bash
cp .env.example .env
```

Then edit `.env` with your credentials from [Plaid Dashboard](https://dashboard.plaid.com):

```
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_sandbox_secret_here
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

The Flask app will start on `http://localhost:5000`.

## API Endpoints

### POST `/api/create-link-token`

Creates a Plaid Link token for the front-end.

**Request:**
```json
{
  "user_id": "user-123"
}
```

**Response:**
```json
{
  "link_token": "link-sandbox-xxx"
}
```

### POST `/api/exchange-token`

Exchanges the public token from Plaid Link for an access token.

**Request:**
```json
{
  "public_token": "public-sandbox-xxx"
}
```

**Response:**
```json
{
  "access_token": "access-sandbox-xxx",
  "item_id": "item-id"
}
```

### POST `/api/webhook`

Receives and handles Plaid webhook events (transactions, item updates, etc.).

**Supported Events:**
- `TRANSACTIONS` - When transactions are available
- `ITEM` - Item-related events

### GET `/health`

Health check endpoint for monitoring.

## Frontend Integration

You'll need to add Plaid Link to your frontend. Here's a minimal example with vanilla JavaScript:

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.plaid.com/link/v3/stable/link-initialize.js"></script>
</head>
<body>
    <button onclick="openPlaidLink()">Connect Bank Account</button>

    <script>
        async function openPlaidLink() {
            // Step 1: Get link token from backend
            const linkTokenResponse = await fetch('/api/create-link-token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: 'user-123' })
            });
            const { link_token } = await linkTokenResponse.json();

            // Step 2: Initialize Plaid Link
            const handler = Plaid.create({
                token: link_token,
                onSuccess: async (publicToken) => {
                    // Step 3: Exchange token with backend
                    const exchangeResponse = await fetch('/api/exchange-token', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ public_token: publicToken })
                    });
                    const { access_token, item_id } = await exchangeResponse.json();
                    console.log('Bank account connected!', { access_token, item_id });
                },
                onExit: (err) => {
                    console.error('User exited Plaid Link', err);
                }
            });

            handler.open();
        }
    </script>
</body>
</html>
```

## Architecture

1. **Frontend** - Initializes Plaid Link with a link token
2. **Backend** (`app.py`) - Manages Plaid API communication and token exchange
3. **Plaid Servers** - Handles bank connections and data
4. **Webhooks** - Receives real-time updates about account data

## Security

- The `plaid-link-verify` library validates all webhook signatures
- The `@verifier.protect` decorator validates request signatures on sensitive endpoints
- Never expose `PLAID_SECRET` to the frontend - it's server-side only
- The public token is short-lived and single-use
- Access tokens are used for all subsequent authenticated API calls

## Testing

In development, use Plaid's sandbox credentials and test bank account:

- Username: `user_good`
- Password: `pass_good`

See [Plaid Sandbox Documentation](https://plaid.com/docs/sandbox) for more test credentials.

## Production Deployment

Before going to production:

1. Update environment variables to use production credentials
2. Change `host=plaid.Environment.Sandbox` to `host=plaid.Environment.Production`
3. Enable HTTPS for all endpoints
4. Set up proper error logging and monitoring
5. Test webhook handling thoroughly
6. Implement database persistence for access tokens

## Troubleshooting

**Invalid signature errors:**
- Ensure `PLAID_SECRET` is correct
- Check webhook signature validation is enabled
- Verify the request hasn't been modified in transit

**Token exchange failures:**
- Confirm the public token is valid and hasn't expired (5 minute lifetime)
- Check Plaid API credentials are correct
- Review Plaid dashboard for any errors

**Missing data in webhooks:**
- Ensure webhook endpoint is publicly accessible
- Configure the webhook URL in Plaid dashboard
- Check logs for validation errors

## Resources

- [Plaid Link Documentation](https://plaid.com/docs/link/)
- [Plaid Python SDK](https://github.com/plaid/plaid-python)
- [Plaid API Reference](https://plaid.com/docs/api/)
