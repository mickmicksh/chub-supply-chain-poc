# Plaid Link Integration

A Python Flask application that integrates Plaid Link for secure bank account connections.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Plaid API Credentials

1. Sign up for a Plaid account at [https://dashboard.plaid.com](https://dashboard.plaid.com)
2. Create a new application
3. Copy your Client ID and Secret (use Sandbox credentials for development)

### 3. Configure Environment Variables

Copy the example environment file and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env` and add your Plaid credentials:
```
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_secret_here
```

### 4. Run the Application

```bash
python app.py
```

The app will start on `http://localhost:5000`

## API Endpoints

- **GET `/health`** - Health check endpoint
- **POST `/api/create-link-token`** - Create a Plaid Link token
  - Request body: `{ "user_id": "unique_user_id" }`
  - Response: `{ "link_token": "link-sandbox-..." }`

- **POST `/api/exchange-token`** - Exchange public token for access token
  - Request body: `{ "public_token": "public-sandbox-..." }`
  - Response: `{ "access_token": "access-sandbox-...", "item_id": "..." }`

- **POST `/api/webhook`** - Plaid webhook endpoint for handling events

## Frontend Integration

Open `index.html` in a browser (or serve it via Flask) to test the Plaid Link flow:

1. Click "Connect Bank"
2. Follow the Plaid Link flow (use test credentials for Sandbox)
3. Successfully linked accounts will display the item ID

## Testing with Plaid Sandbox

Plaid provides test credentials in the Link flow. Use:
- **Test bank**: Search for "Plaid" or "Sandbox"
- **Username**: `user_good` or `user_bad` (for error testing)
- **Password**: `pass_good` or `pass_bad`

## Security Notes

- **Never commit `.env`** - Add to `.gitignore`
- **Use HTTPS in production** - Plaid Link requires secure connections
- **Validate tokens server-side** - The `@verifier.protect` decorator validates requests
- **Store access tokens securely** - Use encrypted database fields
- **Implement webhook verification** - Use `verify_webhook()` for signature validation

## Next Steps

1. **Store access tokens**: Implement database storage for access tokens
2. **Add transaction endpoints**: Use `transactions_get()` to retrieve transactions
3. **Handle webhooks**: Process transaction updates and item status changes
4. **Production deployment**: Switch to production Plaid credentials
5. **Error handling**: Implement comprehensive error handling for production

## Resources

- [Plaid API Documentation](https://plaid.com/docs/api/)
- [Plaid Link Documentation](https://plaid.com/docs/link/web/)
- [Plaid Python SDK](https://github.com/plaid/plaid-python)
