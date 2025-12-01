"""
Unit tests for I/O utilities (io.py).
Tests file operations: JSON, pickle, CSV, images, and directory management.
"""
import pytest
import json
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from PIL import Image
from unittest.mock import patch, mock_open

from ml.utils.io import (
    save_json,
    load_json,
    save_pickle,
    load_pickle,
    save_csv,
    load_csv,
    save_image,
    load_image,
    write_log,
    get_file_timestamp,
    file_exists_and_newer,
    ensure_dir_exists
)


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return {
        'key1': 'value1',
        'key2': [1, 2, 3],
        'key3': {'nested': 'data'}
    }


@pytest.fixture
def sample_dataframe():
    """Create sample DataFrame for testing."""
    return pd.DataFrame({
        'col1': [1, 2, 3],
        'col2': ['a', 'b', 'c']
    })


@pytest.fixture
def sample_image():
    """Create sample PIL Image for testing."""
    return Image.new('RGB', (100, 100), color='red')


class TestJSONOperations:
    """Tests for JSON save/load operations."""
    
    def test_save_json_success(self, tmp_path, sample_data):
        """Test successful JSON save."""
        file_path = tmp_path / "test.json"
        
        save_json(sample_data, file_path)
        
        assert file_path.exists()
        assert file_path.stat().st_size > 0
    
    def test_save_json_creates_directory(self, tmp_path, sample_data):
        """Test that save_json creates parent directory."""
        file_path = tmp_path / "nested" / "dir" / "test.json"
        
        save_json(sample_data, file_path)
        
        assert file_path.exists()
        assert file_path.parent.exists()
    
    def test_load_json_success(self, tmp_path, sample_data):
        """Test successful JSON load."""
        file_path = tmp_path / "test.json"
        save_json(sample_data, file_path)
        
        loaded_data = load_json(file_path)
        
        assert loaded_data == sample_data
    
    def test_load_json_file_not_found(self, tmp_path):
        """Test loading non-existent JSON file."""
        file_path = tmp_path / "nonexistent.json"
        
        with pytest.raises(FileNotFoundError):
            load_json(file_path)
    
    def test_save_load_json_roundtrip(self, tmp_path, sample_data):
        """Test JSON save/load roundtrip."""
        file_path = tmp_path / "test.json"
        
        save_json(sample_data, file_path)
        loaded_data = load_json(file_path)
        
        assert loaded_data == sample_data
    
    def test_save_json_unicode(self, tmp_path):
        """Test saving JSON with unicode characters."""
        data = {'text': 'Café español 中文'}
        file_path = tmp_path / "unicode.json"
        
        save_json(data, file_path)
        loaded_data = load_json(file_path)
        
        assert loaded_data == data


class TestPickleOperations:
    """Tests for pickle save/load operations."""
    
    def test_save_pickle_success(self, tmp_path):
        """Test successful pickle save."""
        data = {'key': 'value', 'list': [1, 2, 3]}
        file_path = tmp_path / "test.pkl"
        
        save_pickle(data, file_path)
        
        assert file_path.exists()
        assert file_path.stat().st_size > 0
    
    def test_save_pickle_creates_directory(self, tmp_path):
        """Test that save_pickle creates parent directory."""
        data = {'key': 'value'}
        file_path = tmp_path / "nested" / "dir" / "test.pkl"
        
        save_pickle(data, file_path)
        
        assert file_path.exists()
        assert file_path.parent.exists()
    
    def test_load_pickle_success(self, tmp_path):
        """Test successful pickle load."""
        data = {'key': 'value', 'list': [1, 2, 3], 'numpy': np.array([1, 2, 3])}
        file_path = tmp_path / "test.pkl"
        save_pickle(data, file_path)
        
        loaded_data = load_pickle(file_path)
        
        assert loaded_data['key'] == data['key']
        assert loaded_data['list'] == data['list']
        np.testing.assert_array_equal(loaded_data['numpy'], data['numpy'])
    
    def test_load_pickle_file_not_found(self, tmp_path):
        """Test loading non-existent pickle file."""
        file_path = tmp_path / "nonexistent.pkl"
        
        with pytest.raises(FileNotFoundError):
            load_pickle(file_path)
    
    def test_save_load_pickle_complex_object(self, tmp_path):
        """Test saving/loading complex objects."""
        class CustomClass:
            def __init__(self, value):
                self.value = value
        
        obj = CustomClass(42)
        file_path = tmp_path / "complex.pkl"
        
        save_pickle(obj, file_path)
        loaded_obj = load_pickle(file_path)
        
        assert loaded_obj.value == obj.value


