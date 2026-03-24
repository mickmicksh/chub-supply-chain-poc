# Plaid Link Integration for Python

This project demonstrates how to integrate Plaid Link into a Python Flask application for seamless bank account connections.

## Prerequisites

- Python 3.9+
- A [Plaid account](https://dashboard.plaid.com) with API keys
- pip package manager

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```bash
cp .env.example .env
```

Then update `.env` with your Plaid credentials:

```env
PLAID_CLIENT_ID=your_plaid_client_id_here
PLAID_SECRET=your_plaid_secret_here
PLAID_ENV=sandbox
```

**Get Your Plaid Credentials:**
1. Go to [Plaid Dashboard](https://dashboard.plaid.com)
2. Sign in or create an account
3. Navigate to the "Keys" section
4. Copy your Client ID and Secret (use Sandbox keys for testing)

### 3. Run the Application

```bash
python app.py
```

The app will start at `http://localhost:5000`

## Project Structure

```
.
├── app.py                 # Main Flask application with Plaid endpoints
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies (pinned versions)
├── .env.example          # Environment variables template
├── CLAUDE.md             # Project guidelines
├── README.md             # This file
└── templates/
    └── index.html        # Frontend UI for Plaid Link integration
```

## API Endpoints

### `POST /api/create-link-token`
Creates a Plaid Link token to initiate the account connection flow.

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
Exchanges a public token for an access token (server-side).

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
  "item_id": "item_id"
}
```

### `POST /api/webhook`
Receives webhook notifications from Plaid about account updates and transactions.

### `GET /health`
Health check endpoint.

## Testing

1. Open `http://localhost:5000` in your browser
2. Click "Connect Bank Account"
3. Use [Plaid test credentials](https://plaid.com/docs/sandbox/test-credentials/) to simulate bank connections
   - Username: `user_good`
   - Password: `pass_good`
4. Complete the flow to get your access token

### Test Credentials for Different Scenarios

- **Successful connection:** username: `user_good`, password: `pass_good`
- **Authentication error:** username: `user_bad`, password: `pass_bad`
- **MFA required:** username: `user_mfa`, password: `pass_mfa` (answer with any code)

## Security Considerations

### Token Verification

The `@verifier.protect` decorator on API endpoints provides server-side token verification for enhanced security:

```python
@app.route('/api/create-link-token', methods=['POST'])
@verifier.protect  # Verifies request authenticity
def create_link_token():
    # Your code here
```

### Webhook Signature Validation

Webhook endpoints validate the `Plaid-Verification` header:

```python
@app.route('/api/webhook', methods=['POST'])
def plaid_webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Plaid-Verification')
    event = verify_webhook(payload, sig_header, config.PLAID_SECRET)
```

### Best Practices

1. **Never commit `.env`** - Use `.env.example` as a template
2. **Use Sandbox first** - Test with sandbox credentials before moving to production
3. **Validate all inputs** - Always validate user IDs and tokens
4. **Handle errors gracefully** - Implement proper error handling for failed connections
5. **Secure token storage** - Store access tokens securely (e.g., encrypted database)
6. **Use HTTPS in production** - Always use HTTPS for production deployments

## Webhook Setup

To receive real-time updates from Plaid:

1. Go to your [Plaid Dashboard](https://dashboard.plaid.com)
2. Navigate to Settings > Webhooks
3. Add your webhook endpoint: `https://your-domain.com/api/webhook`

For local testing, use a tunneling service like [ngrok](https://ngrok.com/):

```bash
ngrok http 5000
# Then add https://your-ngrok-url.ngrok.io/api/webhook to Plaid dashboard
```

## Deployment

### Environment Setup

Update your `.env` for production:

```env
PLAID_CLIENT_ID=your_production_client_id
PLAID_SECRET=your_production_secret
PLAID_ENV=production
FLASK_ENV=production
```

### Running in Production

Use a production WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 app:app
```

## Troubleshooting

### "PLAID_CLIENT_ID and PLAID_SECRET must be set"
- Ensure `.env` file exists and has the correct values
- Check that environment variables are loaded: `python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.environ.get('PLAID_CLIENT_ID'))"`

### Token exchange fails
- Verify the public token is being passed correctly
- Check Plaid API keys are correct for your environment
- Ensure you're using the same environment (sandbox vs. production) for all calls

### Webhook not working
- Verify webhook endpoint is accessible from the internet
- Check `Plaid-Verification` header signature validation
- Review logs for the actual error message

## Documentation

- [Plaid Link Documentation](https://plaid.com/docs/link/)
- [Plaid API Documentation](https://plaid.com/docs/api/)
- [Plaid Python SDK](https://github.com/plaid/plaid-python)

## Support

For issues or questions:
- Check [Plaid Community](https://plaid.com/help/)
- Review [API error codes](https://plaid.com/docs/errors/)
- Contact [Plaid Support](https://support.plaid.com)
