# Stripe Checkout Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Your Stripe API Keys

1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Navigate to **Developers** → **API keys**
3. Copy your **Secret Key** and **Publishable Key**

### 3. Set Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and add your actual Stripe API keys:

```
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
FLASK_SECRET_KEY=your-secret-key
```

### 4. Run the Application

```bash
python app.py
```

The app will be available at `http://localhost:5000`

## Testing Checklist

### Test Payment Flow
1. Visit `http://localhost:5000`
2. Click "Checkout" button
3. Use test card: **4242 4242 4242 4242**
4. Enter any future expiry date and any CVC
5. You should be redirected to the success page

### Test Declined Payment
1. Use test card: **4000 0000 0000 0002**
2. This should show an error message

### Test 3D Secure
1. Use test card: **4000 0025 0000 3155**
2. This requires additional authentication

## Webhook Setup (Production)

1. In Stripe Dashboard, go to **Developers** → **Webhooks**
2. Add endpoint: `https://yourdomain.com/webhook`
3. Select events: `checkout.session.completed`
4. Copy the signing secret to `STRIPE_WEBHOOK_SECRET`

## Files Overview

- `app.py` - Main Flask application with Stripe checkout
- `requirements.txt` - Python dependencies (pinned versions)
- `.env.example` - Environment variables template
- `CLAUDE.md` - Project guidelines and dependencies

## Next Steps

- Update the product details in `/create-checkout-session` route
- Implement order fulfillment in the webhook handler
- Add database integration for order tracking
- Set up email confirmations
- Configure for production deployment
