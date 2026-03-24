# Stripe Checkout Integration

A Python Flask application for Stripe Checkout payment processing with webhook support.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and add your Stripe API credentials:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:
- `STRIPE_SECRET_KEY`: Get from https://dashboard.stripe.com/apikeys
- `STRIPE_WEBHOOK_SECRET`: Set up webhooks in Stripe Dashboard and copy the signing secret

### 3. Run the Application

```bash
python app.py
```

The app will run on `http://localhost:5000`

## API Endpoints

### POST `/create-checkout-session`
Creates a Stripe Checkout session and redirects to the payment page.

### POST `/webhook`
Handles Stripe webhook events (e.g., `checkout.session.completed`)

### GET `/health`
Health check endpoint

## Testing

Use Stripe test cards with the application:

| Card Number | Behavior |
|-------------|----------|
| 4242 4242 4242 4242 | Success |
| 4000 0000 0000 0002 | Decline |
| 4000 0025 0000 3155 | 3D Secure required |

All test cards expire in the future and use any 3-digit CVC.

## Production Deployment

Before deploying to production:
1. Replace test API keys with live keys
2. Configure proper SSL/TLS certificates
3. Set up actual webhook endpoints
4. Implement proper order fulfillment logic
5. Add database for storing payment records
