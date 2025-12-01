"""
Tests for utils logs module.
"""
from unittest import TestCase
from unittest.mock import patch

from ml.utils.logs import get_ml_logger


class LogsUtilsTest(TestCase):
    """Tests for logs utility functions."""

    def test_get_ml_logger(self):
        """Test getting ML logger."""
        logger = get_ml_logger('test.module')
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, 'test.module')

    def test_get_ml_logger_different_modules(self):
        """Test getting loggers for different modules."""
        logger1 = get_ml_logger('module1')
        logger2 = get_ml_logger('module2')
        
        self.assertNotEqual(logger1.name, logger2.name)

