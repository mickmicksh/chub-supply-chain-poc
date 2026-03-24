# Plaid Link Integration - Python Flask App

A complete Python Flask application for integrating Plaid Link to allow users to securely connect their bank accounts.

## Features

- ✅ Plaid Link token generation
- ✅ Public token exchange for access tokens
- ✅ Webhook handling with signature verification
- ✅ Support for Auth and Transactions products
- ✅ Sandbox, Development, and Production environments
- ✅ Secure token verification with `plaid-link-verify`

## Prerequisites

- Python 3.9+
- A [Plaid account](https://dashboard.plaid.com) with API keys
- pip package manager

## Setup

1. **Clone or initialize the project:**
   ```bash
   cd /tmp/proj-e820b0af
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your Plaid credentials:
   ```
   PLAID_CLIENT_ID=your_client_id_here
   PLAID_SECRET=your_secret_key_here
   PLAID_ENV=sandbox
   ```

## Running the Application

```bash
python app.py
```

The app will run on `http://localhost:5000`.

## API Endpoints

### Create Link Token
**POST** `/api/create-link-token`

Request:
```json
{
  "user_id": "user-123",
  "country_codes": ["US"],
  "language": "en"
}
```

Response:
```json
{
  "link_token": "link-xxx",
  "expiration": "2026-03-23T15:30:00Z"
}
```

### Exchange Token
**POST** `/api/exchange-token`

After user successfully links their account through Plaid Link, exchange the public token for an access token.

Request:
```json
{
  "public_token": "public-xxx"
}
```

Response:
```json
{
  "access_token": "access-xxx",
  "item_id": "item-xxx"
}
```

### Webhook
**POST** `/api/webhook`

Plaid sends webhook notifications to this endpoint. The application verifies the webhook signature and handles:
- `TRANSACTIONS`: Account transactions updated
- `AUTH`: Account authentication data available
- `ITEM`: Item status changes

## Frontend Integration

Example HTML to integrate Plaid Link:

```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.plaid.com/link/v3/stable/link-initialize.js"></script>
</head>
<body>
  <button id="link-button">Connect Bank Account</button>

  <script>
    const handler = Plaid.create({
      token: '', // Will be set after fetching from backend
      onSuccess: (public_token, metadata) => {
        fetch('/api/exchange-token', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ public_token })
        }).then(r => r.json()).then(data => {
          console.log('Account linked!', data);
        });
      },
      onExit: (err, metadata) => {
        console.log('User exited Plaid Link');
      }
    });

    document.getElementById('link-button').addEventListener('click', async () => {
      const response = await fetch('/api/create-link-token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 'user-123' })
      });
      const { link_token } = await response.json();

      handler.open(link_token);
    });
  </script>
</body>
</html>
```

## Production Deployment

1. Update environment to `production`:
   ```
   PLAID_ENV=production
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

2. Configure proper webhook URL in Plaid dashboard pointing to your production server

3. Use a production WSGI server (e.g., Gunicorn):
   ```bash
   gunicorn -w 4 app:app
   ```

## Security Considerations

- **Token Storage**: Store `access_token` and `item_id` securely in your database
- **Webhook Verification**: All webhooks are verified using `plaid-link-verify`
- **Environment Variables**: Never commit `.env` file to version control
- **HTTPS**: Always use HTTPS in production

## Documentation

- [Plaid API Documentation](https://plaid.com/docs)
- [Plaid Link Documentation](https://plaid.com/docs/link/)
- [Python SDK Reference](https://github.com/plaid/plaid-python)

## Troubleshooting

**Missing environment variables:**
```
ValueError: PLAID_CLIENT_ID environment variable is required
```
Solution: Ensure `.env` file is created and contains valid credentials.

**Invalid Link Token:**
```
Invalid link_token
```
Solution: Ensure link token hasn't expired (tokens expire after 1 hour).

## Error Handling

The application catches Plaid API exceptions and returns appropriate HTTP status codes:
- `400`: Bad request or invalid input
- `401`: Authentication failed
- `500`: Internal server error

## Next Steps

1. Store `access_token` in a database (encrypted)
2. Implement account data retrieval using the access token
3. Set up proper logging and monitoring
4. Configure webhook URL in Plaid dashboard
5. Add comprehensive error handling and validation
