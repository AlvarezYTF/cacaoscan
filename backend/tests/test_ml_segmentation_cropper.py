"""
Unit tests for segmentation cropper module (cropper.py).
Tests crop generation and image processing functionality.
"""
import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PIL import Image
import cv2

from ml.segmentation.cropper import (
    CacaoCropper,
    create_cacao_cropper
)


@pytest.fixture
def mock_image_path(tmp_path):
    """Create a temporary image file for testing."""
    image_path = tmp_path / "test_image.jpg"
    img = Image.new('RGB', (512, 512), color='red')
    img.save(image_path)
    return image_path


@pytest.fixture
def mock_yolo_inference():
    """Create a mock YOLO inference object."""
    mock_inference = Mock()
    mock_inference.get_best_prediction.return_value = {
        'confidence': 0.9,
        'area': 10000,
        'bbox': [100, 100, 200, 200],
        'mask': np.ones((512, 512), dtype=np.float32) * 0.9
    }
    return mock_inference


@pytest.fixture
def cropper(mock_yolo_inference):
    """Create a CacaoCropper instance for testing."""
    with patch('ml.segmentation.cropper.get_crops_dir'), \
         patch('ml.segmentation.cropper.get_masks_dir'), \
         patch('ml.segmentation.cropper.ensure_dir_exists'):
        return CacaoCropper(
            yolo_inference=mock_yolo_inference,
            crop_size=512,
            padding=10,
            save_masks=False,
            overwrite=False,
            enable_yolo=True
        )


