"""Unit tests for Plaid Link integration."""

import pytest
import os
from unittest.mock import patch, MagicMock
from app import app, create_link_token, exchange_token


@pytest.fixture
def client():
    """Create a test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestLinkToken:
    """Tests for link token creation."""

    @patch.dict(os.environ, {
        'PLAID_CLIENT_ID': 'test_client_id',
        'PLAID_SECRET': 'test_secret'
    })
    @patch('app.client.link_token_create')
    def test_create_link_token_success(self, mock_create, client):
        """Test successful link token creation."""
        # Mock the Plaid API response
        mock_response = MagicMock()
        mock_response.link_token = 'link-sandbox-test-token'
        mock_create.return_value = mock_response

        response = client.post('/api/create-link-token', json={
            'user_id': 'test-user-123'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert 'link_token' in data
        assert data['link_token'] == 'link-sandbox-test-token'

    def test_create_link_token_missing_credentials(self, client):
        """Test link token creation with missing credentials."""
        with patch.dict(os.environ, {}, clear=True):
            response = client.post('/api/create-link-token', json={
                'user_id': 'test-user-123'
            })
            # Should fail due to missing credentials
            assert response.status_code in [400, 500]


class TestTokenExchange:
    """Tests for token exchange."""

    @patch.dict(os.environ, {
        'PLAID_CLIENT_ID': 'test_client_id',
        'PLAID_SECRET': 'test_secret'
    })
    @patch('app.client.item_public_token_exchange')
    def test_exchange_token_success(self, mock_exchange, client):
        """Test successful token exchange."""
        # Mock the Plaid API response
        mock_response = MagicMock()
        mock_response.access_token = 'access-sandbox-test-token'
        mock_response.item_id = 'item-test-id'
        mock_exchange.return_value = mock_response

        response = client.post('/api/exchange-token', json={
            'public_token': 'public-sandbox-test-token'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'item_id' in data

    def test_exchange_token_missing_public_token(self, client):
        """Test token exchange with missing public token."""
        response = client.post('/api/exchange-token', json={})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


class TestWebhook:
    """Tests for webhook handling."""

    @patch('app.verify_webhook')
    def test_webhook_transactions_update(self, mock_verify, client):
        """Test webhook handling for transaction updates."""
        mock_verify.return_value = {
            'webhook_type': 'TRANSACTIONS',
            'item_id': 'item-test-id'
        }

        response = client.post(
            '/api/webhook',
            data='{"test": "data"}',
            headers={'Plaid-Verification': 'test-signature'}
        )

        assert response.status_code == 200

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
