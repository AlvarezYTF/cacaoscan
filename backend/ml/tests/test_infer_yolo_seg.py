"""
Tests for YOLO segmentation inference.
"""
import pytest
import numpy as np
import torch
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from ml.segmentation.infer_yolo_seg import YOLOSegmentationInference, create_yolo_inference


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

