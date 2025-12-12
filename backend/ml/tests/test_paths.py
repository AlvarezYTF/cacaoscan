"""
Tests for ML path utilities.
"""
import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from ml.utils.paths import (
    get_project_root,
    get_media_root,
    get_datasets_dir,
    get_cacao_images_dir,
    get_raw_images_dir,
    get_crops_dir,
    get_masks_dir,
    get_processed_images_dir,
    get_converted_jpg_dir,
    get_artifacts_dir,
    get_yolo_artifacts_dir,
    get_regressors_artifacts_dir,
    ensure_dir_exists,
    get_dataset_csv_path,
    get_missing_ids_log_path,
    get_raw_image_path,
    get_crop_image_path,
    get_mask_image_path
)


def test_get_project_root():
    """Test getting project root."""
    result = get_project_root()
    
    assert isinstance(result, Path)
    assert result.is_absolute()


def test_get_media_root():
    """Test getting media root."""
    result = get_media_root()
    
    assert isinstance(result, Path)


def test_get_media_root_with_env_var(monkeypatch):
    """Test getting media root with environment variable."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv('CACAO_MEDIA_ROOT', tmpdir)
        result = get_media_root()
        
        assert str(result) == str(Path(tmpdir).resolve())


def test_get_datasets_dir():
    """Test getting datasets directory."""
    result = get_datasets_dir()
    
    assert isinstance(result, Path)
    assert 'datasets' in str(result)


def test_get_cacao_images_dir():
    """Test getting cacao images directory."""
    result = get_cacao_images_dir()
    
    assert isinstance(result, Path)
    assert 'cacao_images' in str(result)


def test_get_raw_images_dir():
    """Test getting raw images directory."""
    result = get_raw_images_dir()
    
    assert isinstance(result, Path)
    assert 'raw' in str(result)


def test_get_crops_dir():
    """Test getting crops directory."""
    result = get_crops_dir()
    
    assert isinstance(result, Path)
    assert 'crops' in str(result)


def test_get_masks_dir():
    """Test getting masks directory."""
    result = get_masks_dir()
    
    assert isinstance(result, Path)
    assert 'masks' in str(result)


def test_get_processed_images_dir():
    """Test getting processed images directory."""
    result = get_processed_images_dir()
    
    assert isinstance(result, Path)
    assert 'processed' in str(result)


def test_get_converted_jpg_dir():
    """Test getting converted JPG directory."""
    result = get_converted_jpg_dir()
    
    assert isinstance(result, Path)
    assert 'converted_jpg' in str(result)


def test_get_artifacts_dir():
    """Test getting artifacts directory."""
    result = get_artifacts_dir()
    
    assert isinstance(result, Path)
    assert 'artifacts' in str(result)


def test_get_yolo_artifacts_dir():
    """Test getting YOLO artifacts directory."""
    result = get_yolo_artifacts_dir()
    
    assert isinstance(result, Path)
    assert 'yolov8-seg' in str(result)


def test_get_regressors_artifacts_dir():
    """Test getting regressors artifacts directory."""
    result = get_regressors_artifacts_dir()
    
    assert isinstance(result, Path)
    assert 'regressors' in str(result)


def test_ensure_dir_exists():
    """Test ensuring directory exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir) / "test_subdir"
        result = ensure_dir_exists(test_dir)
        
        assert result == test_dir
        assert test_dir.exists()
        assert test_dir.is_dir()


def test_ensure_dir_exists_already_exists():
    """Test ensuring directory exists when it already exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir) / "existing_dir"
        test_dir.mkdir()
        
        result = ensure_dir_exists(test_dir)
        
        assert result == test_dir
        assert test_dir.exists()


def test_get_dataset_csv_path():
    """Test getting dataset CSV path."""
    result = get_dataset_csv_path()
    
    assert isinstance(result, Path)
    assert result.name == "dataset.csv"


def test_get_dataset_csv_path_with_env_var(monkeypatch):
    """Test getting dataset CSV path with environment variable."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmpfile:
        tmpfile_path = tmpfile.name
        monkeypatch.setenv('CACAO_DATASET_CSV', tmpfile_path)
        result = get_dataset_csv_path()
        
        assert str(result) == str(Path(tmpfile_path).resolve())
        
        os.unlink(tmpfile_path)


def test_get_missing_ids_log_path():
    """Test getting missing IDs log path."""
    result = get_missing_ids_log_path()
    
    assert isinstance(result, Path)
    assert result.name == "missing_ids.log"


def test_get_raw_image_path():
    """Test getting raw image path."""
    result = get_raw_image_path(123)
    
    assert isinstance(result, Path)
    assert result.name == "123.bmp"
    assert 'raw' in str(result)


def test_get_crop_image_path():
    """Test getting crop image path."""
    result = get_crop_image_path(456)
    
    assert isinstance(result, Path)
    assert result.name == "456.png"
    assert 'crops' in str(result)


def test_get_mask_image_path():
    """Test getting mask image path."""
    result = get_mask_image_path(789)
    
    assert isinstance(result, Path)
    assert result.name == "789.png"
    assert 'masks' in str(result)


