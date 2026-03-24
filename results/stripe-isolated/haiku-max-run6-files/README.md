# Stripe Checkout Page - Python

A Flask-based Stripe checkout integration with webhook support.

## Prerequisites

- Python 3.9+
- A [Stripe account](https://dashboard.stripe.com/register) with API keys
- pip package manager

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and add your Stripe API keys:

```bash
cp .env.example .env
```

Then edit `.env` with your Stripe credentials:
- Get your **Secret Key** from https://dashboard.stripe.com/apikeys
- Get your **Webhook Signing Secret** from https://dashboard.stripe.com/webhooks

### 3. Run the Application

```bash
python app.py
```

The app will be available at `http://localhost:5000`

## Usage

1. Visit `http://localhost:5000` in your browser
2. Click the "Checkout" button
3. Use one of the Stripe test cards to complete payment:
   - **Success**: `4242 4242 4242 4242`
   - **Decline**: `4000 0000 0000 0002`
   - **3D Secure**: `4000 0025 0000 3155`

## Routes

- `GET /` - Home page with checkout button
- `POST /create-checkout-session` - Creates a Stripe checkout session
- `GET /success` - Success page after payment
- `GET /cancel` - Cancel page if user cancels checkout
- `POST /webhook` - Webhook endpoint for Stripe events

## File Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── CLAUDE.md             # Project guidelines
└── README.md             # This file
```

## Testing with Webhooks

To test webhooks locally, you can use the Stripe CLI:

```bash
# Login to Stripe CLI
stripe login

# Forward webhook events to your local server
stripe listen --forward-to localhost:5000/webhook

# This will output your webhook signing secret - add it to .env
```

## Next Steps

- Customize the product details in `/create-checkout-session`
- Implement order fulfillment in the webhook handler
- Add database integration to persist orders
- Deploy to production using a service like Heroku, Railway, or AWS

## References

- [Stripe Checkout Documentation](https://stripe.com/docs/payments/checkout)
- [Stripe Python SDK](https://github.com/stripe/stripe-python)
- [Flask Documentation](https://flask.palletsprojects.com/)
