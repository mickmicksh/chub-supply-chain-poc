# Plaid Link Integration Setup

## Prerequisites
- Python 3.9+
- A [Plaid account](https://dashboard.plaid.com) with sandbox credentials
- pip package manager

## Installation Steps

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and add your Plaid credentials:
```bash
cp .env.example .env
```

Edit `.env` and add your Plaid sandbox credentials:
```
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_sandbox_secret_here
PLAID_ENV=sandbox
```

You can find these credentials in your [Plaid Dashboard](https://dashboard.plaid.com).

### 3. Run the Flask App
```bash
python app.py
```

The app will be available at `http://localhost:5000`.

## API Endpoints

### Create Link Token
**POST** `/api/create-link-token`

Request body:
```json
{
  "user_id": "user-123"
}
```

Response:
```json
{
  "link_token": "link-sandbox-abcdef..."
}
```

### Exchange Token
**POST** `/api/exchange-token`

Request body:
```json
{
  "public_token": "public-sandbox-abcdef..."
}
```

Response:
```json
{
  "access_token": "access-sandbox-abcdef...",
  "item_id": "item-abcdef..."
}
```

### Webhook Handler
**POST** `/api/webhook`

Plaid sends webhook events to this endpoint. Ensure your Plaid dashboard has this webhook URL configured.

## Frontend Integration

### Using Plaid Link with React

```html
<!-- Add Plaid Link script to your HTML -->
<script src="https://cdn.plaid.com/link/v3/stable/link-initialize.js"></script>
```

```javascript
// Initialize Plaid Link
const handler = Plaid.create({
  token: linkToken,
  onSuccess: async (publicToken, metadata) => {
    // Exchange public token for access token
    const response = await fetch('/api/exchange-token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ public_token: publicToken })
    });
    const data = await response.json();
    console.log('Access token:', data.access_token);
  },
  onExit: (err, metadata) => {
    console.log('User exited Plaid Link');
  },
  onEvent: (eventName, metadata) => {
    console.log('Plaid Link event:', eventName);
  }
});

// Open Plaid Link
handler.open();
```

## Testing with Plaid Sandbox

Plaid provides test credentials for sandbox testing:

- **Username**: `user_good`
- **Password**: `pass_good`
- **Account**: Chase Checking
- **Routing Number**: 111000000
- **Account Number**: 1111111116

Use these credentials in the Plaid Link flow to test your integration.

## Security Best Practices

1. **Never expose API keys**: Keep `PLAID_SECRET` and `PLAID_CLIENT_ID` secure
2. **Use HTTPS in production**: Always use HTTPS for webhook endpoints
3. **Verify webhooks**: The `plaid-link-verify` package handles webhook verification
4. **Token management**: Store access tokens securely in your database
5. **Error handling**: Never log sensitive token information

## Troubleshooting

### Missing environment variables
Ensure all required variables are set in `.env`:
```bash
export PLAID_CLIENT_ID=your_client_id
export PLAID_SECRET=your_sandbox_secret
```

### Link token creation fails
- Verify your API credentials are correct
- Check that your Plaid account is in good standing
- Ensure the `client_name` in the request matches your Plaid application

### Webhook verification fails
- Confirm the `Plaid-Verification` header is present in requests
- Check that the webhook URL is correctly configured in your Plaid dashboard
- Verify the `PLAID_SECRET` matches your Plaid account

## Next Steps

1. Set up a database to store user access tokens and item IDs
2. Implement account information retrieval using the access token
3. Set up webhook handlers for transaction updates
4. Deploy to production when ready
