"""
Unit tests for ML metrics analysis views.
"""
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
)


class ModelMetricsStatsViewTest(APITestCase):
    """Tests for ModelMetricsStatsView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    def test_metrics_stats_requires_authentication(self):
        """Test that metrics stats requires authentication."""
        url = reverse('ml-metrics-stats')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.ml.metrics_analysis_views.ModelMetrics')
    def test_metrics_stats_success(self, mock_metrics):
        """Test successful metrics stats retrieval."""
        mock_metrics.objects.count.return_value = 10
        mock_metrics.objects.filter.return_value.count.return_value = 5
        mock_metrics.objects.values.return_value.annotate.return_value = []
        mock_metrics.objects.aggregate.return_value = {'average_r2_score': 0.85}
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-metrics-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # La respuesta puede estar en response.data o response.data['data'] dependiendo de create_success_response
        if 'data' in response.data:
            self.assertIn('total_models', response.data['data'])
        else:
            self.assertIn('total_models', response.data)


class ModelPerformanceTrendViewTest(APITestCase):
    """Tests for ModelPerformanceTrendView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    def test_performance_trend_requires_authentication(self):
        """Test that performance trend requires authentication."""
        url = reverse('ml-performance-trend')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.ml.metrics_analysis_views.ModelMetrics')
    def test_performance_trend_success(self, mock_metrics):
        """Test successful performance trend retrieval."""
        # Mock get_performance_trend to return sample trend data
        mock_trend_data = [
            {
                'created_at': '2024-01-01T00:00:00Z',
                'r2_score': 0.85,
                'mae': 2.5,
                'rmse': 3.0,
                'mse': 9.0,
            },
            {
                'created_at': '2024-01-02T00:00:00Z',
                'r2_score': 0.90,
                'mae': 2.0,
                'rmse': 2.5,
                'mse': 6.25,
            }
        ]
        mock_metrics.get_performance_trend.return_value = mock_trend_data
        
        # Mock objects.filter for current_metrics query
        # The view calls: ModelMetrics.objects.filter(...).order_by('-created_at').first()
        mock_current_metric = Mock()
        mock_current_metric.performance_summary = {'r2_score': 0.90, 'mae': 2.0}
        
        mock_order_by = Mock()
        mock_order_by.first.return_value = mock_current_metric
        
        mock_filter = Mock()
        mock_filter.order_by.return_value = mock_order_by
        
        mock_metrics.objects.filter.return_value = mock_filter
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-performance-trend')
        response = self.client.get(url, {
            'model_name': 'test_model',
            'target': 'alto'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # La respuesta puede estar en response.data o response.data['data'] dependiendo de create_success_response
        response_data = response.data.get('data', response.data)
        self.assertIn('trend_data', response_data)
        self.assertIn('improvement_trend', response_data)


class BestModelsViewTest(APITestCase):
    """Tests for BestModelsView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    def test_best_models_requires_authentication(self):
        """Test that best models requires authentication."""
        url = reverse('ml-best-models')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.ml.metrics_analysis_views.ModelMetrics')
    def test_best_models_success(self, mock_metrics):
        """Test successful best models retrieval."""
        mock_queryset = Mock()
        mock_queryset.filter.return_value.order_by.return_value = []
        mock_metrics.objects.filter.return_value = mock_queryset
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-best-models')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # La respuesta puede estar en response.data o response.data['data'] dependiendo de create_success_response
        response_data = response.data.get('data', response.data)
        self.assertIn('best_models', response_data)


class ProductionModelsViewTest(APITestCase):
    """Tests for ProductionModelsView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
    
    def test_production_models_requires_authentication(self):
        """Test that production models requires authentication."""
        url = reverse('ml-production-models')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @patch('api.views.ml.metrics_analysis_views.ModelMetrics')
    def test_production_models_success(self, mock_metrics):
        """Test successful production models retrieval."""
        mock_queryset = Mock()
        mock_queryset.filter.return_value = []
        mock_metrics.objects.filter.return_value = mock_queryset
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        
        url = reverse('ml-production-models')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # La respuesta puede estar en response.data o response.data['data'] dependiendo de create_success_response
        response_data = response.data.get('data', response.data)
        self.assertIn('production_models', response_data)

