# Plaid Link Integration - Python

A complete, production-ready Python implementation for integrating Plaid Link to securely connect bank accounts.

## Features

✅ Secure token creation and exchange
✅ Webhook validation and event handling
✅ Error handling and logging
✅ Development and production environments
✅ Sandbox testing ready
✅ Example HTML client included

## Prerequisites

- Python 3.9+
- A Plaid account with API keys (free at https://dashboard.plaid.com)
- pip package manager

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example file and add your Plaid credentials:

```bash
cp .env.example .env
```

Edit `.env` with your Plaid credentials:

```env
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_secret_here
PLAID_ENV=sandbox
FLASK_ENV=development
FLASK_DEBUG=True
```

**Get your credentials:**
1. Sign up or log in to [Plaid Dashboard](https://dashboard.plaid.com)
2. Navigate to Team Settings → Keys
3. Copy your Client ID and Secret (use Sandbox keys for testing)

### 3. Run the Application

```bash
python app.py
```

The app will start on `http://localhost:5000`

### 4. Test the Integration

#### Option A: Using the Web Client

Open `http://localhost:5000/client.html` in your browser and:
1. Click "Initialize Link Token"
2. Click "Open Link"
3. Use Plaid test credentials (e.g., username: `user_good`, password: `pass_good`)
4. Authorize the connection

#### Option B: Using cURL

**Create a Link Token:**
```bash
curl -X POST http://localhost:5000/api/create-link-token \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user-123"}'
```

**Exchange a Public Token:**
```bash
curl -X POST http://localhost:5000/api/exchange-token \
  -H "Content-Type: application/json" \
  -d '{"public_token": "public-token-from-link"}'
```

## Architecture

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/create-link-token` | Create Plaid Link token |
| POST | `/api/exchange-token` | Exchange public token for access token |
| POST | `/api/webhook` | Plaid webhook receiver |

### Security Features

- **LinkVerifier**: Protects endpoints with request signature verification
- **Webhook Validation**: Verifies webhook authenticity using Plaid-Verification headers
- **Environment Isolation**: Separate configs for sandbox, development, and production
- **Error Handling**: Graceful error responses without exposing sensitive data

## Key Files

```
├── app.py                 # Main Flask application
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── client.html            # Web client for testing
└── README.md              # This file
```

## API Flow

### Bank Connection Flow

```
1. User clicks "Connect Bank"
   ↓
2. Backend creates Link token → POST /api/create-link-token
   ↓
3. Frontend opens Plaid Link modal with token
   ↓
4. User selects bank and logs in within Plaid Link
   ↓
5. Plaid returns public_token → Frontend sends to backend
   ↓
6. Backend exchanges public_token → POST /api/exchange-token
   ↓
7. Backend receives access_token + item_id
   ↓
8. Store securely in database (encrypted)
```

### Webhook Flow

```
Plaid → POST /api/webhook
   ↓
Verify signature with Plaid-Verification header
   ↓
Process event (TRANSACTIONS, ITEM, etc.)
   ↓
Return 200 OK to acknowledge receipt
```

## Webhook Events

### TRANSACTIONS Webhook

Fired when new transactions are available or synced:

```python
{
    "webhook_type": "TRANSACTIONS",
    "webhook_code": "SYNC_UPDATES_AVAILABLE",
    "item_id": "...",
    "initial_update_complete": true,
    "new_transactions": 5
}
```

### ITEM Webhook

Fired for account or institution-level events:

```python
{
    "webhook_type": "ITEM",
    "webhook_code": "ERROR",
    "item_id": "...",
    "error": {
        "error_type": "ITEM_LOGIN_REQUIRED",
        "error_code": "ITEM_LOGIN_REQUIRED"
    }
}
```

## Testing in Sandbox

Plaid provides test credentials for sandbox environments:

### Test Users

| Username | Password | Behavior |
|----------|----------|----------|
| `user_good` | `pass_good` | Successful login |
| `user_bad` | `pass_bad` | Invalid credentials |
| `user_locked` | `pass_locked` | Account locked |

### Test Institutions

Search for these in the institution search during Link flow:
- Chase
- Bank of America
- Wells Fargo
- Any US bank

## Production Deployment

### Before Going Live

1. **Switch to Production Keys**
   ```env
   PLAID_ENV=production
   PLAID_CLIENT_ID=prod_client_id
   PLAID_SECRET=prod_secret
   ```

2. **Secure Token Storage**
   - Encrypt access tokens at rest
   - Use HTTPS only (no HTTP in production)
   - Store in secure database with encryption

3. **Webhook Configuration**
   - Register your webhook URL in Plaid Dashboard
   - Must be publicly accessible HTTPS endpoint
   - Implement proper error handling and retries

4. **Environment Variables**
   - Never commit `.env` files
   - Use environment-specific configuration
   - Use secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.)

5. **Error Handling**
   - Log errors for monitoring
   - Don't expose sensitive data in responses
   - Implement proper status codes

6. **Rate Limiting**
   - Implement rate limiting on endpoints
   - Monitor API usage against Plaid quotas

## Troubleshooting

### "PLAID_CLIENT_ID and PLAID_SECRET must be set"

**Solution:** Ensure `.env` file exists and has correct values:
```bash
cat .env  # Check if PLAID_CLIENT_ID and PLAID_SECRET are set
```

### "Invalid public_token"

**Solution:** Public tokens expire after 30 minutes. Create a new Link token and exchange immediately.

### Webhook not received

**Solution:**
1. Verify webhook URL is publicly accessible (not localhost)
2. Check Plaid Dashboard → Webhook Settings
3. Use Plaid's webhook tester to verify endpoint

### "INVALID_REQUEST" errors

**Solution:** Ensure:
- Credentials are from the correct environment (sandbox vs production)
- Request body is valid JSON
- All required fields are present

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| plaid-python | 25.1.0 | Official Plaid Python SDK |
| plaid-link-verify | 1.2.3 | Server-side token & webhook verification |
| flask | 3.0.0 | Web framework |
| python-dotenv | 1.0.0 | Environment variable management |

## Documentation

- [Plaid Documentation](https://plaid.com/docs/)
- [Plaid Link Guide](https://plaid.com/docs/link/)
- [API Reference](https://plaid.com/docs/api/)
- [Webhook Reference](https://plaid.com/docs/api/webhooks/)

## Security Considerations

- **Never log or expose access tokens**
- **Always validate webhook signatures**
- **Use HTTPS in production**
- **Encrypt tokens at rest**
- **Implement proper access control**
- **Monitor and audit token usage**
- **Rotate credentials regularly**

## Support

For issues with Plaid, visit [Plaid Support](https://support.plaid.com) or check the [Status Page](https://status.plaid.com/).

## License

This example is provided as-is for educational purposes.
