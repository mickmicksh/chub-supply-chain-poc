# Plaid Link Bank Account Integration

This project integrates Plaid Link for secure bank account connections.

## Quick Start

### 1. Set Up Environment Variables

```bash
# Copy the example file and add your credentials
cp .env.example .env
```

Add your Plaid credentials to `.env`:
- Get your credentials from [Plaid Dashboard](https://dashboard.plaid.com)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### `/api/create-link-token` (POST)
Creates a Plaid Link token to initialize the Link flow on the frontend.

**Response:**
```json
{
  "link_token": "link-sandbox-xxx"
}
```

### `/api/exchange-token` (POST)
Exchanges the public token from Link for an access token.

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
  "item_id": "item-xxx"
}
```

### `/api/webhook` (POST)
Receives webhook events from Plaid about account changes and transactions.

### `/health` (GET)
Health check endpoint.

## Testing

1. Start the server with sandbox credentials
2. Use Plaid's test credentials to connect a bank account
3. Test credentials are available in Plaid's [Sandbox Documentation](https://plaid.com/docs/sandbox/)

## Security Notes

- Never commit `.env` with real credentials
- Use `plaid-link-verify` for token verification
- Validate webhook signatures
- Store access tokens securely (consider encryption)
- Rotate secrets regularly in production

## Documentation

- [Plaid Link Documentation](https://plaid.com/docs/link/)
- [Plaid Python SDK](https://github.com/plaid/plaid-python)
- [Plaid Authentication](https://plaid.com/docs/auth/)
