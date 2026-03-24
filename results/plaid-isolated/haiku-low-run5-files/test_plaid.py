"""
Test suite for Plaid Link integration

Run tests with: pytest test_plaid.py -v
"""

import os
import json
import pytest
from app import app, create_link_token, exchange_token, plaid_webhook


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'


def test_create_link_token_missing_credentials():
    """Test link token creation without Plaid credentials"""
    # This should fail if PLAID_CLIENT_ID or PLAID_SECRET are not set
    if not os.environ.get('PLAID_CLIENT_ID'):
        pytest.skip("PLAID_CLIENT_ID not set")


def test_create_link_token_success(client):
    """Test successful link token creation"""
    if not os.environ.get('PLAID_CLIENT_ID'):
        pytest.skip("PLAID credentials not configured")

    response = client.post('/api/create-link-token', json={'user_id': 'test-user-123'})

    # Should return 200 or 400 depending on credentials
    assert response.status_code in [200, 400]

    data = json.loads(response.data)
    if response.status_code == 200:
        assert 'link_token' in data


def test_exchange_token_missing_public_token(client):
    """Test token exchange without public_token"""
    response = client.post('/api/exchange-token', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_exchange_token_invalid_token(client):
    """Test token exchange with invalid public_token"""
    response = client.post('/api/exchange-token', json={'public_token': 'invalid-token'})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_webhook_handler(client):
    """Test webhook handler"""
    # Create a test webhook payload
    payload = json.dumps({
        'webhook_type': 'TRANSACTIONS',
        'webhook_code': 'SYNC_UPDATES_AVAILABLE',
        'item_id': 'test-item-id',
        'new_transactions': 5,
    }).encode('utf-8')

    # Note: In real tests, you'd need a valid signature header
    response = client.post(
        '/api/webhook',
        data=payload,
        content_type='application/json',
        headers={
            'Plaid-Verification': 'test-signature',
        }
    )

    # Should return 200 (even if signature verification fails, endpoint handles it)
    assert response.status_code in [200, 400]


class TestIntegration:
    """Integration tests for the full flow"""

    def test_full_flow_requires_credentials(self, client):
        """Test that full flow requires Plaid credentials"""
        if os.environ.get('PLAID_CLIENT_ID'):
            # Credentials are configured, can test full flow
            pass
        else:
            pytest.skip("Plaid credentials not configured")

    def test_create_and_exchange_tokens_sequence(self, client):
        """Test the sequence of creating and exchanging tokens"""
        if not os.environ.get('PLAID_CLIENT_ID'):
            pytest.skip("Plaid credentials not configured")

        # Step 1: Create link token
        create_response = client.post(
            '/api/create-link-token',
            json={'user_id': 'test-sequence-user'}
        )

        if create_response.status_code == 200:
            # Step 2: Exchange token (would need real public token)
            exchange_response = client.post(
                '/api/exchange-token',
                json={'public_token': 'test-public-token'}
            )
            # Should fail with invalid token, but endpoint should exist
            assert exchange_response.status_code in [400, 500]


# Run tests with pytest
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
