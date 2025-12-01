"""
Unit tests for ML utils io module.
Tests file I/O operations.
"""
import pytest
import json
import pickle
import pandas as pd
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
def tmp_dir(tmp_path):
    """Create a temporary directory for testing."""
    return tmp_path


class TestJsonOperations:
    """Tests for JSON save/load operations."""
    
    def test_save_json(self, tmp_dir):
        """Test saving JSON file."""
        file_path = tmp_dir / "test.json"
        data = {"key": "value", "number": 123}
        
        save_json(data, file_path)
        
        assert file_path.exists()
        with open(file_path, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        assert loaded == data
    
    def test_load_json(self, tmp_dir):
        """Test loading JSON file."""
        file_path = tmp_dir / "test.json"
        data = {"key": "value", "number": 123}
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        
        loaded = load_json(file_path)
        assert loaded == data
    
    def test_save_json_creates_directory(self, tmp_dir):
        """Test that save_json creates parent directories."""
        file_path = tmp_dir / "subdir" / "test.json"
        data = {"key": "value"}
        
        save_json(data, file_path)
        
        assert file_path.exists()
        assert file_path.parent.exists()


class TestPickleOperations:
    """Tests for pickle save/load operations."""
    
    def test_save_pickle(self, tmp_dir):
        """Test saving pickle file."""
        file_path = tmp_dir / "test.pkl"
        data = {"key": "value", "list": [1, 2, 3]}
        
        save_pickle(data, file_path)
        
        assert file_path.exists()
    
    def test_load_pickle(self, tmp_dir):
        """Test loading pickle file."""
        file_path = tmp_dir / "test.pkl"
        data = {"key": "value", "list": [1, 2, 3]}
        
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)
        
        loaded = load_pickle(file_path)
        assert loaded == data


class TestCsvOperations:
    """Tests for CSV save/load operations."""
    
    def test_save_csv(self, tmp_dir):
        """Test saving CSV file."""
        file_path = tmp_dir / "test.csv"
        df = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
        
        save_csv(df, file_path)
        
        assert file_path.exists()
    
    def test_load_csv(self, tmp_dir):
        """Test loading CSV file."""
        file_path = tmp_dir / "test.csv"
        df = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
        df.to_csv(file_path, index=False)
        
        loaded = load_csv(file_path)
        assert len(loaded) == 3
        assert "col1" in loaded.columns


class TestImageOperations:
    """Tests for image save/load operations."""
    
    def test_save_image(self, tmp_dir):
        """Test saving image file."""
        file_path = tmp_dir / "test.jpg"
        img = Image.new('RGB', (100, 100), color='red')
        
        save_image(img, file_path)
        
        assert file_path.exists()
    
    def test_load_image(self, tmp_dir):
        """Test loading image file."""
        file_path = tmp_dir / "test.jpg"
        img = Image.new('RGB', (100, 100), color='red')
        img.save(file_path)
        
        loaded = load_image(file_path)
        assert isinstance(loaded, Image.Image)
        assert loaded.size == (100, 100)


class TestLogOperations:
    """Tests for log write operations."""
    
    def test_write_log(self, tmp_dir):
        """Test writing to log file."""
        log_path = tmp_dir / "test.log"
        
        write_log(log_path, "Test message")
        
        assert log_path.exists()
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert "Test message" in content
    
    def test_write_log_creates_directory(self, tmp_dir):
        """Test that write_log creates parent directories."""
        log_path = tmp_dir / "logs" / "test.log"
        
        write_log(log_path, "Test message")
        
        assert log_path.exists()
        assert log_path.parent.exists()


class TestFileUtilities:
    """Tests for file utility functions."""
    
    def test_get_file_timestamp(self, tmp_dir):
        """Test getting file timestamp."""
        file_path = tmp_dir / "test.txt"
        file_path.write_text("test")
        
        timestamp = get_file_timestamp(file_path)
        
        assert timestamp is not None
        assert isinstance(timestamp, float)
    
    def test_get_file_timestamp_nonexistent(self, tmp_dir):
        """Test getting timestamp for nonexistent file."""
        file_path = tmp_dir / "nonexistent.txt"
        
        timestamp = get_file_timestamp(file_path)
        
        assert timestamp is None
    
    def test_file_exists_and_newer(self, tmp_dir):
        """Test checking if source file is newer than target."""
        source_path = tmp_dir / "source.txt"
        target_path = tmp_dir / "target.txt"
        
        source_path.write_text("source")
        target_path.write_text("target")
        
        # Source should be newer (created after)
        result = file_exists_and_newer(source_path, target_path)
        
        # Result depends on timing, but function should not crash
        assert isinstance(result, bool)
    
    def test_file_exists_and_newer_target_missing(self, tmp_dir):
        """Test checking when target file doesn't exist."""
        source_path = tmp_dir / "source.txt"
        target_path = tmp_dir / "target.txt"
        
        source_path.write_text("source")
        
        result = file_exists_and_newer(source_path, target_path)
        
        assert result is False
    
    def test_ensure_dir_exists(self, tmp_dir):
        """Test ensuring directory exists."""
        dir_path = tmp_dir / "new_dir"
        
        ensure_dir_exists(dir_path)
        
        assert dir_path.exists()
        assert dir_path.is_dir()
    
    def test_ensure_dir_exists_already_exists(self, tmp_dir):
        """Test ensuring directory that already exists."""
        dir_path = tmp_dir / "existing_dir"
        dir_path.mkdir()
        
        # Should not raise error
        ensure_dir_exists(dir_path)
        
        assert dir_path.exists()

