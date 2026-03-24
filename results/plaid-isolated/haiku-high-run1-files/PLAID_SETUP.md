# Plaid Link Integration Setup Guide

## Quick Start

### 1. Get Plaid Credentials
1. Sign up at https://dashboard.plaid.com
2. Create a new app and copy your credentials:
   - `Client ID`
   - `Secret` (use Sandbox secret for testing)

### 2. Environment Setup
```bash
cp .env.example .env
# Edit .env with your Plaid credentials
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```

The app will start at `http://localhost:5000`

## API Endpoints

### Create Link Token
- **POST** `/api/create-link-token`
- Creates a Link token to start the bank connection flow
- Response: `{ "link_token": "link-sandbox-..." }`

### Exchange Token
- **POST** `/api/exchange-token`
- Exchanges the public token from Link for an access token
- Request: `{ "public_token": "public-sandbox-..." }`
- Response: `{ "access_token": "access-sandbox-...", "item_id": "..." }`

### Webhook Handler
- **POST** `/api/webhook`
- Receives events from Plaid (e.g., transaction updates)
- Plaid sends `Plaid-Verification` header for signature verification

## Integration Flow

1. **Frontend**: Call `/api/create-link-token` to get a link token
2. **Frontend**: Display Plaid Link modal with the token
3. **User**: Completes bank connection in Link modal
4. **Frontend**: Send public token to `/api/exchange-token`
5. **Backend**: Stores access token securely for API calls
6. **Backend**: Receives webhooks at `/api/webhook` for account updates

## Key Features Included

- ✅ Link token generation
- ✅ Public token exchange (token security)
- ✅ Webhook signature verification with `plaid-link-verify`
- ✅ Error handling with proper HTTP status codes
- ✅ Sandbox environment for testing
- ✅ Health check endpoint

## Security Notes

- **Never expose access tokens** - store them securely in your database
- **Verify webhooks** - use `plaid-link-verify` for signature validation
- **Use environment variables** - don't commit secrets to version control
- **Test in Sandbox** - before going to production

## Testing with Sandbox Credentials

Plaid provides test credentials:
- **Username**: `user_good`
- **Password**: `pass_good`
- Works with major US banks in Sandbox environment

Visit https://plaid.com/docs/#sandbox for more test credentials.

## Next Steps

1. Implement frontend JavaScript to call the endpoints
2. Store access tokens in your database
3. Fetch account/transaction data using the Plaid SDK
4. Deploy to production (switch to Production environment)
5. Update PLAID_SECRET in environment for production

## Resources

- [Plaid Documentation](https://plaid.com/docs)
- [Plaid Python SDK](https://github.com/plaid/plaid-python)
- [Link Flow Guide](https://plaid.com/docs/link/web/)