class TestCSVOperations:
    """Tests for CSV save/load operations."""
    
    def test_save_csv_success(self, tmp_path, sample_dataframe):
        """Test successful CSV save."""
        file_path = tmp_path / "test.csv"
        
        save_csv(sample_dataframe, file_path)
        
        assert file_path.exists()
        assert file_path.stat().st_size > 0
    
    def test_save_csv_with_index(self, tmp_path, sample_dataframe):
        """Test CSV save with index."""
        file_path = tmp_path / "test_index.csv"
        
        save_csv(sample_dataframe, file_path, index=True)
        
        assert file_path.exists()
        # Verify index is included
        loaded = pd.read_csv(file_path, index_col=0)
        assert len(loaded) == len(sample_dataframe)
    
    def test_save_csv_creates_directory(self, tmp_path, sample_dataframe):
        """Test that save_csv creates parent directory."""
        file_path = tmp_path / "nested" / "dir" / "test.csv"
        
        save_csv(sample_dataframe, file_path)
        
        assert file_path.exists()
        assert file_path.parent.exists()
    
    def test_load_csv_success(self, tmp_path, sample_dataframe):
        """Test successful CSV load."""
        file_path = tmp_path / "test.csv"
        save_csv(sample_dataframe, file_path)
        
        loaded_df = load_csv(file_path)
        
        pd.testing.assert_frame_equal(loaded_df, sample_dataframe)
    
    def test_load_csv_file_not_found(self, tmp_path):
        """Test loading non-existent CSV file."""
        file_path = tmp_path / "nonexistent.csv"
        
        with pytest.raises(FileNotFoundError):
            load_csv(file_path)


class TestImageOperations:
    """Tests for image save/load operations."""
    
    def test_save_image_success(self, tmp_path, sample_image):
        """Test successful image save."""
        file_path = tmp_path / "test.png"
        
        save_image(sample_image, file_path)
        
        assert file_path.exists()
        assert file_path.stat().st_size > 0
    
    def test_save_image_creates_directory(self, tmp_path, sample_image):
        """Test that save_image creates parent directory."""
        file_path = tmp_path / "nested" / "dir" / "test.png"
        
        save_image(sample_image, file_path)
        
        assert file_path.exists()
        assert file_path.parent.exists()
    
    def test_save_image_with_format(self, tmp_path, sample_image):
        """Test saving image with explicit format."""
        file_path = tmp_path / "test.jpg"
        
        save_image(sample_image, file_path, format='JPEG')
        
        assert file_path.exists()
        # Verify it's actually JPEG
        loaded = Image.open(file_path)
        assert loaded.format == 'JPEG'
    
    def test_load_image_success(self, tmp_path, sample_image):
        """Test successful image load."""
        file_path = tmp_path / "test.png"
        save_image(sample_image, file_path)
        
        loaded_image = load_image(file_path)
        
        assert loaded_image.size == sample_image.size
        assert loaded_image.mode == sample_image.mode
    
    def test_load_image_file_not_found(self, tmp_path):
        """Test loading non-existent image file."""
        file_path = tmp_path / "nonexistent.png"
        
        with pytest.raises(FileNotFoundError):
            load_image(file_path)
    
    def test_save_load_image_roundtrip(self, tmp_path, sample_image):
        """Test image save/load roundtrip."""
        file_path = tmp_path / "test.png"
        
        save_image(sample_image, file_path)
        loaded_image = load_image(file_path)
        
        assert loaded_image.size == sample_image.size
        assert loaded_image.mode == sample_image.mode


