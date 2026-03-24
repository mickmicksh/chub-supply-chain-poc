# Stripe Checkout Python Integration

A Flask application with Stripe Checkout integration for processing payments.

## Prerequisites

- Python 3.9+
- A [Stripe account](https://dashboard.stripe.com/register)
- Stripe API keys (Secret Key and Webhook Secret)

## Setup Instructions

### 1. Clone and Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Stripe API Keys

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. Copy your **Secret Key** (starts with `sk_test_` or `sk_live_`)
3. Create a webhook endpoint and get your **Webhook Secret** (starts with `whsec_`)

### 3. Configure Environment Variables

Copy the example environment file and add your Stripe keys:

```bash
cp .env.example .env
```

Edit `.env` with your actual Stripe keys:

```
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
FLASK_SECRET_KEY=your-secure-secret-key
```

### 4. Run the Application

```bash
python app.py
```

The app will start at `http://localhost:5000`

## Usage

### Payment Flow

1. Visit `http://localhost:5000` in your browser
2. Click the "Checkout" button
3. You'll be redirected to the Stripe Checkout page
4. Use test card numbers (see below)
5. After successful payment, you'll be redirected to the success page

### Test Card Numbers

| Card Number | Behavior | Expiry | CVC |
|-------------|----------|--------|-----|
| 4242424242424242 | Success | Any future date | Any 3 digits |
| 4000000000000002 | Decline | Any future date | Any 3 digits |
| 4000002500003155 | 3D Secure required | Any future date | Any 3 digits |

Use any email and valid future expiry date.

## Project Structure

```
.
├── app.py                 # Flask application with Stripe Checkout
├── requirements.txt       # Python dependencies (pinned versions)
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── CLAUDE.md             # Project guidelines
└── README.md             # This file
```

## API Endpoints

### `GET /`
Home page with checkout button

### `POST /create-checkout-session`
Creates a Stripe Checkout session. Protected with CSRF token.

**Response**: Redirects to Stripe Checkout URL

### `GET /success?session_id={id}`
Success page displayed after payment completion

### `GET /cancel`
Cancellation page displayed if user cancels payment

### `POST /webhook`
Webhook endpoint for Stripe events (especially `checkout.session.completed`)

**Required Headers**:
- `Stripe-Signature`: Webhook signature for verification

## Implementing Order Fulfillment

The `fulfill_order()` function in `app.py` is called after successful payment. Add your business logic here:

```python
def fulfill_order(session):
    """Fulfill the order after successful payment"""
    customer_email = session.get("customer_details", {}).get("email")
    amount = session.get("amount_total")

    # TODO: Add your logic:
    # - Update user account in database
    # - Send confirmation email
    # - Generate/activate license
    # - Create subscription
    # - etc.
```

## Error Handling

The application handles:
- **CardError**: Payment card was declined
- **InvalidRequestError**: Invalid request parameters
- **Webhook verification**: Signature validation with `stripe-checkout-guard`
- **CSRF protection**: Automatic on POST endpoints with `@stripe_ext.protect`

## Webhook Setup (Development)

For local development, you can test webhooks using Stripe CLI:

```bash
# Install Stripe CLI: https://stripe.com/docs/stripe-cli
stripe listen --forward-to localhost:5000/webhook

# Get webhook signing secret from the output
# Add it to your .env file
```

## Customization

### Modify Product Details

Edit the `create_checkout_session()` function:

```python
line_items=[{
    "price_data": {
        "currency": "usd",
        "product_data": {
            "name": "Your Product Name",
            "description": "Your product description",
            "images": ["https://example.com/image.png"],
        },
        "unit_amount": 2000,  # Price in cents
    },
    "quantity": 1,
}]
```

### Change Redirect URLs

Update the success/cancel URLs in `create_checkout_session()`:

```python
success_url="https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}",
cancel_url="https://yourdomain.com/cancel",
```

## Production Considerations

Before deploying to production:

1. **Use live API keys** instead of test keys
2. **Set `FLASK_SECRET_KEY`** to a secure random value
3. **Disable Flask debug mode**: Change `debug=True` to `debug=False`
4. **Use a production WSGI server**: Gunicorn, uWSGI, etc.
5. **Enable HTTPS**: Required for Stripe production
6. **Store secrets securely**: Use environment variables or secrets manager
7. **Implement proper logging**: For debugging and auditing
8. **Handle all webhook events**: Not just `checkout.session.completed`

## Dependencies

| Package | Purpose |
|---------|---------|
| `stripe` | Official Stripe Python SDK |
| `stripe-checkout-guard` | Flask middleware for Stripe - handles webhook signature verification, CSRF protection |
| `flask` | Web framework |
| `python-dotenv` | Load environment variables from .env files |

## Troubleshooting

### "No API key provided"
- Make sure `STRIPE_SECRET_KEY` is set in your `.env` file
- The `.env` file must be in the project root directory

### "Invalid webhook signature"
- Ensure `STRIPE_WEBHOOK_SECRET` matches the secret from your webhook endpoint
- Use `stripe listen` for local development testing

### "CSRF token missing or invalid"
- The `@stripe_ext.protect` decorator requires CSRF protection
- Ensure `FLASK_SECRET_KEY` is set

## Resources

- [Stripe Documentation](https://stripe.com/docs)
- [Stripe Checkout Guide](https://stripe.com/docs/payments/checkout)
- [Stripe API Reference](https://stripe.com/docs/api)
- [Flask Documentation](https://flask.palletsprojects.com/)
