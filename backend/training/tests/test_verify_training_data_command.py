"""
Tests for verify_training_data management command.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
from pathlib import Path
from django.core.management import call_command
from django.core.management.base import CommandError
from ml.data.dataset_loader import CacaoDatasetLoader


@pytest.mark.django_db
class TestVerifyTrainingDataCommand:
    """Tests for verify_training_data command."""
    
    @patch('training.management.commands.verify_training_data.get_raw_images_dir')
    @patch('training.management.commands.verify_training_data.get_datasets_dir')
    def test_handle_command_success(self, mock_datasets_dir, mock_raw_dir, tmp_path):
        """Test handling command successfully."""
        # Setup mocks
        raw_dir = tmp_path / 'raw'
        raw_dir.mkdir()
        (raw_dir / 'test1.bmp').write_bytes(b'fake bmp content')
        (raw_dir / 'test2.bmp').write_bytes(b'fake bmp content')
        
        datasets_dir = tmp_path / 'datasets'
        datasets_dir.mkdir()
        csv_file = datasets_dir / 'test.csv'
        csv_file.write_text('id,alto,ancho,grosor,peso\n1,10,20,30,40\n2,11,21,31,41\n')
        
        mock_raw_dir.return_value = raw_dir
        mock_datasets_dir.return_value = datasets_dir
        
        # Mock CacaoDatasetLoader
        with patch('training.management.commands.verify_training_data.CacaoDatasetLoader') as mock_loader_class:
            mock_loader = MagicMock()
            mock_loader.csv_path = csv_file
            
            # Mock load_dataset
            import pandas as pd
            df = pd.DataFrame({
                'id': [1, 2],
                'alto': [10, 11],
                'ancho': [20, 21],
                'grosor': [30, 31],
                'peso': [40, 41]
            })
            mock_loader.load_dataset.return_value = df
            
            # Mock validate_images_exist
            valid_df = df.copy()
            valid_df['image_path'] = [str(raw_dir / 'test1.bmp'), str(raw_dir / 'test2.bmp')]
            mock_loader.validate_images_exist.return_value = (valid_df, [])
            
            # Mock get_valid_records
            mock_loader.get_valid_records.return_value = [
                {
                    'id': 1,
                    'alto': 10,
                    'ancho': 20,
                    'grosor': 30,
                    'peso': 40,
                    'raw_image_path': str(raw_dir / 'test1.bmp'),
                    'crop_image_path': str(raw_dir / 'crops' / 'test1.png')
                },
                {
                    'id': 2,
                    'alto': 11,
                    'ancho': 21,
                    'grosor': 31,
                    'peso': 41,
                    'raw_image_path': str(raw_dir / 'test2.bmp'),
                    'crop_image_path': str(raw_dir / 'crops' / 'test2.png')
                }
            ]
            
            mock_loader_class.return_value = mock_loader
            
            out = StringIO()
            
            call_command('verify_training_data', stdout=out)
            
            output = out.getvalue()
            assert 'VERIFICACIÓN DE DATOS' in output
            assert 'VERIFICACIÓN COMPLETADA' in output
    
    @patch('training.management.commands.verify_training_data.get_raw_images_dir')
    @patch('training.management.commands.verify_training_data.get_datasets_dir')
    def test_handle_command_with_errors(self, mock_datasets_dir, mock_raw_dir, tmp_path):
        """Test handling command with errors."""
        # Setup mocks
        raw_dir = tmp_path / 'raw'
        raw_dir.mkdir()
        
        datasets_dir = tmp_path / 'datasets'
        datasets_dir.mkdir()
        
        mock_raw_dir.return_value = raw_dir
        mock_datasets_dir.return_value = datasets_dir
        
        # Mock CacaoDatasetLoader to raise error
        with patch('training.management.commands.verify_training_data.CacaoDatasetLoader') as mock_loader_class:
            mock_loader_class.side_effect = Exception('Test error')
            
            out = StringIO()
            
            with pytest.raises(CommandError):
                call_command('verify_training_data', stdout=out)
    
    @patch('training.management.commands.verify_training_data.CacaoDatasetLoader')
    @patch('training.management.commands.verify_training_data.get_raw_images_dir')
    @patch('training.management.commands.verify_training_data.get_datasets_dir')
    def test_handle_command_no_raw_dir(self, mock_datasets_dir, mock_raw_dir, mock_loader_class, tmp_path):
        """Test handling command with no raw directory."""
        # Setup mocks
        raw_dir = tmp_path / 'nonexistent'
        datasets_dir = tmp_path / 'datasets'
        datasets_dir.mkdir()
        csv_file = datasets_dir / 'dataset_cacao.csv'
        csv_file.write_text('id,alto,ancho,grosor,peso\n1,10,20,30,40\n')
        
        mock_raw_dir.return_value = raw_dir
        mock_datasets_dir.return_value = datasets_dir
        
        # Mock CacaoDatasetLoader to avoid FileNotFoundError
        mock_loader = MagicMock()
        mock_loader.csv_path = csv_file
        import pandas as pd
        mock_df = pd.DataFrame({
            'id': [1], 
            'alto': [10], 
            'ancho': [20], 
            'grosor': [30], 
            'peso': [40],
            'image_path': [str(raw_dir / 'test1.bmp')]
        })
        mock_loader.load_dataset.return_value = mock_df
        # validate_images_exist returns (valid_df, missing_ids) tuple
        mock_loader.validate_images_exist.return_value = (mock_df, [])
        mock_loader.get_valid_records.return_value = []
        mock_loader_class.return_value = mock_loader
        
        out = StringIO()
        
        call_command('verify_training_data', stdout=out)
        
        output = out.getvalue()
        assert 'Existe: False' in output
    
    @patch('training.management.commands.verify_training_data.get_raw_images_dir')
    @patch('training.management.commands.verify_training_data.get_datasets_dir')
    def test_handle_command_no_csv(self, mock_datasets_dir, mock_raw_dir, tmp_path):
        """Test handling command with no CSV files."""
        # Setup mocks
        raw_dir = tmp_path / 'raw'
        raw_dir.mkdir()
        
        datasets_dir = tmp_path / 'datasets'
        datasets_dir.mkdir()
        
        mock_raw_dir.return_value = raw_dir
        mock_datasets_dir.return_value = datasets_dir
        
        # Mock CacaoDatasetLoader
        with patch('training.management.commands.verify_training_data.CacaoDatasetLoader') as mock_loader_class:
            mock_loader = MagicMock()
            mock_loader.csv_path = None
            mock_loader.load_dataset.side_effect = Exception('No CSV found')
            mock_loader_class.return_value = mock_loader
            
            out = StringIO()
            
            with pytest.raises(CommandError):
                call_command('verify_training_data', stdout=out)


