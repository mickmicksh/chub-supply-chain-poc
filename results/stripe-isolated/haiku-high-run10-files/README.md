# Stripe Checkout Integration

A complete Flask-based Stripe checkout implementation following Stripe best practices with webhook support, error handling, and test mode cards.

## Project Structure

```
.
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies (pinned versions)
├── .env.example               # Environment variables template
├── templates/
│   ├── index.html             # Checkout page
│   ├── success.html           # Payment success page
│   └── cancel.html            # Payment cancelled page
└── README.md                  # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your Stripe API keys:

```bash
cp .env.example .env
```

Then edit `.env` with your credentials:

```
STRIPE_SECRET_KEY=sk_test_your_test_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
FLASK_ENV=development
```

**Get your API keys from:** https://dashboard.stripe.com/apikeys

### 3. Run the Application

```bash
python app.py
```

The application will start at `http://localhost:5000`

## Usage

### Main Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Display the checkout page |
| `/create-checkout-session` | POST | Create a Stripe checkout session |
| `/success` | GET | Handle successful payments |
| `/cancel` | GET | Handle cancelled payments |
| `/webhook` | POST | Receive Stripe webhook events |

### Test Mode

The application runs in Stripe **test mode** by default. Use these test cards:

| Card | Number | Behavior |
|------|--------|----------|
| Visa | 4242 4242 4242 4242 | ✓ Success |
| Visa | 4000 0000 0000 0002 | ✗ Decline |
| Visa | 4000 0025 0000 3155 | 3D Secure required |

**Any future expiry date and any 3-digit CVC**

## Features

✓ **Stripe-hosted checkout** - Secure, PCI-compliant payment page
✓ **CSRF protection** - Via stripe-checkout-guard middleware
✓ **Webhook handling** - Listen for payment completion events
✓ **Error handling** - Graceful error messages for card declines
✓ **Session management** - Track payment sessions
✓ **Test mode cards** - Built-in test card references
✓ **Responsive UI** - Mobile-friendly checkout interface

## Implementation Details

### Creating a Checkout Session

```python
session = stripe.checkout.Session.create(
    payment_method_types=["card"],
    line_items=[{
        "price_data": {
            "currency": "usd",
            "product_data": {"name": "Premium Plan"},
            "unit_amount": 2000,  # in cents ($20.00)
        },
        "quantity": 1,
    }],
    mode="payment",
    success_url="http://localhost:5000/success?session_id={CHECKOUT_SESSION_ID}",
    cancel_url="http://localhost:5000/cancel",
)
```

### Handling Webhooks

Stripe sends webhook events to `/webhook`. The current implementation handles:

- `checkout.session.completed` - Called when payment is completed

Add custom logic in the webhook handler to:
- Send confirmation emails
- Update database records
- Activate user accounts
- Create invoices

## Production Deployment

Before deploying to production:

1. **Switch to live keys** in your `.env`:
   ```
   STRIPE_SECRET_KEY=sk_live_your_live_key_here
   ```

2. **Update URLs** in `app.py` to use your production domain:
   ```python
   success_url="https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}",
   cancel_url="https://yourdomain.com/cancel",
   ```

3. **Set up webhook endpoint** in Stripe Dashboard:
   - Go to: Developers → Webhooks → Add Endpoint
   - Endpoint URL: `https://yourdomain.com/webhook`
   - Events: `checkout.session.completed`
   - Copy webhook secret to `.env`

4. **Disable debug mode**:
   ```python
   app.run(port=5000, debug=False)
   ```

5. **Use a production WSGI server** (not Flask dev server):
   ```bash
   pip install gunicorn
   gunicorn app:app
   ```

## Troubleshooting

### "Invalid API Key" Error
- Check that `STRIPE_SECRET_KEY` is set correctly in `.env`
- Make sure you're using a **Secret Key** (starts with `sk_`), not a Publishable Key

### Webhook Not Firing
- Verify webhook secret in `.env` matches Stripe Dashboard
- Check application logs for webhook errors
- Use Stripe Dashboard → Developers → Webhooks to retry failed deliveries

### CORS Issues
- If calling from a different domain, add CORS headers:
  ```python
  from flask_cors import CORS
  CORS(app)
  ```

## Resources

- [Stripe Checkout Documentation](https://stripe.com/docs/payments/checkout)
- [Stripe API Reference](https://stripe.com/docs/api)
- [Stripe Testing Guide](https://stripe.com/docs/testing)
- [Flask Documentation](https://flask.palletsprojects.com/)

## License

MIT
