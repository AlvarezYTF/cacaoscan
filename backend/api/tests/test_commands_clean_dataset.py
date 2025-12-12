"""
Tests for clean_dataset management command.
"""
import pytest
import csv
import tempfile
from pathlib import Path
from io import StringIO
from unittest.mock import patch, Mock
from django.test import override_settings
from django.core.management import call_command

from api.management.commands.clean_dataset import Command


@pytest.mark.django_db
class TestCleanDatasetCommand:
    """Tests for clean_dataset command."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def sample_csv(self, temp_dir):
        """Create sample CSV file."""
        csv_path = temp_dir / "dataset_cacao.csv"
        
        with csv_path.open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['ID', 'ALTO', 'ANCHO', 'GROSOR', 'PESO', 'filename', 'image_path'])
            writer.writeheader()
            writer.writerow({
                'ID': '1',
                'ALTO': '10.0',
                'ANCHO': '20.0',
                'GROSOR': '5.0',
                'PESO': '100.0',
                'filename': 'test.jpg',
                'image_path': '/path/to/test.jpg'
            })
            writer.writerow({
                'ID': '2',
                'ALTO': '60.0',  # Outlier
                'ANCHO': '30.0',
                'GROSOR': '20.0',
                'PESO': '100.0',
                'filename': 'test2.jpg',
                'image_path': '/path/to/test2.jpg'
            })
            writer.writerow({
                'ID': '3',
                'ALTO': '',  # Missing
                'ANCHO': '20.0',
                'GROSOR': '5.0',
                'PESO': '100.0',
                'filename': 'test3.jpg',
                'image_path': '/path/to/test3.jpg'
            })
        
        return csv_path
    
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_handle_file_not_found(self, temp_dir):
        """Test handling when input file doesn't exist."""
        command = Command()
        command.stderr = StringIO()
        
        with patch('api.management.commands.clean_dataset.settings') as mock_settings:
            mock_settings.MEDIA_ROOT = str(temp_dir)
            
            command.handle()
            
            output = command.stderr.getvalue()
            # The command writes error message to stderr when file is not found
            assert len(output) > 0 and ('not found' in output.lower() or 'dataset_cacao.csv' in output.lower())
    
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_validate_required_columns_missing(self, temp_dir):
        """Test validation with missing required columns."""
        csv_path = temp_dir / "dataset_cacao.csv"
        csv_path.write_text("id,alto\n1,10.0\n", encoding='utf-8')
        
        with patch('api.management.commands.clean_dataset.settings') as mock_settings:
            mock_settings.MEDIA_ROOT = str(temp_dir)
            
            command = Command()
            command.stderr = StringIO()
            
            command.handle()
            
            output = command.stderr.getvalue()
            assert len(output) > 0
    
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_process_row_valid(self):
        """Test processing valid row."""
        command = Command()
        reasons = {'missing_file': 0, 'non_numeric': 0, 'outlier': 0}
        
        row = {
            'ID': '1',
            'ALTO': '10.0',
            'ANCHO': '20.0',
            'GROSOR': '5.0',
            'PESO': '5.0',  # Changed to be within valid range
            'filename': 'test.jpg',
            'image_path': '/path/to/test.jpg'
        }
        
        opts = {
            'max_alto': 60.0,
            'max_ancho': 30.0,
            'max_grosor': 20.0,
            'max_peso': 200.0,  # Increased to allow peso 100.0
            'min_alto': 5.0,
            'min_ancho': 3.0,
            'min_grosor': 1.0,
            'min_peso': 0.2
        }
        
        result = command._process_row(row, opts, reasons)
        
        assert result is not None
        assert result == row
        assert reasons['missing_file'] == 0
        assert reasons['non_numeric'] == 0
        assert reasons['outlier'] == 0
    
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_process_row_missing_file(self):
        """Test processing row with missing filename."""
        command = Command()
        reasons = {'missing_file': 0, 'non_numeric': 0, 'outlier': 0}
        
        row = {
            'ID': '1',
            'ALTO': '10.0',
            'ANCHO': '20.0',
            'GROSOR': '5.0',
            'PESO': '100.0',
            'filename': '',
            'image_path': ''
        }
        
        opts = {}
        
        result = command._process_row(row, opts, reasons)
        
        assert result is None
        assert reasons['missing_file'] == 1
    
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_parse_measurements_valid(self):
        """Test parsing valid measurements."""
        command = Command()
        
        row = {
            'ALTO': '10.0',
            'ANCHO': '20.0',
            'GROSOR': '5.0',
            'PESO': '100.0'
        }
        
        measurements = command._parse_measurements(row)
        
        assert measurements is not None
        assert measurements['alto'] == 10.0
        assert measurements['ancho'] == 20.0
        assert measurements['grosor'] == 5.0
        assert measurements['peso'] == 100.0
    
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_parse_measurements_comma_decimal(self):
        """Test parsing measurements with comma as decimal separator."""
        command = Command()
        
        row = {
            'ALTO': '10,5',
            'ANCHO': '20,3',
            'GROSOR': '5,2',
            'PESO': '100,5'
        }
        
        measurements = command._parse_measurements(row)
        
        assert measurements is not None
        assert measurements['alto'] == 10.5
    
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_parse_measurements_invalid(self):
        """Test parsing invalid measurements."""
        command = Command()
        
        row = {
            'ALTO': 'invalid',
            'ANCHO': '20.0',
            'GROSOR': '5.0',
            'PESO': '100.0'
        }
        
        measurements = command._parse_measurements(row)
        
        assert measurements is None
    
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_validate_outliers_valid(self):
        """Test validating outliers with valid values."""
        command = Command()
        
        measurements = {
            'alto': 10.0,
            'ancho': 20.0,
            'grosor': 5.0,
            'peso': 8.0
        }
        
        opts = {
            'max_alto': 60.0,
            'max_ancho': 30.0,
            'max_grosor': 20.0,
            'max_peso': 10.0,
            'min_alto': 5.0,
            'min_ancho': 3.0,
            'min_grosor': 1.0,
            'min_peso': 0.2
        }
        
        result = command._validate_outliers(measurements, opts)
        
        assert result is True
    
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_validate_outliers_invalid(self):
        """Test validating outliers with invalid values."""
        command = Command()
        
        measurements = {
            'alto': 100.0,  # Too high
            'ancho': 20.0,
            'grosor': 5.0,
            'peso': 8.0
        }
        
        opts = {
            'max_alto': 60.0,
            'max_ancho': 30.0,
            'max_grosor': 20.0,
            'max_peso': 10.0,
            'min_alto': 5.0,
            'min_ancho': 3.0,
            'min_grosor': 1.0,
            'min_peso': 0.2
        }
        
        result = command._validate_outliers(measurements, opts)
        
        assert result is False
    
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_ensure_output_columns(self):
        """Test ensuring output columns exist."""
        command = Command()
        
        fieldnames = ['ID', 'ALTO', 'ANCHO']
        new_fieldnames = command._ensure_output_columns(fieldnames)
        
        assert 'filename' in new_fieldnames
        assert 'image_path' in new_fieldnames
    
    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_ensure_output_columns_already_exists(self):
        """Test ensuring output columns when they already exist."""
        command = Command()
        
        fieldnames = ['ID', 'ALTO', 'filename', 'image_path']
        new_fieldnames = command._ensure_output_columns(fieldnames)
        
        assert new_fieldnames == fieldnames


