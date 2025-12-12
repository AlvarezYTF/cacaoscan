"""
Tests for measurement calibration module.

NOTA: Estos tests están actualizados después de eliminar funcionalidad de monedas/reglas.
El sistema ahora usa exclusivamente pixel_calibration.json para calibración.
"""
import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch

from ml.measurement.calibration import (
    CalibrationMethod,
    CalibrationResult,
    CalibrationParams,
    CalibrationManager,
    get_calibration_manager,
    calibrate_image,
    convert_pixels_to_mm,
    convert_mm_to_pixels
)


class TestCalibrationMethod:
    """Tests for CalibrationMethod enum."""
    
    def test_dataset_calibration(self):
        """Test dataset calibration method."""
        assert CalibrationMethod.DATASET_CALIBRATION.value == "dataset_calibration"
    
    def test_manual_points(self):
        """Test manual points method."""
        assert CalibrationMethod.MANUAL_POINTS.value == "manual_points"


class TestCalibrationManager:
    """Tests for CalibrationManager class."""
    
    @patch('ml.measurement.calibration.get_regressors_artifacts_dir')
    @patch('ml.measurement.calibration.ensure_dir_exists')
    def test_init(self, mock_ensure_dir, mock_get_dir):
        """Test CalibrationManager initialization."""
        mock_dir = Mock()
        mock_get_dir.return_value = mock_dir
        
        manager = CalibrationManager()
        
        assert manager.manual_calibrator is not None
        assert manager.current_calibration is None
    
    @patch('ml.measurement.calibration.get_regressors_artifacts_dir')
    def test_calibrate_image_dataset_calibration(self, mock_get_dir):
        """Test calibrating image with dataset calibration."""
        manager = CalibrationManager()
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = manager.calibrate_image(image, CalibrationMethod.DATASET_CALIBRATION)
        
        assert result.success is True
        assert result.method == CalibrationMethod.DATASET_CALIBRATION
    
    @patch('ml.measurement.calibration.get_regressors_artifacts_dir')
    def test_calibrate_image_error(self, mock_get_dir):
        """Test calibrating image with error."""
        manager = CalibrationManager()
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Test with invalid method
        with patch.object(manager, 'calibrate_image', side_effect=Exception("Error")):
            result = manager.calibrate_image(image, CalibrationMethod.DATASET_CALIBRATION)
            
            # Should handle error gracefully
            assert result is not None
    
    @patch('ml.measurement.calibration.get_regressors_artifacts_dir')
    def test_convert_pixels_to_mm_with_calibration(self, mock_get_dir):
        """Test converting pixels to mm with calibration."""
        manager = CalibrationManager()
        manager.current_calibration = CalibrationParams(
            pixels_per_mm=0.2,
            method=CalibrationMethod.DATASET_CALIBRATION,
            confidence=0.9,
            timestamp="1234567890",
            image_dimensions=(100, 100)
        )
        
        result = manager.convert_pixels_to_mm(100.0)
        
        assert result == 500.0  # 100 / 0.2
    
    @patch('ml.measurement.calibration.get_regressors_artifacts_dir')
    def test_convert_mm_to_pixels(self, mock_get_dir):
        """Test converting mm to pixels."""
        manager = CalibrationManager()
        manager.current_calibration = CalibrationParams(
            pixels_per_mm=0.2,
            method=CalibrationMethod.DATASET_CALIBRATION,
            confidence=0.9,
            timestamp="1234567890",
            image_dimensions=(100, 100)
        )
        
        result = manager.convert_mm_to_pixels(50.0)
        
        assert result == 10.0  # 50 * 0.2
    
    @patch('ml.measurement.calibration.get_regressors_artifacts_dir')
    def test_save_calibration(self, mock_get_dir):
        """Test saving calibration."""
        manager = CalibrationManager()
        
        calibration_result = CalibrationResult(
            success=True,
            pixels_per_mm=0.2,
            confidence=0.9,
            method=CalibrationMethod.DATASET_CALIBRATION,
            detected_points=[]
        )
        
        manager.save_calibration(calibration_result)
        
        assert manager.current_calibration is not None
        assert manager.current_calibration.pixels_per_mm == 0.2
    
    @patch('ml.measurement.calibration.get_regressors_artifacts_dir')
    def test_save_calibration_failed(self, mock_get_dir):
        """Test saving failed calibration."""
        manager = CalibrationManager()
        
        calibration_result = CalibrationResult(
            success=False,
            pixels_per_mm=0.0,
            confidence=0.0,
            method=CalibrationMethod.DATASET_CALIBRATION,
            detected_points=[],
            error_message="Error"
        )
        
        with pytest.raises(ValueError, match="No se puede guardar"):
            manager.save_calibration(calibration_result)


class TestModuleFunctions:
    """Tests for module-level convenience functions."""
    
    @patch('ml.measurement.calibration.get_calibration_manager')
    def test_get_calibration_manager(self, mock_get):
        """Test get_calibration_manager function."""
        mock_manager = Mock()
        mock_get.return_value = mock_manager
        
        result = get_calibration_manager()
        
        assert result == mock_manager
    
    @patch('ml.measurement.calibration.get_calibration_manager')
    def test_calibrate_image_function(self, mock_get):
        """Test calibrate_image convenience function."""
        mock_manager = Mock()
        mock_result = CalibrationResult(
            success=True,
            pixels_per_mm=0.2,
            confidence=0.9,
            method=CalibrationMethod.DATASET_CALIBRATION,
            detected_points=[]
        )
        mock_manager.calibrate_image.return_value = mock_result
        mock_get.return_value = mock_manager
        
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        result = calibrate_image(image, CalibrationMethod.DATASET_CALIBRATION)
        
        assert result.success is True
    
    @patch('ml.measurement.calibration.get_calibration_manager')
    def test_convert_pixels_to_mm_function(self, mock_get):
        """Test convert_pixels_to_mm convenience function."""
        mock_manager = Mock()
        mock_manager.convert_pixels_to_mm.return_value = 500.0
        mock_get.return_value = mock_manager
        
        result = convert_pixels_to_mm(100.0)
        
        assert result == 500.0
    
    @patch('ml.measurement.calibration.get_calibration_manager')
    def test_convert_mm_to_pixels_function(self, mock_get):
        """Test convert_mm_to_pixels convenience function."""
        mock_manager = Mock()
        mock_manager.convert_mm_to_pixels.return_value = 10.0
        mock_get.return_value = mock_manager
        
        result = convert_mm_to_pixels(50.0)
        
        assert result == 10.0
