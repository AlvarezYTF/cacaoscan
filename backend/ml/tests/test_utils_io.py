"""
Tests for utils io module.
"""
import json
import pickle
import tempfile
from unittest import TestCase
from pathlib import Path
from PIL import Image
import pandas as pd
import numpy as np

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


class IOUtilsTest(TestCase):
    """Tests for IO utility functions."""

    def test_save_and_load_json(self):
        """Test saving and loading JSON."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_path = Path(f.name)

        try:
            data = {'test': 'value', 'number': 123}
            save_json(data, temp_path)
            
            loaded_data = load_json(temp_path)
            self.assertEqual(loaded_data, data)
        finally:
            temp_path.unlink(missing_ok=True)

    def test_save_and_load_pickle(self):
        """Test saving and loading pickle."""
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pkl') as f:
            temp_path = Path(f.name)

        try:
            data = {'test': 'value', 'array': np.array([1, 2, 3])}
            save_pickle(data, temp_path)
            
            loaded_data = load_pickle(temp_path)
            self.assertEqual(loaded_data['test'], data['test'])
            np.testing.assert_array_equal(loaded_data['array'], data['array'])
        finally:
            temp_path.unlink(missing_ok=True)

    def test_save_and_load_csv(self):
        """Test saving and loading CSV."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            temp_path = Path(f.name)

        try:
            df = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})
            save_csv(df, temp_path)
            
            loaded_df = load_csv(temp_path)
            pd.testing.assert_frame_equal(loaded_df, df)
        finally:
            temp_path.unlink(missing_ok=True)

    def test_save_and_load_image(self):
        """Test saving and loading image."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.png') as f:
            temp_path = Path(f.name)
        
        # File handle is closed when exiting the 'with' block

        try:
            image = Image.new('RGB', (100, 100), color='red')
            save_image(image, temp_path)
            
            loaded_image = load_image(temp_path)
            self.assertEqual(loaded_image.size, image.size)
            # Close the loaded image to release file handle on Windows
            loaded_image.close()
        finally:
            # Retry deletion in case file is still locked on Windows
            import time
            max_retries = 3
            for _ in range(max_retries):
                try:
                    temp_path.unlink(missing_ok=True)
                    break
                except PermissionError:
                    time.sleep(0.1)

    def test_write_log(self):
        """Test writing to log file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            temp_path = Path(f.name)

        try:
            write_log(temp_path, 'Test log message')
            
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('Test log message', content)
        finally:
            temp_path.unlink(missing_ok=True)

    def test_get_file_timestamp(self):
        """Test getting file timestamp."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = Path(f.name)

        try:
            timestamp = get_file_timestamp(temp_path)
            self.assertIsNotNone(timestamp)
            self.assertIsInstance(timestamp, float)
        finally:
            temp_path.unlink(missing_ok=True)

    def test_file_exists_and_newer(self):
        """Test checking if file is newer."""
        with tempfile.NamedTemporaryFile(delete=False) as f1:
            temp_path1 = Path(f1.name)
        
        with tempfile.NamedTemporaryFile(delete=False) as f2:
            temp_path2 = Path(f2.name)

        try:
            result = file_exists_and_newer(temp_path1, temp_path2)
            self.assertIsInstance(result, bool)
        finally:
            temp_path1.unlink(missing_ok=True)
            temp_path2.unlink(missing_ok=True)

    def test_ensure_dir_exists(self):
        """Test ensuring directory exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = Path(temp_dir) / 'new_subdir'
            ensure_dir_exists(new_dir)
            self.assertTrue(new_dir.exists())
            self.assertTrue(new_dir.is_dir())

