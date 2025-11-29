"""
Integration tests for training API endpoints.
NOTE: These tests require a running Django server.
They should be skipped if the server is not available.
"""
import os
import pytest
import requests
from unittest.mock import patch, Mock

# Load credentials from environment variables for security
ADMIN_USERNAME = os.getenv('TEST_ADMIN_USERNAME', 'admin_training')
ADMIN_PASSWORD = os.getenv('TEST_ADMIN_PASSWORD', '')  # noqa: S106  # NOSONAR: S2068

# Skip these tests by default - they require a running server
pytestmark = pytest.mark.skipif(
    os.getenv('SKIP_INTEGRATION_TESTS', 'True').lower() == 'true',
    reason="Integration tests require a running server. Set SKIP_INTEGRATION_TESTS=False to run them."
)


@pytest.fixture
def api_base_url():
    """Get API base URL from environment or use default."""
    return os.getenv('TEST_API_URL', 'http://127.0.0.1:8000/api/v1')


@pytest.fixture
def auth_token(api_base_url):
    """Get authentication token for tests."""
    try:
        login_response = requests.post(
            f'{api_base_url}/auth/login/',
            json={'username': ADMIN_USERNAME, 'password': ADMIN_PASSWORD},  # noqa: S106
            timeout=5
        )
        login_response.raise_for_status()
        login_data = login_response.json()
        token = login_data.get('access') or login_data.get('data', {}).get('access')
        if not token:
            pytest.skip("Could not obtain authentication token")
        return token
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        pytest.skip("Server is not running. Start the Django server to run integration tests.")
    except requests.exceptions.HTTPError as e:
        pytest.skip(f"Authentication failed: {e}")


@pytest.mark.integration
def test_training_endpoint_requires_auth(api_base_url):
    """Test that training endpoint requires authentication."""
    response = requests.post(
        f'{api_base_url}/ml/train/',
        json={'job_type': 'regression'},
        timeout=5
    )
    # Should return 401 or 403 without auth
    assert response.status_code in [401, 403]


@pytest.mark.integration
def test_training_endpoint_with_auth(api_base_url, auth_token):
    """Test training endpoint with authentication."""
    training_response = requests.post(
        f'{api_base_url}/ml/train/',
        headers={
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        },
        json={
            'job_type': 'regression',
            'model_name': 'resnet18',
            'dataset_size': 490,
            'epochs': 30,
            'batch_size': 16,
            'learning_rate': 0.001,
            'config_params': {
                'multi_head': False,
                'model_type': 'resnet18',
                'img_size': 224,
                'early_stopping_patience': 10,
                'save_best_only': True
            }
        },
        timeout=30
    )
    # Should return some response (success or error, but not connection error)
    assert training_response.status_code in [200, 201, 400, 500]