class TestCacaoCropper:
    """Tests for CacaoCropper class."""
    
    def test_cropper_initialization(self, mock_yolo_inference):
        """Test cropper initialization."""
        with patch('ml.segmentation.cropper.get_crops_dir'), \
             patch('ml.segmentation.cropper.get_masks_dir'), \
             patch('ml.segmentation.cropper.ensure_dir_exists'):
            cropper = CacaoCropper(
                yolo_inference=mock_yolo_inference,
                crop_size=256,
                padding=5,
                save_masks=True,
                overwrite=True,
                enable_yolo=True
            )
            
            assert cropper.yolo_inference == mock_yolo_inference
            assert cropper.crop_size == 256
            assert cropper.padding == 5
            assert cropper.save_masks is True
            assert cropper.overwrite is True
            assert cropper.enable_yolo is True
    
    def test_should_skip_processing_force_process(self, cropper, mock_image_path, tmp_path):
        """Test that force_process skips existing check."""
        crop_path = tmp_path / "1.png"
        crop_path.touch()
        
        with patch('ml.segmentation.cropper.get_crops_dir', return_value=tmp_path):
            result = cropper._should_skip_processing(crop_path, mock_image_path, force_process=True)
            
            assert result is False
    
    def test_should_skip_processing_overwrite(self, cropper, mock_image_path, tmp_path):
        """Test that overwrite skips existing check."""
        cropper.overwrite = True
        crop_path = tmp_path / "1.png"
        crop_path.touch()
        
        with patch('ml.segmentation.cropper.get_crops_dir', return_value=tmp_path):
            result = cropper._should_skip_processing(crop_path, mock_image_path, force_process=False)
            
            assert result is False
    
    def test_get_yolo_prediction_with_fallback_success(self, cropper, mock_image_path):
        """Test successful YOLO prediction."""
        prediction = cropper._get_yolo_prediction_with_fallback(mock_image_path)
        
        assert prediction is not None
        assert 'confidence' in prediction
        assert 'mask' in prediction
    
    def test_get_yolo_prediction_with_fallback_lower_threshold(self, cropper, mock_image_path):
        """Test YOLO prediction with lower threshold fallback."""
        cropper.yolo_inference.get_best_prediction.return_value = None
        cropper.yolo_inference.predict.return_value = [
            {'confidence': 0.2, 'area': 5000, 'mask': np.ones((512, 512), dtype=np.float32) * 0.8}
        ]
        
        prediction = cropper._get_yolo_prediction_with_fallback(mock_image_path)
        
        assert prediction is not None
    
    def test_validate_prediction_quality_low_confidence(self, cropper, mock_image_path):
        """Test validation with low confidence prediction."""
        prediction = {
            'confidence': 0.3,
            'mask': np.ones((512, 512), dtype=np.float32) * 0.5
        }
        
        # Should not raise, just log warning
        cropper._validate_prediction_quality(prediction, mock_image_path)
    
    def test_validate_prediction_quality_small_mask(self, cropper, mock_image_path):
        """Test validation with small mask area."""
        prediction = {
            'confidence': 0.9,
            'mask': np.zeros((512, 512), dtype=np.float32)
        }
        prediction['mask'][10:20, 10:20] = 0.5  # Small area
        
        # Should not raise, just log warning
        cropper._validate_prediction_quality(prediction, mock_image_path)
    
    def test_prepare_mask_resize(self, cropper):
        """Test mask preparation with resizing."""
        mask = np.ones((256, 256), dtype=np.float32) * 0.8
        image_height = 512
        image_width = 512
        
        result = cropper._prepare_mask(mask, image_height, image_width)
        
        assert result.shape == (image_height, image_width)
        assert result.dtype == np.uint8
    
    def test_prepare_mask_normalize(self, cropper):
        """Test mask normalization."""
        mask = np.ones((512, 512), dtype=np.float32) * 0.5
        
        result = cropper._prepare_mask(mask, 512, 512)
        
        assert result.dtype == np.uint8
        assert result.max() <= 255
    
    def test_process_image_skip_existing(self, cropper, mock_image_path, tmp_path):
        """Test processing when crop already exists."""
        crop_path = tmp_path / "1.png"
        crop_path.touch()
        
        with patch('ml.segmentation.cropper.get_crops_dir', return_value=tmp_path), \
             patch('ml.segmentation.cropper.get_masks_dir', return_value=tmp_path), \
             patch.object(cropper, '_should_skip_processing', return_value=True):
            result = cropper.process_image(mock_image_path, image_id=1, force_process=False)
            
            assert result['success'] is True
            assert result.get('skipped', False) is True
    
    def test_process_image_yolo_disabled(self, mock_image_path, tmp_path):
        """Test processing with YOLO disabled."""
        with patch('ml.segmentation.cropper.get_crops_dir', return_value=tmp_path), \
             patch('ml.segmentation.cropper.get_masks_dir', return_value=tmp_path), \
             patch('ml.segmentation.cropper.ensure_dir_exists'):
            cropper = CacaoCropper(
                yolo_inference=None,
                enable_yolo=False
            )
            
            with patch.object(cropper, '_process_with_opencv_fallback', return_value={
                'success': True,
                'crop_path': tmp_path / "1.png",
                'confidence': 0.5
            }):
                result = cropper.process_image(mock_image_path, image_id=1)
                
                assert result['success'] is True
    
    def test_process_image_yolo_success(self, cropper, mock_image_path, tmp_path):
        """Test successful processing with YOLO."""
        with patch('ml.segmentation.cropper.get_crops_dir', return_value=tmp_path), \
             patch('ml.segmentation.cropper.get_masks_dir', return_value=tmp_path), \
             patch('cv2.imread', return_value=np.zeros((512, 512, 3), dtype=np.uint8)), \
             patch('cv2.cvtColor', return_value=np.zeros((512, 512, 3), dtype=np.uint8)), \
             patch.object(cropper, '_should_skip_processing', return_value=False), \
             patch.object(cropper, '_create_and_save_crop'), \
             patch('ml.segmentation.cropper.validate_crop_quality', return_value=True), \
             patch('ml.segmentation.cropper.create_transparent_crop', return_value=np.zeros((200, 200, 4), dtype=np.uint8)):
            
            result = cropper.process_image(mock_image_path, image_id=1, force_process=True)
            
            assert result['success'] is True
            assert 'crop_path' in result
            assert 'confidence' in result
    
    def test_process_image_no_detection(self, cropper, mock_image_path, tmp_path):
        """Test processing when no detection is found."""
        cropper.yolo_inference.get_best_prediction.return_value = None
        cropper.yolo_inference.predict.return_value = []
        
        with patch('ml.segmentation.cropper.get_crops_dir', return_value=tmp_path), \
             patch('ml.segmentation.cropper.get_masks_dir', return_value=tmp_path), \
             patch.object(cropper, '_should_skip_processing', return_value=False):
            result = cropper.process_image(mock_image_path, image_id=1, force_process=True)
            
            assert result['success'] is False
            assert 'error' in result
    
    def test_process_with_opencv_fallback(self, cropper, mock_image_path, tmp_path):
        """Test OpenCV fallback processing."""
        # Create a mock RGBA image array where object occupies ~30% of the area (realistic)
        mock_rgba_array = np.zeros((200, 200, 4), dtype=np.uint8)
        # Create a smaller object in the center (50x50 pixels = 2500px, out of 40000px = 6.25%)
        center_x, center_y = 100, 100
        size = 50
        mock_rgba_array[center_y-size//2:center_y+size//2, center_x-size//2:center_x+size//2, :3] = 255
        mock_rgba_array[center_y-size//2:center_y+size//2, center_x-size//2:center_x+size//2, 3] = 255  # Alpha channel
        
        with patch('ml.segmentation.cropper.get_crops_dir', return_value=tmp_path), \
             patch('ml.segmentation.cropper.get_masks_dir', return_value=tmp_path), \
             patch('cv2.imread', return_value=np.zeros((512, 512, 3), dtype=np.uint8)), \
             patch('ml.segmentation.processor._remove_background_opencv', return_value=Image.fromarray(mock_rgba_array, 'RGBA')), \
             patch('ml.data.transforms.validate_crop_quality', return_value=True), \
             patch('ml.data.transforms.create_transparent_crop', return_value=mock_rgba_array), \
             patch('ml.utils.io.save_image'):
            
            result = cropper._process_with_opencv_fallback(mock_image_path, image_id=1)
            
            assert result['success'] is True
            assert 'crop_path' in result
            assert result.get('confidence') == 0.5  # Fallback confidence
    
    def test_should_reprocess_source_newer(self, cropper, mock_image_path, tmp_path):
        """Test reprocessing when source is newer."""
        crop_path = tmp_path / "crop.png"
        crop_path.touch()
        
        # Make source newer
        import time
        time.sleep(0.1)
        mock_image_path.touch()
        
        with patch('ml.segmentation.cropper.get_file_timestamp') as mock_timestamp:
            mock_timestamp.side_effect = lambda p: p.stat().st_mtime
            
            result = cropper._should_reprocess(mock_image_path, crop_path)
            
            assert result is True
    
    def test_process_batch_success(self, cropper, tmp_path):
        """Test batch processing."""
        image_records = [
            {'id': 1, 'raw_image_path': tmp_path / "1.jpg"},
            {'id': 2, 'raw_image_path': tmp_path / "2.jpg"},
        ]
        
        for record in image_records:
            record['raw_image_path'].touch()
        
        with patch('ml.segmentation.cropper.get_crops_dir', return_value=tmp_path), \
             patch.object(cropper, 'process_image', return_value={'success': True, 'skipped': False}):
            result = cropper.process_batch(image_records, limit=0)
            
            assert result['total'] == 2
            assert result['successful'] == 2
            assert result['failed'] == 0
    
    def test_process_batch_with_limit(self, cropper, tmp_path):
        """Test batch processing with limit."""
        image_records = [
            {'id': 1, 'raw_image_path': tmp_path / "1.jpg"},
            {'id': 2, 'raw_image_path': tmp_path / "2.jpg"},
            {'id': 3, 'raw_image_path': tmp_path / "3.jpg"},
        ]
        
        for record in image_records:
            record['raw_image_path'].touch()
        
        with patch('ml.segmentation.cropper.get_crops_dir', return_value=tmp_path), \
             patch.object(cropper, 'process_image', return_value={'success': True, 'skipped': False}):
            result = cropper.process_batch(image_records, limit=2)
            
            assert result['total'] == 2
            assert result['successful'] == 2


class TestCreateCacaoCropper:
    """Tests for create_cacao_cropper function."""
    
    @patch('ml.segmentation.infer_yolo_seg.create_yolo_inference')
    def test_create_cacao_cropper_with_yolo(self, mock_create_yolo):
        """Test creating cropper with YOLO enabled."""
        mock_inference = Mock()
        mock_create_yolo.return_value = mock_inference
        
        with patch('ml.segmentation.cropper.get_crops_dir'), \
             patch('ml.segmentation.cropper.get_masks_dir'), \
             patch('ml.segmentation.cropper.ensure_dir_exists'):
            cropper = create_cacao_cropper(
                confidence_threshold=0.6,
                crop_size=256,
                padding=5,
                save_masks=True,
                overwrite=True,
                enable_yolo=True
            )
            
            assert cropper.yolo_inference == mock_inference
            assert cropper.enable_yolo is True
    
    @patch('ml.segmentation.infer_yolo_seg.create_yolo_inference')
    def test_create_cacao_cropper_yolo_disabled(self, mock_create_yolo):
        """Test creating cropper with YOLO disabled."""
        with patch('ml.segmentation.cropper.get_crops_dir'), \
             patch('ml.segmentation.cropper.get_masks_dir'), \
             patch('ml.segmentation.cropper.ensure_dir_exists'):
            cropper = create_cacao_cropper(enable_yolo=False)
            
            assert cropper.yolo_inference is None
            assert cropper.enable_yolo is False
    
    @patch('ml.segmentation.infer_yolo_seg.create_yolo_inference')
    def test_create_cacao_cropper_yolo_failure(self, mock_create_yolo):
        """Test creating cropper when YOLO fails to load."""
        mock_create_yolo.side_effect = Exception("YOLO load failed")
        
        with patch('ml.segmentation.cropper.get_crops_dir'), \
             patch('ml.segmentation.cropper.get_masks_dir'), \
             patch('ml.segmentation.cropper.ensure_dir_exists'):
            cropper = create_cacao_cropper(enable_yolo=True)
            
            assert cropper.yolo_inference is None
            assert cropper.enable_yolo is False

