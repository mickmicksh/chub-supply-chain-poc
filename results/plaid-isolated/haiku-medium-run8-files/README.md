# Plaid Link Integration for Python

A complete Python Flask application for integrating Plaid Link to enable secure bank account connections in your application.

## Features

✅ **Plaid Link Integration** - Secure bank account connection flow
✅ **Token Exchange** - Convert public tokens to access tokens
✅ **Webhook Handling** - Process Plaid webhook events
✅ **Production Ready** - Security best practices and error handling
✅ **Responsive UI** - Modern, user-friendly Plaid Link interface
✅ **Comprehensive Tests** - Unit tests for all API endpoints
✅ **Docker Ready** - Easy deployment with containerization

## Tech Stack

- **Backend**: Flask 3.0.0 with Python 3.9+
- **Plaid SDK**: plaid-python 25.1.0
- **Security**: plaid-link-verify for webhook verification
- **Frontend**: Vanilla JavaScript with modern CSS
- **Testing**: pytest with mock support

## Quick Start

### Prerequisites
- Python 3.9 or higher
- [Plaid Account](https://dashboard.plaid.com) with sandbox credentials
- pip package manager

### Installation

1. **Clone and Setup**
```bash
# Navigate to project directory
cd plaid-link-integration

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Plaid credentials
# PLAID_CLIENT_ID=your_client_id
# PLAID_SECRET=your_sandbox_secret
```

3. **Run the Application**
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```
├── app.py                    # Main Flask application
├── models.py                 # Data models
├── config.py                 # Configuration management
├── utils.py                  # Utility functions
├── test_app.py               # Unit tests
├── index.html                # Frontend UI
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── SETUP.md                  # Detailed setup guide
├── QUICKSTART.md             # Quick start guide
└── README.md                 # This file
```

## API Reference

### Create Link Token
Creates a Plaid Link token for the frontend.

**Endpoint**: `POST /api/create-link-token`

**Request**:
```json
{
  "user_id": "user-123"
}
```

**Response**:
```json
{
  "link_token": "link-sandbox-..."
}
```

### Exchange Token
Exchanges a public token for an access token.

**Endpoint**: `POST /api/exchange-token`

**Request**:
```json
{
  "public_token": "public-sandbox-..."
}
```

**Response**:
```json
{
  "access_token": "access-sandbox-...",
  "item_id": "item-..."
}
```

### Webhook Handler
Receives and processes Plaid webhook events.

**Endpoint**: `POST /api/webhook`

**Headers**:
```
Plaid-Verification: <signature>
```

### Health Check
Health check endpoint.

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "ok"
}
```

## Frontend Integration

The `index.html` file provides a complete frontend implementation with:
- Plaid Link integration
- Token exchange handling
- Error management
- Token display and copy functionality
- Responsive design

Open `index.html` in a browser to test the full flow.

## Testing

Run the unit tests:

```bash
# Run all tests
pytest test_app.py -v

# Run with coverage
pytest test_app.py --cov=app

# Run specific test
pytest test_app.py::TestLinkToken::test_create_link_token_success -v
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PLAID_CLIENT_ID` | Yes | - | Plaid API client ID |
| `PLAID_SECRET` | Yes | - | Plaid API secret |
| `PLAID_ENV` | No | `sandbox` | Plaid environment (sandbox/production) |
| `FLASK_ENV` | No | `development` | Flask environment |
| `FLASK_DEBUG` | No | `True` | Flask debug mode |

### Application Configuration

Edit `config.py` to customize:
- Flask settings
- Plaid configuration
- Security options
- Logging level

## Security

### Best Practices

1. **Environment Variables**: Never commit credentials to version control
2. **HTTPS**: Always use HTTPS in production
3. **Webhook Verification**: All webhooks are automatically verified
4. **Token Storage**: Store access tokens securely in your database
5. **Error Handling**: Never expose sensitive information in error messages
6. **Rate Limiting**: Implement rate limiting for production

### CORS Configuration

Update `config.py` to set allowed origins:
```python
CORS_ORIGINS = 'https://yourdomain.com'
```

## Database Integration

The `models.py` file provides classes for:
- `User` - User information and bank connections
- `BankAccount` - Bank account connection data
- `Account` - Individual accounts within a connection
- `Transaction` - Bank transactions
- `PlaidWebhookEvent` - Webhook event tracking

Integrate with your preferred database (PostgreSQL, MongoDB, etc.)

## Webhook Handling

The webhook endpoint automatically:
1. Verifies webhook signature using `plaid-link-verify`
2. Parses the webhook payload
3. Routes to appropriate handlers based on `webhook_type`
4. Returns appropriate HTTP status codes

Example webhook types:
- `TRANSACTIONS` - Transaction updates
- `ITEM` - Item-related updates
- `AUTH` - Authentication-related updates

## Deployment

### Docker

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t plaid-link .
docker run -p 5000:5000 --env-file .env plaid-link
```

### Heroku

1. Create `Procfile`:
```
web: python app.py
```

2. Deploy:
```bash
heroku create your-app-name
git push heroku main
heroku config:set PLAID_CLIENT_ID=your_id
heroku config:set PLAID_SECRET=your_secret
```

## Error Handling

The application handles common errors:
- Invalid credentials
- Missing required fields
- API rate limiting
- Webhook signature verification failures
- Invalid tokens

All errors return appropriate HTTP status codes and error messages.

## Troubleshooting

### Port Already in Use
```bash
# Use environment variable to change port
PORT=5001 python app.py
```

### CORS Errors
Ensure `CORS_ORIGINS` in `config.py` matches your frontend URL.

### Webhook Not Receiving Events
1. Verify webhook URL in Plaid dashboard
2. Check that `PLAID_SECRET` is correct
3. Ensure your server is accessible from the internet
4. Use ngrok for local development: `ngrok http 5000`

### Missing Plaid Credentials
Verify `.env` file exists and contains:
- `PLAID_CLIENT_ID`
- `PLAID_SECRET`

## Testing with Plaid

Use these test credentials in the Plaid Link interface:

**Checking Account**
- Username: `user_good`
- Password: `pass_good`

**Savings Account**
- Username: `user_good`
- Password: `pass_good`

More test credentials available in [Plaid Docs](https://plaid.com/docs/sandbox/).

## Documentation

- [Plaid Documentation](https://plaid.com/docs)
- [Plaid Link Guide](https://plaid.com/docs/link/)
- [Plaid API Reference](https://plaid.com/docs/api/)
- [Flask Documentation](https://flask.palletsprojects.com/)

## Support & Resources

- **Plaid Support**: https://support.plaid.com
- **Plaid Status**: https://status.plaid.com
- **GitHub Issues**: Report issues in this repository

## License

This project is provided as-is for educational and development purposes.

## Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 standards
- All tests pass
- New features include tests
- Documentation is updated

## Next Steps

1. **User Authentication** - Add user login/signup
2. **Database** - Integrate with PostgreSQL or MongoDB
3. **Account Details** - Fetch connected account information
4. **Transaction Sync** - Implement transaction retrieval and syncing
5. **Analytics** - Add usage tracking and analytics
6. **Mobile App** - Create iOS/Android apps using Plaid mobile SDKs
7. **Multi-account** - Support multiple bank connections per user

---

**Happy Banking! 🏦**

For questions or support, visit [Plaid Documentation](https://plaid.com/docs) or contact [Plaid Support](https://support.plaid.com).
