# Stripe Checkout Setup Guide

## Prerequisites

- Python 3.9+
- A [Stripe account](https://dashboard.stripe.com/register)
- Stripe API keys (from your Stripe Dashboard)

## Installation Steps

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

Copy the `.env.example` file to `.env` and fill in your Stripe API keys:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:
- **STRIPE_SECRET_KEY**: Get from [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
- **STRIPE_PUBLIC_KEY**: Get from [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
- **STRIPE_WEBHOOK_SECRET**: Set up webhooks in [Stripe Dashboard](https://dashboard.stripe.com/webhooks)

### 4. Run the Application

```bash
python app.py
```

The app will be available at: `http://localhost:5000`

## Testing

### Test Credit Cards

Use these test card numbers in the checkout form:

| Number | Behavior |
|--------|----------|
| 4242424242424242 | Success |
| 4000000000000002 | Decline |
| 4000002500003155 | 3D Secure required |

Use any future expiration date and any 3-digit CVC.

## Setting Up Webhooks (for Production)

1. Go to [Stripe Webhooks](https://dashboard.stripe.com/webhooks)
2. Click "Add endpoint"
3. Enter your endpoint URL: `https://yourdomain.com/webhook`
4. Select events: `checkout.session.completed`
5. Copy the signing secret to your `.env` file as `STRIPE_WEBHOOK_SECRET`

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies (pinned versions)
├── .env.example          # Environment variables template
├── CLAUDE.md             # Project guidelines
└── SETUP.md              # This file
```

## Next Steps

1. Implement order fulfillment in the `stripe_webhook()` function
2. Add database support for storing orders
3. Configure CORS if building a separate frontend
4. Deploy to production (e.g., Heroku, AWS, DigitalOcean)

## Troubleshooting

**Module not found errors:**
- Ensure virtual environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

**Stripe API errors:**
- Check that your API keys are correct in `.env`
- Ensure you're using test keys for development

**Webhook issues:**
- Use Stripe CLI for local testing: `stripe listen --forward-to localhost:5000/webhook`
- Check webhook logs in [Stripe Dashboard](https://dashboard.stripe.com/webhooks)
