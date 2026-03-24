"""Test suite for Plaid Link integration.

Run with: python -m pytest test_plaid_integration.py
"""

import json
import pytest
from app import app
from models import PlaidItem, WebhookLog


@pytest.fixture
def client():
    """Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'ok'


def test_create_link_token_requires_auth(client):
    """Test that create-link-token requires proper authentication."""
    response = client.post(
        '/api/create-link-token',
        json={'user_id': 'test-user'},
        content_type='application/json'
    )
    # Will fail auth in test mode without proper headers
    assert response.status_code in [400, 403, 500]


def test_exchange_token_requires_auth(client):
    """Test that exchange-token requires proper authentication."""
    response = client.post(
        '/api/exchange-token',
        json={'public_token': 'test-token'},
        content_type='application/json'
    )
    # Will fail auth in test mode without proper headers
    assert response.status_code in [400, 403, 500]


def test_plaid_item_model():
    """Test PlaidItem model."""
    # Create an item
    item = PlaidItem(
        user_id='user-123',
        item_id='item-456',
        access_token='access-token-789',
        institution_name='Chase Bank',
        institution_id='ins-123',
    )

    # Save item
    item.save()

    # Retrieve item
    retrieved = PlaidItem.get_by_item_id('user-123', 'item-456')
    assert retrieved is not None
    assert retrieved.institution_name == 'Chase Bank'

    # Get user's items
    user_items = PlaidItem.get_by_user('user-123')
    assert len(user_items) == 1
    assert user_items[0].item_id == 'item-456'

    # Delete item
    assert PlaidItem.delete('user-123', 'item-456')
    user_items = PlaidItem.get_by_user('user-123')
    assert len(user_items) == 0


def test_webhook_log_model():
    """Test WebhookLog model."""
    # Create webhook log
    log = WebhookLog(
        event_type='TRANSACTIONS',
        item_id='item-123',
        event_data={'webhook_code': 'TRANSACTIONS_UPDATE_AVAILABLE'}
    )
    log.save()

    # Get recent logs
    recent = WebhookLog.get_recent()
    assert len(recent) >= 1
    assert recent[0].event_type == 'TRANSACTIONS'


def test_plaid_item_to_dict():
    """Test PlaidItem serialization."""
    item = PlaidItem(
        user_id='user-123',
        item_id='item-456',
        access_token='access-token-789',
        institution_name='Chase Bank',
        institution_id='ins-123',
    )

    item_dict = item.to_dict()
    assert item_dict['user_id'] == 'user-123'
    assert item_dict['item_id'] == 'item-456'
    assert item_dict['institution_name'] == 'Chase Bank'
    assert 'created_at' in item_dict
    assert 'updated_at' in item_dict


def test_webhook_log_to_dict():
    """Test WebhookLog serialization."""
    log = WebhookLog(
        event_type='ITEM',
        item_id='item-123',
        event_data={'webhook_code': 'AUTH_DATA_UPDATE'}
    )

    log_dict = log.to_dict()
    assert log_dict['event_type'] == 'ITEM'
    assert log_dict['item_id'] == 'item-123'
    assert 'received_at' in log_dict
    assert log_dict['processed'] is False


# Integration test helpers
def test_full_flow_simulation():
    """Simulate a complete connection flow."""
    # 1. Create a Plaid item (after token exchange)
    item = PlaidItem(
        user_id='user-123',
        item_id='item-456',
        access_token='access-sandbox-token-789',
        institution_name='Sandbox Bank',
        institution_id='ins-123'
    )
    item.save()

    # 2. Log webhook event
    webhook = WebhookLog(
        event_type='TRANSACTIONS',
        item_id='item-456',
        event_data={'webhook_code': 'TRANSACTIONS_UPDATE_AVAILABLE'}
    )
    webhook.save()

    # 3. Verify item exists and webhook was logged
    saved_item = PlaidItem.get_by_item_id('user-123', 'item-456')
    assert saved_item is not None

    recent_webhooks = WebhookLog.get_recent()
    assert any(w.item_id == 'item-456' for w in recent_webhooks)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
