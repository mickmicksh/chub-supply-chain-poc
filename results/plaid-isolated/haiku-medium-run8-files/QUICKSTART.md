# Plaid Link Integration - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
```bash
cp .env.example .env
```

Edit `.env` and add your Plaid credentials from [Plaid Dashboard](https://dashboard.plaid.com):
```
PLAID_CLIENT_ID=your_client_id_here
PLAID_SECRET=your_sandbox_secret_here
PLAID_ENV=sandbox
```

### 3. Run the Application
```bash
python app.py
```

The app will start on `http://localhost:5000`

### 4. Open the Frontend
Open `index.html` in your browser or serve it through a simple HTTP server:
```bash
# Python 3
python -m http.server 8000

# Then visit http://localhost:8000
```

### 5. Test with Plaid Sandbox Credentials
When Plaid Link opens, use:
- **Username**: `user_good`
- **Password**: `pass_good`

## 📁 Project Structure

```
├── app.py                 # Flask application with Plaid API integration
├── models.py              # Data models for user and bank account storage
├── utils.py               # Helper functions and decorators
├── config.py              # Flask configuration settings
├── index.html             # Frontend UI for Plaid Link
├── test_app.py            # Unit tests
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── SETUP.md              # Detailed setup instructions
└── CLAUDE.md             # Project guidelines
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/create-link-token` | POST | Create a Plaid Link token for the frontend |
| `/api/exchange-token` | POST | Exchange public token for access token |
| `/api/webhook` | POST | Receive Plaid webhook events |
| `/health` | GET | Health check endpoint |

## 📝 Example: Create Link Token

```bash
curl -X POST http://localhost:5000/api/create-link-token \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user-123"}'
```

Response:
```json
{
  "link_token": "link-sandbox-abcdef..."
}
```

## 🧪 Run Tests

```bash
pytest test_app.py -v
```

## 🔐 Security Checklist

- [ ] Never commit `.env` to version control
- [ ] Use HTTPS in production
- [ ] Validate all webhook signatures
- [ ] Store access tokens securely
- [ ] Implement rate limiting
- [ ] Use strong secret keys in production

## 📚 Documentation

- [Plaid Documentation](https://plaid.com/docs)
- [Plaid Link Guide](https://plaid.com/docs/link/)
- [Flask Documentation](https://flask.palletsprojects.com/)

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Use a different port
python app.py --port 5001
```

### Missing Credentials
Ensure `.env` file exists and contains:
- `PLAID_CLIENT_ID`
- `PLAID_SECRET`

### CORS Issues
Update `CORS_ORIGINS` in `.env` to match your frontend URL:
```
CORS_ORIGINS=http://localhost:3000
```

## 📞 Support

- Plaid Support: https://support.plaid.com
- Plaid Status: https://status.plaid.com

## 🎯 Next Steps

1. **Database Integration**: Replace in-memory models with a real database (PostgreSQL, MongoDB, etc.)
2. **Authentication**: Add user authentication and authorization
3. **Account Retrieval**: Implement `/accounts` endpoint to fetch connected accounts
4. **Transactions**: Build transaction sync with webhook handling
5. **Error Handling**: Implement comprehensive error handling and logging
6. **Deployment**: Deploy to production (Heroku, AWS, Google Cloud, etc.)

## 💡 Pro Tips

- Test webhook handling with tools like ngrok for local development
- Monitor Plaid API usage in your dashboard to optimize costs
- Implement transaction caching to reduce API calls
- Set up automated tests for CI/CD pipelines
- Use environment-specific configurations for dev, staging, and production

Good luck! 🎉
