"""
Tests for cacao cropper.
"""
import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from ml.segmentation.cropper import CacaoCropper, create_cacao_cropper


class TestCacaoCropper:
    """Tests for CacaoCropper class."""
    
    @pytest.fixture
    def cropper(self):
        """Create cropper instance."""
        return CacaoCropper(
            yolo_inference=None,
            crop_size=512,
            padding=10,
            save_masks=False,
            overwrite=False,
            enable_yolo=False
        )
    
    @pytest.fixture
    def image_path(self, tmp_path):
        """Create test image path."""
        image_file = tmp_path / "test_image.jpg"
        image_file.write_bytes(b"fake image content")
        return image_file
    
    def test_initialization(self, cropper):
        """Test cropper initialization."""
        assert cropper.crop_size == 512
        assert cropper.padding == 10
        assert cropper.save_masks is False
        assert cropper.overwrite is False
    
    def test_should_skip_processing_new_file(self, cropper, tmp_path):
        """Test should skip processing for new file."""
        crop_path = tmp_path / "crop.png"
        image_path = tmp_path / "image.jpg"
        image_path.write_bytes(b"test")
        
        result = cropper._should_skip_processing(crop_path, image_path, force_process=False)
        
        assert result is False  # Should not skip new file
    
    def test_should_skip_processing_existing_file(self, cropper, tmp_path):
        """Test should skip processing for existing file."""
        crop_path = tmp_path / "crop.png"
        crop_path.write_bytes(b"existing crop")
        image_path = tmp_path / "image.jpg"
        image_path.write_bytes(b"test")
        
        with patch.object(cropper, '_should_reprocess', return_value=False):
            result = cropper._should_skip_processing(crop_path, image_path, force_process=False)
            
            assert result is True
    
    def test_prepare_mask_same_size(self, cropper):
        """Test preparing mask of same size."""
        mask = np.zeros((100, 100), dtype=np.float32)
        
        result = cropper._prepare_mask(mask, 100, 100)
        
        assert result.shape == (100, 100)
        assert result.dtype == np.uint8
    
    def test_prepare_mask_different_size(self, cropper):
        """Test preparing mask of different size."""
        mask = np.zeros((50, 50), dtype=np.float32)
        
        result = cropper._prepare_mask(mask, 100, 100)
        
        assert result.shape == (100, 100)
        assert result.dtype == np.uint8
    
    def test_prepare_mask_normalized(self, cropper):
        """Test preparing normalized mask."""
        mask = np.ones((100, 100), dtype=np.float32) * 0.5
        
        result = cropper._prepare_mask(mask, 100, 100)
        
        assert result.dtype == np.uint8
        assert result.max() <= 255
    
    @patch('ml.segmentation.cropper.validate_crop_quality')
    @patch('ml.segmentation.cropper.create_transparent_crop')
    @patch('ml.segmentation.cropper.save_image')
    def test_create_and_save_crop(self, mock_save, mock_create, mock_validate, cropper, tmp_path):
        """Test creating and saving crop."""
        image_rgb = np.zeros((100, 100, 3), dtype=np.uint8)
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[20:80, 20:80] = 255
        crop_path = tmp_path / "crop.png"
        mask_path = tmp_path / "mask.png"
        
        mock_validate.return_value = True
        mock_create.return_value = np.zeros((100, 100, 4), dtype=np.uint8)
        
        cropper._create_and_save_crop(image_rgb, mask, crop_path, mask_path)
        
        assert mock_save.called
    
    @patch('ml.segmentation.cropper.get_crops_dir')
    @patch('ml.segmentation.cropper.get_masks_dir')
    def test_process_image_skip_existing(self, mock_masks_dir, mock_crops_dir, cropper, tmp_path):
        """Test processing image that already exists."""
        crop_path = tmp_path / "1.png"
        crop_path.write_bytes(b"existing")
        mock_crops_dir.return_value = tmp_path
        mock_masks_dir.return_value = tmp_path
        
        image_path = tmp_path / "image.jpg"
        image_path.write_bytes(b"test")
        
        with patch.object(cropper, '_should_skip_processing', return_value=True):
            result = cropper.process_image(image_path, 1, force_process=False)
            
            assert result['success']
            assert result['skipped']
    
    @patch('ml.segmentation.cropper.cv2.imread')
    @patch('ml.segmentation.cropper.get_crops_dir')
    def test_process_image_with_opencv_fallback(self, mock_crops_dir, mock_imread, cropper, tmp_path):
        """Test processing image with OpenCV fallback."""
        mock_crops_dir.return_value = tmp_path
        mock_imread.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        
        image_path = tmp_path / "image.jpg"
        image_path.write_bytes(b"test")
        
        with patch('ml.segmentation.cropper._remove_background_opencv') as mock_remove:
            mock_remove.return_value = np.zeros((100, 100, 4), dtype=np.uint8)
            
            with patch('ml.segmentation.cropper.validate_crop_quality', return_value=True):
                with patch('ml.segmentation.cropper.create_transparent_crop') as mock_create:
                    mock_create.return_value = np.zeros((100, 100, 4), dtype=np.uint8)
                    
                    with patch('ml.segmentation.cropper.save_image'):
                        result = cropper._process_with_opencv_fallback(image_path, 1)
                        
                        assert result['success']
                        assert result['method'] == 'fallback_chain'
    
    def test_should_reprocess_newer_source(self, cropper, tmp_path):
        """Test should reprocess when source is newer."""
        source_path = tmp_path / "source.jpg"
        target_path = tmp_path / "target.png"
        
        source_path.write_bytes(b"test")
        target_path.write_bytes(b"test")
        
        # Make source newer
        import time
        time.sleep(0.1)
        source_path.write_bytes(b"updated")
        
        with patch('ml.segmentation.cropper.get_file_timestamp') as mock_timestamp:
            mock_timestamp.side_effect = lambda p: p.stat().st_mtime if p.exists() else None
            
            result = cropper._should_reprocess(source_path, target_path)
            
            assert result is True
    
    def test_update_stats_from_result_success(self, cropper):
        """Test updating stats from successful result."""
        stats = {'processed': 0, 'successful': 0, 'failed': 0, 'skipped': 0, 'errors': []}
        record = {'id': 1}
        result = {'success': True, 'skipped': False}
        
        cropper._update_stats_from_result(stats, record, result)
        
        assert stats['processed'] == 1
        assert stats['successful'] == 1
    
    def test_update_stats_from_result_skipped(self, cropper):
        """Test updating stats from skipped result."""
        stats = {'processed': 0, 'successful': 0, 'failed': 0, 'skipped': 0, 'errors': []}
        record = {'id': 1}
        result = {'success': True, 'skipped': True}
        
        cropper._update_stats_from_result(stats, record, result)
        
        assert stats['processed'] == 1
        assert stats['skipped'] == 1
    
    def test_update_stats_from_result_failed(self, cropper):
        """Test updating stats from failed result."""
        stats = {'processed': 0, 'successful': 0, 'failed': 0, 'skipped': 0, 'errors': []}
        record = {'id': 1}
        result = {'success': False, 'error': 'Test error'}
        
        cropper._update_stats_from_result(stats, record, result)
        
        assert stats['processed'] == 1
        assert stats['failed'] == 1
        assert len(stats['errors']) == 1
    
    @patch('ml.segmentation.cropper.get_crops_dir')
    def test_process_batch(self, mock_crops_dir, cropper, tmp_path):
        """Test processing batch of images."""
        mock_crops_dir.return_value = tmp_path
        
        image_records = [
            {'id': 1, 'raw_image_path': tmp_path / "image1.jpg"},
            {'id': 2, 'raw_image_path': tmp_path / "image2.jpg"}
        ]
        
        for record in image_records:
            record['raw_image_path'].write_bytes(b"test")
        
        with patch.object(cropper, 'process_image') as mock_process:
            mock_process.return_value = {'success': True, 'skipped': False}
            
            result = cropper.process_batch(image_records, limit=0)
            
            assert result['total'] == 2
            assert result['processed'] == 2
            assert mock_process.call_count == 2


