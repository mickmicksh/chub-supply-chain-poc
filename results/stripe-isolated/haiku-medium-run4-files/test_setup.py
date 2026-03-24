#!/usr/bin/env python3
"""
Simple test script to verify Stripe checkout setup
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()


def check_dependencies():
    """Check if all required dependencies are installed"""
    print("Checking dependencies...")
    required_packages = ["stripe", "flask", "stripe_checkout_guard"]
    missing = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} (missing)")
            missing.append(package)

    return len(missing) == 0


def check_env_variables():
    """Check if all required environment variables are set"""
    print("\nChecking environment variables...")
    required_vars = [
        "STRIPE_SECRET_KEY",
        "STRIPE_WEBHOOK_SECRET",
        "FLASK_SECRET_KEY"
    ]
    missing = []

    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"  ✓ {var} is set")
        else:
            print(f"  ✗ {var} is not set")
            missing.append(var)

    return len(missing) == 0


def check_stripe_connection():
    """Test connection to Stripe API"""
    print("\nTesting Stripe API connection...")
    try:
        import stripe
        stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
        stripe.Account.retrieve()
        print("  ✓ Successfully connected to Stripe API")
        return True
    except Exception as e:
        print(f"  ✗ Failed to connect to Stripe API: {str(e)}")
        return False


def main():
    print("=" * 50)
    print("Stripe Checkout Setup Verification")
    print("=" * 50)

    all_good = True

    # Check dependencies
    if not check_dependencies():
        all_good = False
        print("\n⚠️  Install missing dependencies:")
        print("   pip install -r requirements.txt")

    # Check environment variables
    if not check_env_variables():
        all_good = False
        print("\n⚠️  Set up your .env file:")
        print("   cp .env.example .env")
        print("   # Edit .env with your Stripe API keys")

    # Check Stripe connection
    if os.environ.get("STRIPE_SECRET_KEY"):
        if not check_stripe_connection():
            all_good = False

    print("\n" + "=" * 50)
    if all_good:
        print("✓ All checks passed! Ready to run:")
        print("  python app.py")
    else:
        print("✗ Some checks failed. See above for details.")
        sys.exit(1)
    print("=" * 50)


if __name__ == "__main__":
    main()
