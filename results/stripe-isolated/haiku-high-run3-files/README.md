# Stripe Checkout Integration

A Flask application that implements Stripe Checkout for collecting payments.

## Prerequisites

- Python 3.9+
- A Stripe account: https://dashboard.stripe.com/register
- pip package manager

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your Stripe API Keys

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. Copy your **Secret Key** (starts with `sk_test_`)
3. Create a `.env` file in your project root:

```bash
cp .env.example .env
```

4. Replace `sk_test_your_secret_key_here` with your actual Secret Key

### 3. (Optional) Set Up Webhooks

For testing webhook functionality:

1. Install [Stripe CLI](https://stripe.com/docs/stripe-cli)
2. Authenticate: `stripe login`
3. Forward webhook events: `stripe listen --forward-to localhost:5000/webhook`
4. Copy the webhook signing secret (starts with `whsec_`) and add it to `.env`

## Running the Application

```bash
# Set environment variables
export STRIPE_SECRET_KEY=sk_test_your_key
export STRIPE_WEBHOOK_SECRET=whsec_your_secret  # Optional, only if testing webhooks

# Run the application
python app.py
```

The application will start on `http://localhost:5000`

## Testing with Stripe Test Cards

Use these test card numbers at checkout:

| Card Number | Behavior |
|------------|----------|
| 4242424242424242 | Success |
| 4000000000000002 | Decline |
| 4000002500003155 | 3D Secure required |

For all test cards, use:
- **Expiry Date**: Any future date (e.g., 12/25)
- **CVC**: Any 3 digits (e.g., 123)
- **Cardholder Name**: Any name

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── CLAUDE.md             # Project guidelines
└── README.md             # This file
```

## Features Implemented

✓ Stripe Checkout Session creation
✓ Success and cancellation handling
✓ CSRF protection (via stripe-checkout-guard)
✓ Webhook signature verification
✓ Error handling for card failures
✓ Test card support

## Next Steps

1. **Customize the Product**: Modify the product name, amount, and description in `app.py`
2. **Add Database**: Store order information in a database
3. **Email Confirmation**: Send confirmation emails to customers
4. **Production Deployment**: Switch to live API keys and update URLs

## Documentation

- [Stripe Checkout Documentation](https://stripe.com/docs/payments/checkout)
- [Stripe Python SDK](https://github.com/stripe/stripe-python)
- [Flask Documentation](https://flask.palletsprojects.com/)
