# Plaid Link Integration Setup Guide

This project integrates Plaid Link for secure bank account connections in your Python application.

## Prerequisites

- Python 3.9+
- pip package manager
- A [Plaid account](https://dashboard.plaid.com) with API keys

## Quick Start

### 1. Create Environment Variables

Copy the example environment file and fill in your Plaid credentials:

```bash
cp .env.example .env
```

Edit `.env` and add your Plaid API credentials from the [Plaid Dashboard](https://dashboard.plaid.com):

```
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_sandbox_secret_here
PLAID_ENV=sandbox
FLASK_ENV=development
FLASK_DEBUG=True
```

### 2. Install Dependencies

Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

### 3. Run the Application

Start the Flask development server:

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## API Endpoints

### `GET /health`
Health check endpoint.

**Response:**
```json
{"status": "ok"}
```

### `POST /api/create-link-token`
Create a Plaid Link token to initiate bank account connection.

**Request Body:**
```json
{
  "user_id": "user-123"
}
```

**Response:**
```json
{
  "link_token": "link-sandbox-...",
  "expiration": "2026-03-24T13:50:00Z"
}
```

### `POST /api/exchange-token`
Exchange Plaid's public token for an access token.

**Request Body:**
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
Plaid webhook endpoint for transaction and account updates.

**Plaid Headers:**
- `Plaid-Verification`: Signature for webhook verification

## Testing with Plaid Sandbox

Use these test credentials in Plaid Link:
- **Username:** user_good
- **Password:** pass_good
- **2FA Code:** 123456 (when prompted)

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies (pinned versions)
├── .env.example          # Example environment variables
├── .env                  # Local environment variables (not in git)
├── .gitignore            # Git ignore rules
├── SETUP.md              # This file
├── CLAUDE.md             # Project guidelines
└── venv/                 # Virtual environment (optional)
```

## Security Considerations

1. **Never commit `.env` files** - Always use `.env.example` as a template
2. **Use webhook verification** - The `@verify.protect` decorator validates webhook signatures
3. **HTTPS in Production** - Always use HTTPS when deploying to production
4. **Token Storage** - Store access tokens securely (encrypted database)
5. **Rate Limiting** - Implement rate limiting on endpoints in production

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PLAID_CLIENT_ID` | Your Plaid Client ID | `abc123...` |
| `PLAID_SECRET` | Your Plaid Secret | `xyz789...` |
| `PLAID_ENV` | Plaid environment | `sandbox` or `production` |
| `FLASK_ENV` | Flask environment | `development` or `production` |
| `FLASK_DEBUG` | Enable Flask debug mode | `True` or `False` |

## Troubleshooting

### Missing Environment Variables
If you see an error about missing environment variables:
1. Make sure `.env` file exists in the project root
2. Check that all required variables are set
3. Restart the Flask application

### Webhook Verification Failures
1. Ensure `PLAID_SECRET` matches exactly in `.env`
2. Verify webhook signature headers are being sent correctly
3. Check Flask logs for detailed error messages

### API Errors
- **400 Bad Request**: Check request body format and required fields
- **401 Unauthorized**: Verify Plaid credentials in `.env`
- **500 Internal Error**: Check Flask logs for detailed error information

## Production Deployment

Before deploying to production:

1. Change `PLAID_ENV` to `production`
2. Use production Plaid credentials
3. Set `FLASK_ENV` to `production`
4. Disable `FLASK_DEBUG`
5. Use a production WSGI server (Gunicorn, uWSGI)
6. Set up proper HTTPS/SSL certificates
7. Configure proper error logging and monitoring
8. Store access tokens in an encrypted database

## Resources

- [Plaid Documentation](https://plaid.com/docs)
- [Plaid Link Integration Guide](https://plaid.com/docs/link)
- [Plaid Python SDK](https://github.com/plaid/plaid-python)
- [Flask Documentation](https://flask.palletsprojects.com)
