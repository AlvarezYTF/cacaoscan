"""
Tests for response helper functions.
"""
import pytest
from rest_framework import status
from rest_framework.response import Response

from core.utils.response_helpers import create_error_response, create_success_response


def test_create_error_response_with_message():
    """Test creating error response with just message."""
    response = create_error_response("Test error message")
    
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['error'] == "Test error message"
    assert response.data['details'] == "Test error message"


def test_create_error_response_with_error_type():
    """Test creating error response with error type."""
    response = create_error_response(
        "Test error",
        error_type="ValidationError"
    )
    
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['error'] == "Test error"
    assert response.data['error_type'] == "ValidationError"


def test_create_error_response_with_custom_status_code():
    """Test creating error response with custom status code."""
    response = create_error_response(
        "Not found",
        status_code=status.HTTP_404_NOT_FOUND
    )
    
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data['error'] == "Not found"


def test_create_error_response_with_dict_details():
    """Test creating error response with dict details."""
    details = {
        'field1': ['Error 1', 'Error 2'],
        'field2': 'Single error'
    }
    response = create_error_response(
        "Validation failed",
        details=details
    )
    
    assert isinstance(response, Response)
    assert response.data['error'] == "Validation failed"
    assert 'field1: Error 1, Error 2' in response.data['details']
    assert 'field2: Single error' in response.data['details']


def test_create_error_response_with_string_details():
    """Test creating error response with string details."""
    response = create_error_response(
        "Error occurred",
        details="Additional details here"
    )
    
    assert isinstance(response, Response)
    assert response.data['error'] == "Error occurred"
    assert response.data['details'] == "Additional details here"


def test_create_error_response_with_none_details():
    """Test creating error response with None details."""
    response = create_error_response("Error message", details=None)
    
    assert isinstance(response, Response)
    assert response.data['error'] == "Error message"
    assert response.data['details'] == "Error message"


def test_create_success_response_with_message():
    """Test creating success response with just message."""
    response = create_success_response("Operation successful")
    
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['success'] is True
    assert response.data['message'] == "Operation successful"


def test_create_success_response_with_data():
    """Test creating success response with data."""
    data = {
        'id': 1,
        'name': 'Test Item',
        'status': 'active'
    }
    response = create_success_response("Created successfully", data=data)
    
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['success'] is True
    assert response.data['message'] == "Created successfully"
    assert response.data['id'] == 1
    assert response.data['name'] == 'Test Item'
    assert response.data['status'] == 'active'


def test_create_success_response_with_custom_status_code():
    """Test creating success response with custom status code."""
    response = create_success_response(
        "Created",
        status_code=status.HTTP_201_CREATED
    )
    
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['success'] is True


def test_create_success_response_with_empty_data():
    """Test creating success response with empty data dict."""
    response = create_success_response("Success", data={})
    
    assert isinstance(response, Response)
    assert response.data['success'] is True
    assert response.data['message'] == "Success"


def test_create_success_response_without_data():
    """Test creating success response without data parameter."""
    response = create_success_response("Success", data=None)
    
    assert isinstance(response, Response)
    assert response.data['success'] is True
    assert response.data['message'] == "Success"
    assert 'id' not in response.data


