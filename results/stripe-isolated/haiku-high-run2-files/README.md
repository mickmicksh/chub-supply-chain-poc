# Stripe Checkout Payment Page

A Python Flask application for integrating Stripe Checkout for payment processing.

## Prerequisites

- Python 3.9+
- A [Stripe account](https://dashboard.stripe.com/register)
- pip package manager

## Installation

1. **Clone the repository and install dependencies:**

```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**

Copy `.env.example` to `.env` and fill in your Stripe API keys:

```bash
cp .env.example .env
```

Get your API keys from:
- **Secret Key** & **Publishable Key**: https://dashboard.stripe.com/apikeys
- **Webhook Secret**: Create a webhook endpoint at https://dashboard.stripe.com/webhooks

3. **Load environment variables:**

For local development, you can use `python-dotenv`:

```bash
pip install python-dotenv
```

Then add this to the top of `app.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Running the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Features

- **Home Page** (`/`) - Displays a product with checkout button
- **Checkout Session** (`/create-checkout-session`) - Creates a Stripe checkout session
- **Success Page** (`/success`) - Shown after successful payment
- **Cancel Page** (`/cancel`) - Shown if payment is cancelled
- **Webhook Handler** (`/webhook`) - Processes Stripe webhook events

## Testing with Test Cards

Use these test card numbers with any future expiration date and any 3-digit CVC:

| Number | Behavior |
|--------|----------|
| `4242 4242 4242 4242` | Successful charge |
| `4000 0000 0000 0002` | Card declined |
| `4000 0025 0000 3155` | 3D Secure authentication required |

## Production Deployment

Before deploying to production:

1. Replace test API keys with live keys from Stripe Dashboard
2. Set `debug=False` in Flask configuration
3. Use a production WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```
4. Use HTTPS for all endpoints
5. Validate webhook signatures using your webhook secret
6. Implement proper order fulfillment in the webhook handler

## Files

- `app.py` - Main Flask application with Stripe integration
- `requirements.txt` - Python dependencies with pinned versions
- `.env.example` - Template for environment variables
- `CLAUDE.md` - Project guidelines and dependencies

## Security Notes

- Never commit `.env` file or real API keys to version control
- The `@stripe_ext.protect` decorator handles CSRF protection
- Webhook signatures are verified using your webhook secret
- Always validate payment intents on the server side
