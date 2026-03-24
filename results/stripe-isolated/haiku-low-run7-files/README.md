# Stripe Checkout Integration

A complete Python Flask implementation of Stripe Checkout with webhook handling, product management, and payment processing.

## Features

- ✅ Multiple product pricing plans
- ✅ Secure Stripe Checkout integration
- ✅ Webhook signature verification
- ✅ CSRF protection on payment routes
- ✅ Error handling and validation
- ✅ Session management
- ✅ Test mode support

## Prerequisites

- Python 3.9 or higher
- pip package manager
- A [Stripe account](https://dashboard.stripe.com/register) with API keys
- Git (optional, for version control)

## Setup

### 1. Clone or create the project directory
```bash
cd /path/to/your/project
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and add your Stripe API keys:
```
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
FLASK_SECRET_KEY=your_random_secret_key_here
```

**Get your API keys from:**
- Secret Key: https://dashboard.stripe.com/apikeys
- Webhook Secret: https://dashboard.stripe.com/webhooks

### 5. Run the application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Testing

### Using Test Cards

Stripe provides test card numbers for different scenarios:

| Card Number | Behavior |
|---|---|
| `4242 4242 4242 4242` | Successful payment |
| `4000 0000 0000 0002` | Payment declined |
| `4000 0025 0000 3155` | Requires 3D Secure |

- **Expiry Date:** Any future date (e.g., 12/26)
- **CVC:** Any 3-4 digit number
- **ZIP:** Any 5 digits

### Testing Webhooks Locally

For local development, you need to forward Stripe webhook events to your local server:

1. Install Stripe CLI: https://stripe.com/docs/stripe-cli
2. Authenticate with Stripe:
   ```bash
   stripe login
   ```
3. Forward webhooks to your local app:
   ```bash
   stripe listen --forward-to localhost:5000/webhook
   ```
4. The CLI will provide your webhook signing secret

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
├── README.md            # This file
└── templates/
    ├── index.html       # Product listing page
    ├── success.html     # Payment success page
    └── cancel.html      # Payment cancelled page
```

## API Endpoints

### GET `/`
Home page with product listings

### POST `/create-checkout-session`
Create a Stripe checkout session
- **Request body:**
  ```json
  {
    "product_id": "basic",
    "email": "customer@example.com"
  }
  ```
- **Response:**
  ```json
  {
    "url": "https://checkout.stripe.com/..."
  }
  ```

### GET `/success?session_id={SESSION_ID}`
Payment success confirmation page

### GET `/cancel`
Payment cancellation page

### POST `/webhook`
Stripe webhook endpoint (handles checkout.session.completed events)

## Configuration

### Adding New Products

Edit the `PRODUCTS` dictionary in `app.py`:

```python
PRODUCTS = {
    "your_product_id": {
        "name": "Product Name",
        "price": 9999,  # Price in cents
        "description": "Product description",
    },
}
```

### Webhook Events

The application currently handles:
- `checkout.session.completed` - Payment successful
- `payment_intent.succeeded` - Payment confirmed

Add more events in the `stripe_webhook()` function as needed.

## Deployment

### Production Checklist

- [ ] Update `FLASK_ENV=production` in `.env`
- [ ] Set strong `SECRET_KEY` in `.env`
- [ ] Use environment variables (never hardcode keys)
- [ ] Update URLs in `create_checkout_session()` to your domain
- [ ] Enable HTTPS
- [ ] Set up proper logging
- [ ] Configure webhook endpoint in Stripe dashboard
- [ ] Test with live API keys in test mode first

### Recommended Deployment Platforms

- **Heroku**: `heroku create` and `git push heroku main`
- **AWS**: Deploy to EC2 or Elastic Beanstalk
- **PythonAnywhere**: Simple Python hosting
- **DigitalOcean**: App Platform or Droplet

## Error Handling

The application handles common errors:

- **CardError**: Payment card was declined
- **InvalidRequestError**: Invalid payment request
- **Stripe API Errors**: General API failures

All errors are caught and returned to the user with appropriate HTTP status codes.

## Security Features

- ✅ CSRF protection on payment routes (via `StripeFlask`)
- ✅ Webhook signature verification
- ✅ Session validation
- ✅ Input validation
- ✅ HTTPS required in production

## Support

For issues with:
- **Stripe Integration**: https://support.stripe.com
- **Flask**: https://flask.palletsprojects.com
- **This Project**: Review logs and check `flask log`

## License

MIT License - feel free to use this project as a template.
