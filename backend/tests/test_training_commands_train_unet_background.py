"""
Unit tests for train_unet_background command module (train_unet_background.py).
Tests Django management command for training U-Net background removal model.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.core.management.base import CommandError
from pathlib import Path

from training.management.commands.train_unet_background import Command, _generate_single_mask


@pytest.fixture
def command():
    """Create a Command instance for testing."""
    return Command()


@pytest.fixture
def mock_options():
    """Create mock command options."""
    return {
        'epochs': 20,
        'batch_size': 4,
        'max_images': None,
        'learning_rate': 1e-4,
        'force': False
    }


class TestTrainUnetBackgroundCommand:
    """Tests for train_unet_background Command class."""
    
    def test_command_initialization(self):
        """Test command initialization."""
        cmd = Command()
        assert cmd is not None
    
    @patch('training.management.commands.train_unet_background.get_project_root')
    def test_check_existing_model_exists(self, mock_get_root, command, tmp_path):
        """Test checking when model already exists."""
        project_root = tmp_path
        mock_get_root.return_value = project_root
        
        segmentation_dir = project_root / "ml" / "segmentation"
        segmentation_dir.mkdir(parents=True)
        model_path = segmentation_dir / "cacao_unet.pth"
        model_path.write_bytes(b"model data")
        
        result = command._check_existing_model({'force': False})
        
        assert result == model_path
    
    @patch('training.management.commands.train_unet_background.get_project_root')
    def test_check_existing_model_not_exists(self, mock_get_root, command, tmp_path):
        """Test checking when model doesn't exist."""
        project_root = tmp_path
        mock_get_root.return_value = project_root
        
        result = command._check_existing_model({'force': False})
        
        assert result is None
    
    @patch('training.management.commands.train_unet_background.get_project_root')
    def test_check_existing_model_force(self, mock_get_root, command, tmp_path):
        """Test checking when force flag is set."""
        project_root = tmp_path
        mock_get_root.return_value = project_root
        
        segmentation_dir = project_root / "ml" / "segmentation"
        segmentation_dir.mkdir(parents=True)
        model_path = segmentation_dir / "cacao_unet.pth"
        model_path.write_bytes(b"model data")
        
        result = command._check_existing_model({'force': True})
        
        assert result is None
    
    @patch('training.management.commands.train_unet_background.get_raw_images_dir')
    def test_get_image_files_success(self, mock_get_raw_dir, command, tmp_path):
        """Test getting image files successfully."""
        raw_dir = tmp_path / "raw_images"
        raw_dir.mkdir()
        (raw_dir / "image1.bmp").touch()
        (raw_dir / "image2.jpg").touch()
        (raw_dir / "image3.png").touch()
        
        mock_get_raw_dir.return_value = raw_dir
        
        image_files = command._get_image_files()
        
        assert len(image_files) == 3
    
    @patch('training.management.commands.train_unet_background.get_raw_images_dir')
    def test_get_image_files_not_found(self, mock_get_raw_dir, command):
        """Test getting image files when directory doesn't exist."""
        mock_get_raw_dir.return_value = Path("/nonexistent")
        
        with pytest.raises(CommandError, match="Directorio de imágenes raw no encontrado"):
            command._get_image_files()
    
    @patch('training.management.commands.train_unet_background.get_raw_images_dir')
    def test_get_image_files_no_images(self, mock_get_raw_dir, command, tmp_path):
        """Test getting image files when no images found."""
        raw_dir = tmp_path / "raw_images"
        raw_dir.mkdir()
        
        mock_get_raw_dir.return_value = raw_dir
        
        with pytest.raises(CommandError, match="No se encontraron imágenes"):
            command._get_image_files()
    
    @patch('training.management.commands.train_unet_background.get_raw_images_dir')
    def test_get_image_files_max_images(self, mock_get_raw_dir, command, tmp_path):
        """Test getting image files with max_images limit."""
        raw_dir = tmp_path / "raw_images"
        raw_dir.mkdir()
        for i in range(10):
            (raw_dir / f"image{i}.bmp").touch()
        
        mock_get_raw_dir.return_value = raw_dir
        
        image_files = command._get_image_files(max_images=5)
        
        assert len(image_files) == 5
    
    @patch('cv2.imread')
    @patch('cv2.resize')
    @patch('cv2.grabCut')
    @patch('cv2.imwrite')
    def test_generate_single_mask_success(self, mock_imwrite, mock_grabcut, mock_resize,
                                          mock_imread, tmp_path):
        """Test successful mask generation."""
        jpg_path = tmp_path / "test.jpg"
        mask_path = tmp_path / "mask.png"
        
        # Mock OpenCV functions
        mock_img = Mock(shape=(512, 512, 3))
        mock_imread.return_value = mock_img
        mock_resize.return_value = mock_img
        mock_grabcut.return_value = None
        mock_imwrite.return_value = True
        
        success, error = _generate_single_mask((jpg_path, mask_path))
        
        assert success is True
        assert error is None
    
    @patch('cv2.imread')
    def test_generate_single_mask_image_read_error(self, mock_imread, tmp_path):
        """Test mask generation when image read fails."""
        jpg_path = tmp_path / "test.jpg"
        mask_path = tmp_path / "mask.png"
        
        mock_imread.return_value = None
        
        success, error = _generate_single_mask((jpg_path, mask_path))
        
        assert success is False
        assert "Error leyendo imagen" in error
    
    @patch('cv2.imread')
    def test_generate_single_mask_too_small(self, mock_imread, tmp_path):
        """Test mask generation when image is too small."""
        jpg_path = tmp_path / "test.jpg"
        mask_path = tmp_path / "mask.png"
        
        mock_img = Mock(shape=(30, 30, 3))
        mock_imread.return_value = mock_img
        
        success, error = _generate_single_mask((jpg_path, mask_path))
        
        assert success is False
        assert "muy pequeña" in error

