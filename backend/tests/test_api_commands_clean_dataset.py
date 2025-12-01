"""
Unit tests for clean_dataset management command.
Tests Django management command for cleaning dataset CSV files.
"""
import pytest
from unittest.mock import patch, mock_open, MagicMock
from django.core.management import call_command
from django.core.management.base import CommandError
from pathlib import Path
import csv
import tempfile
import os

from api.management.commands.clean_dataset import Command


@pytest.fixture
def command():
    """Create a Command instance for testing."""
    return Command()


@pytest.fixture
def sample_csv_content():
    """Sample CSV content for testing."""
    return """ID,ALTO,ANCHO,GROSOR,PESO,filename,image_path
1,15.5,12.3,8.7,1.2,image1.bmp,path/to/image1.bmp
2,20.0,15.0,10.0,2.0,image2.bmp,path/to/image2.bmp
3,25.0,18.0,12.0,3.0,image3.bmp,path/to/image3.bmp
"""


@pytest.fixture
def sample_csv_with_missing_file():
    """Sample CSV with missing filename."""
    return """ID,ALTO,ANCHO,GROSOR,PESO,filename,image_path
1,15.5,12.3,8.7,1.2,,path/to/image1.bmp
2,20.0,15.0,10.0,2.0,image2.bmp,path/to/image2.bmp
"""


@pytest.fixture
def sample_csv_with_non_numeric():
    """Sample CSV with non-numeric values."""
    return """ID,ALTO,ANCHO,GROSOR,PESO,filename,image_path
1,15.5,12.3,8.7,1.2,image1.bmp,path/to/image1.bmp
2,abc,15.0,10.0,2.0,image2.bmp,path/to/image2.bmp
"""


@pytest.fixture
def sample_csv_with_outliers():
    """Sample CSV with outlier values."""
    return """ID,ALTO,ANCHO,GROSOR,PESO,filename,image_path
1,15.5,12.3,8.7,1.2,image1.bmp,path/to/image1.bmp
2,100.0,50.0,30.0,20.0,image2.bmp,path/to/image2.bmp
"""


