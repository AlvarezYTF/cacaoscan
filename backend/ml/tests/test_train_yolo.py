"""
Tests for YOLO training module.
"""
import pytest
import numpy as np
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from ml.segmentation.train_yolo import (
    YOLOTrainingManager,
    create_yolo_trainer,
    train_cacao_yolo_model
)


class TestYOLOTrainingManager:
    """Tests for YOLOTrainingManager class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)
    
    @patch('ml.segmentation.train_yolo.YOLO')
    @patch('ml.segmentation.train_yolo.get_yolo_artifacts_dir')
    @patch('ml.segmentation.train_yolo.ensure_dir_exists')
    def test_initialization(
        self, mock_ensure_dir, mock_get_dir, mock_yolo, temp_dir
    ):
        """Test YOLOTrainingManager initialization."""
        mock_get_dir.return_value = temp_dir
        
        manager = YOLOTrainingManager(
            dataset_size=150,
            train_split=0.7,
            val_split=0.2,
            test_split=0.1,
            epochs=100,
            batch_size=16
        )
        
        assert manager.dataset_size == 150
        assert manager.train_split == 0.7
        assert manager.val_split == 0.2
        assert manager.test_split == 0.1
        assert manager.epochs == 100
        assert manager.batch_size == 16
    
    @patch('ml.segmentation.train_yolo.YOLO')
    def test_initialization_yolo_not_available(self, mock_yolo):
        """Test initialization when YOLO is not available."""
        with patch('ml.segmentation.train_yolo.YOLO', None):
            with pytest.raises(ImportError, match="Ultralytics no está instalado"):
                YOLOTrainingManager()
    
    @patch('ml.segmentation.train_yolo.YOLO')
    @patch('ml.segmentation.train_yolo.get_yolo_artifacts_dir')
    @patch('ml.segmentation.train_yolo.ensure_dir_exists')
    def test_create_dataset_structure(
        self, mock_ensure_dir, mock_get_dir, mock_yolo, temp_dir
    ):
        """Test creating dataset structure."""
        mock_get_dir.return_value = temp_dir
        
        manager = YOLOTrainingManager()
        dataset_dir = manager.create_dataset_structure()
        
        assert dataset_dir.exists()
        mock_ensure_dir.assert_called()
    
    @patch('ml.segmentation.train_yolo.YOLO')
    @patch('ml.segmentation.train_yolo.get_yolo_artifacts_dir')
    @patch('ml.segmentation.train_yolo.ensure_dir_exists')
    @patch('ml.segmentation.train_yolo.CacaoDatasetLoader')
    def test_generate_annotations_from_crops(
        self, mock_loader_class, mock_ensure_dir, mock_get_dir, mock_yolo, temp_dir
    ):
        """Test generating annotations from crops."""
        mock_get_dir.return_value = temp_dir
        
        # Mock dataset loader
        mock_loader = Mock()
        mock_df = Mock()
        mock_df.__len__ = Mock(return_value=200)
        mock_df.iterrows.return_value = [
            (0, {'id': 1}),
            (1, {'id': 2}),
        ]
        mock_loader.load_dataset.return_value = mock_df
        mock_loader.validate_images_exist.return_value = (mock_df, [])
        mock_loader_class.return_value = mock_loader
        
        manager = YOLOTrainingManager(dataset_size=2)
        
        with patch.object(manager, '_generate_automatic_annotation') as mock_gen:
            mock_gen.return_value = [{'class_id': 0, 'bbox': [0.5, 0.5, 0.2, 0.2], 'mask': np.zeros((100, 100)), 'confidence': 0.8}]
            
            annotations = manager.generate_annotations_from_crops()
            
            assert isinstance(annotations, dict)
    
    @patch('ml.segmentation.train_yolo.YOLO')
    @patch('ml.segmentation.train_yolo.get_yolo_artifacts_dir')
    @patch('ml.segmentation.train_yolo.ensure_dir_exists')
    def test_normalize_mask(self, mock_ensure_dir, mock_get_dir, mock_yolo, temp_dir):
        """Test mask normalization."""
        mock_get_dir.return_value = temp_dir
        
        manager = YOLOTrainingManager()
        mask = np.zeros((50, 50), dtype=np.uint8)
        
        result = manager._normalize_mask(mask, 100, 100)
        
        assert result.shape == (100, 100)
        assert result.dtype == np.uint8
    
    @patch('ml.segmentation.train_yolo.YOLO')
    @patch('ml.segmentation.train_yolo.get_yolo_artifacts_dir')
    @patch('ml.segmentation.train_yolo.ensure_dir_exists')
    def test_calculate_yolo_bbox_from_mask(
        self, mock_ensure_dir, mock_get_dir, mock_yolo, temp_dir
    ):
        """Test calculating YOLO bbox from mask."""
        mock_get_dir.return_value = temp_dir
        
        manager = YOLOTrainingManager()
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[30:70, 30:70] = 255
        
        bbox = manager._calculate_yolo_bbox_from_mask(mask, 100, 100)
        
        assert bbox is not None
        assert len(bbox) == 4
        assert all(0.0 <= x <= 1.0 for x in bbox)
    
    @patch('ml.segmentation.train_yolo.YOLO')
    @patch('ml.segmentation.train_yolo.get_yolo_artifacts_dir')
    @patch('ml.segmentation.train_yolo.ensure_dir_exists')
    def test_calculate_yolo_bbox_empty_mask(
        self, mock_ensure_dir, mock_get_dir, mock_yolo, temp_dir
    ):
        """Test calculating YOLO bbox from empty mask."""
        mock_get_dir.return_value = temp_dir
        
        manager = YOLOTrainingManager()
        mask = np.zeros((100, 100), dtype=np.uint8)
        
        bbox = manager._calculate_yolo_bbox_from_mask(mask, 100, 100)
        
        assert bbox is None
    
    @patch('ml.segmentation.train_yolo.YOLO')
    @patch('ml.segmentation.train_yolo.get_yolo_artifacts_dir')
    @patch('ml.segmentation.train_yolo.ensure_dir_exists')
    def test_create_annotation_dict(
        self, mock_ensure_dir, mock_get_dir, mock_yolo, temp_dir
    ):
        """Test creating annotation dictionary."""
        mock_get_dir.return_value = temp_dir
        
        manager = YOLOTrainingManager()
        bbox = [0.5, 0.5, 0.2, 0.2]
        mask = np.zeros((100, 100), dtype=np.uint8)
        confidence = 0.8
        
        annotation = manager._create_annotation_dict(bbox, mask, confidence)
        
        assert annotation['class_id'] == 0
        assert annotation['bbox'] == bbox
        assert annotation['confidence'] == confidence
    
    @patch('ml.segmentation.train_yolo.YOLO')
    @patch('ml.segmentation.train_yolo.get_yolo_artifacts_dir')
    @patch('ml.segmentation.train_yolo.ensure_dir_exists')
    @patch('ml.segmentation.train_yolo.cv2.imread')
    def test_generate_annotation_fallback(
        self, mock_imread, mock_ensure_dir, mock_get_dir, mock_yolo, temp_dir
    ):
        """Test fallback annotation generation."""
        mock_get_dir.return_value = temp_dir
        mock_imread.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        
        manager = YOLOTrainingManager()
        image_path = temp_dir / "test.bmp"
        image_path.write_bytes(b"fake")
        
        annotation = manager._generate_annotation_fallback(image_path)
        
        assert annotation is not None
        assert len(annotation) == 1
        assert 'bbox' in annotation[0]
        assert 'mask' in annotation[0]
    
    @patch('ml.segmentation.train_yolo.YOLO')
    @patch('ml.segmentation.train_yolo.get_yolo_artifacts_dir')
    @patch('ml.segmentation.train_yolo.ensure_dir_exists')
    @patch('ml.segmentation.train_yolo.cv2.imread')
    def test_generate_annotation_fallback_no_image(
        self, mock_imread, mock_ensure_dir, mock_get_dir, mock_yolo, temp_dir
    ):
        """Test fallback annotation with no image."""
        mock_get_dir.return_value = temp_dir
        mock_imread.return_value = None
        
        manager = YOLOTrainingManager()
        image_path = temp_dir / "test.bmp"
        
        annotation = manager._generate_annotation_fallback(image_path)
        
        assert annotation is None
    
    @patch('ml.segmentation.train_yolo.YOLO')
    @patch('ml.segmentation.train_yolo.get_yolo_artifacts_dir')
    @patch('ml.segmentation.train_yolo.ensure_dir_exists')
    def test_generate_automatic_annotation(
        self, mock_ensure_dir, mock_get_dir, mock_yolo, temp_dir
    ):
        """Test automatic annotation generation."""
        mock_get_dir.return_value = temp_dir
        
        manager = YOLOTrainingManager()
        image_path = temp_dir / "test.bmp"
        image_path.write_bytes(b"fake")
        
        with patch.object(manager, '_generate_annotation_from_yolo', return_value=None):
            with patch.object(manager, '_generate_annotation_from_crop', return_value=None):
                with patch.object(manager, '_generate_annotation_fallback') as mock_fallback:
                    mock_fallback.return_value = [{'class_id': 0, 'bbox': [0.5, 0.5, 0.2, 0.2], 'mask': np.zeros((100, 100)), 'confidence': 0.5}]
                    
                    annotation = manager._generate_automatic_annotation(image_path)
                    
                    assert annotation is not None
    
    @patch('ml.segmentation.train_yolo.YOLO')
    @patch('ml.segmentation.train_yolo.get_yolo_artifacts_dir')
    @patch('ml.segmentation.train_yolo.ensure_dir_exists')
    def test_create_yolo_dataset(
        self, mock_ensure_dir, mock_get_dir, mock_yolo, temp_dir
    ):
        """Test creating YOLO dataset."""
        mock_get_dir.return_value = temp_dir
        
        manager = YOLOTrainingManager()
        manager.create_dataset_structure()
        
        annotations = {
            '1': [{'class_id': 0, 'bbox': [0.5, 0.5, 0.2, 0.2], 'mask': np.zeros((100, 100)), 'confidence': 0.8}],
            '2': [{'class_id': 0, 'bbox': [0.5, 0.5, 0.2, 0.2], 'mask': np.zeros((100, 100)), 'confidence': 0.8}],
        }
        
        with patch('ml.segmentation.train_yolo.get_raw_images_dir', return_value=temp_dir):
            with patch('ml.segmentation.train_yolo.cv2.imread') as mock_imread:
                mock_imread.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
                
                # Create fake image files
                for img_id in ['1', '2']:
                    img_path = temp_dir / f"{img_id}.bmp"
                    img_path.write_bytes(b"fake")
                
                splits = manager.create_yolo_dataset(annotations)
                
                assert 'train' in splits
                assert 'val' in splits
                assert 'test' in splits
    
    @patch('ml.segmentation.train_yolo.YOLO')
    @patch('ml.segmentation.train_yolo.get_yolo_artifacts_dir')
    @patch('ml.segmentation.train_yolo.ensure_dir_exists')
    def test_create_yolo_label_file(
        self, mock_ensure_dir, mock_get_dir, mock_yolo, temp_dir
    ):
        """Test creating YOLO label file."""
        mock_get_dir.return_value = temp_dir
        
        manager = YOLOTrainingManager()
        label_path = temp_dir / "label.txt"
        annotations = [
            {'class_id': 0, 'bbox': [0.5, 0.5, 0.2, 0.2]},
            {'class_id': 0, 'bbox': [0.6, 0.6, 0.3, 0.3]},
        ]
        
        manager._create_yolo_label_file(label_path, annotations)
        
        assert label_path.exists()
        content = label_path.read_text()
        assert '0' in content
    
    @patch('ml.segmentation.train_yolo.YOLO')
    @patch('ml.segmentation.train_yolo.get_yolo_artifacts_dir')
    @patch('ml.segmentation.train_yolo.ensure_dir_exists')
    def test_create_dataset_yaml(
        self, mock_ensure_dir, mock_get_dir, mock_yolo, temp_dir
    ):
        """Test creating dataset YAML."""
        mock_get_dir.return_value = temp_dir
        
        manager = YOLOTrainingManager()
        manager.create_dataset_structure()
        
        manager._create_dataset_yaml()
        
        yaml_path = manager.dataset_dir / "dataset.yaml"
        assert yaml_path.exists()
    
    @patch('ml.segmentation.train_yolo.YOLO')
    @patch('ml.segmentation.train_yolo.get_yolo_artifacts_dir')
    @patch('ml.segmentation.train_yolo.ensure_dir_exists')
    def test_train_model(
        self, mock_ensure_dir, mock_get_dir, mock_yolo, temp_dir
    ):
        """Test training model."""
        mock_get_dir.return_value = temp_dir
        
        manager = YOLOTrainingManager(epochs=1)
        manager.create_dataset_structure()
        manager._create_dataset_yaml()
        
        mock_model = Mock()
        mock_results = Mock()
        mock_results.save_dir = temp_dir / "runs"
        mock_results.save_dir.mkdir(parents=True, exist_ok=True)
        (mock_results.save_dir / "weights").mkdir(parents=True, exist_ok=True)
        (mock_results.save_dir / "weights" / "best.pt").write_bytes(b"fake")
        (mock_results.save_dir / "weights" / "last.pt").write_bytes(b"fake")
        mock_model.train.return_value = mock_results
        mock_yolo.return_value = mock_model
        
        results = manager.train_model(model_name="yolov8s-seg", pretrained=True)
        
        assert 'model_name' in results
        assert 'best_model_path' in results
    
    @patch('ml.segmentation.train_yolo.YOLO')
    @patch('ml.segmentation.train_yolo.get_yolo_artifacts_dir')
    @patch('ml.segmentation.train_yolo.ensure_dir_exists')
    def test_validate_model(
        self, mock_ensure_dir, mock_get_dir, mock_yolo, temp_dir
    ):
        """Test validating model."""
        mock_get_dir.return_value = temp_dir
        
        manager = YOLOTrainingManager()
        manager.create_dataset_structure()
        manager._create_dataset_yaml()
        
        model_path = temp_dir / "model.pt"
        model_path.write_bytes(b"fake")
        
        mock_model = Mock()
        mock_results = Mock()
        mock_results.box = Mock()
        mock_results.box.map50 = 0.8
        mock_results.box.map = 0.75
        mock_results.box.mp = 0.85
        mock_results.box.mr = 0.80
        mock_results.seg = Mock()
        mock_results.seg.map50 = 0.78
        mock_results.seg.map = 0.73
        mock_model.val.return_value = mock_results
        mock_yolo.return_value = mock_model
        
        metrics = manager.validate_model(model_path)
        
        assert 'mAP50' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics


class TestCreateYoloTrainer:
    """Tests for create_yolo_trainer function."""
    
    @patch('ml.segmentation.train_yolo.YOLOTrainingManager')
    def test_create_yolo_trainer(self, mock_manager_class):
        """Test creating YOLO trainer."""
        mock_instance = Mock()
        mock_manager_class.return_value = mock_instance
        
        result = create_yolo_trainer(dataset_size=150, epochs=100, batch_size=16)
        
        assert result is not None
        mock_manager_class.assert_called_once()


class TestTrainCacaoYoloModel:
    """Tests for train_cacao_yolo_model function."""
    
    @patch('ml.segmentation.train_yolo.create_yolo_trainer')
    def test_train_cacao_yolo_model(self, mock_create_trainer):
        """Test training cacao YOLO model."""
        mock_trainer = Mock()
        mock_trainer.run_full_training_pipeline.return_value = {'success': True}
        mock_create_trainer.return_value = mock_trainer
        
        result = train_cacao_yolo_model(
            dataset_size=150,
            epochs=100,
            batch_size=16,
            model_name="yolov8s-seg"
        )
        
        assert result['success'] is True
        mock_trainer.run_full_training_pipeline.assert_called_once()


