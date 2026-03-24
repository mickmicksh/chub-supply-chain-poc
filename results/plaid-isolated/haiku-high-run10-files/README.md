# Plaid Link Integration - Python Flask App

A complete integration example for Plaid Link, enabling secure bank account connections in your Python application.

## Project Structure

```
.
├── app.py                   # Main Flask application with Plaid Link endpoints
├── requirements.txt         # Python dependencies (pinned versions)
├── .env.example            # Environment variables template
├── frontend_example.html   # HTML/JavaScript frontend demo
├── CLAUDE.md              # Project guidelines
└── README.md              # This file
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
```

Then edit `.env` and add your Plaid credentials:

```env
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_secret_key_here
PLAID_ENV=sandbox
FLASK_ENV=development
```

**Get your credentials:**
1. Sign up at [Plaid Dashboard](https://dashboard.plaid.com)
2. Go to Keys section to find your Client ID and Secret
3. Use `sandbox` environment for testing

### 3. Run the Application

```bash
python app.py
```

The server will start at `http://localhost:5000`

### 4. Test the Integration

Open `frontend_example.html` in your browser to test the flow:
1. Click "Connect Bank Account"
2. Complete the Plaid Link flow with test credentials
3. Your access token and item ID will be displayed

## API Endpoints

### POST `/api/create-link-token`
Creates a Link token to initialize Plaid Link on the frontend.

**Request:**
```json
{
  "user_id": "user-123"
}
```

**Response:**
```json
{
  "link_token": "link-sandbox-abc123..."
}
```

### POST `/api/exchange-token`
Exchanges a public token for an access token after user completes Plaid Link.

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
  "item_id": "abc123..."
}
```

### POST `/api/webhook`
Handles Plaid webhook events (transactions updated, item changes, etc).

**Webhook Types Handled:**
- `TRANSACTIONS`: Transaction updates
- `ITEM`: Item status changes

### GET `/health`
Health check endpoint for deployment monitoring.

## Plaid Link Flow

```
User                Frontend              Backend               Plaid
  |                    |                     |                  |
  +---> Click Button -->|                     |                  |
  |                    +---> Create Token --->|                  |
  |                    |<--- Link Token ------+                  |
  |                    +---> Plaid Link -----------+             |
  |                    |    (Opens Modal)         |              |
  |                    |                          +-- Authenticate ->
  |                    |                          <-- Public Token --
  |                    +---> Exchange Token ----->|                  |
  |                    |<--- Access Token --------+                  |
  |<--- Display Result-+                          |                  |
```

## Key Features

- ✅ **Secure Token Verification** - `plaid-link-verify` validates all tokens
- ✅ **Webhook Handling** - Signature verification for webhook events
- ✅ **Error Handling** - Comprehensive error responses
- ✅ **Environment Configuration** - Sandbox/Development/Production support
- ✅ **Type-Safe** - Proper request/response models using Plaid SDK

## Testing with Plaid

Use these test credentials in Plaid Link:

| Flow | Username | Password |
|------|----------|----------|
| Success | user_good | pass_good |
| Auth Required | user_good | fail_auth |
| Locked | user_locked | pass_locked |

See [Plaid Test Credentials](https://plaid.com/docs/sandbox/credentials/) for more options.

## Storing Access Tokens

**⚠️ Important Security Notes:**

1. **Never expose access tokens to the frontend** - The `frontend_example.html` displays tokens for demo only
2. **In production**, send the access token directly to your backend:
   ```javascript
   // Instead of displaying the token
   await fetch('/api/store-access-token', {
     method: 'POST',
     body: JSON.stringify({ access_token, item_id })
   });
   ```

3. **Encrypt tokens at rest** using industry-standard encryption
4. **Use HTTPS only** in production
5. **Implement token rotation** for long-term security

## Webhooks

Configure your webhook URL in [Plaid Dashboard](https://dashboard.plaid.com):

```
https://yourdomain.com/api/webhook
```

The webhook handler verifies Plaid's signature before processing events.

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PLAID_CLIENT_ID` | Your Plaid Client ID | `client_id_abc123` |
| `PLAID_SECRET` | Your Plaid Secret Key | `secret_abc123` |
| `PLAID_ENV` | Plaid environment | `sandbox`, `development`, `production` |
| `FLASK_ENV` | Flask environment | `development`, `production` |

## Dependencies

See `requirements.txt` for all dependencies with pinned versions:

- **plaid-python**: Official Plaid SDK
- **plaid-link-verify**: Token verification and webhook signature validation
- **flask**: Web framework
- **python-dotenv**: Environment variable management

## Troubleshooting

### "Missing required environment variables"
Make sure you've created a `.env` file with your Plaid credentials.

### "Invalid link token"
Ensure your Client ID and Secret are correct in the `.env` file.

### "Webhook signature verification failed"
Verify that your webhook URL is correctly configured in the Plaid Dashboard and matches your server address.

### CORS Issues
If testing locally, add CORS headers to Flask. For production, configure proper CORS policies.

## Next Steps

1. **Store Access Tokens Securely** - Implement database storage with encryption
2. **Implement Token Refresh** - Handle token rotation for long-term access
3. **Add Authentication** - Secure your endpoints with user authentication
4. **Process Transactions** - Use the access token to fetch account and transaction data
5. **Deploy to Production** - Update environment variables and webhook URLs

## Documentation

- [Plaid Link Documentation](https://plaid.com/docs/link/)
- [Plaid Python SDK](https://github.com/plaid/plaid-python)
- [Flask Documentation](https://flask.palletsprojects.com/)

## License

This example is provided as-is for educational purposes.