class TestLogOperations:
    """Tests for log write operations."""
    
    def test_write_log_success(self, tmp_path):
        """Test successful log write."""
        log_path = tmp_path / "test.log"
        message = "Test log message"
        
        write_log(log_path, message)
        
        assert log_path.exists()
        assert log_path.read_text().strip() == message
    
    def test_write_log_creates_directory(self, tmp_path):
        """Test that write_log creates parent directory."""
        log_path = tmp_path / "nested" / "dir" / "test.log"
        message = "Test message"
        
        write_log(log_path, message)
        
        assert log_path.exists()
        assert log_path.parent.exists()
    
    def test_write_log_append(self, tmp_path):
        """Test that write_log appends to existing file."""
        log_path = tmp_path / "test.log"
        message1 = "First message"
        message2 = "Second message"
        
        write_log(log_path, message1)
        write_log(log_path, message2)
        
        content = log_path.read_text()
        assert message1 in content
        assert message2 in content
        assert content.count('\n') == 2


class TestFileTimestampOperations:
    """Tests for file timestamp operations."""
    
    def test_get_file_timestamp_existing(self, tmp_path):
        """Test getting timestamp of existing file."""
        file_path = tmp_path / "test.txt"
        file_path.write_text("test")
        
        timestamp = get_file_timestamp(file_path)
        
        assert timestamp is not None
        assert isinstance(timestamp, float)
        assert timestamp > 0
    
    def test_get_file_timestamp_nonexistent(self, tmp_path):
        """Test getting timestamp of non-existent file."""
        file_path = tmp_path / "nonexistent.txt"
        
        timestamp = get_file_timestamp(file_path)
        
        assert timestamp is None
    
    def test_file_exists_and_newer_source_newer(self, tmp_path):
        """Test file_exists_and_newer when source is newer."""
        source_path = tmp_path / "source.txt"
        target_path = tmp_path / "target.txt"
        
        target_path.write_text("target")
        # Wait a bit and create source
        import time
        time.sleep(0.1)
        source_path.write_text("source")
        
        result = file_exists_and_newer(source_path, target_path)
        
        assert result is True
    
    def test_file_exists_and_newer_target_newer(self, tmp_path):
        """Test file_exists_and_newer when target is newer."""
        source_path = tmp_path / "source.txt"
        target_path = tmp_path / "target.txt"
        
        source_path.write_text("source")
        # Wait a bit and create target
        import time
        time.sleep(0.1)
        target_path.write_text("target")
        
        result = file_exists_and_newer(source_path, target_path)
        
        assert result is False
    
    def test_file_exists_and_newer_target_not_exists(self, tmp_path):
        """Test file_exists_and_newer when target doesn't exist."""
        source_path = tmp_path / "source.txt"
        target_path = tmp_path / "target.txt"
        
        source_path.write_text("source")
        
        result = file_exists_and_newer(source_path, target_path)
        
        assert result is False
    
    def test_file_exists_and_newer_source_not_exists(self, tmp_path):
        """Test file_exists_and_newer when source doesn't exist."""
        source_path = tmp_path / "source.txt"
        target_path = tmp_path / "target.txt"
        
        target_path.write_text("target")
        
        result = file_exists_and_newer(source_path, target_path)
        
        assert result is False


class TestDirectoryOperations:
    """Tests for directory operations."""
    
    def test_ensure_dir_exists_new_directory(self, tmp_path):
        """Test ensuring a new directory exists."""
        dir_path = tmp_path / "new_dir"
        
        ensure_dir_exists(dir_path)
        
        assert dir_path.exists()
        assert dir_path.is_dir()
    
    def test_ensure_dir_exists_existing_directory(self, tmp_path):
        """Test ensuring an existing directory exists."""
        dir_path = tmp_path / "existing_dir"
        dir_path.mkdir()
        
        # Should not raise error
        ensure_dir_exists(dir_path)
        
        assert dir_path.exists()
    
    def test_ensure_dir_exists_nested_directories(self, tmp_path):
        """Test ensuring nested directories exist."""
        dir_path = tmp_path / "level1" / "level2" / "level3"
        
        ensure_dir_exists(dir_path)
        
        assert dir_path.exists()
        assert dir_path.is_dir()
        assert dir_path.parent.exists()
        assert dir_path.parent.parent.exists()

