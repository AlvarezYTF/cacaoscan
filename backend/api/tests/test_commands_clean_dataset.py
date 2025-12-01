"""
Tests for clean_dataset management command.
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.management import call_command
from django.conf import settings
from pathlib import Path
from io import StringIO
import csv
import tempfile
import os


class CleanDatasetCommandTest(TestCase):
    """Tests for clean_dataset command."""

    def setUp(self):
        """Set up test fixtures."""
        self.stdout = StringIO()
        self.stderr = StringIO()
        self.temp_dir = tempfile.mkdtemp()
        self.datasets_dir = Path(self.temp_dir) / 'datasets'
        self.datasets_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_test_csv(self, filename: str, rows: list) -> Path:
        """Create a test CSV file."""
        csv_path = self.datasets_dir / filename
        fieldnames = ['ID', 'ALTO', 'ANCHO', 'GROSOR', 'PESO', 'filename', 'image_path']
        
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        return csv_path

    @patch('api.management.commands.clean_dataset.settings')
    def test_clean_dataset_valid_rows(self, mock_settings):
        """Test cleaning dataset with valid rows."""
        mock_settings.MEDIA_ROOT = str(self.temp_dir)
        
        rows = [
            {
                'ID': '1', 'ALTO': '10.5', 'ANCHO': '8.0', 'GROSOR': '5.0', 'PESO': '2.5',
                'filename': 'test1.jpg', 'image_path': '/path/to/test1.jpg'
            },
            {
                'ID': '2', 'ALTO': '12.0', 'ANCHO': '9.0', 'GROSOR': '6.0', 'PESO': '3.0',
                'filename': 'test2.jpg', 'image_path': '/path/to/test2.jpg'
            }
        ]
        
        self._create_test_csv('dataset_cacao.csv', rows)

        call_command('clean_dataset', stdout=self.stdout, stderr=self.stderr)

        output_path = self.datasets_dir / 'dataset_cacao.clean.csv'
        self.assertTrue(output_path.exists())

    @patch('api.management.commands.clean_dataset.settings')
    def test_clean_dataset_missing_file(self, mock_settings):
        """Test cleaning dataset when input file doesn't exist."""
        mock_settings.MEDIA_ROOT = str(self.temp_dir)

        call_command('clean_dataset', stdout=self.stdout, stderr=self.stderr)

        error_output = self.stderr.getvalue()
        self.assertIn('not found', error_output)

    @patch('api.management.commands.clean_dataset.settings')
    def test_clean_dataset_outlier_filtering(self, mock_settings):
        """Test filtering outliers from dataset."""
        mock_settings.MEDIA_ROOT = str(self.temp_dir)
        
        rows = [
            {
                'ID': '1', 'ALTO': '100.0', 'ANCHO': '8.0', 'GROSOR': '5.0', 'PESO': '2.5',
                'filename': 'test1.jpg', 'image_path': '/path/to/test1.jpg'
            },
            {
                'ID': '2', 'ALTO': '12.0', 'ANCHO': '9.0', 'GROSOR': '6.0', 'PESO': '3.0',
                'filename': 'test2.jpg', 'image_path': '/path/to/test2.jpg'
            }
        ]
        
        self._create_test_csv('dataset_cacao.csv', rows)

        call_command('clean_dataset', '--max-alto', '60.0', stdout=self.stdout, stderr=self.stderr)

        output_path = self.datasets_dir / 'dataset_cacao.clean.csv'
        if output_path.exists():
            with open(output_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                kept_rows = list(reader)
                self.assertEqual(len(kept_rows), 1)

    def test_validate_required_columns(self):
        """Test validation of required columns."""
        from api.management.commands.clean_dataset import Command
        command = Command()

        valid_fieldnames = ['ID', 'ALTO', 'ANCHO', 'GROSOR', 'PESO']
        self.assertTrue(command._validate_required_columns(valid_fieldnames, Path('test.csv')))

        invalid_fieldnames = ['ID', 'ALTO', 'ANCHO']
        self.assertFalse(command._validate_required_columns(invalid_fieldnames, Path('test.csv')))

    def test_parse_measurements(self):
        """Test parsing measurements from row."""
        from api.management.commands.clean_dataset import Command
        command = Command()

        row = {'ALTO': '10.5', 'ANCHO': '8.0', 'GROSOR': '5.0', 'PESO': '2.5'}
        measurements = command._parse_measurements(row)
        
        self.assertIsNotNone(measurements)
        self.assertEqual(measurements['alto'], 10.5)
        self.assertEqual(measurements['ancho'], 8.0)

    def test_validate_outliers(self):
        """Test outlier validation."""
        from api.management.commands.clean_dataset import Command
        command = Command()

        opts = {
            'min_alto': 5.0, 'max_alto': 60.0,
            'min_ancho': 3.0, 'max_ancho': 30.0,
            'min_grosor': 1.0, 'max_grosor': 20.0,
            'min_peso': 0.2, 'max_peso': 10.0
        }

        valid_measurements = {'alto': 10.0, 'ancho': 8.0, 'grosor': 5.0, 'peso': 2.5}
        self.assertTrue(command._validate_outliers(valid_measurements, opts))

        invalid_measurements = {'alto': 100.0, 'ancho': 8.0, 'grosor': 5.0, 'peso': 2.5}
        self.assertFalse(command._validate_outliers(invalid_measurements, opts))

