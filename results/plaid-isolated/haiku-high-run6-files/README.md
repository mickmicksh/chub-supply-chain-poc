# Plaid Link Integration - Python Flask App

A secure Python Flask backend for integrating Plaid Link to enable bank account connections in your application.

## Features

- ✅ Create Plaid Link tokens for secure account linking
- ✅ Exchange public tokens for access tokens
- ✅ Handle Plaid webhooks with signature verification
- ✅ Support for transactions and item webhooks
- ✅ Built-in error handling and logging
- ✅ Secure request/response handling with `plaid-link-verify`

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Copy `.env.example` to `.env` and add your Plaid credentials:

```bash
cp .env.example .env
```

Edit `.env` with your credentials from [Plaid Dashboard](https://dashboard.plaid.com/team/keys):

```env
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_secret_key_here
```

### 3. Run the Flask App

```bash
python app.py
```

The server will start at `http://localhost:5000`

### 4. Test the Integration

Open `plaid_link_client.html` in your browser or integrate the JavaScript code into your frontend.

## API Endpoints

### POST `/api/create-link-token`

Creates a Plaid Link token for the frontend.

**Request:**
```json
{
  "user_id": "user-123",
  "client_name": "My App"
}
```

**Response:**
```json
{
  "link_token": "link-sandbox-xxx",
  "expiration": "2024-03-25T13:57:00Z"
}
```

### POST `/api/exchange-token`

Exchanges a public token (from Plaid Link) for an access token.

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
  "item_id": "item-xxx"
}
```

### POST `/api/webhook`

Receives and processes Plaid webhooks. Requires valid Plaid webhook signature.

**Webhook Types Handled:**
- `TRANSACTIONS` - New transactions available
- `ITEM` - Item status changes (e.g., auth expired)

### GET `/health`

Health check endpoint.

## Frontend Integration

The `plaid_link_client.html` file shows a complete example of:

1. Calling `/api/create-link-token` to get a link token
2. Opening Plaid Link with `Plaid.create()`
3. Handling successful linking and calling `/api/exchange-token`
4. Handling errors and exit events

## Security

- All requests are protected with `@verifier.protect` decorator
- Webhook signatures are verified with `plaid-link-verify`
- Credentials are stored in environment variables
- Use HTTPS in production

## Environment Modes

### Sandbox (Default)
```env
PLAID_CLIENT_ID=your_sandbox_client_id
PLAID_SECRET=your_sandbox_secret
```

### Production
Update the configuration in `app.py`:
```python
host=plaid.Environment.Production,
```

Then use production credentials from [Plaid Dashboard](https://dashboard.plaid.com/team/keys).

## Error Handling

The app includes comprehensive error handling for:
- Invalid requests (missing required fields)
- Plaid API errors
- Webhook signature verification failures
- Token exchange failures

## Webhook Setup

To receive webhooks in development:

1. Use [ngrok](https://ngrok.com/) to expose your local server:
   ```bash
   ngrok http 5000
   ```

2. Update your Plaid Dashboard webhook URL to: `https://your-ngrok-url.ngrok.io/api/webhook`

3. Your webhooks will now be received locally

## Testing

Use Plaid's test credentials in Sandbox mode:
- Username: `user_good`
- Password: `pass_good`
- Use test account numbers as provided by Plaid

## Next Steps

1. ✅ Implement actual transaction storage in `handle_transactions_update()`
2. ✅ Implement user re-authentication flow in `handle_item_update()`
3. ✅ Add database models for storing access tokens securely
4. ✅ Implement proper authentication/authorization for your endpoints
5. ✅ Set up HTTPS and move to production environment

## Dependencies

- `plaid-python` - Official Plaid SDK
- `plaid-link-verify` - Token & webhook verification
- `flask` - Web framework
- `python-dotenv` - Environment variable management

## Troubleshooting

### "Invalid client credentials"
- Verify `PLAID_CLIENT_ID` and `PLAID_SECRET` in `.env`
- Ensure you're using credentials from the same environment (sandbox vs production)

### "Webhook signature invalid"
- Verify webhook is coming from Plaid (check headers)
- Ensure `PLAID_SECRET` is correct in your `.env`

### "Link token expired"
- Link tokens expire after 1 hour; create a new token if needed

## References

- [Plaid Link Documentation](https://plaid.com/docs/link/)
- [Plaid Python SDK](https://github.com/plaid/plaid-python)
- [Plaid Webhooks](https://plaid.com/docs/api/webhooks/)
- [Plaid API Reference](https://plaid.com/docs/api/)
