# Stripe Checkout Integration

A Python Flask application for integrating Stripe checkout payments with proper error handling, webhook verification, and session management.

## Features

- ✅ Simple checkout flow with Stripe Hosted Checkout
- ✅ Flask middleware for CSRF protection and webhook signature verification
- ✅ Error handling for card and request errors
- ✅ Webhook endpoint for payment completion events
- ✅ Test card support for development

## Setup Instructions

### 1. Prerequisites

- Python 3.9+
- A [Stripe account](https://dashboard.stripe.com/register) with API keys
- pip package manager

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file and add your Stripe API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
- Get your `STRIPE_SECRET_KEY` from [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
- Get your `STRIPE_WEBHOOK_SECRET` after setting up webhooks (see below)

```
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

### 4. Run the Application

```bash
python app.py
```

The application will start at `http://localhost:5000`

## Usage

### Checkout Flow

1. Visit `http://localhost:5000/` to see the home page
2. Click the "Checkout" button to create a checkout session
3. Use test card numbers to complete payment:
   - **Success**: `4242 4242 4242 4242`
   - **Decline**: `4000 0000 0000 0002`
   - **3D Secure**: `4000 0025 0000 3155`

### Webhook Setup (Production)

To receive payment completion events:

1. Go to [Stripe Webhooks](https://dashboard.stripe.com/webhooks)
2. Click "Add endpoint"
3. Set the endpoint URL to your server: `https://yourdomain.com/webhook`
4. Select events: `checkout.session.completed`
5. Copy the signing secret and add it to your `.env` file

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page with checkout button |
| POST | `/create-checkout-session` | Create a checkout session |
| GET | `/success` | Success page after payment |
| GET | `/cancel` | Cancellation page |
| POST | `/webhook` | Stripe webhook receiver |
| GET | `/health` | Health check |

## Testing

The app includes test endpoints for development:

- Use [Stripe Test Cards](https://stripe.com/docs/testing) to simulate payments
- No real charges are made with test API keys
- Monitor webhooks in [Stripe Dashboard → Webhooks](https://dashboard.stripe.com/webhooks)

## Project Structure

```
.
├── app.py                 # Flask application with checkout logic
├── requirements.txt       # Python dependencies with pinned versions
├── .env.example          # Example environment variables
├── .gitignore            # Git ignore rules
├── CLAUDE.md             # Project guidelines
└── README.md             # This file
```

## Code Style

- Python 3.9+
- PEP 8 compliant
- All dependencies pinned to specific versions

## Next Steps

1. ✅ Create a virtual environment: `python -m venv venv && source venv/bin/activate`
2. ✅ Install dependencies: `pip install -r requirements.txt`
3. ✅ Set up environment variables: `cp .env.example .env && # edit .env`
4. ✅ Run the app: `python app.py`
5. Add order fulfillment logic in the `stripe_webhook()` function
6. Deploy to production with your domain
7. Set up webhook endpoint in Stripe Dashboard

## Documentation

- [Stripe Checkout Docs](https://stripe.com/docs/payments/checkout)
- [Stripe API Reference](https://stripe.com/docs/api)
- [Flask Documentation](https://flask.palletsprojects.com/)

## Support

For issues or questions:
- Check [Stripe Documentation](https://stripe.com/docs)
- Review [Stripe Support](https://support.stripe.com)
