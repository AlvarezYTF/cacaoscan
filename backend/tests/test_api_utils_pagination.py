"""
Tests unitarios para api.utils.pagination.

Cubre todas las funciones de paginación:
- get_pagination_params
- paginate_queryset
- build_pagination_urls
- create_paginated_response
"""
from unittest.mock import Mock, MagicMock, patch
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from rest_framework.response import Response
from rest_framework import status
from rest_framework.serializers import Serializer

from api.utils.pagination import (
    get_pagination_params,
    paginate_queryset,
    build_pagination_urls,
    create_paginated_response
)


class TestSerializer(Serializer):
    """Mock serializer for testing."""
    class Meta:
        fields = ['id', 'username']
    
    def to_representation(self, instance):
        return {'id': instance.id, 'username': instance.username}


class PaginationTestCase(TestCase):
    """Tests para funciones de paginación."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        
        # Create test users
        self.users = []
        for i in range(25):
            user = User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@test.com',
                password='testpass123'
            )
            self.users.append(user)

    def test_get_pagination_params_defaults(self):
        """Test get_pagination_params with default values."""
        request = self.factory.get('/api/test/')
        page, page_size = get_pagination_params(request)
        
        self.assertEqual(page, 1)
        self.assertEqual(page_size, 20)

    def test_get_pagination_params_from_query(self):
        """Test get_pagination_params extracts from query parameters."""
        request = self.factory.get('/api/test/?page=3&page_size=10')
        page, page_size = get_pagination_params(request)
        
        self.assertEqual(page, 3)
        self.assertEqual(page_size, 10)

    def test_get_pagination_params_custom_defaults(self):
        """Test get_pagination_params with custom default page size."""
        request = self.factory.get('/api/test/')
        page, page_size = get_pagination_params(request, default_page_size=50, max_page_size=200)
        
        self.assertEqual(page, 1)
        self.assertEqual(page_size, 50)

    def test_get_pagination_params_enforces_max_page_size(self):
        """Test get_pagination_params enforces max_page_size."""
        request = self.factory.get('/api/test/?page_size=500')
        page, page_size = get_pagination_params(request, max_page_size=100)
        
        self.assertEqual(page_size, 100)

    def test_get_pagination_params_min_page_is_one(self):
        """Test get_pagination_params enforces minimum page of 1."""
        request = self.factory.get('/api/test/?page=0')
        page, page_size = get_pagination_params(request)
        
        self.assertEqual(page, 1)

    def test_get_pagination_params_min_page_size_is_one(self):
        """Test get_pagination_params enforces minimum page_size of 1."""
        request = self.factory.get('/api/test/?page_size=0')
        page, page_size = get_pagination_params(request)
        
        self.assertEqual(page_size, 20)  # Falls back to default

    def test_get_pagination_params_negative_page(self):
        """Test get_pagination_params handles negative page."""
        request = self.factory.get('/api/test/?page=-5')
        page, page_size = get_pagination_params(request)
        
        self.assertEqual(page, 1)

    def test_get_pagination_params_invalid_types(self):
        """Test get_pagination_params handles invalid types gracefully."""
        request = self.factory.get('/api/test/?page=invalid&page_size=also_invalid')
        page, page_size = get_pagination_params(request)
        
        # Should return defaults
        self.assertEqual(page, 20)  # Default when invalid
        self.assertEqual(page_size, 20)

    def test_paginate_queryset_basic(self):
        """Test paginate_queryset with basic queryset."""
        queryset = User.objects.all()
        page_obj, paginator = paginate_queryset(queryset, page=1, page_size=10)
        
        self.assertIsNotNone(page_obj)
        self.assertIsNotNone(paginator)
        self.assertEqual(len(page_obj.object_list), 10)
        self.assertEqual(paginator.count, 25)

    def test_paginate_queryset_last_page(self):
        """Test paginate_queryset with last page."""
        queryset = User.objects.all()
        page_obj, paginator = paginate_queryset(queryset, page=3, page_size=10)
        
        self.assertEqual(len(page_obj.object_list), 5)  # 25 total, 10 per page, page 3 has 5

    def test_paginate_queryset_raises_on_invalid_page(self):
        """Test paginate_queryset raises ValueError for page beyond total."""
        queryset = User.objects.all()
        
        with self.assertRaises(ValueError) as context:
            paginate_queryset(queryset, page=100, page_size=10)
        
        self.assertIn("no existe", str(context.exception).lower())

    def test_paginate_queryset_empty_queryset(self):
        """Test paginate_queryset with empty queryset."""
        User.objects.all().delete()
        queryset = User.objects.all()
        page_obj, paginator = paginate_queryset(queryset, page=1, page_size=10)
        
        self.assertEqual(len(page_obj.object_list), 0)
        self.assertEqual(paginator.count, 0)

    def test_build_pagination_urls_with_next(self):
        """Test build_pagination_urls when has_next is True."""
        request = self.factory.get('/api/test/?filter=value')
        urls = build_pagination_urls(request, page=1, page_size=10, has_next=True, has_previous=False)
        
        self.assertIsNotNone(urls['next'])
        self.assertIsNone(urls['previous'])
        self.assertIn('page=2', urls['next'])
        self.assertIn('page_size=10', urls['next'])

    def test_build_pagination_urls_with_previous(self):
        """Test build_pagination_urls when has_previous is True."""
        request = self.factory.get('/api/test/?page=3')
        urls = build_pagination_urls(request, page=3, page_size=10, has_next=False, has_previous=True)
        
        self.assertIsNone(urls['next'])
        self.assertIsNotNone(urls['previous'])
        self.assertIn('page=2', urls['previous'])
        self.assertIn('page_size=10', urls['previous'])

    def test_build_pagination_urls_preserves_query_params(self):
        """Test build_pagination_urls preserves existing query parameters."""
        request = self.factory.get('/api/test/?filter=value&sort=name')
        urls = build_pagination_urls(request, page=1, page_size=10, has_next=True, has_previous=False)
        
        self.assertIn('filter=value', urls['next'])
        self.assertIn('sort=name', urls['next'])

    def test_build_pagination_urls_first_page(self):
        """Test build_pagination_urls on first page."""
        request = self.factory.get('/api/test/')
        urls = build_pagination_urls(request, page=1, page_size=10, has_next=True, has_previous=False)
        
        self.assertIsNotNone(urls['next'])
        self.assertIsNone(urls['previous'])

    def test_build_pagination_urls_last_page(self):
        """Test build_pagination_urls on last page."""
        request = self.factory.get('/api/test/')
        urls = build_pagination_urls(request, page=5, page_size=5, has_next=False, has_previous=True)
        
        self.assertIsNone(urls['next'])
        self.assertIsNotNone(urls['previous'])

    @patch('api.utils.pagination.get_pagination_params')
    @patch('api.utils.pagination.paginate_queryset')
    @patch('api.utils.pagination.build_pagination_urls')
    def test_create_paginated_response_basic(self, mock_build_urls, mock_paginate, mock_get_params):
        """Test create_paginated_response with basic parameters."""
        # Setup mocks
        mock_get_params.return_value = (1, 20)
        
        queryset = User.objects.all()
        page_obj = Mock()
        page_obj.object_list = queryset[:10]
        page_obj.has_next.return_value = True
        page_obj.has_previous.return_value = False
        
        paginator = Mock()
        paginator.count = 25
        paginator.num_pages = 3
        
        mock_paginate.return_value = (page_obj, paginator)
        mock_build_urls.return_value = {'next': 'http://test/api/test/?page=2', 'previous': None}
        
        request = self.factory.get('/api/test/')
        response = create_paginated_response(request, queryset, TestSerializer)
        
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertIn('page', response.data)
        self.assertIn('page_size', response.data)
        self.assertIn('total_pages', response.data)

    def test_create_paginated_response_real_queryset(self):
        """Test create_paginated_response with real queryset and serializer."""
        queryset = User.objects.all().order_by('id')
        request = self.factory.get('/api/test/?page=1&page_size=10')
        
        response = create_paginated_response(request, queryset, TestSerializer)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 25)
        self.assertEqual(response.data['page'], 1)
        self.assertEqual(response.data['page_size'], 10)
        self.assertEqual(len(response.data['results']), 10)

    def test_create_paginated_response_with_extra_data(self):
        """Test create_paginated_response includes extra_data."""
        queryset = User.objects.all()
        request = self.factory.get('/api/test/')
        extra_data = {'custom_field': 'custom_value'}
        
        response = create_paginated_response(
            request, queryset, TestSerializer,
            extra_data=extra_data
        )
        
        self.assertEqual(response.data['custom_field'], 'custom_value')

    def test_create_paginated_response_with_serializer_context(self):
        """Test create_paginated_response passes serializer_context."""
        queryset = User.objects.all()
        request = self.factory.get('/api/test/')
        serializer_context = {'include_details': True}
        
        with patch('api.utils.pagination.TestSerializer') as mock_serializer_class:
            mock_serializer = Mock()
            mock_serializer.data = [{'id': 1}]
            mock_serializer_class.return_value = mock_serializer
            
            create_paginated_response(
                request, queryset, mock_serializer_class,
                serializer_context=serializer_context
            )
            
            # Check that serializer was instantiated with context
            call_kwargs = mock_serializer_class.call_args[1]
            self.assertIn('include_details', call_kwargs['context'])

    def test_create_paginated_response_invalid_page_returns_error(self):
        """Test create_paginated_response returns error for invalid page."""
        queryset = User.objects.all()
        request = self.factory.get('/api/test/?page=100')
        
        response = create_paginated_response(request, queryset, TestSerializer)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    @patch('api.utils.pagination.getLogger')
    def test_create_paginated_response_exception_handling(self, mock_get_logger):
        """Test create_paginated_response handles exceptions."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        queryset = User.objects.all()
        request = self.factory.get('/api/test/')
        
        # Mock paginate_queryset to raise exception
        with patch('api.utils.pagination.paginate_queryset') as mock_paginate:
            mock_paginate.side_effect = Exception("Unexpected error")
            
            response = create_paginated_response(request, queryset, TestSerializer)
            
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertIn('error', response.data)
            mock_logger.error.assert_called_once()

