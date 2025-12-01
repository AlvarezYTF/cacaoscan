"""
Unit tests for measurement calibration module (calibration.py).
Tests calibration functionality for pixel-to-mm conversion.
"""
import pytest
import numpy as np
import cv2
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from ml.measurement.calibration import (
    CalibrationManager,
    CalibrationMethod,
    ReferenceObject,
    CalibrationResult,
    CalibrationParams,
    CoinDetector,
    RulerDetector,
    get_calibration_manager,
    calibrate_image,
    convert_pixels_to_mm,
    convert_mm_to_pixels
)


@pytest.fixture
def mock_image():
    """Create a mock OpenCV image (BGR format)."""
    return np.zeros((512, 512, 3), dtype=np.uint8)


@pytest.fixture
def calibration_manager():
    """Create a CalibrationManager instance for testing."""
    with patch('ml.measurement.calibration.get_regressors_artifacts_dir'), \
         patch('ml.measurement.calibration.ensure_dir_exists'):
        return CalibrationManager()


class TestCalibrationMethod:
    """Tests for CalibrationMethod enum."""
    
    def test_calibration_method_values(self):
        """Test that all calibration methods are defined."""
        assert CalibrationMethod.COIN_DETECTION.value == "coin_detection"
        assert CalibrationMethod.RULER_DETECTION.value == "ruler_detection"
        assert CalibrationMethod.MANUAL_POINTS.value == "manual_points"
        assert CalibrationMethod.AUTO_REFERENCE.value == "auto_reference"


class TestReferenceObject:
    """Tests for ReferenceObject enum."""
    
    def test_reference_object_values(self):
        """Test that all reference objects are defined."""
        assert ReferenceObject.COIN_1000_COP.value['diameter_mm'] == 23.0
        assert ReferenceObject.COIN_500_COP.value['diameter_mm'] == 21.0
        assert ReferenceObject.RULER_1CM.value['length_mm'] == 10.0


class TestCoinDetector:
    """Tests for CoinDetector class."""
    
    def test_coin_detector_initialization(self):
        """Test coin detector initialization."""
        detector = CoinDetector()
        
        assert detector.min_coin_area == 100
        assert detector.max_coin_area == 10000
    
    @patch('cv2.cvtColor')
    @patch('cv2.GaussianBlur')
    @patch('cv2.HoughCircles')
    def test_detect_coins_success(self, mock_hough, mock_blur, mock_cvt, mock_image):
        """Test successful coin detection."""
        mock_hough.return_value = np.array([[[100, 100, 30], [200, 200, 25]]], dtype=np.float32)
        mock_blur.return_value = np.zeros((512, 512), dtype=np.uint8)
        mock_cvt.return_value = np.zeros((512, 512), dtype=np.uint8)
        
        detector = CoinDetector()
        coins = detector.detect_coins(mock_image)
        
        assert isinstance(coins, list)
        if len(coins) > 0:
            assert 'center' in coins[0]
            assert 'radius' in coins[0]
            assert 'diameter_pixels' in coins[0]
    
    @patch('cv2.HoughCircles')
    def test_detect_coins_no_circles(self, mock_hough, mock_image):
        """Test coin detection when no circles are found."""
        mock_hough.return_value = None
        
        detector = CoinDetector()
        coins = detector.detect_coins(mock_image)
        
        assert isinstance(coins, list)
        assert len(coins) == 0
    
    def test_classify_coin_by_size(self):
        """Test coin classification by size."""
        detector = CoinDetector()
        
        # Test 1000 COP coin size
        coin_type = detector._classify_coin_by_size(25)  # ~50 pixels diameter
        assert coin_type == ReferenceObject.COIN_1000_COP
        
        # Test 500 COP coin size
        coin_type = detector._classify_coin_by_size(20)  # ~40 pixels diameter
        assert coin_type == ReferenceObject.COIN_500_COP


