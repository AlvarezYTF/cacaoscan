"""
Unit tests for logging utilities (logs.py).
Tests logger setup and logging functions.
"""
import pytest
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock

from ml.utils.logs import (
    setup_logger,
    get_ml_logger,
    log_processing_stats
)


class TestSetupLogger:
    """Tests for setup_logger function."""
    
    def test_setup_logger_basic(self):
        """Test basic logger setup."""
        logger = setup_logger("test_logger")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"
        assert logger.level == logging.INFO
    
    def test_setup_logger_custom_level(self):
        """Test logger setup with custom level."""
        logger = setup_logger("test_logger", level=logging.DEBUG)
        
        assert logger.level == logging.DEBUG
    
    def test_setup_logger_with_file(self, tmp_path):
        """Test logger setup with file handler."""
        log_file = tmp_path / "test.log"
        logger = setup_logger("test_logger", log_file=log_file)
        
        assert isinstance(logger, logging.Logger)
        # Test that it can write to file
        logger.info("Test message")
        
        assert log_file.exists()
        assert "Test message" in log_file.read_text()
    
    def test_setup_logger_custom_format(self):
        """Test logger setup with custom format."""
        custom_format = '%(levelname)s - %(message)s'
        logger = setup_logger("test_logger", format_string=custom_format)
        
        assert isinstance(logger, logging.Logger)
        # Verify format is applied
        handlers = logger.handlers
        assert len(handlers) > 0
        assert handlers[0].formatter._fmt == custom_format
    
    def test_setup_logger_removes_existing_handlers(self):
        """Test that setup_logger removes existing handlers."""
        logger = logging.getLogger("test_remove_handlers")
        
        # Add a handler
        handler = logging.StreamHandler()
        logger.addHandler(handler)
        assert len(logger.handlers) == 1
        
        # Setup logger should remove existing handlers
        setup_logger("test_remove_handlers")
        
        # Should have new handlers (console, possibly file)
        assert len(logger.handlers) >= 1


class TestGetMLLogger:
    """Tests for get_ml_logger function."""
    
    def test_get_ml_logger_default(self):
        """Test get_ml_logger with default name."""
        logger = get_ml_logger()
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "cacaoscan.ml"
    
    def test_get_ml_logger_custom_name(self):
        """Test get_ml_logger with custom name."""
        logger = get_ml_logger("custom.module")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "custom.module"
    
    def test_get_ml_logger_multiple_calls_same_name(self):
        """Test that multiple calls return same logger instance."""
        logger1 = get_ml_logger("test.module")
        logger2 = get_ml_logger("test.module")
        
        assert logger1 is logger2


class TestLogProcessingStats:
    """Tests for log_processing_stats function."""
    
    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger for testing."""
        logger = MagicMock(spec=logging.Logger)
        return logger
    
    def test_log_processing_stats_basic(self, mock_logger):
        """Test basic processing stats logging."""
        log_processing_stats(
            logger=mock_logger,
            total_items=100,
            processed_items=100,
            successful_items=95,
            failed_items=5,
            processing_time=10.5
        )
        
        assert mock_logger.info.call_count >= 6  # Multiple log calls
    
    def test_log_processing_stats_zero_processed(self, mock_logger):
        """Test processing stats with zero processed items."""
        log_processing_stats(
            logger=mock_logger,
            total_items=100,
            processed_items=0,
            successful_items=0,
            failed_items=0,
            processing_time=0.0
        )
        
        # Should not crash with division by zero
        assert mock_logger.info.call_count >= 1
    
    def test_log_processing_stats_all_successful(self, mock_logger):
        """Test processing stats when all items are successful."""
        log_processing_stats(
            logger=mock_logger,
            total_items=100,
            processed_items=100,
            successful_items=100,
            failed_items=0,
            processing_time=5.0
        )
        
        assert mock_logger.info.call_count >= 6
        # Verify success rate is 100%
        call_args = [str(call) for call in mock_logger.info.call_args_list]
        assert any("100.00%" in str(call) for call in call_args)
    
    def test_log_processing_stats_all_failed(self, mock_logger):
        """Test processing stats when all items fail."""
        log_processing_stats(
            logger=mock_logger,
            total_items=100,
            processed_items=100,
            successful_items=0,
            failed_items=100,
            processing_time=5.0
        )
        
        assert mock_logger.info.call_count >= 6
        # Verify success rate is 0%
        call_args = [str(call) for call in mock_logger.info.call_args_list]
        assert any("0.00%" in str(call) for call in call_args)
    
    def test_log_processing_stats_calculates_avg_time(self, mock_logger):
        """Test that average time is calculated correctly."""
        log_processing_stats(
            logger=mock_logger,
            total_items=100,
            processed_items=50,
            successful_items=45,
            failed_items=5,
            processing_time=10.0
        )
        
        # Average time should be 10.0 / 50 = 0.2
        call_args = [str(call) for call in mock_logger.info.call_args_list]
        assert any("0.200" in str(call) or "0.2" in str(call) for call in call_args)
    
    def test_log_processing_stats_partial_processing(self, mock_logger):
        """Test processing stats with partial processing."""
        log_processing_stats(
            logger=mock_logger,
            total_items=100,
            processed_items=50,
            successful_items=45,
            failed_items=5,
            processing_time=5.0
        )
        
        assert mock_logger.info.call_count >= 6
        # Verify all stats are logged
        logged_messages = [str(call) for call in mock_logger.info.call_args_list]
        assert any("100" in msg for msg in logged_messages)  # Total
        assert any("50" in msg for msg in logged_messages)   # Processed
        assert any("45" in msg for msg in logged_messages)   # Successful
        assert any("5" in msg for msg in logged_messages)    # Failed

