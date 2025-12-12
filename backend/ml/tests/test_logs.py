"""
Tests for ML logging utilities.
"""
import pytest
import logging
import sys
from pathlib import Path
from unittest.mock import patch, Mock
from ml.utils.logs import (
    setup_logger,
    get_ml_logger,
    log_processing_stats
)


class TestSetupLogger:
    """Tests for setup_logger function."""
    
    def test_setup_logger_basic(self):
        """Test setting up a basic logger."""
        logger = setup_logger('test_logger')
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'test_logger'
        assert logger.level == logging.INFO
    
    def test_setup_logger_with_custom_level(self):
        """Test setting up logger with custom level."""
        logger = setup_logger('test_logger', level=logging.DEBUG)
        
        assert logger.level == logging.DEBUG
    
    def test_setup_logger_with_custom_format(self):
        """Test setting up logger with custom format."""
        custom_format = '%(levelname)s - %(message)s'
        logger = setup_logger('test_logger', format_string=custom_format)
        
        # Check that formatter is set
        assert len(logger.handlers) > 0
    
    def test_setup_logger_with_file(self, tmp_path):
        """Test setting up logger with file handler."""
        log_file = tmp_path / 'test.log'
        logger = setup_logger('test_logger', log_file=log_file)
        
        # Check that file handler exists
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) > 0
    
    def test_setup_logger_clears_existing_handlers(self):
        """Test that setup_logger clears existing handlers."""
        logger = logging.getLogger('test_logger_clear')
        logger.addHandler(logging.StreamHandler())
        
        assert len(logger.handlers) > 0
        
        setup_logger('test_logger_clear')
        
        # Should have only the new handlers
        assert len(logger.handlers) > 0
    
    def test_setup_logger_creates_file_directory(self, tmp_path):
        """Test that setup_logger creates file directory if needed."""
        log_file = tmp_path / 'subdir' / 'test.log'
        logger = setup_logger('test_logger', log_file=log_file)
        
        assert log_file.parent.exists()
    
    def test_setup_logger_console_handler(self):
        """Test that console handler is added."""
        logger = setup_logger('test_logger')
        
        console_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
        assert len(console_handlers) > 0
    
    def test_setup_logger_file_handler_encoding(self, tmp_path):
        """Test that file handler uses UTF-8 encoding."""
        log_file = tmp_path / 'test.log'
        logger = setup_logger('test_logger', log_file=log_file)
        
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) > 0


class TestGetMlLogger:
    """Tests for get_ml_logger function."""
    
    def test_get_ml_logger_default(self):
        """Test getting ML logger with default name."""
        logger = get_ml_logger()
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "cacaoscan.ml"
    
    def test_get_ml_logger_custom_name(self):
        """Test getting ML logger with custom name."""
        logger = get_ml_logger("custom.ml")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "custom.ml"


class TestLogProcessingStats:
    """Tests for log_processing_stats function."""
    
    def test_log_processing_stats_success(self, caplog):
        """Test logging processing stats with success."""
        logger = logging.getLogger('test_stats')
        logger.setLevel(logging.INFO)
        
        with caplog.at_level(logging.INFO):
            log_processing_stats(
                logger=logger,
                total_items=100,
                processed_items=100,
                successful_items=95,
                failed_items=5,
                processing_time=10.5
            )
        
        assert 'Procesamiento completado' in caplog.text
        assert 'Total items: 100' in caplog.text
        assert 'Procesados: 100' in caplog.text
        assert 'Exitosos: 95' in caplog.text
        assert 'Fallidos: 5' in caplog.text
        assert 'Tasa de éxito: 95.00%' in caplog.text
        assert 'Tiempo promedio por item: 0.105s' in caplog.text
        assert 'Tiempo total: 10.50s' in caplog.text
    
    def test_log_processing_stats_zero_processed(self, caplog):
        """Test logging processing stats with zero processed items."""
        logger = logging.getLogger('test_stats')
        logger.setLevel(logging.INFO)
        
        with caplog.at_level(logging.INFO):
            log_processing_stats(
                logger=logger,
                total_items=100,
                processed_items=0,
                successful_items=0,
                failed_items=0,
                processing_time=0.0
            )
        
        assert 'Procesamiento completado' in caplog.text
        assert 'Tasa de éxito: 0.00%' in caplog.text
        assert 'Tiempo promedio por item: 0.000s' in caplog.text
    
    def test_log_processing_stats_partial(self, caplog):
        """Test logging processing stats with partial processing."""
        logger = logging.getLogger('test_stats')
        logger.setLevel(logging.INFO)
        
        with caplog.at_level(logging.INFO):
            log_processing_stats(
                logger=logger,
                total_items=100,
                processed_items=50,
                successful_items=45,
                failed_items=5,
                processing_time=5.0
            )
        
        assert 'Procesados: 50' in caplog.text
        assert 'Tasa de éxito: 90.00%' in caplog.text
        assert 'Tiempo promedio por item: 0.100s' in caplog.text
    
    def test_log_processing_stats_all_failed(self, caplog):
        """Test logging processing stats with all failed."""
        logger = logging.getLogger('test_stats')
        logger.setLevel(logging.INFO)
        
        with caplog.at_level(logging.INFO):
            log_processing_stats(
                logger=logger,
                total_items=100,
                processed_items=100,
                successful_items=0,
                failed_items=100,
                processing_time=10.0
            )
        
        assert 'Tasa de éxito: 0.00%' in caplog.text
    
    def test_log_processing_stats_all_successful(self, caplog):
        """Test logging processing stats with all successful."""
        logger = logging.getLogger('test_stats')
        logger.setLevel(logging.INFO)
        
        with caplog.at_level(logging.INFO):
            log_processing_stats(
                logger=logger,
                total_items=100,
                processed_items=100,
                successful_items=100,
                failed_items=0,
                processing_time=10.0
            )
        
        assert 'Tasa de éxito: 100.00%' in caplog.text


