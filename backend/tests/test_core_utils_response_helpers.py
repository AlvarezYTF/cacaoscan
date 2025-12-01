"""
Unit tests for core utils response_helpers module.
Tests response creation functions.
"""
import pytest
from rest_framework import status
from rest_framework.response import Response

from core.utils.response_helpers import (
    create_error_response,
    create_success_response
)


class TestCreateErrorResponse:
    """Tests for create_error_response function."""
    
    def test_create_error_response_basic(self):
        """Test creating a basic error response."""
        response = create_error_response("Test error message")
        
        assert isinstance(response, Response)
        assert response.status_code == 400
        assert response.data['success'] is False
        assert response.data['message'] == "Test error message"
    
    def test_create_error_response_with_error_type(self):
        """Test creating error response with error type."""
        response = create_error_response(
            "Test error",
            error_type="ValidationError",
            status_code=422
        )
        
        assert response.status_code == 422
        assert response.data['error_type'] == "ValidationError"
    
    def test_create_error_response_with_details(self):
        """Test creating error response with details."""
        details = {'field': 'email', 'reason': 'invalid format'}
        response = create_error_response(
            "Validation failed",
            details=details,
            status_code=400
        )
        
        assert response.data['details'] == details
    
    def test_create_error_response_custom_status_code(self):
        """Test creating error response with custom status code."""
        response = create_error_response(
            "Internal error",
            status_code=500
        )
        
        assert response.status_code == 500


class TestCreateSuccessResponse:
    """Tests for create_success_response function."""
    
    def test_create_success_response_basic(self):
        """Test creating a basic success response."""
        response = create_success_response("Operation successful")
        
        assert isinstance(response, Response)
        assert response.status_code == 200
        assert response.data['success'] is True
        assert response.data['message'] == "Operation successful"
    
    def test_create_success_response_with_data(self):
        """Test creating success response with data."""
        data = {'id': 1, 'name': 'test'}
        response = create_success_response(
            "Created successfully",
            data=data,
            status_code=201
        )
        
        assert response.status_code == 201
        assert response.data['id'] == 1
        assert response.data['name'] == 'test'
    
    def test_create_success_response_custom_status_code(self):
        """Test creating success response with custom status code."""
        response = create_success_response(
            "Updated successfully",
            status_code=204
        )
        
        assert response.status_code == 204
    
    def test_create_success_response_data_overrides_message(self):
        """Test that data keys override message in response."""
        data = {'message': 'Different message', 'id': 1}
        response = create_success_response(
            "Original message",
            data=data
        )
        
        # Data should override message
        assert response.data['message'] == 'Different message'
        assert response.data['id'] == 1

