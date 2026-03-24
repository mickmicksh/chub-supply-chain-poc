# Plaid Link Integration

A Python Flask application that integrates Plaid Link for secure bank account connections. This setup allows users to connect their bank accounts to your application through Plaid's secure authentication flow.

## Features

- 🏦 Secure bank account linking with Plaid Link
- 🔐 Token verification and webhook signature validation
- 📊 Support for transactions and auth product flows
- 🧪 Sandbox environment for testing
- ⚡ Error handling and logging

## Prerequisites

- Python 3.9+
- A [Plaid account](https://dashboard.plaid.com) with API keys
- pip package manager

## Setup

### 1. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file and add your Plaid credentials:

```bash
cp .env.example .env
```

Edit `.env` with your Plaid credentials:

```
PLAID_CLIENT_ID=your_client_id_from_plaid_dashboard
PLAID_SECRET=your_secret_from_plaid_dashboard
PLAID_ENV=sandbox
FLASK_ENV=development
FLASK_DEBUG=True
```

### 4. Run the Application

```bash
python app.py
```

The application will start at `http://localhost:5000`

## API Endpoints

### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

### POST `/api/create-link-token`
Creates a Plaid Link token to initiate the bank connection flow.

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

### POST `/api/exchange-token`
Exchanges the public token returned by Plaid Link for an access token.

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
  "item_id": "item-..."
}
```

### POST `/api/webhook`
Receives webhook events from Plaid (e.g., transaction updates).

The endpoint automatically verifies webhook signatures using `plaid-link-verify`.

## Testing

### Using the Web Interface

1. Open `http://localhost:5000` in your browser
2. Click "Connect Bank Account"
3. Use Plaid's test credentials to complete the flow
   - Username: `user_good`
   - Password: `pass_good`
   - Verification code: `123456`

### Using cURL

```bash
# Create a link token
curl -X POST http://localhost:5000/api/create-link-token \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user-123"}'

# Exchange token (use the public_token from Plaid Link flow)
curl -X POST http://localhost:5000/api/exchange-token \
  -H "Content-Type: application/json" \
  -d '{"public_token": "public-sandbox-..."}'
```

## Security Considerations

1. **Never commit `.env` file** - It contains sensitive credentials
2. **Use `plaid-link-verify`** - Validates webhook signatures and protects endpoints
3. **Token storage** - Store access tokens securely in your database
4. **HTTPS in production** - Always use HTTPS for production deployments
5. **Environment variables** - Use environment variables for all secrets

## Project Structure

```
.
├── app.py                 # Main Flask application
├── index.html            # Frontend interface for Plaid Link
├── requirements.txt      # Python dependencies (pinned versions)
├── .env.example         # Example environment variables
├── .gitignore           # Git ignore rules
├── README.md            # This file
└── CLAUDE.md            # Project guidelines
```

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| plaid-python | 25.1.0 | Official Plaid Python SDK |
| plaid-link-verify | 2.0.1 | Server-side token verification and webhook signature validation |
| flask | 2.3.3 | Web framework |
| python-dotenv | 1.0.0 | Load environment variables from .env file |
| requests | 2.31.0 | HTTP library |

## Error Handling

The application includes comprehensive error handling:

- **API exceptions** - Gracefully handled with JSON error responses
- **Missing credentials** - Application exits with helpful error message
- **Invalid webhooks** - Webhook signature verification prevents spoofing
- **404/500 errors** - Standard error handlers return JSON responses

## Logging

Enable application logging in development:

```bash
FLASK_ENV=development python app.py
```

## Production Deployment

1. **Update environment**:
   ```
   PLAID_ENV=production
   FLASK_ENV=production
   FLASK_DEBUG=False
   ```

2. **Use a production WSGI server**:
   ```bash
   pip install gunicorn
   gunicorn app:app
   ```

3. **Configure HTTPS** - Use a reverse proxy (nginx, etc.) with SSL

4. **Database setup** - Store access tokens and item IDs in a database

## Troubleshooting

### `ModuleNotFoundError: No module named 'plaid'`
- Ensure virtual environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### `Missing PLAID_CLIENT_ID or PLAID_SECRET`
- Copy `.env.example` to `.env`: `cp .env.example .env`
- Add your Plaid credentials to `.env`

### Webhook signature verification fails
- Ensure `PLAID_SECRET` in `.env` matches your Plaid dashboard secret
- Verify webhook request headers are not modified

## Resources

- [Plaid Documentation](https://plaid.com/docs/)
- [Plaid Link Integration Guide](https://plaid.com/docs/link/)
- [Plaid Python SDK](https://github.com/plaid/plaid-python)
- [Flask Documentation](https://flask.palletsprojects.com/)

## License

This project is provided as-is for educational and development purposes.