class TestRulerDetector:
    """Tests for RulerDetector class."""
    
    def test_ruler_detector_initialization(self):
        """Test ruler detector initialization."""
        detector = RulerDetector()
        
        assert detector.min_line_length == 50
        assert detector.max_line_length == 500
    
    @patch('cv2.cvtColor')
    @patch('cv2.Canny')
    @patch('cv2.HoughLinesP')
    def test_detect_rulers_success(self, mock_hough, mock_canny, mock_cvt, mock_image):
        """Test successful ruler detection."""
        mock_hough.return_value = np.array([[[10, 10, 100, 10]]], dtype=np.int32)
        mock_canny.return_value = np.zeros((512, 512), dtype=np.uint8)
        mock_cvt.return_value = np.zeros((512, 512), dtype=np.uint8)
        
        detector = RulerDetector()
        rulers = detector.detect_rulers(mock_image)
        
        assert isinstance(rulers, list)
        if len(rulers) > 0:
            assert 'start_point' in rulers[0]
            assert 'end_point' in rulers[0]
            assert 'length_pixels' in rulers[0]
    
    @patch('cv2.HoughLinesP')
    def test_detect_rulers_no_lines(self, mock_hough, mock_image):
        """Test ruler detection when no lines are found."""
        mock_hough.return_value = None
        
        detector = RulerDetector()
        rulers = detector.detect_rulers(mock_image)
        
        assert isinstance(rulers, list)
        assert len(rulers) == 0


