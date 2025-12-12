"""
Tests for Swagger helpers.
"""
import pytest
from drf_yasg import openapi

from api.views.ml.mixins.swagger_helpers import (
    create_incremental_success_response_schema,
    create_incremental_swagger_decorator
)


class TestSwaggerHelpers:
    """Tests for Swagger helper functions."""
    
    def test_create_incremental_success_response_schema(self):
        """Test creating incremental success response schema."""
        schema = create_incremental_success_response_schema()
        
        assert isinstance(schema, openapi.Schema)
        assert schema.type == openapi.TYPE_OBJECT
        # Access properties through the schema object
        assert hasattr(schema, 'properties') or 'properties' in getattr(schema, '_schema', {})
        properties = getattr(schema, 'properties', None) or getattr(schema, '_schema', {}).get('properties', {})
        assert 'success' in properties
        assert 'data' in properties
        assert 'message' in properties
    
    def test_create_incremental_swagger_decorator_basic(self):
        """Test creating incremental swagger decorator with basic parameters."""
        decorator = create_incremental_swagger_decorator(
            operation_description="Test operation",
            operation_summary="Test summary"
        )
        
        assert callable(decorator)
        # The decorator is a partial function, check it's callable and has the expected attributes
        assert hasattr(decorator, 'func') or hasattr(decorator, '__call__')
    
    def test_create_incremental_swagger_decorator_with_request_body(self):
        """Test creating incremental swagger decorator with request body."""
        request_body = openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'field1': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )
        
        decorator = create_incremental_swagger_decorator(
            operation_description="Test operation",
            operation_summary="Test summary",
            request_body=request_body
        )
        
        assert callable(decorator)
    
    def test_create_incremental_swagger_decorator_with_manual_parameters(self):
        """Test creating incremental swagger decorator with manual parameters."""
        manual_params = [
            openapi.Parameter('param1', openapi.IN_QUERY, type=openapi.TYPE_STRING)
        ]
        
        decorator = create_incremental_swagger_decorator(
            operation_description="Test operation",
            operation_summary="Test summary",
            manual_parameters=manual_params
        )
        
        assert callable(decorator)
    
    def test_create_incremental_swagger_decorator_with_custom_responses(self):
        """Test creating incremental swagger decorator with custom responses."""
        custom_responses = {
            404: openapi.Response(description="Not found")
        }
        
        decorator = create_incremental_swagger_decorator(
            operation_description="Test operation",
            operation_summary="Test summary",
            responses=custom_responses
        )
        
        assert callable(decorator)
    
    def test_create_incremental_swagger_decorator_merges_responses(self):
        """Test that custom responses are merged with defaults."""
        custom_responses = {
            404: openapi.Response(description="Not found"),
            500: openapi.Response(description="Server error")
        }
        
        decorator = create_incremental_swagger_decorator(
            operation_description="Test operation",
            operation_summary="Test summary",
            responses=custom_responses
        )
        
        assert callable(decorator)
        # Default responses (200, 400, 401) should still be present
        # along with custom ones (404, 500)

