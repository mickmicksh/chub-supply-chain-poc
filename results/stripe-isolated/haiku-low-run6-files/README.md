# Stripe Checkout Python Integration

A Flask-based Stripe Checkout integration with webhook support for payment processing.

## Prerequisites

- Python 3.9+
- A [Stripe account](https://dashboard.stripe.com/register) with API keys
- pip package manager

## Setup

### 1. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and add your Stripe API keys:

```bash
cp .env.example .env
```

Edit `.env` and add:
- `STRIPE_SECRET_KEY`: Your Stripe secret key (from https://dashboard.stripe.com/apikeys)
- `STRIPE_WEBHOOK_SECRET`: Your webhook endpoint secret (from https://dashboard.stripe.com/webhooks)

### 4. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

1. Navigate to `http://localhost:5000`
2. Click the "Checkout" button
3. Use Stripe's test card: **4242 4242 4242 4242**
4. Enter any future expiration date and any CVC
5. Complete the payment

## Testing

### Test Cards

| Number | Behavior |
|--------|----------|
| 4242 4242 4242 4242 | Successful payment |
| 4000 0000 0000 0002 | Card declined |
| 4000 0025 0000 3155 | 3D Secure required |

### Webhook Testing

To test webhooks locally, use Stripe's webhook testing tools:

```bash
# Using Stripe CLI
stripe listen --forward-to localhost:5000/webhook
```

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── .gitignore            # Git ignore rules
├── CLAUDE.md             # Project guidelines
└── README.md             # This file
```

## Key Endpoints

- `GET /` - Checkout page
- `POST /create-checkout-session` - Create Stripe Checkout session
- `GET /success` - Payment success page
- `GET /cancel` - Payment cancelled page
- `POST /webhook` - Stripe webhook handler

## Security Notes

- The `@stripe_ext.protect` decorator on the checkout endpoint provides CSRF protection
- Webhook signatures are verified using `verify_webhook()`
- Never commit your `.env` file with real API keys
- Use environment variables for all sensitive configuration

## Next Steps

1. Customize the product data in `create_checkout_session()`
2. Implement order fulfillment in the `fulfill_order()` function
3. Add database integration for order tracking
4. Set up email notifications for successful payments
5. Deploy to a production environment with HTTPS

## Support

For more information on Stripe Checkout, see the [Stripe documentation](https://stripe.com/docs/checkout).
