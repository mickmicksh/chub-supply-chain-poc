# Plaid Link Bank Account Integration

A Python Flask application integrating Plaid Link for secure bank account connections.

## Features

- 🔐 Secure bank account linking with Plaid Link
- 💳 Token-based authentication
- 🪝 Webhook support for transaction updates
- 📊 Multi-product support (auth, transactions, etc.)
- 🧪 Sandbox environment for testing

## Prerequisites

- Python 3.9+
- Plaid account with API keys ([Sign up](https://dashboard.plaid.com))
- pip package manager

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and add your Plaid credentials:

```bash
cp .env.example .env
```

Edit `.env` with your Plaid credentials:

```
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_secret_here
PLAID_ENV=sandbox
```

You can find your credentials in your [Plaid Dashboard](https://dashboard.plaid.com/team/keys).

### 3. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### 4. Test the Integration

1. Open your browser to `http://localhost:5000`
2. Click "Connect Bank Account"
3. Use Plaid's test credentials:
   - Username: `user_good`
   - Password: `pass_good`
   - Select any bank to test

## API Endpoints

### `POST /api/create-link-token`

Creates a Link token for initializing Plaid Link.

**Request:**
```json
{
  "user_id": "user-123"
}
```

**Response:**
```json
{
  "link_token": "link-sandbox-..."
}
```

### `POST /api/exchange-token`

Exchanges a public token for an access token after successful account linking.

**Request:**
```json
{
  "public_token": "public-sandbox-..."
}
```

**Response:**
```json
{
  "access_token": "access-sandbox-...",
  "item_id": "item-id-..."
}
```

### `POST /api/webhook`

Receives and processes webhook events from Plaid (transactions, item updates, etc.).

**Headers:**
```
Plaid-Verification: <signature>
```

## Project Structure

```
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── static/
│   └── index.html        # Test UI for Plaid Link
└── README.md            # This file
```

## Security Considerations

- **Never commit `.env`** - Add to `.gitignore`
- **Store secrets securely** - Use environment variables or secrets management
- **Verify webhooks** - Use `plaid-link-verify` to validate webhook signatures
- **Use HTTPS in production** - Required for secure token handling
- **Token rotation** - Implement regular token refresh in production

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PLAID_CLIENT_ID` | Your Plaid client ID | `client_id_...` |
| `PLAID_SECRET` | Your Plaid API secret | `secret_...` |
| `PLAID_ENV` | Plaid environment | `sandbox` or `production` |
| `FLASK_ENV` | Flask environment | `development` or `production` |
| `FLASK_DEBUG` | Enable debug mode | `True` or `False` |

## Testing

### Sandbox Credentials

Plaid provides test credentials for development:

- **Successful Auth**: `user_good` / `pass_good`
- **MFA Required**: `user_custom` / `pass_custom`
- **No Transactions**: `user_auth_only` / `pass_auth_only`

See [Plaid Testing Guide](https://plaid.com/docs/sandbox/) for more test credentials.

### CURL Examples

Create link token:
```bash
curl -X POST http://localhost:5000/api/create-link-token \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user-123"}'
```

Exchange public token:
```bash
curl -X POST http://localhost:5000/api/exchange-token \
  -H "Content-Type: application/json" \
  -d '{"public_token": "public-sandbox-abc123"}'
```

## Deployment

### Production Checklist

- [ ] Set `PLAID_ENV=production` with production credentials
- [ ] Enable HTTPS/TLS
- [ ] Set `FLASK_ENV=production` and `FLASK_DEBUG=False`
- [ ] Configure webhook URL in Plaid Dashboard
- [ ] Implement proper logging and monitoring
- [ ] Set up database for storing access tokens
- [ ] Implement token refresh logic
- [ ] Use a production WSGI server (Gunicorn, uWSGI)

### Example Gunicorn Command

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Troubleshooting

### "PLAID_CLIENT_ID and PLAID_SECRET are required"

Ensure your `.env` file exists and contains valid Plaid credentials.

### "Invalid link token"

- Check that your credentials are correct
- Verify you're using the sandbox environment during testing
- Ensure the link token hasn't expired

### Webhook signature verification failed

- Verify the webhook URL is correctly configured in Plaid Dashboard
- Ensure `plaid-link-verify` is installed
- Check that `PLAID_SECRET` matches your Plaid settings

## Resources

- [Plaid Documentation](https://plaid.com/docs/)
- [Plaid Link Integration Guide](https://plaid.com/docs/link/)
- [Plaid Python SDK](https://github.com/plaid/plaid-python)
- [Plaid API Reference](https://plaid.com/docs/api/)

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- [Plaid Support](https://support.plaid.com/)
- [Plaid Community](https://community.plaid.com/)
