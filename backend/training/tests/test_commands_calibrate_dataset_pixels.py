"""
Tests for calibrate_dataset_pixels management command.
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from pathlib import Path
from io import StringIO
import tempfile
import json


class CalibrateDatasetPixelsCommandTest(TestCase):
    """Tests for calibrate_dataset_pixels command."""

    def setUp(self):
        """Set up test fixtures."""
        self.stdout = StringIO()
        self.stderr = StringIO()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_existing_records(self):
        """Test loading existing calibration records."""
        from training.management.commands.calibrate_dataset_pixels import Command
        command = Command()

        calibration_file = Path(self.temp_dir) / 'calibration.json'
        calibration_data = {
            'calibration_records': [
                {'id': 1, 'filename': 'test1.jpg'},
                {'id': 2, 'filename': 'test2.jpg'}
            ]
        }

        with open(calibration_file, 'w', encoding='utf-8') as f:
            json.dump(calibration_data, f)

        records = command._load_existing_records(calibration_file)
        self.assertEqual(len(records), 2)
        self.assertIn(1, records)
        self.assertIn(2, records)

    def test_load_existing_records_no_file(self):
        """Test loading records when file doesn't exist."""
        from training.management.commands.calibrate_dataset_pixels import Command
        command = Command()

        calibration_file = Path(self.temp_dir) / 'nonexistent.json'
        records = command._load_existing_records(calibration_file)
        self.assertEqual(len(records), 0)

    def test_calculate_scale_factors(self):
        """Test calculating scale factors."""
        from training.management.commands.calibrate_dataset_pixels import Command
        command = Command()

        pixel_measurements = {
            'height_pixels': 100,
            'width_pixels': 80
        }
        real_dimensions = {
            'alto': 10.0,
            'ancho': 8.0
        }

        scale_factors = command._calculate_scale_factors(pixel_measurements, real_dimensions)
        
        self.assertIn('alto_mm_per_pixel', scale_factors)
        self.assertIn('ancho_mm_per_pixel', scale_factors)
        self.assertIn('average_mm_per_pixel', scale_factors)
        self.assertEqual(scale_factors['alto_mm_per_pixel'], 0.1)
        self.assertEqual(scale_factors['ancho_mm_per_pixel'], 0.1)

    def test_calculate_basic_stats(self):
        """Test calculating basic statistics."""
        from training.management.commands.calibrate_dataset_pixels import Command
        command = Command()

        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        stats = command._calculate_basic_stats(values)

        self.assertIn('mean', stats)
        self.assertIn('std', stats)
        self.assertIn('min', stats)
        self.assertIn('max', stats)
        self.assertEqual(stats['mean'], 3.0)
        self.assertEqual(stats['min'], 1.0)
        self.assertEqual(stats['max'], 5.0)

    def test_calculate_basic_stats_empty(self):
        """Test calculating stats with empty list."""
        from training.management.commands.calibrate_dataset_pixels import Command
        command = Command()

        stats = command._calculate_basic_stats([])
        self.assertEqual(stats['mean'], 0)
        self.assertEqual(stats['std'], 0)
        self.assertEqual(stats['min'], 0)
        self.assertEqual(stats['max'], 0)

