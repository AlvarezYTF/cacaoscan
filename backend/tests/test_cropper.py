"""
Tests para el procesador de recortes.
"""
import pytest
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PIL import Image

from ml.segmentation.cropper import CacaoCropper, create_cacao_cropper


class TestCacaoCropper:
    """Tests para CacaoCropper."""
    
    def setup_method(self):
        """ConfiguraciÃ³n antes de cada test."""
        self.mock_yolo = Mock()
        self.cropper = CacaoCropper(
            yolo_inference=self.mock_yolo,
            crop_size=512,
            padding=10,
            save_masks=False,
            overwrite=False
        )
    
    def test_init(self):
        """Test de inicializaciÃ³n."""
        assert self.cropper.yolo_inference == self.mock_yolo
        assert self.cropper.crop_size == 512
        assert self.cropper.padding == 10
        assert self.cropper.save_masks == False
        assert self.cropper.overwrite == False
    
    def test_should_reprocess_newer_source(self):
        """Test de reprocesamiento con fuente mÃ¡s nueva."""
        with patch('ml.segmentation.cropper.get_file_timestamp') as mock_timestamp:
            mock_timestamp.side_effect = [2000.0, 1000.0]  # source newer than target
            
            result = self.cropper._should_reprocess(
                Path("source.bmp"),
                Path("target.png")
            )
            
            assert result == True
    
    def test_should_reprocess_older_source(self):
        """Test de reprocesamiento con fuente mÃ¡s antigua."""
        with patch('ml.segmentation.cropper.get_file_timestamp') as mock_timestamp:
            mock_timestamp.side_effect = [1000.0, 2000.0]  # source older than target
            
            result = self.cropper._should_reprocess(
                Path("source.bmp"),
                Path("target.png")
            )
            
            assert result == False
    
    def test_should_reprocess_missing_target(self):
        """Test de reprocesamiento con objetivo faltante."""
        with patch('ml.segmentation.cropper.get_file_timestamp') as mock_timestamp:
            mock_timestamp.side_effect = [1000.0, None]  # target doesn't exist
            
            result = self.cropper._should_reprocess(
                Path("source.bmp"),
                Path("target.png")
            )
            
            assert result == True
    
    @patch('ml.segmentation.cropper.cv2.imread')
    @patch('ml.segmentation.cropper.create_transparent_crop')
    @patch('ml.segmentation.cropper.resize_crop_to_square')
    @patch('ml.segmentation.cropper.save_image')
    def test_process_image_success(self, mock_save, mock_resize, mock_crop, mock_imread):
        """Test de procesamiento exitoso de imagen."""
        # Mock de predicciÃ³n exitosa
        prediction = {
            'confidence': 0.8,
            'class_id': 0,
            'class_name': 'cacao',
            'bbox': [100, 100, 200, 200],
            'mask': np.ones((100, 100), dtype=np.float32),
            'area': 5000,
            'center': (150, 150)
        }
        
        self.mock_yolo.get_best_prediction.return_value = prediction
        self.mock_yolo.validate_prediction_quality.return_value = True
        
        # Mock de imagen
        mock_image = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
        mock_imread.return_value = mock_image
        
        # Mock de transforms
        mock_transparent_crop = np.random.randint(0, 255, (150, 150, 4), dtype=np.uint8)
        mock_crop.return_value = mock_transparent_crop
        
        mock_square_crop = np.random.randint(0, 255, (512, 512, 4), dtype=np.uint8)
        mock_resize.return_value = mock_square_crop
        
        # Mock de archivos
        with patch.object(Path, 'exists', return_value=False):
            result = self.cropper.process_image(Path("test.bmp"), 1)
        
        assert result['success'] == True
        assert result['confidence'] == 0.8
        assert result['area'] == 5000
        mock_save.assert_called_once()
    
    def test_process_image_no_detections(self):
        """Test de procesamiento sin detecciones."""
        self.mock_yolo.get_best_prediction.return_value = None
        
        with patch.object(Path, 'exists', return_value=False):
            result = self.cropper.process_image(Path("test.bmp"), 1)
        
        assert result['success'] == False
        assert 'No se encontraron detecciones' in result['error']
    
    def test_process_image_low_quality(self):
        """Test de procesamiento con predicciÃ³n de baja calidad."""
        prediction = {
            'confidence': 0.3,  # Baja confianza
            'mask': np.ones((100, 100), dtype=np.float32),
            'area': 50,  # Ãrea muy pequeÃ±a
            'bbox': [100, 100, 200, 200]
        }
        
        self.mock_yolo.get_best_prediction.return_value = prediction
        self.mock_yolo.validate_prediction_quality.return_value = False
        
        with patch.object(Path, 'exists', return_value=False):
            result = self.cropper.process_image(Path("test.bmp"), 1)
        
        assert result['success'] == False
        assert 'PredicciÃ³n de baja calidad' in result['error']
    
    @patch('ml.segmentation.cropper.cv2.imread')
    def test_process_image_load_error(self, mock_imread):
        """Test de procesamiento con error de carga."""
        prediction = {
            'confidence': 0.8,
            'mask': np.ones((100, 100), dtype=np.float32),
            'area': 5000,
            'bbox': [100, 100, 200, 200]
        }
        
        self.mock_yolo.get_best_prediction.return_value = prediction
        self.mock_yolo.validate_prediction_quality.return_value = True
        
        mock_imread.return_value = None  # Error de carga
        
        with patch.object(Path, 'exists', return_value=False):
            result = self.cropper.process_image(Path("test.bmp"), 1)
        
        assert result['success'] == False
        assert 'No se pudo cargar la imagen' in result['error']
    
    def test_process_batch(self):
        """Test de procesamiento por lotes."""
        # Mock de registros
        records = [
            {'id': 1, 'raw_image_path': Path("1.bmp")},
            {'id': 2, 'raw_image_path': Path("2.bmp")},
            {'id': 3, 'raw_image_path': Path("3.bmp")}
        ]
        
        # Mock de resultados de procesamiento
        def mock_process_image(path, image_id):
            if image_id == 2:
                return {'success': False, 'error': 'Test error'}
            else:
                return {'success': True, 'skipped': False}
        
        self.cropper.process_image = mock_process_image
        
        stats = self.cropper.process_batch(records, limit=0)
        
        assert stats['total'] == 3
        assert stats['processed'] == 3
        assert stats['successful'] == 2
        assert stats['failed'] == 1
        assert len(stats['errors']) == 1
        assert stats['errors'][0]['id'] == 2
    
    def test_process_batch_with_limit(self):
        """Test de procesamiento por lotes con lÃ­mite."""
        records = [
            {'id': 1, 'raw_image_path': Path("1.bmp")},
            {'id': 2, 'raw_image_path': Path("2.bmp")},
            {'id': 3, 'raw_image_path': Path("3.bmp")}
        ]
        
        def mock_process_image(path, image_id):
            return {'success': True, 'skipped': False}
        
        self.cropper.process_image = mock_process_image
        
        stats = self.cropper.process_batch(records, limit=2)
        
        assert stats['total'] == 2  # Limitado a 2
        assert stats['processed'] == 2


class TestCreateCacaoCropper:
    """Tests para la funciÃ³n de conveniencia."""
    
    @patch('ml.segmentation.cropper.create_yolo_inference')
    def test_create_cacao_cropper(self, mock_create_yolo):
        """Test de creaciÃ³n de procesador de crops."""
        mock_yolo = Mock()
        mock_create_yolo.return_value = mock_yolo
        
        cropper = create_cacao_cropper(
            confidence_threshold=0.7,
            crop_size=256,
            padding=5,
            save_masks=True,
            overwrite=True
        )
        
        assert isinstance(cropper, CacaoCropper)
        assert cropper.crop_size == 256
        assert cropper.padding == 5
        assert cropper.save_masks == True
        assert cropper.overwrite == True
        mock_create_yolo.assert_called_once_with(confidence_threshold=0.7)


