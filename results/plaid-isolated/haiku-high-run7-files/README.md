# Plaid Link Integration for Python

This project demonstrates how to integrate Plaid Link into a Python Flask application for secure bank account connections.

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

Copy the `.env.example` file to `.env` and fill in your Plaid credentials:

```bash
cp .env.example .env
```

Edit `.env` and add your Plaid API credentials:

```
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_secret_here
PLAID_ENVIRONMENT=sandbox
```

You can get these from your [Plaid Dashboard](https://dashboard.plaid.com/account/credentials/sandbox).

### 3. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`.

## Project Structure

```
.
├── app.py                 # Main Flask application with Plaid Link endpoints
├── requirements.txt       # Python dependencies (with pinned versions)
├── .env.example          # Environment variables template
├── CLAUDE.md             # Project guidelines
├── README.md             # This file
└── templates/
    └── index.html        # Frontend template with Plaid Link integration
```

## API Endpoints

### `POST /api/create-link-token`

Creates a Plaid Link token for initiating the bank connection flow.

**Request:**
```json
{
  "user_id": "user-123"
}
```

**Response:**
```json
{
  "link_token": "link-sandbox-xxx"
}
```

### `POST /api/exchange-token`

Exchanges the public token returned by Plaid Link for an access token.

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
  "item_id": "item-id-xxx"
}
```

### `POST /api/webhook`

Receives webhook notifications from Plaid (transactions updates, item updates, etc.).

### `GET /health`

Health check endpoint.

## Frontend Integration

The `templates/index.html` file provides a complete example of how to:

1. Request a link token from your backend
2. Initialize Plaid Link with the token
3. Handle the success callback and exchange the public token
4. Display success/error messages to the user

## Security Features

- **Token Verification**: Uses `plaid-link-verify` for server-side token validation
- **Webhook Signature Verification**: Validates webhook signatures with Plaid
- **Environment-based Configuration**: Secrets stored in environment variables
- **Decorator-based Protection**: API endpoints protected with `@verifier.protect` decorator

## Testing

### Test with Sandbox Credentials

1. Start the server
2. Navigate to `http://localhost:5000`
3. Click "Connect Bank Account"
4. Use Plaid's [test credentials](https://plaid.com/docs/sandbox) to test the flow

### Common Test Credentials

- **Username**: `user_good`
- **Password**: `pass_good`
- **Account Type**: Select any bank

## Error Handling

The application includes error handling for:
- Missing environment variables
- Invalid Plaid API credentials
- API request failures
- Webhook verification failures

## Production Deployment

When deploying to production:

1. Change `PLAID_ENVIRONMENT` to `production`
2. Use production API credentials from your Plaid Dashboard
3. Update `FLASK_DEBUG` to `false`
4. Configure HTTPS for all endpoints
5. Set up proper webhook URL in Plaid Dashboard
6. Use a production-grade WSGI server (gunicorn, etc.)

## Next Steps

- Implement transaction retrieval using the access token
- Set up webhook handlers for transaction updates
- Add user account management and token storage
- Implement reconnection flow for expired items

## Documentation

See [Plaid Link Documentation](https://plaid.com/docs/link) for more information.