class TestCreateCacaoCropper:
    """Tests for create_cacao_cropper function."""
    
    @patch('ml.segmentation.cropper.create_yolo_inference')
    def test_create_cacao_cropper_with_yolo(self, mock_create_yolo):
        """Test creating cropper with YOLO enabled."""
        mock_yolo = Mock()
        mock_create_yolo.return_value = mock_yolo
        
        cropper = create_cacao_cropper(enable_yolo=True)
        
        assert cropper.enable_yolo is True
        assert cropper.yolo_inference is not None
    
    @patch('ml.segmentation.cropper.create_yolo_inference')
    def test_create_cacao_cropper_without_yolo(self, mock_create_yolo):
        """Test creating cropper with YOLO disabled."""
        cropper = create_cacao_cropper(enable_yolo=False)
        
        assert cropper.enable_yolo is False
        assert cropper.yolo_inference is None
        mock_create_yolo.assert_not_called()
    
    @patch('ml.segmentation.cropper.create_yolo_inference')
    def test_create_cacao_cropper_yolo_error(self, mock_create_yolo):
        """Test creating cropper when YOLO fails to load."""
        mock_create_yolo.side_effect = Exception("YOLO load error")
        
        cropper = create_cacao_cropper(enable_yolo=True)
        
        assert cropper.enable_yolo is False
        assert cropper.yolo_inference is None
    
    @patch('ml.segmentation.cropper.get_crops_dir')
    def test_get_yolo_prediction_with_fallback_success(self, mock_crops_dir, cropper, tmp_path):
        """Test getting YOLO prediction with successful prediction."""
        mock_crops_dir.return_value = tmp_path
        
        mock_yolo = Mock()
        mock_prediction = {
            'confidence': 0.8,
            'area': 1000,
            'mask': np.ones((100, 100), dtype=np.float32),
            'bbox': [10, 10, 50, 50]
        }
        mock_yolo.get_best_prediction.return_value = mock_prediction
        
        cropper.yolo_inference = mock_yolo
        cropper.enable_yolo = True
        
        image_path = tmp_path / "image.jpg"
        image_path.write_bytes(b"test")
        
        result = cropper._get_yolo_prediction_with_fallback(image_path)
        
        assert result == mock_prediction
    
    @patch('ml.segmentation.cropper.get_crops_dir')
    def test_get_yolo_prediction_with_fallback_lower_threshold(self, mock_crops_dir, cropper, tmp_path):
        """Test getting YOLO prediction with lower threshold fallback."""
        mock_crops_dir.return_value = tmp_path
        
        mock_yolo = Mock()
        mock_yolo.get_best_prediction.return_value = None
        mock_prediction = {
            'confidence': 0.15,
            'area': 1000,
            'mask': np.ones((100, 100), dtype=np.float32),
            'bbox': [10, 10, 50, 50]
        }
        mock_yolo.predict.return_value = [mock_prediction]
        
        cropper.yolo_inference = mock_yolo
        cropper.enable_yolo = True
        
        image_path = tmp_path / "image.jpg"
        image_path.write_bytes(b"test")
        
        result = cropper._get_yolo_prediction_with_fallback(image_path)
        
        assert result is not None
    
    def test_validate_prediction_quality_high_confidence(self, cropper, tmp_path):
        """Test validating prediction quality with high confidence."""
        prediction = {
            'confidence': 0.9,
            'area': 1000,
            'mask': np.ones((100, 100), dtype=np.float32)
        }
        image_path = tmp_path / "image.jpg"
        image_path.write_bytes(b"test")
        
        cropper._validate_prediction_quality(prediction, image_path)
        
        # Should not raise exception
    
    def test_validate_prediction_quality_low_confidence(self, cropper, tmp_path):
        """Test validating prediction quality with low confidence."""
        prediction = {
            'confidence': 0.3,
            'area': 1000,
            'mask': np.ones((100, 100), dtype=np.float32)
        }
        image_path = tmp_path / "image.jpg"
        image_path.write_bytes(b"test")
        
        cropper._validate_prediction_quality(prediction, image_path)
        
        # Should log warning but not raise exception
    
    def test_validate_prediction_quality_small_area(self, cropper, tmp_path):
        """Test validating prediction quality with small area."""
        prediction = {
            'confidence': 0.8,
            'area': 50,
            'mask': np.ones((10, 10), dtype=np.float32)
        }
        image_path = tmp_path / "image.jpg"
        image_path.write_bytes(b"test")
        
        cropper._validate_prediction_quality(prediction, image_path)
        
        # Should log warning but not raise exception
    
    @patch('ml.segmentation.cropper.get_crops_dir')
    @patch('ml.segmentation.cropper.get_masks_dir')
    @patch('ml.segmentation.cropper.cv2.imread')
    def test_process_image_with_yolo(self, mock_imread, mock_masks_dir, mock_crops_dir, tmp_path):
        """Test processing image with YOLO enabled."""
        mock_crops_dir.return_value = tmp_path
        mock_masks_dir.return_value = tmp_path
        mock_imread.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        
        mock_yolo = Mock()
        mock_prediction = {
            'confidence': 0.8,
            'area': 1000,
            'mask': np.ones((100, 100), dtype=np.float32),
            'bbox': [10, 10, 50, 50]
        }
        mock_yolo.get_best_prediction.return_value = mock_prediction
        
        cropper = CacaoCropper(
            yolo_inference=mock_yolo,
            enable_yolo=True
        )
        
        image_path = tmp_path / "image.jpg"
        image_path.write_bytes(b"test")
        
        with patch.object(cropper, '_should_skip_processing', return_value=False):
            with patch.object(cropper, '_prepare_mask', return_value=np.ones((100, 100), dtype=np.uint8) * 255):
                with patch.object(cropper, '_create_and_save_crop'):
                    result = cropper.process_image(image_path, 1)
                    
                    assert result['success']
    
    @patch('ml.segmentation.cropper.get_crops_dir')
    def test_process_image_yolo_no_detections(self, mock_crops_dir, tmp_path):
        """Test processing image when YOLO finds no detections."""
        mock_crops_dir.return_value = tmp_path
        
        mock_yolo = Mock()
        mock_yolo.get_best_prediction.return_value = None
        mock_yolo.predict.return_value = []
        
        cropper = CacaoCropper(
            yolo_inference=mock_yolo,
            enable_yolo=True
        )
        
        image_path = tmp_path / "image.jpg"
        image_path.write_bytes(b"test")
        
        with patch.object(cropper, '_should_skip_processing', return_value=False):
            result = cropper.process_image(image_path, 1)
            
            assert result['success'] is False
            assert 'error' in result
    
    @patch('ml.segmentation.cropper.get_crops_dir')
    def test_process_image_yolo_error_fallback(self, mock_crops_dir, tmp_path):
        """Test processing image when YOLO errors and falls back to OpenCV."""
        mock_crops_dir.return_value = tmp_path
        
        mock_yolo = Mock()
        mock_yolo.get_best_prediction.side_effect = Exception("YOLO error")
        
        cropper = CacaoCropper(
            yolo_inference=mock_yolo,
            enable_yolo=True
        )
        
        image_path = tmp_path / "image.jpg"
        image_path.write_bytes(b"test")
        
        with patch.object(cropper, '_should_skip_processing', return_value=False):
            with patch.object(cropper, '_process_with_opencv_fallback') as mock_fallback:
                mock_fallback.return_value = {'success': True, 'skipped': False}
                
                result = cropper.process_image(image_path, 1)
                
                assert result['success']
                mock_fallback.assert_called_once()
    
    @patch('ml.segmentation.cropper.get_crops_dir')
    def test_process_batch_with_limit(self, mock_crops_dir, cropper, tmp_path):
        """Test processing batch with limit."""
        mock_crops_dir.return_value = tmp_path
        
        image_records = [
            {'id': 1, 'raw_image_path': tmp_path / "image1.jpg"},
            {'id': 2, 'raw_image_path': tmp_path / "image2.jpg"},
            {'id': 3, 'raw_image_path': tmp_path / "image3.jpg"}
        ]
        
        for record in image_records:
            record['raw_image_path'].write_bytes(b"test")
        
        with patch.object(cropper, 'process_image') as mock_process:
            mock_process.return_value = {'success': True, 'skipped': False}
            
            result = cropper.process_batch(image_records, limit=2)
            
            assert result['total'] == 2
            assert mock_process.call_count == 2
    
    @patch('ml.segmentation.cropper.get_crops_dir')
    def test_process_batch_with_progress_callback(self, mock_crops_dir, cropper, tmp_path):
        """Test processing batch with progress callback."""
        mock_crops_dir.return_value = tmp_path
        
        image_records = [
            {'id': 1, 'raw_image_path': tmp_path / "image1.jpg"},
            {'id': 2, 'raw_image_path': tmp_path / "image2.jpg"}
        ]
        
        for record in image_records:
            record['raw_image_path'].write_bytes(b"test")
        
        callback_calls = []
        
        def progress_callback(current, total, result):
            callback_calls.append((current, total, result))
        
        with patch.object(cropper, 'process_image') as mock_process:
            mock_process.return_value = {'success': True, 'skipped': False}
            
            cropper.process_batch(image_records, progress_callback=progress_callback)
            
            assert len(callback_calls) == 2
    
    @patch('ml.segmentation.cropper.get_crops_dir')
    def test_process_batch_with_errors(self, mock_crops_dir, cropper, tmp_path):
        """Test processing batch with errors."""
        mock_crops_dir.return_value = tmp_path
        
        image_records = [
            {'id': 1, 'raw_image_path': tmp_path / "image1.jpg"},
            {'id': 2, 'raw_image_path': tmp_path / "image2.jpg"}
        ]
        
        for record in image_records:
            record['raw_image_path'].write_bytes(b"test")
        
        with patch.object(cropper, 'process_image') as mock_process:
            mock_process.side_effect = Exception("Processing error")
            
            result = cropper.process_batch(image_records)
            
            assert result['failed'] == 2
            assert len(result['errors']) == 2