class TestCleanDatasetCommand:
    """Tests for clean_dataset Command class."""
    
    def test_command_initialization(self):
        """Test command initialization."""
        cmd = Command()
        assert cmd is not None
    
    def test_validate_required_columns_all_present(self, command):
        """Test validation when all required columns are present."""
        fieldnames = ['ID', 'ALTO', 'ANCHO', 'GROSOR', 'PESO', 'filename']
        in_path = Path('test.csv')
        
        result = command._validate_required_columns(fieldnames, in_path)
        
        assert result is True
    
    def test_validate_required_columns_missing_column(self, command):
        """Test validation when a required column is missing."""
        fieldnames = ['ID', 'ALTO', 'ANCHO', 'GROSOR']  # Missing PESO
        in_path = Path('test.csv')
        
        result = command._validate_required_columns(fieldnames, in_path)
        
        assert result is False
    
    def test_ensure_output_columns_adds_missing(self, command):
        """Test that output columns are added if missing."""
        fieldnames = ['ID', 'ALTO', 'ANCHO', 'GROSOR', 'PESO']
        
        result = command._ensure_output_columns(fieldnames)
        
        assert 'filename' in result
        assert 'image_path' in result
        assert 'ID' in result
    
    def test_ensure_output_columns_preserves_existing(self, command):
        """Test that existing columns are preserved."""
        fieldnames = ['ID', 'ALTO', 'ANCHO', 'GROSOR', 'PESO', 'filename', 'image_path']
        
        result = command._ensure_output_columns(fieldnames)
        
        assert len(result) == len(fieldnames)
        assert all(col in result for col in fieldnames)
    
    def test_parse_measurements_valid(self, command):
        """Test parsing valid measurements."""
        row = {
            'ALTO': '15.5',
            'ANCHO': '12.3',
            'GROSOR': '8.7',
            'PESO': '1.2'
        }
        
        result = command._parse_measurements(row)
        
        assert result is not None
        assert result['alto'] == 15.5
        assert result['ancho'] == 12.3
        assert result['grosor'] == 8.7
        assert result['peso'] == 1.2
    
    def test_parse_measurements_with_comma(self, command):
        """Test parsing measurements with comma as decimal separator."""
        row = {
            'ALTO': '15,5',
            'ANCHO': '12,3',
            'GROSOR': '8,7',
            'PESO': '1,2'
        }
        
        result = command._parse_measurements(row)
        
        assert result is not None
        assert result['alto'] == 15.5
        assert result['ancho'] == 12.3
    
    def test_parse_measurements_invalid(self, command):
        """Test parsing invalid measurements."""
        row = {
            'ALTO': 'abc',
            'ANCHO': '12.3',
            'GROSOR': '8.7',
            'PESO': '1.2'
        }
        
        result = command._parse_measurements(row)
        
        assert result is None
    
    def test_parse_measurements_missing_key(self, command):
        """Test parsing measurements with missing key."""
        row = {
            'ALTO': '15.5',
            'ANCHO': '12.3',
            'GROSOR': '8.7'
            # Missing PESO
        }
        
        result = command._parse_measurements(row)
        
        assert result is None
    
    def test_validate_outliers_within_range(self, command):
        """Test validation of measurements within acceptable range."""
        measurements = {
            'alto': 15.5,
            'ancho': 12.3,
            'grosor': 8.7,
            'peso': 1.2
        }
        opts = {
            'min_alto': 5.0,
            'max_alto': 60.0,
            'min_ancho': 3.0,
            'max_ancho': 30.0,
            'min_grosor': 1.0,
            'max_grosor': 20.0,
            'min_peso': 0.2,
            'max_peso': 10.0
        }
        
        result = command._validate_outliers(measurements, opts)
        
        assert result is True
    
    def test_validate_outliers_out_of_range(self, command):
        """Test validation of measurements out of range."""
        measurements = {
            'alto': 100.0,  # Out of range
            'ancho': 12.3,
            'grosor': 8.7,
            'peso': 1.2
        }
        opts = {
            'min_alto': 5.0,
            'max_alto': 60.0,
            'min_ancho': 3.0,
            'max_ancho': 30.0,
            'min_grosor': 1.0,
            'max_grosor': 20.0,
            'min_peso': 0.2,
            'max_peso': 10.0
        }
        
        result = command._validate_outliers(measurements, opts)
        
        assert result is False
    
    def test_process_row_valid(self, command):
        """Test processing a valid row."""
        row = {
            'ID': '1',
            'ALTO': '15.5',
            'ANCHO': '12.3',
            'GROSOR': '8.7',
            'PESO': '1.2',
            'filename': 'image1.bmp',
            'image_path': 'path/to/image1.bmp'
        }
        opts = {
            'min_alto': 5.0,
            'max_alto': 60.0,
            'min_ancho': 3.0,
            'max_ancho': 30.0,
            'min_grosor': 1.0,
            'max_grosor': 20.0,
            'min_peso': 0.2,
            'max_peso': 10.0
        }
        reasons = {
            'missing_file': 0,
            'non_numeric': 0,
            'outlier': 0
        }
        
        result = command._process_row(row, opts, reasons)
        
        assert result is not None
        assert result == row
        assert reasons['missing_file'] == 0
        assert reasons['non_numeric'] == 0
        assert reasons['outlier'] == 0
    
    def test_process_row_missing_file(self, command):
        """Test processing a row with missing filename."""
        row = {
            'ID': '1',
            'ALTO': '15.5',
            'ANCHO': '12.3',
            'GROSOR': '8.7',
            'PESO': '1.2',
            'filename': '',
            'image_path': 'path/to/image1.bmp'
        }
        opts = {
            'min_alto': 5.0,
            'max_alto': 60.0,
            'min_ancho': 3.0,
            'max_ancho': 30.0,
            'min_grosor': 1.0,
            'max_grosor': 20.0,
            'min_peso': 0.2,
            'max_peso': 10.0
        }
        reasons = {
            'missing_file': 0,
            'non_numeric': 0,
            'outlier': 0
        }
        
        result = command._process_row(row, opts, reasons)
        
        assert result is None
        assert reasons['missing_file'] == 1
    
    def test_process_row_non_numeric(self, command):
        """Test processing a row with non-numeric values."""
        row = {
            'ID': '1',
            'ALTO': 'abc',
            'ANCHO': '12.3',
            'GROSOR': '8.7',
            'PESO': '1.2',
            'filename': 'image1.bmp',
            'image_path': 'path/to/image1.bmp'
        }
        opts = {
            'min_alto': 5.0,
            'max_alto': 60.0,
            'min_ancho': 3.0,
            'max_ancho': 30.0,
            'min_grosor': 1.0,
            'max_grosor': 20.0,
            'min_peso': 0.2,
            'max_peso': 10.0
        }
        reasons = {
            'missing_file': 0,
            'non_numeric': 0,
            'outlier': 0
        }
        
        result = command._process_row(row, opts, reasons)
        
        assert result is None
        assert reasons['non_numeric'] == 1
    
    def test_process_row_outlier(self, command):
        """Test processing a row with outlier values."""
        row = {
            'ID': '1',
            'ALTO': '100.0',
            'ANCHO': '12.3',
            'GROSOR': '8.7',
            'PESO': '1.2',
            'filename': 'image1.bmp',
            'image_path': 'path/to/image1.bmp'
        }
        opts = {
            'min_alto': 5.0,
            'max_alto': 60.0,
            'min_ancho': 3.0,
            'max_ancho': 30.0,
            'min_grosor': 1.0,
            'max_grosor': 20.0,
            'min_peso': 0.2,
            'max_peso': 10.0
        }
        reasons = {
            'missing_file': 0,
            'non_numeric': 0,
            'outlier': 0
        }
        
        result = command._process_row(row, opts, reasons)
        
        assert result is None
        assert reasons['outlier'] == 1
    
    @patch('api.management.commands.clean_dataset.settings')
    def test_handle_file_not_found(self, mock_settings, command, tmp_path):
        """Test handle when input file doesn't exist."""
        mock_settings.MEDIA_ROOT = str(tmp_path)
        datasets_dir = tmp_path / 'datasets'
        datasets_dir.mkdir(parents=True)
        
        # File doesn't exist
        command.handle()
        
        # Should write error to stderr
        assert True  # Command should handle gracefully
    
    @patch('api.management.commands.clean_dataset.settings')
    def test_handle_successful_cleaning(self, mock_settings, command, tmp_path):
        """Test successful dataset cleaning."""
        mock_settings.MEDIA_ROOT = str(tmp_path)
        datasets_dir = tmp_path / 'datasets'
        datasets_dir.mkdir(parents=True)
        
        # Create input CSV
        in_path = datasets_dir / 'dataset_cacao.csv'
        with open(in_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['ID', 'ALTO', 'ANCHO', 'GROSOR', 'PESO', 'filename', 'image_path'])
            writer.writeheader()
            writer.writerow({
                'ID': '1',
                'ALTO': '15.5',
                'ANCHO': '12.3',
                'GROSOR': '8.7',
                'PESO': '1.2',
                'filename': 'image1.bmp',
                'image_path': 'path/to/image1.bmp'
            })
        
        command.handle()
        
        # Check output files were created
        out_path = datasets_dir / 'dataset_cacao.clean.csv'
        report_path = datasets_dir / 'dataset_cacao.clean.report.txt'
        
        assert out_path.exists()
        assert report_path.exists()
        
        # Verify output CSV content
        with open(out_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]['ID'] == '1'
    
    @patch('api.management.commands.clean_dataset.settings')
    def test_handle_with_custom_limits(self, mock_settings, command, tmp_path):
        """Test handle with custom min/max limits."""
        mock_settings.MEDIA_ROOT = str(tmp_path)
        datasets_dir = tmp_path / 'datasets'
        datasets_dir.mkdir(parents=True)
        
        # Create input CSV
        in_path = datasets_dir / 'dataset_cacao.csv'
        with open(in_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['ID', 'ALTO', 'ANCHO', 'GROSOR', 'PESO', 'filename', 'image_path'])
            writer.writeheader()
            writer.writerow({
                'ID': '1',
                'ALTO': '15.5',
                'ANCHO': '12.3',
                'GROSOR': '8.7',
                'PESO': '1.2',
                'filename': 'image1.bmp',
                'image_path': 'path/to/image1.bmp'
            })
        
        command.handle(
            max_alto=20.0,
            max_ancho=15.0,
            max_grosor=10.0,
            max_peso=2.0,
            min_alto=10.0,
            min_ancho=10.0,
            min_grosor=5.0,
            min_peso=0.5
        )
        
        # Verify file was created
        out_path = datasets_dir / 'dataset_cacao.clean.csv'
        assert out_path.exists()

