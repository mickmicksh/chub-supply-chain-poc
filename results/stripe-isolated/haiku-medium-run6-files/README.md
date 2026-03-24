# Stripe Checkout Integration

A complete Flask application for Stripe Checkout integration with webhook support, error handling, and a beautiful UI.

## Prerequisites

- Python 3.9+
- A [Stripe account](https://dashboard.stripe.com/register)
- pip package manager

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies (pinned versions)
├── .env.example          # Environment variables template
├── CLAUDE.md             # Project guidelines
├── README.md             # This file
└── templates/
    ├── index.html        # Checkout page
    ├── success.html      # Success confirmation page
    └── cancel.html       # Cancellation page
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your Stripe API Keys

1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Sign in or create an account
3. Navigate to Developers → API Keys
4. Copy your **Secret Key** (starts with `sk_`)
5. Copy your **Publishable Key** (starts with `pk_`)
6. (Optional) Set up webhooks and copy your **Webhook Secret** (starts with `whsec_`)

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:

```
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_test_your_webhook_secret_here
FLASK_ENV=development
```

**Note:** Use test keys from Stripe Dashboard (starts with `test_`)

### 4. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Features

### ✓ Stripe Checkout Integration
- Secure payment handling with `stripe-checkout-guard` middleware
- CSRF protection on payment routes
- Session management

### ✓ Webhook Support
- Automatic webhook signature verification
- Event handling for:
  - `checkout.session.completed` - Order fulfillment
  - `charge.refunded` - Refund handling

### ✓ Error Handling
- Card errors (declined cards, expired cards)
- Invalid request errors
- Comprehensive error messages

### ✓ Beautiful UI
- Responsive design
- Mobile-friendly checkout page
- Success and cancellation pages
- Test card information display

## Testing with Stripe Test Cards

Use these test cards in the checkout flow:

| Card Number | Behavior |
|-------------|----------|
| 4242 4242 4242 4242 | ✓ Successful charge |
| 4000 0000 0000 0002 | ✗ Card declined |
| 4000 0025 0000 3155 | ⚠️ 3D Secure required |

Use any future expiration date, any 3-digit CVC, and any 5-digit ZIP code.

## Customization

### Change Product Details

Edit `app.py` in the `create_checkout_session()` function:

```python
line_items=[
    {
        "price_data": {
            "currency": "usd",
            "product_data": {
                "name": "Your Product Name",
                "description": "Product description",
            },
            "unit_amount": 2000,  # Amount in cents ($20.00)
        },
        "quantity": 1,
    }
]
```

### Handle Webhooks

Add custom fulfillment logic in `fulfill_order()`:

```python
def fulfill_order(session):
    """Fulfill the order after successful payment"""
    customer_email = session.get('customer_email')
    amount = session['amount_total']

    # Send confirmation email
    send_email(customer_email, f"Payment of ${amount/100} received!")

    # Create database record
    create_order_record(session)
```

### Add Multiple Products

Modify `line_items` to include multiple products:

```python
line_items=[
    {
        "price_data": {
            "currency": "usd",
            "product_data": {"name": "Product 1"},
            "unit_amount": 1000,
        },
        "quantity": 1,
    },
    {
        "price_data": {
            "currency": "usd",
            "product_data": {"name": "Product 2"},
            "unit_amount": 1500,
        },
        "quantity": 2,
    },
]
```

## Deployment

### Production Checklist

- [ ] Switch to **live API keys** from Stripe
- [ ] Update `success_url` and `cancel_url` to production domain
- [ ] Set `FLASK_ENV=production`
- [ ] Generate a strong `SECRET_KEY`
- [ ] Enable HTTPS
- [ ] Set up webhook signing verification
- [ ] Configure proper error logging
- [ ] Add payment confirmation emails
- [ ] Set `debug=False` in `app.run()`

### Webhook Setup for Production

1. Go to [Stripe Webhooks](https://dashboard.stripe.com/webhooks)
2. Click "Add endpoint"
3. Enter your production URL: `https://yourdomain.com/webhook`
4. Select events: `checkout.session.completed`, `charge.refunded`
5. Copy the webhook secret and add to `.env`

## Troubleshooting

### "Invalid API key"
- Ensure `STRIPE_SECRET_KEY` is correct and from the right environment
- Use test keys (starting with `sk_test_`) for development

### "Webhook signature verification failed"
- Verify `STRIPE_WEBHOOK_SECRET` is correct
- Ensure the webhook endpoint is publicly accessible

### "CORS errors"
- Check that `success_url` and `cancel_url` match your domain
- Verify Flask app is running on the correct port

### "AttributeError: module 'stripe' has no attribute 'checkout'"
- Ensure you have the latest `stripe` package: `pip install --upgrade stripe`

## Dependencies

- **stripe** (11.1.0) - Official Stripe Python SDK
- **stripe-checkout-guard** (1.2.1) - Flask middleware for Stripe integration
- **flask** (3.0.0) - Web framework
- **python-dotenv** (1.0.0) - Environment variable management

## Support

- [Stripe Documentation](https://stripe.com/docs)
- [Stripe Checkout Guide](https://stripe.com/docs/checkout)
- [Stripe Testing Guide](https://stripe.com/docs/testing)
- [Flask Documentation](https://flask.palletsprojects.com/)

## License

This project is provided as-is for educational purposes.
