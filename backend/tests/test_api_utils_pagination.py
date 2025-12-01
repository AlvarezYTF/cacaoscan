"""
Unit tests for API utils pagination module.
Tests pagination helper functions.
"""
import pytest
from unittest.mock import Mock, MagicMock
from django.core.paginator import Paginator, Page
from django.http import HttpRequest

from api.utils.pagination import (
    get_pagination_params,
    paginate_queryset,
    build_pagination_urls
)


@pytest.fixture
def mock_request():
    """Create a mock HTTP request for testing."""
    request = Mock(spec=HttpRequest)
    request.GET = {}
    request.build_absolute_uri.return_value = "http://example.com/api/items"
    return request


@pytest.fixture
def sample_queryset():
    """Create a sample queryset for testing."""
    return list(range(100))  # 100 items


class TestGetPaginationParams:
    """Tests for get_pagination_params function."""
    
    def test_get_params_default(self, mock_request):
        """Test getting default pagination parameters."""
        page, page_size = get_pagination_params(mock_request)
        
        assert page == 1
        assert page_size == 20
    
    def test_get_params_custom_defaults(self, mock_request):
        """Test getting pagination params with custom defaults."""
        page, page_size = get_pagination_params(mock_request, default_page_size=50)
        
        assert page == 1
        assert page_size == 50
    
    def test_get_params_from_query(self, mock_request):
        """Test getting pagination params from query string."""
        mock_request.GET = {'page': '2', 'page_size': '30'}
        
        page, page_size = get_pagination_params(mock_request)
        
        assert page == 2
        assert page_size == 30
    
    def test_get_params_page_less_than_one(self, mock_request):
        """Test that page less than 1 is corrected to 1."""
        mock_request.GET = {'page': '0', 'page_size': '20'}
        
        page, page_size = get_pagination_params(mock_request)
        
        assert page == 1
        assert page_size == 20
    
    def test_get_params_page_size_exceeds_max(self, mock_request):
        """Test that page size exceeding max is limited."""
        mock_request.GET = {'page': '1', 'page_size': '200'}
        
        page, page_size = get_pagination_params(mock_request, max_page_size=100)
        
        assert page == 1
        assert page_size == 100
    
    def test_get_params_invalid_values(self, mock_request):
        """Test handling of invalid parameter values."""
        mock_request.GET = {'page': 'invalid', 'page_size': 'also_invalid'}
        
        page, page_size = get_pagination_params(mock_request)
        
        # Should return defaults on error
        assert page == 20  # default_page_size
        assert page_size == 20


class TestPaginateQueryset:
    """Tests for paginate_queryset function."""
    
    def test_paginate_queryset_basic(self, sample_queryset):
        """Test basic queryset pagination."""
        page_obj, paginator = paginate_queryset(sample_queryset, page=1, page_size=10)
        
        assert isinstance(page_obj, Page)
        assert isinstance(paginator, Paginator)
        assert len(page_obj) == 10
        assert paginator.count == 100
    
    def test_paginate_queryset_last_page(self, sample_queryset):
        """Test pagination of last page."""
        page_obj, paginator = paginate_queryset(sample_queryset, page=10, page_size=10)
        
        assert len(page_obj) == 10
        assert page_obj.number == 10
    
    def test_paginate_queryset_invalid_page(self, sample_queryset):
        """Test pagination with invalid page number."""
        with pytest.raises(ValueError, match="no existe"):
            paginate_queryset(sample_queryset, page=100, page_size=10)
    
    def test_paginate_queryset_empty(self):
        """Test pagination of empty queryset."""
        empty_queryset = []
        
        with pytest.raises(ValueError):
            paginate_queryset(empty_queryset, page=1, page_size=10)


class TestBuildPaginationUrls:
    """Tests for build_pagination_urls function."""
    
    def test_build_urls_with_next_and_previous(self, mock_request):
        """Test building URLs with both next and previous."""
        mock_request.GET = {'filter': 'active'}
        
        urls = build_pagination_urls(
            mock_request,
            page=2,
            page_size=20,
            has_next=True,
            has_previous=True
        )
        
        assert urls['next'] is not None
        assert urls['previous'] is not None
        assert 'page=3' in urls['next']
        assert 'page=1' in urls['previous']
        assert 'page_size=20' in urls['next']
    
    def test_build_urls_only_next(self, mock_request):
        """Test building URLs with only next page."""
        urls = build_pagination_urls(
            mock_request,
            page=1,
            page_size=20,
            has_next=True,
            has_previous=False
        )
        
        assert urls['next'] is not None
        assert urls['previous'] is None
    
    def test_build_urls_only_previous(self, mock_request):
        """Test building URLs with only previous page."""
        urls = build_pagination_urls(
            mock_request,
            page=2,
            page_size=20,
            has_next=False,
            has_previous=True
        )
        
        assert urls['next'] is None
        assert urls['previous'] is not None
    
    def test_build_urls_no_pages(self, mock_request):
        """Test building URLs with no next or previous."""
        urls = build_pagination_urls(
            mock_request,
            page=1,
            page_size=20,
            has_next=False,
            has_previous=False
        )
        
        assert urls['next'] is None
        assert urls['previous'] is None
    
    def test_build_urls_preserves_query_params(self, mock_request):
        """Test that query parameters are preserved in URLs."""
        mock_request.GET = {'filter': 'active', 'sort': 'name'}
        
        urls = build_pagination_urls(
            mock_request,
            page=2,
            page_size=20,
            has_next=True,
            has_previous=True
        )
        
        assert 'filter=active' in urls['next']
        assert 'sort=name' in urls['next']

