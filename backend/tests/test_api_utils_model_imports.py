"""
Tests unitarios para api.utils.model_imports.

Cubre todas las funciones de importación segura de modelos:
- get_model_safely
- get_models_safely
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth.models import User

from api.utils.model_imports import (
    get_model_safely,
    get_models_safely
)


class ModelImportsTestCase(TestCase):
    """Tests para funciones de importación de modelos."""

    def test_get_model_safely_valid_model(self):
        """Test get_model_safely with valid model path."""
        result = get_model_safely('django.contrib.auth.models.User')
        
        self.assertEqual(result, User)

    def test_get_model_safely_invalid_module(self):
        """Test get_model_safely with invalid module path."""
        result = get_model_safely('nonexistent.module.NonexistentModel')
        
        self.assertIsNone(result)

    def test_get_model_safely_invalid_class(self):
        """Test get_model_safely with valid module but invalid class."""
        result = get_model_safely('django.contrib.auth.models.NonexistentModel')
        
        self.assertIsNone(result)

    def test_get_model_safely_invalid_path_format(self):
        """Test get_model_safely with invalid path format."""
        result = get_model_safely('invalid_path')
        
        self.assertIsNone(result)

    def test_get_model_safely_empty_string(self):
        """Test get_model_safely with empty string."""
        result = get_model_safely('')
        
        self.assertIsNone(result)

    @patch('api.utils.model_imports.logger')
    def test_get_model_safely_logs_on_failure(self, mock_logger):
        """Test get_model_safely logs debug message on failure."""
        get_model_safely('nonexistent.module.Model')
        
        mock_logger.debug.assert_called_once()
        log_message = mock_logger.debug.call_args[0][0]
        self.assertIn("Could not import", log_message)

    def test_get_models_safely_single_valid_model(self):
        """Test get_models_safely with single valid model."""
        models = get_models_safely({
            'User': 'django.contrib.auth.models.User'
        })
        
        self.assertIn('User', models)
        self.assertEqual(models['User'], User)

    def test_get_models_safely_multiple_valid_models(self):
        """Test get_models_safely with multiple valid models."""
        models = get_models_safely({
            'User': 'django.contrib.auth.models.User',
            'Group': 'django.contrib.auth.models.Group'
        })
        
        self.assertIn('User', models)
        self.assertIn('Group', models)
        self.assertIsNotNone(models['User'])
        self.assertIsNotNone(models['Group'])

    def test_get_models_safely_mixed_valid_invalid(self):
        """Test get_models_safely with mix of valid and invalid models."""
        models = get_models_safely({
            'User': 'django.contrib.auth.models.User',
            'Invalid': 'nonexistent.module.InvalidModel'
        })
        
        self.assertIn('User', models)
        self.assertIn('Invalid', models)
        self.assertEqual(models['User'], User)
        self.assertIsNone(models['Invalid'])

    def test_get_models_safely_all_invalid(self):
        """Test get_models_safely with all invalid models."""
        models = get_models_safely({
            'Model1': 'nonexistent.module.Model1',
            'Model2': 'nonexistent.module.Model2'
        })
        
        self.assertIn('Model1', models)
        self.assertIn('Model2', models)
        self.assertIsNone(models['Model1'])
        self.assertIsNone(models['Model2'])

    def test_get_models_safely_empty_dict(self):
        """Test get_models_safely with empty dictionary."""
        models = get_models_safely({})
        
        self.assertEqual(models, {})

    def test_get_models_safely_preserves_variable_names(self):
        """Test get_models_safely preserves variable names as keys."""
        models = get_models_safely({
            'CacaoImage': 'nonexistent.models.CacaoImage',
            'CacaoPrediction': 'nonexistent.models.CacaoPrediction'
        })
        
        self.assertIn('CacaoImage', models)
        self.assertIn('CacaoPrediction', models)

    @patch('api.utils.model_imports.get_model_safely')
    def test_get_models_safely_calls_get_model_safely_for_each(self, mock_get_model):
        """Test get_models_safely calls get_model_safely for each model."""
        mock_get_model.return_value = User
        
        model_paths = {
            'User': 'django.contrib.auth.models.User',
            'Group': 'django.contrib.auth.models.Group'
        }
        
        get_models_safely(model_paths)
        
        self.assertEqual(mock_get_model.call_count, 2)
        call_args = [call[0][0] for call in mock_get_model.call_args_list]
        self.assertIn('django.contrib.auth.models.User', call_args)
        self.assertIn('django.contrib.auth.models.Group', call_args)