class TestCalibrationManager:
    """Tests for CalibrationManager class."""
    
    def test_manager_initialization(self):
        """Test calibration manager initialization."""
        with patch('ml.measurement.calibration.get_regressors_artifacts_dir'), \
             patch('ml.measurement.calibration.ensure_dir_exists'):
            manager = CalibrationManager()
            
            assert manager.coin_detector is not None
            assert manager.ruler_detector is not None
            assert manager.current_calibration is None
    
    def test_calibrate_image_coin_detection(self, calibration_manager, mock_image):
        """Test calibration with coin detection method."""
        mock_coins = [{
            'center': (100, 100),
            'radius': 25,
            'diameter_pixels': 50,
            'coin_type': ReferenceObject.COIN_1000_COP,
            'confidence': 0.9
        }]
        calibration_manager.coin_detector.detect_coins = Mock(return_value=mock_coins)
        
        with patch.object(calibration_manager, '_create_calibration_image', return_value=mock_image), \
             patch.object(calibration_manager, '_save_calibration_image', return_value=Path('/tmp/cal.jpg')):
            result = calibration_manager.calibrate_image(
                mock_image,
                method=CalibrationMethod.COIN_DETECTION
            )
            
            assert isinstance(result, CalibrationResult)
            assert result.success is True
            assert result.pixels_per_mm > 0
    
    def test_calibrate_image_no_coins(self, calibration_manager, mock_image):
        """Test calibration when no coins are detected."""
        calibration_manager.coin_detector.detect_coins = Mock(return_value=[])
        
        result = calibration_manager.calibrate_image(
            mock_image,
            method=CalibrationMethod.COIN_DETECTION
        )
        
        assert isinstance(result, CalibrationResult)
        assert result.success is False
        assert 'no se detectaron' in result.error_message.lower() or 'error' in result.error_message.lower()
    
    def test_calibrate_image_ruler_detection(self, calibration_manager, mock_image):
        """Test calibration with ruler detection method."""
        mock_rulers = [{
            'start_point': (10, 10),
            'end_point': (110, 10),
            'length_pixels': 100,
            'ruler_type': ReferenceObject.RULER_1CM,
            'confidence': 0.8
        }]
        calibration_manager.ruler_detector.detect_rulers = Mock(return_value=mock_rulers)
        
        with patch.object(calibration_manager, '_create_calibration_image', return_value=mock_image), \
             patch.object(calibration_manager, '_save_calibration_image', return_value=Path('/tmp/cal.jpg')):
            result = calibration_manager.calibrate_image(
                mock_image,
                method=CalibrationMethod.RULER_DETECTION
            )
            
            assert isinstance(result, CalibrationResult)
            assert result.success is True
            assert result.pixels_per_mm > 0
    
    def test_calibrate_image_manual_points(self, calibration_manager):
        """Test calibration with manual points."""
        manual_points = [(100, 100), (200, 100)]
        
        result = calibration_manager.calibrate_image(
            np.zeros((512, 512, 3), dtype=np.uint8),
            method=CalibrationMethod.MANUAL_POINTS,
            manual_points=manual_points
        )
        
        assert isinstance(result, CalibrationResult)
        assert result.success is True
        assert result.pixels_per_mm > 0
    
    def test_calibrate_image_manual_points_insufficient(self, calibration_manager):
        """Test calibration with insufficient manual points."""
        manual_points = [(100, 100)]  # Only one point
        
        result = calibration_manager.calibrate_image(
            np.zeros((512, 512, 3), dtype=np.uint8),
            method=CalibrationMethod.MANUAL_POINTS,
            manual_points=manual_points
        )
        
        assert isinstance(result, CalibrationResult)
        assert result.success is False
    
    def test_calibrate_image_auto_reference(self, calibration_manager, mock_image):
        """Test calibration with auto reference method."""
        mock_coins = [{
            'center': (100, 100),
            'radius': 25,
            'diameter_pixels': 50,
            'coin_type': ReferenceObject.COIN_1000_COP,
            'confidence': 0.9
        }]
        calibration_manager.coin_detector.detect_coins = Mock(return_value=mock_coins)
        
        with patch.object(calibration_manager, '_create_calibration_image', return_value=mock_image), \
             patch.object(calibration_manager, '_save_calibration_image', return_value=Path('/tmp/cal.jpg')):
            result = calibration_manager.calibrate_image(
                mock_image,
                method=CalibrationMethod.AUTO_REFERENCE
            )
            
            assert isinstance(result, CalibrationResult)
    
    def test_save_calibration_success(self, calibration_manager):
        """Test saving calibration."""
        calibration_result = CalibrationResult(
            success=True,
            pixels_per_mm=0.035,
            confidence=0.9,
            method=CalibrationMethod.COIN_DETECTION,
            reference_object=ReferenceObject.COIN_1000_COP,
            detected_points=[(100, 100)]
        )
        
        with patch('ml.measurement.calibration.save_json'), \
             patch('time.time', return_value=1234567890):
            calibration_manager.save_calibration(calibration_result)
            
            assert calibration_manager.current_calibration is not None
            assert calibration_manager.current_calibration.pixels_per_mm == 0.035
    
    def test_save_calibration_failed(self, calibration_manager):
        """Test saving failed calibration."""
        calibration_result = CalibrationResult(
            success=False,
            pixels_per_mm=0.0,
            confidence=0.0,
            method=CalibrationMethod.COIN_DETECTION,
            reference_object=None,
            detected_points=[]
        )
        
        with pytest.raises(ValueError, match="No se puede guardar una calibración fallida"):
            calibration_manager.save_calibration(calibration_result)
    
    def test_load_calibration_success(self, calibration_manager, tmp_path):
        """Test loading calibration."""
        calibration_data = {
            'pixels_per_mm': 0.035,
            'method': 'coin_detection',
            'reference_object': None,
            'confidence': 0.9,
            'timestamp': '1234567890',
            'image_dimensions': (512, 512),
            'validation_score': 0.95
        }
        
        calibration_file = tmp_path / "current_calibration.json"
        with patch('ml.measurement.calibration.get_regressors_artifacts_dir', return_value=tmp_path), \
             patch('ml.measurement.calibration.load_json', return_value=calibration_data):
            result = calibration_manager.load_calibration()
            
            assert result is not None
            assert result.pixels_per_mm == 0.035
    
    def test_load_calibration_not_found(self, calibration_manager, tmp_path):
        """Test loading calibration when file doesn't exist."""
        with patch('ml.measurement.calibration.get_regressors_artifacts_dir', return_value=tmp_path):
            result = calibration_manager.load_calibration()
            
            assert result is None
    
    def test_convert_pixels_to_mm(self, calibration_manager):
        """Test converting pixels to millimeters."""
        calibration_params = CalibrationParams(
            pixels_per_mm=0.035,
            method=CalibrationMethod.COIN_DETECTION,
            reference_object=ReferenceObject.COIN_1000_COP,
            confidence=0.9,
            timestamp="1234567890",
            image_dimensions=(512, 512)
        )
        calibration_manager.current_calibration = calibration_params
        
        mm = calibration_manager.convert_pixels_to_mm(100.0)
        
        assert mm == 100.0 / 0.035
        assert isinstance(mm, float)
    
    def test_convert_pixels_to_mm_no_calibration(self, calibration_manager):
        """Test converting pixels to mm when no calibration is loaded."""
        calibration_manager.current_calibration = None
        
        with pytest.raises(ValueError, match="No hay calibración cargada"):
            calibration_manager.convert_pixels_to_mm(100.0)
    
    def test_convert_mm_to_pixels(self, calibration_manager):
        """Test converting millimeters to pixels."""
        calibration_params = CalibrationParams(
            pixels_per_mm=0.035,
            method=CalibrationMethod.COIN_DETECTION,
            reference_object=ReferenceObject.COIN_1000_COP,
            confidence=0.9,
            timestamp="1234567890",
            image_dimensions=(512, 512)
        )
        calibration_manager.current_calibration = calibration_params
        
        pixels = calibration_manager.convert_mm_to_pixels(10.0)
        
        assert pixels == 10.0 * 0.035
        assert isinstance(pixels, float)
    
    def test_validate_calibration(self, calibration_manager, mock_image):
        """Test calibration validation."""
        calibration_params = CalibrationParams(
            pixels_per_mm=0.035,
            method=CalibrationMethod.COIN_DETECTION,
            reference_object=ReferenceObject.COIN_1000_COP,
            confidence=0.9,
            timestamp="1234567890",
            image_dimensions=(512, 512)
        )
        calibration_manager.current_calibration = calibration_params
        
        mock_result = CalibrationResult(
            success=True,
            pixels_per_mm=0.036,
            confidence=0.9,
            method=CalibrationMethod.COIN_DETECTION,
            reference_object=ReferenceObject.COIN_1000_COP,
            detected_points=[(100, 100)]
        )
        
        with patch.object(calibration_manager, 'calibrate_image', return_value=mock_result):
            validation = calibration_manager.validate_calibration(mock_image)
            
            assert isinstance(validation, dict)
            assert 'valid' in validation
            assert 'accuracy_score' in validation


