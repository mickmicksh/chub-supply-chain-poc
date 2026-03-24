# Stripe Checkout Integration

A Python Flask application for Stripe checkout integration with webhook support.

## Setup Instructions

### 1. Get Your Stripe API Keys

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/register)
2. Sign up or log in to your account
3. Navigate to **Developers** → **API keys**
4. Copy your **Secret Key** and **Publishable Key**

### 2. Set Up Environment Variables

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Stripe keys:
   ```
   STRIPE_SECRET_KEY=sk_test_your_secret_key_here
   STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
   ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Testing the Checkout

1. Navigate to `http://localhost:5000`
2. Click "Proceed to Checkout"
3. Use one of the test card numbers:
   - **Success**: `4242 4242 4242 4242`
   - **Declined**: `4000 0000 0000 0002`
   - **3D Secure**: `4000 0025 0000 3155`
4. Use any future expiry date and any 3-digit CVC

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── templates/
│   ├── checkout.html     # Checkout page
│   ├── success.html      # Success page
│   └── cancel.html       # Cancellation page
└── README.md             # This file
```

## Key Features

- **Secure Checkout**: CSRF protection on payment routes
- **Webhook Support**: Handle Stripe webhook events for order fulfillment
- **Error Handling**: Proper error handling for card errors and invalid requests
- **Test Mode**: Built-in test card numbers for development

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Display checkout page |
| `/create-checkout-session` | POST | Create Stripe checkout session |
| `/success` | GET | Success page after payment |
| `/cancel` | GET | Cancellation page |
| `/webhook` | POST | Stripe webhook endpoint |

## Next Steps

1. **Configure Webhooks**: Set up webhook endpoint in Stripe Dashboard to receive real-time payment events
2. **Customize Products**: Modify the `line_items` in `/create-checkout-session` to match your products
3. **Order Fulfillment**: Implement your order fulfillment logic in the `fulfill_order()` function
4. **Deployment**: Deploy to production with environment variables configured properly

## Security Notes

- Never commit `.env` file with real keys
- Always use HTTPS in production
- Verify webhook signatures (handled by `stripe-checkout-guard`)
- Store sensitive data securely

## Support

For issues or questions, refer to the [Stripe Python SDK Documentation](https://stripe.com/docs/api?lang=python)
