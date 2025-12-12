"""
Tests for YOLO segmentation inference.
"""
import pytest
import numpy as np
import torch
import cv2
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from ml.segmentation.infer_yolo_seg import (
    YOLOSegmentationInference,
    create_yolo_inference
)


class TestYOLOSegmentationInference:
    """Tests for YOLOSegmentationInference class."""
    
    @patch('ml.segmentation.infer_yolo_seg.YOLO')
    @patch('ml.segmentation.infer_yolo_seg.get_yolo_artifacts_dir')
    def test_initialization_with_model_path(self, mock_get_dir, mock_yolo, tmp_path):
        """Test initialization with model path."""
        mock_get_dir.return_value = tmp_path
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        
        model_path = tmp_path / "model.pt"
        model_path.write_bytes(b"fake model")
        
        inference = YOLOSegmentationInference(model_path=model_path, confidence_threshold=0.5)
        
        assert inference.confidence_threshold == 0.5
        assert inference.model is not None
    
    @patch('ml.segmentation.infer_yolo_seg.YOLO')
    @patch('ml.segmentation.infer_yolo_seg.get_yolo_artifacts_dir')
    def test_initialization_without_model_path(self, mock_get_dir, mock_yolo, tmp_path):
        """Test initialization without model path."""
        mock_get_dir.return_value = tmp_path
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        
        with patch.object(YOLOSegmentationInference, '_find_custom_model', return_value=None):
            inference = YOLOSegmentationInference(confidence_threshold=0.5)
            
            assert inference.confidence_threshold == 0.5
    
    @patch('ml.segmentation.infer_yolo_seg.YOLO')
    def test_initialization_yolo_not_available(self, mock_yolo):
        """Test initialization when YOLO is not available."""
        mock_yolo.__class__ = None
        
        with patch('ml.segmentation.infer_yolo_seg.YOLO', None):
            with pytest.raises(ImportError, match="Ultralytics no está instalado"):
                YOLOSegmentationInference(confidence_threshold=0.5)
    
    @patch('ml.segmentation.infer_yolo_seg.YOLO')
    @patch('ml.segmentation.infer_yolo_seg.get_yolo_artifacts_dir')
    def test_predict(self, mock_get_dir, mock_yolo, tmp_path):
        """Test prediction."""
        mock_get_dir.return_value = tmp_path
        mock_model = Mock()
        mock_result = Mock()
        mock_result.boxes = Mock()
        mock_result.masks = Mock()
        mock_result.masks.data = [torch.zeros((100, 100))]
        mock_model.return_value = [mock_result]
        mock_yolo.return_value = mock_model
        
        inference = YOLOSegmentationInference(confidence_threshold=0.5)
        inference.model = mock_model
        
        image_path = tmp_path / "image.jpg"
        image_path.write_bytes(b"fake image")
        
        results = inference.predict(image_path)
        
        assert isinstance(results, list)
    
    @patch('ml.segmentation.infer_yolo_seg.YOLO')
    @patch('ml.segmentation.infer_yolo_seg.get_yolo_artifacts_dir')
    def test_get_best_prediction(self, mock_get_dir, mock_yolo, tmp_path):
        """Test getting best prediction."""
        mock_get_dir.return_value = tmp_path
        mock_model = Mock()
        mock_result = Mock()
        mock_result.boxes = Mock()
        mock_result.masks = Mock()
        mock_result.masks.data = [torch.zeros((100, 100))]
        mock_model.return_value = [mock_result]
        mock_yolo.return_value = mock_model
        
        inference = YOLOSegmentationInference(confidence_threshold=0.5)
        inference.model = mock_model
        
        image_path = tmp_path / "image.jpg"
        image_path.write_bytes(b"fake image")
        
        result = inference.get_best_prediction(image_path)
        
        assert result is None or isinstance(result, dict)


    @patch('ml.segmentation.infer_yolo_seg.YOLO')
    @patch('ml.segmentation.infer_yolo_seg.get_yolo_artifacts_dir')
    @patch('ml.segmentation.infer_yolo_seg.ensure_dir_exists')
    def test_find_custom_model(self, mock_ensure_dir, mock_get_dir, mock_yolo, tmp_path):
        """Test finding custom model."""
        mock_get_dir.return_value = tmp_path
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        
        models_dir = tmp_path / "models" / "cacao_seg_20240101_120000" / "weights"
        models_dir.mkdir(parents=True, exist_ok=True)
        (models_dir / "best.pt").write_bytes(b"fake model")
        
        inference = YOLOSegmentationInference(confidence_threshold=0.5)
        
        custom_model = inference._find_custom_model()
        
        assert custom_model is not None
        assert custom_model.exists()
    
    @patch('ml.segmentation.infer_yolo_seg.YOLO')
    @patch('ml.segmentation.infer_yolo_seg.get_yolo_artifacts_dir')
    @patch('ml.segmentation.infer_yolo_seg.ensure_dir_exists')
    def test_find_custom_model_no_model(self, mock_ensure_dir, mock_get_dir, mock_yolo, tmp_path):
        """Test finding custom model when none exists."""
        mock_get_dir.return_value = tmp_path
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        
        inference = YOLOSegmentationInference(confidence_threshold=0.5)
        
        custom_model = inference._find_custom_model()
        
        assert custom_model is None
    
    @patch('ml.segmentation.infer_yolo_seg.YOLO')
    @patch('ml.segmentation.infer_yolo_seg.get_yolo_artifacts_dir')
    @patch('ml.segmentation.infer_yolo_seg.ensure_dir_exists')
    @patch('ml.segmentation.infer_yolo_seg.cv2.moments')
    def test_calculate_mask_center(self, mock_moments, mock_ensure_dir, mock_get_dir, mock_yolo, tmp_path):
        """Test calculating mask center."""
        mock_get_dir.return_value = tmp_path
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        
        mock_moments.return_value = {'m00': 100.0, 'm10': 5000.0, 'm01': 5000.0}
        
        inference = YOLOSegmentationInference(confidence_threshold=0.5)
        mask = np.ones((100, 100), dtype=np.uint8) * 255
        
        center = inference._calculate_mask_center(mask)
        
        assert len(center) == 2
        assert all(isinstance(x, int) for x in center)
    
    @patch('ml.segmentation.infer_yolo_seg.YOLO')
    @patch('ml.segmentation.infer_yolo_seg.get_yolo_artifacts_dir')
    @patch('ml.segmentation.infer_yolo_seg.ensure_dir_exists')
    @patch('ml.segmentation.infer_yolo_seg.cv2.moments')
    def test_calculate_mask_center_fallback(self, mock_moments, mock_ensure_dir, mock_get_dir, mock_yolo, tmp_path):
        """Test calculating mask center with fallback."""
        mock_get_dir.return_value = tmp_path
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        
        mock_moments.return_value = {'m00': 0.0}
        
        inference = YOLOSegmentationInference(confidence_threshold=0.5)
        mask = np.zeros((100, 100), dtype=np.uint8)
        
        center = inference._calculate_mask_center(mask)
        
        assert len(center) == 2
        assert center == (50, 50)  # Geometric center
    
    @patch('ml.segmentation.infer_yolo_seg.YOLO')
    @patch('ml.segmentation.infer_yolo_seg.get_yolo_artifacts_dir')
    @patch('ml.segmentation.infer_yolo_seg.ensure_dir_exists')
    def test_process_yolo_results(self, mock_ensure_dir, mock_get_dir, mock_yolo, tmp_path):
        """Test processing YOLO results."""
        mock_get_dir.return_value = tmp_path
        mock_model = Mock()
        mock_model.names = {0: 'cacao_grain'}
        mock_yolo.return_value = mock_model
        
        mock_result = Mock()
        mock_box = Mock()
        mock_box.conf = torch.tensor([0.8])
        mock_box.cls = torch.tensor([0])
        mock_box.xyxy = torch.tensor([[10, 10, 50, 50]])
        mock_result.boxes = [mock_box]
        
        mock_mask = Mock()
        mock_mask.data = [torch.ones((100, 100))]
        mock_result.masks = [mock_mask]
        
        inference = YOLOSegmentationInference(confidence_threshold=0.5)
        inference.model = mock_model
        
        predictions = inference._process_yolo_results([mock_result])
        
        assert len(predictions) == 1
        assert 'confidence' in predictions[0]
        assert 'bbox' in predictions[0]
        assert 'mask' in predictions[0]
    
    @patch('ml.segmentation.infer_yolo_seg.YOLO')
    @patch('ml.segmentation.infer_yolo_seg.get_yolo_artifacts_dir')
    @patch('ml.segmentation.infer_yolo_seg.ensure_dir_exists')
    def test_process_yolo_results_no_masks(self, mock_ensure_dir, mock_get_dir, mock_yolo, tmp_path):
        """Test processing YOLO results with no masks."""
        mock_get_dir.return_value = tmp_path
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        
        mock_result = Mock()
        mock_result.masks = None
        
        inference = YOLOSegmentationInference(confidence_threshold=0.5)
        
        predictions = inference._process_yolo_results([mock_result])
        
        assert len(predictions) == 0
    
    @patch('ml.segmentation.infer_yolo_seg.YOLO')
    @patch('ml.segmentation.infer_yolo_seg.get_yolo_artifacts_dir')
    @patch('ml.segmentation.infer_yolo_seg.ensure_dir_exists')
    def test_process_yolo_results_low_confidence(self, mock_ensure_dir, mock_get_dir, mock_yolo, tmp_path):
        """Test processing YOLO results with low confidence."""
        mock_get_dir.return_value = tmp_path
        mock_model = Mock()
        mock_model.names = {0: 'cacao_grain'}
        mock_yolo.return_value = mock_model
        
        mock_result = Mock()
        mock_box = Mock()
        mock_box.conf = torch.tensor([0.3])  # Low confidence
        mock_box.cls = torch.tensor([0])
        mock_box.xyxy = torch.tensor([[10, 10, 50, 50]])
        mock_result.boxes = [mock_box]
        
        mock_mask = Mock()
        mock_mask.data = [torch.ones((100, 100))]
        mock_result.masks = [mock_mask]
        
        inference = YOLOSegmentationInference(confidence_threshold=0.5)
        inference.model = mock_model
        
        predictions = inference._process_yolo_results([mock_result], min_confidence=0.5)
        
        assert len(predictions) == 0
    
    @patch('ml.segmentation.infer_yolo_seg.YOLO')
    @patch('ml.segmentation.infer_yolo_seg.get_yolo_artifacts_dir')
    @patch('ml.segmentation.infer_yolo_seg.ensure_dir_exists')
    def test_try_lower_thresholds(self, mock_ensure_dir, mock_get_dir, mock_yolo, tmp_path):
        """Test trying lower thresholds."""
        mock_get_dir.return_value = tmp_path
        mock_model = Mock()
        mock_model.names = {0: 'cacao_grain'}
        mock_yolo.return_value = mock_model
        
        mock_result = Mock()
        mock_box = Mock()
        mock_box.conf = torch.tensor([0.4])
        mock_box.cls = torch.tensor([0])
        mock_box.xyxy = torch.tensor([[10, 10, 50, 50]])
        mock_result.boxes = [mock_box]
        
        mock_mask = Mock()
        mock_mask.data = [torch.ones((100, 100))]
        mock_result.masks = [mock_mask]
        
        inference = YOLOSegmentationInference(confidence_threshold=0.5)
        inference.model = mock_model
        inference.model.return_value = [mock_result]
        
        image_path = tmp_path / "test.jpg"
        image_path.write_bytes(b"fake")
        
        predictions = inference._try_lower_thresholds(image_path, [0.4, 0.3], min_confidence_ratio=0.8)
        
        assert isinstance(predictions, list)
    
    @patch('ml.segmentation.infer_yolo_seg.YOLO')
    @patch('ml.segmentation.infer_yolo_seg.get_yolo_artifacts_dir')
    @patch('ml.segmentation.infer_yolo_seg.ensure_dir_exists')
    def test_filter_predictions_by_class(self, mock_ensure_dir, mock_get_dir, mock_yolo, tmp_path):
        """Test filtering predictions by class."""
        mock_get_dir.return_value = tmp_path
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        
        predictions = [
            {'class_name': 'cacao_grain', 'confidence': 0.8},
            {'class_name': 'other', 'confidence': 0.7},
        ]
        
        inference = YOLOSegmentationInference(confidence_threshold=0.5)
        
        filtered = inference.filter_predictions_by_class(
            predictions,
            target_classes=['cacao_grain']
        )
        
        assert len(filtered) == 1
        assert filtered[0]['class_name'] == 'cacao_grain'
    
    @patch('ml.segmentation.infer_yolo_seg.YOLO')
    @patch('ml.segmentation.infer_yolo_seg.get_yolo_artifacts_dir')
    @patch('ml.segmentation.infer_yolo_seg.ensure_dir_exists')
    def test_validate_prediction_quality_valid(self, mock_ensure_dir, mock_get_dir, mock_yolo, tmp_path):
        """Test validating valid prediction quality."""
        mock_get_dir.return_value = tmp_path
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        
        prediction = {
            'confidence': 0.8,
            'area': 1000,
            'mask': np.ones((100, 100), dtype=np.float32) * 0.8
        }
        
        inference = YOLOSegmentationInference(confidence_threshold=0.5)
        
        is_valid = inference.validate_prediction_quality(prediction)
        
        assert is_valid is True
    
    @patch('ml.segmentation.infer_yolo_seg.YOLO')
    @patch('ml.segmentation.infer_yolo_seg.get_yolo_artifacts_dir')
    @patch('ml.segmentation.infer_yolo_seg.ensure_dir_exists')
    def test_validate_prediction_quality_invalid_confidence(self, mock_ensure_dir, mock_get_dir, mock_yolo, tmp_path):
        """Test validating prediction with invalid confidence."""
        mock_get_dir.return_value = tmp_path
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        
        prediction = {
            'confidence': 0.3,  # Below threshold
            'area': 1000,
            'mask': np.ones((100, 100), dtype=np.float32)
        }
        
        inference = YOLOSegmentationInference(confidence_threshold=0.5)
        
        is_valid = inference.validate_prediction_quality(prediction)
        
        assert is_valid is False
    
    @patch('ml.segmentation.infer_yolo_seg.YOLO')
    @patch('ml.segmentation.infer_yolo_seg.get_yolo_artifacts_dir')
    @patch('ml.segmentation.infer_yolo_seg.ensure_dir_exists')
    def test_validate_prediction_quality_small_area(self, mock_ensure_dir, mock_get_dir, mock_yolo, tmp_path):
        """Test validating prediction with small area."""
        mock_get_dir.return_value = tmp_path
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        
        prediction = {
            'confidence': 0.8,
            'area': 50,  # Below minimum
            'mask': np.ones((100, 100), dtype=np.float32) * 0.8
        }
        
        inference = YOLOSegmentationInference(confidence_threshold=0.5)
        
        is_valid = inference.validate_prediction_quality(prediction)
        
        assert is_valid is False
    
    @patch('ml.segmentation.infer_yolo_seg.YOLO')
    @patch('ml.segmentation.infer_yolo_seg.get_yolo_artifacts_dir')
    @patch('ml.segmentation.infer_yolo_seg.ensure_dir_exists')
    def test_validate_prediction_quality_empty_mask(self, mock_ensure_dir, mock_get_dir, mock_yolo, tmp_path):
        """Test validating prediction with empty mask."""
        mock_get_dir.return_value = tmp_path
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        
        prediction = {
            'confidence': 0.8,
            'area': 1000,
            'mask': np.zeros((100, 100), dtype=np.float32)
        }
        
        inference = YOLOSegmentationInference(confidence_threshold=0.5)
        
        is_valid = inference.validate_prediction_quality(prediction)
        
        assert is_valid is False
    
    @patch('ml.segmentation.infer_yolo_seg.YOLO')
    @patch('ml.segmentation.infer_yolo_seg.get_yolo_artifacts_dir')
    @patch('ml.segmentation.infer_yolo_seg.ensure_dir_exists')
    @patch('ml.segmentation.infer_yolo_seg.cv2.imwrite')
    def test_save_prediction_debug(self, mock_imwrite, mock_ensure_dir, mock_get_dir, mock_yolo, tmp_path):
        """Test saving prediction debug info."""
        mock_get_dir.return_value = tmp_path
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        
        prediction = {
            'mask': np.ones((100, 100), dtype=np.float32) * 0.8,
            'bbox': [10, 10, 50, 50],
            'confidence': 0.8
        }
        
        inference = YOLOSegmentationInference(confidence_threshold=0.5)
        image_path = tmp_path / "test.jpg"
        image_path.write_bytes(b"fake")
        
        output_dir = tmp_path / "output"
        
        with patch('ml.segmentation.infer_yolo_seg.cv2.imread', return_value=np.zeros((100, 100, 3), dtype=np.uint8)):
            inference.save_prediction_debug(image_path, prediction, output_dir)
            
            assert output_dir.exists()


class TestCreateYoloInference:
    """Tests for create_yolo_inference function."""
    
    @patch('ml.segmentation.infer_yolo_seg.YOLOSegmentationInference')
    def test_create_yolo_inference(self, mock_inference_class):
        """Test creating YOLO inference."""
        mock_instance = Mock()
        mock_inference_class.return_value = mock_instance
        
        result = create_yolo_inference(confidence_threshold=0.5)
        
        assert result is not None
        mock_inference_class.assert_called_once()

