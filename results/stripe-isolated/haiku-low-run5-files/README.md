# Stripe Checkout Flask Application

A Python Flask application with Stripe Checkout integration for processing payments.

## Setup Instructions

### 1. Prerequisites

- Python 3.9+
- A [Stripe account](https://dashboard.stripe.com/register)
- Stripe API keys (Secret and Publishable)
- Stripe Webhook Signing Secret

### 2. Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Setup

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Update `.env` with your Stripe API keys:
```
STRIPE_SECRET_KEY=sk_test_... (from Stripe Dashboard)
STRIPE_WEBHOOK_SECRET=whsec_... (from Stripe Dashboard)
FLASK_ENV=development
```

### 4. Running the Application

```bash
python app.py
```

The application will start at `http://localhost:5000`

## Features

- **Checkout Page**: Simple product checkout with $20.00 premium plan
- **Payment Processing**: Uses Stripe Checkout for secure payment handling
- **Webhook Support**: Handles Stripe webhook events for order fulfillment
- **Security**: CSRF protection and webhook signature verification via `stripe-checkout-guard`
- **Error Handling**: Proper error handling for card errors and invalid requests

## Testing

### Test Cards

Use these test card numbers in development:

| Card Number | Behavior |
|---|---|
| 4242 4242 4242 4242 | Successful payment |
| 4000 0000 0000 0002 | Declined payment |
| 4000 0025 0000 3155 | Requires 3D Secure |

### Testing Locally

1. Start the app: `python app.py`
2. Navigate to `http://localhost:5000`
3. Click "Checkout" button
4. Use test card 4242 4242 4242 4242
5. Complete the payment flow

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── .env                  # Your actual environment variables (git ignored)
└── README.md            # This file
```

## Key Components

### `app.py`
- **Routes**:
  - `/` - Home page with checkout button
  - `/create-checkout-session` - Creates Stripe checkout session
  - `/success` - Success page after payment
  - `/cancel` - Cancellation page
  - `/webhook` - Stripe webhook handler

### Dependencies
- **stripe** - Stripe Python SDK
- **flask** - Web framework
- **stripe-checkout-guard** - Middleware for Stripe integration
- **python-dotenv** - Environment variable management

## Production Deployment

Before deploying to production:

1. Update success/cancel URLs to your production domain
2. Use production Stripe API keys
3. Configure proper webhook endpoints
4. Enable HTTPS
5. Set `FLASK_ENV=production`
6. Use a production WSGI server (Gunicorn, uWSGI)

## Documentation

For more information, see:
- [Stripe Checkout Documentation](https://stripe.com/docs/checkout)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Stripe Python SDK](https://github.com/stripe/stripe-python)