class TestCalibrationConvenienceFunctions:
    """Tests for convenience functions."""
    
    def test_get_calibration_manager(self):
        """Test get_calibration_manager function."""
        with patch('ml.measurement.calibration.CalibrationManager') as mock_class, \
             patch('ml.measurement.calibration._calibration_manager', None):
            mock_instance = Mock()
            mock_class.return_value = mock_instance
            
            result = get_calibration_manager()
            
            assert result == mock_instance
    
    def test_calibrate_image_function(self, mock_image):
        """Test calibrate_image convenience function."""
        with patch('ml.measurement.calibration.get_calibration_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_result = CalibrationResult(
                success=True,
                pixels_per_mm=0.035,
                confidence=0.9,
                method=CalibrationMethod.COIN_DETECTION,
                reference_object=ReferenceObject.COIN_1000_COP,
                detected_points=[(100, 100)]
            )
            mock_manager.calibrate_image.return_value = mock_result
            mock_get_manager.return_value = mock_manager
            
            result = calibrate_image(mock_image, CalibrationMethod.COIN_DETECTION)
            
            assert isinstance(result, CalibrationResult)
            assert result.success is True
    
    def test_convert_pixels_to_mm_function(self):
        """Test convert_pixels_to_mm convenience function."""
        with patch('ml.measurement.calibration.get_calibration_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_manager.convert_pixels_to_mm.return_value = 2857.14
            mock_get_manager.return_value = mock_manager
            
            result = convert_pixels_to_mm(100.0)
            
            assert result == 2857.14
            mock_manager.convert_pixels_to_mm.assert_called_once_with(100.0)
    
    def test_convert_mm_to_pixels_function(self):
        """Test convert_mm_to_pixels convenience function."""
        with patch('ml.measurement.calibration.get_calibration_manager') as mock_get_manager:
            mock_manager = Mock()
            mock_manager.convert_mm_to_pixels.return_value = 3.5
            mock_get_manager.return_value = mock_manager
            
            result = convert_mm_to_pixels(10.0)
            
            assert result == 3.5
            mock_manager.convert_mm_to_pixels.assert_called_once_with(10.0)

