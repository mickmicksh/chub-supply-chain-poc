"""
Test script for Plaid Link integration
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = 'http://localhost:5000'


def test_health_check():
    """Test the health check endpoint."""
    print("Testing health check...")
    response = requests.get(f'{BASE_URL}/health')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    return response.status_code == 200


def test_create_link_token():
    """Test creating a link token."""
    print("Testing create link token...")
    payload = {
        'user_id': 'test-user-123'
    }
    response = requests.post(
        f'{BASE_URL}/api/create-link-token',
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}\n")

    if response.status_code == 200 and 'link_token' in data:
        return True, data.get('link_token')
    return False, None


def test_exchange_token(public_token):
    """Test exchanging a public token for access token."""
    print(f"Testing exchange token with: {public_token}...")
    payload = {
        'public_token': public_token
    }
    response = requests.post(
        f'{BASE_URL}/api/exchange-token',
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
    return response.status_code == 200


def main():
    """Run all tests."""
    print("=" * 60)
    print("Plaid Link Integration Tests")
    print("=" * 60 + "\n")

    # Check environment variables
    if not os.environ.get('PLAID_CLIENT_ID') or not os.environ.get('PLAID_SECRET'):
        print("ERROR: Missing Plaid credentials in .env file")
        print("Please create .env file with PLAID_CLIENT_ID and PLAID_SECRET")
        return

    print("✓ Environment variables configured\n")

    # Test health check
    if not test_health_check():
        print("ERROR: Health check failed. Is the server running on port 5000?")
        return

    # Test create link token
    success, link_token = test_create_link_token()
    if not success:
        print("ERROR: Failed to create link token")
        print("Check your Plaid API credentials")
        return

    print("✓ All tests passed!")
    print(f"\nYour link token: {link_token}")
    print("\nNext steps:")
    print("1. Use this link_token in your frontend to initialize Plaid Link")
    print("2. After user connects their bank, exchange the public_token for access_token")
    print("3. Store the access_token securely for future API calls")


if __name__ == '__main__':
    main()
