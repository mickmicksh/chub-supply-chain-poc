# Plaid Link Integration

A Python Flask application that integrates Plaid Link for secure bank account connections.

## Features

- Create Plaid Link tokens for initiating account linking
- Exchange public tokens for access tokens
- Handle Plaid webhooks for transaction and item updates
- Comprehensive error handling
- Token verification and webhook signature validation

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

Copy `.env.example` to `.env` and add your Plaid credentials:

```bash
cp .env.example .env
```

Edit `.env` with your Plaid credentials from [https://dashboard.plaid.com](https://dashboard.plaid.com):

```
PLAID_CLIENT_ID=your_client_id
PLAID_SECRET=your_sandbox_secret
```

### 3. Run the Application

```bash
python app.py
```

The app will start on `http://localhost:5000`.

## API Endpoints

### Create Link Token
**POST** `/api/create-link-token`

Creates a token for initializing Plaid Link in your frontend.

**Response:**
```json
{
  "link_token": "link-sandbox-xyz..."
}
```

### Exchange Token
**POST** `/api/exchange-token`

Exchanges the public token received from Plaid Link for an access token.

**Request:**
```json
{
  "public_token": "public-sandbox-xyz..."
}
```

**Response:**
```json
{
  "access_token": "access-sandbox-xyz...",
  "item_id": "item-id-xyz..."
}
```

### Webhook Handler
**POST** `/api/webhook`

Receives webhooks from Plaid. Configure this URL in your Plaid dashboard.

**Supports:**
- `TRANSACTIONS` webhook: Fires when transactions are updated
- `ITEM` webhook: Fires when item-related events occur

### Health Check
**GET** `/health`

Simple health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

## Security Features

- **Token Verification**: Uses `plaid-link-verify` for server-side validation
- **Webhook Signature Verification**: Validates webhook authenticity
- **Protected Routes**: API endpoints are protected with the `@verifier.protect` decorator

## Testing

### Using Plaid Sandbox

The app is configured to use Plaid's Sandbox environment by default. Use Plaid's test credentials:

```bash
# Example test credentials (from Plaid docs)
Email: user_good
Password: pass_good
```

### Manual Testing

1. Create a link token:
```bash
curl -X POST http://localhost:5000/api/create-link-token \
  -H "Content-Type: application/json"
```

2. Check health:
```bash
curl http://localhost:5000/health
```

## Production Deployment

### Environment Configuration

For production, update your environment:

1. Change Plaid environment from `Sandbox` to `Production`
2. Use your production Plaid credentials
3. Set `FLASK_DEBUG=False`
4. Configure a proper WSGI server (Gunicorn, uWSGI, etc.)

### Example with Gunicorn

```bash
pip install gunicorn
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
```

### Webhook Configuration

1. Log in to your Plaid dashboard
2. Go to Team Settings > Webhooks
3. Set your webhook URL to: `https://yourdomain.com/api/webhook`

## Error Handling

The application handles common Plaid errors:

- Invalid credentials
- Invalid tokens
- API rate limits
- Network errors

Errors are returned with appropriate HTTP status codes and error messages.

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| plaid-python | 25.1.0 | Official Plaid Python SDK |
| plaid-link-verify | 1.0.0 | Server-side token verification |
| flask | 3.0.0 | Web framework |
| python-dotenv | 1.0.0 | Environment variable management |

## Documentation

- [Plaid Documentation](https://plaid.com/docs/)
- [Plaid Python SDK](https://github.com/plaid/plaid-python)
- [Flask Documentation](https://flask.palletsprojects.com/)

## License

MIT
