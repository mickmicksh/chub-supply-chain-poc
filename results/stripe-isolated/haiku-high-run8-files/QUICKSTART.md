# Quick Start Guide

Get your Stripe checkout page running in 5 minutes!

## 1. Install Dependencies

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

## 2. Set Up Stripe API Keys

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. Copy your **Secret Key** (starts with `sk_test_`)
3. Create `.env` file from the template:
   ```bash
   cp .env.example .env
   ```
4. Add your keys to `.env`:
   ```
   STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE
   STRIPE_WEBHOOK_SECRET=whsec_test_YOUR_KEY_HERE
   FLASK_SECRET_KEY=dev-secret-key
   ```

## 3. Run the App

```bash
python app.py
```

Visit: **http://localhost:5000**

## 4. Test a Payment

Use the test card: **4242 4242 4242 4242**
- Expiry: Any future date
- CVC: Any 3 digits
- Email: Any email

## 5. (Optional) Test Webhooks Locally

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe  # macOS

# Forward webhook events to your local server
stripe listen --forward-to localhost:5000/webhook

# Copy the webhook signing secret into your .env file
```

## Project Files

| File | Purpose |
|------|---------|
| `app.py` | Main Flask application with Stripe integration |
| `templates/` | HTML pages (checkout, success, cancel) |
| `requirements.txt` | Python dependencies (pinned versions) |
| `.env` | Your API keys (never commit this!) |
| `README.md` | Full documentation and API reference |

## Common Tasks

### Change Product Name & Price
Edit `app.py` in `create_checkout_session()`:
```python
"product_data": {"name": "Your Product Name"},
"unit_amount": 5000,  # $50.00
```

### Add Multiple Products
Add items to the `line_items` list in `create_checkout_session()`

### Handle Refunds
Add this to the webhook handler:
```python
if event["type"] == "charge.refunded":
    handle_refund(event["data"]["object"])
```

### Go Live
1. Switch to live API keys in `.env`
2. Update success/cancel URLs to your domain
3. Deploy with Gunicorn (don't use Flask's dev server)
4. Set up HTTPS
5. Update webhook URL in Stripe Dashboard

## Troubleshooting

**"Invalid API Key"** → Check your `STRIPE_SECRET_KEY` in `.env`

**"Webhook signature verification failed"** → Update `STRIPE_WEBHOOK_SECRET`

**Page won't load** → Make sure Flask is running: `python app.py`

**Payment button disabled** → Check browser console for errors

## Next Steps

- ✅ Read [full README.md](README.md) for complete documentation
- ✅ Check out [Stripe Docs](https://stripe.com/docs/payments/checkout) for advanced features
- ✅ Learn about [subscriptions](https://stripe.com/docs/payments/checkout/subscriptions)
- ✅ Set up proper logging and monitoring for production
