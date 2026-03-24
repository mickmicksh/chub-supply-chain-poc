# Plaid Link Integration

A Python Flask application for integrating Plaid Link for secure bank account connections.

## Features

- **Plaid Link Token Creation** - Generate secure tokens to initialize Plaid Link flow
- **Token Exchange** - Exchange public tokens for access tokens
- **Webhook Handling** - Receive and process Plaid webhook events
- **Security** - Server-side token verification and webhook signature validation

## Prerequisites

- Python 3.9+
- A Plaid account with API keys ([Sign up here](https://dashboard.plaid.com))
- pip package manager

## Setup

1. **Clone/create the project** and navigate to the project directory

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Plaid credentials:
   ```
   PLAID_CLIENT_ID=your_client_id
   PLAID_SECRET=your_secret
   ```

   You can find these in your [Plaid Dashboard](https://dashboard.plaid.com)

4. **Run the application**:
   ```bash
   python app.py
   ```
   The server will start on `http://localhost:5000`

## API Endpoints

### 1. Create Link Token
**POST** `/api/create-link-token`

Creates a token to initialize Plaid Link in your frontend.

**Request**:
```json
{
  "user_id": "user-123"
}
```

**Response**:
```json
{
  "link_token": "link-sandbox-...",
  "expiration": "2026-03-24T13:40:00Z"
}
```

### 2. Exchange Token
**POST** `/api/exchange-token`

Exchanges the public token from Plaid Link for a permanent access token.

**Request**:
```json
{
  "public_token": "public-sandbox-..."
}
```

**Response**:
```json
{
  "access_token": "access-sandbox-...",
  "item_id": "item-id-..."
}
```

### 3. Plaid Webhook
**POST** `/api/webhook`

Receives webhook events from Plaid (transactions updates, item changes, etc.)

## Frontend Integration

Here's how to integrate Plaid Link in your frontend (React example):

```javascript
import { PlaidLink } from 'react-plaid-link';

function App() {
  const [linkToken, setLinkToken] = React.useState(null);

  React.useEffect(() => {
    // Create link token
    fetch('/api/create-link-token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: 'user-123' })
    })
      .then(res => res.json())
      .then(data => setLinkToken(data.link_token));
  }, []);

  const onSuccess = (publicToken) => {
    // Exchange token on backend
    fetch('/api/exchange-token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ public_token: publicToken })
    })
      .then(res => res.json())
      .then(data => console.log('Access token:', data.access_token));
  };

  return (
    linkToken && (
      <PlaidLink
        token={linkToken}
        onSuccess={onSuccess}
        onExit={() => console.log('User exited')}
      >
        Open Plaid Link
      </PlaidLink>
    )
  );
}
```

## Testing

1. **Using Plaid Sandbox**: The app is configured to use Plaid's Sandbox environment by default
2. **Test Credentials**: Use Plaid's test credentials when logging in through Plaid Link
3. **Health Check**: `curl http://localhost:5000/health`

## Production Deployment

Before deploying to production:

1. Update `plaid.Environment.Sandbox` to `plaid.Environment.Production` in `app.py`
2. Use production Plaid API keys
3. Enable HTTPS (required for webhook verification)
4. Configure your webhook URL in the Plaid Dashboard
5. Store secrets in environment variables (never commit `.env`)

## Security Notes

- `plaid-link-verify` handles server-side token verification
- Webhooks are automatically verified using HMAC signatures
- Never expose access tokens to the frontend
- Always use HTTPS in production

## Troubleshooting

**Missing environment variables error**:
- Ensure `.env` file exists in the project root with `PLAID_CLIENT_ID` and `PLAID_SECRET`

**API Connection errors**:
- Verify your Plaid credentials are correct
- Check that you're using the correct environment (Sandbox vs Production)

**Webhook signature verification failed**:
- Ensure `PLAID_SECRET` is correct
- Webhooks must be sent over HTTPS

## Resources

- [Plaid Documentation](https://plaid.com/docs)
- [Plaid Link Guide](https://plaid.com/docs/link)
- [Plaid API Reference](https://plaid.com/docs/api)

## License

MIT
