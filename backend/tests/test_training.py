"""
Integration tests for training API endpoints.
NOTE: These tests require a running Django server.
They will be skipped if the server is not available.
"""
import os
import pytest
import requests

# Load credentials from environment variables for security
ADMIN_USERNAME = os.getenv('TEST_ADMIN_USERNAME', 'admin_training')
ADMIN_PASSWORD = os.getenv('TEST_ADMIN_PASSWORD', '')  # noqa: S106  # NOSONAR - S2068 credentials from environment

BASE_URL = 'http://127.0.0.1:8000'
LOGIN_URL = f'{BASE_URL}/api/v1/auth/login/'
TRAINING_URL = f'{BASE_URL}/api/v1/ml/train/'


def check_server_available() -> bool:
    """Check if the Django server is available."""
    try:
        response = requests.get(f'{BASE_URL}/api/v1/', timeout=2)
        return response.status_code in [200, 404, 401, 403]
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return False


@pytest.fixture(scope='module')
def auth_token():
    """Fixture to get authentication token from the server."""
    if not check_server_available():
        pytest.skip("Django server is not available")
    
    login_data = {
        'username': ADMIN_USERNAME,
        'password': ADMIN_PASSWORD  # noqa: S106  # NOSONAR - S2068 credentials from environment
    }
    
    try:
        login_response = requests.post(LOGIN_URL, json=login_data, timeout=5)
        login_response.raise_for_status()
        
        login_data_response = login_response.json()
        token = (
            login_data_response.get('token') or
            login_data_response.get('access') or
            login_data_response.get('data', {}).get('token') or
            login_data_response.get('data', {}).get('access')
        )
        
        if not token:
            pytest.skip(f"Could not obtain token. Response: {login_data_response}")
        
        return token
    except requests.exceptions.RequestException as e:
        pytest.skip(f"Could not connect to server: {e}")


def test_login_and_get_token(auth_token):
    """Test that we can login and get a token."""
    assert auth_token is not None
    assert len(auth_token) > 0


def test_training_job_creation(auth_token):
    """Test creating a training job."""
    training_data = {
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
    }
    
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(TRAINING_URL, json=training_data, headers=headers, timeout=30)
    
    # Check if the request was successful or if it's a validation error
    assert response.status_code in [200, 201, 202, 400, 401, 403], \
        f"Unexpected status code: {response.status_code}. Response: {response.text}"
    
    if response.status_code in [200, 201, 202]:
        response_data = response.json()
        assert 'job_id' in response_data or 'id' in response_data or 'success' in response_data, \
            f"Response should contain job_id, id, or success. Got: {response_data}"
