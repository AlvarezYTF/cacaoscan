"""
Tests for make_cacao_crops management command.
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from io import StringIO


class MakeCacaoCropsCommandTest(TestCase):
    """Tests for make_cacao_crops command."""

    def setUp(self):
        """Set up test fixtures."""
        self.stdout = StringIO()
        self.stderr = StringIO()

    @patch('api.management.commands.make_cacao_crops.CacaoDatasetLoader')
    @patch('api.management.commands.make_cacao_crops.create_cacao_cropper')
    def test_make_cacao_crops_validate_only(self, mock_cropper, mock_loader):
        """Test validate-only mode."""
        mock_dataset_loader = MagicMock()
        mock_dataset_loader.get_dataset_stats.return_value = {
            'total_records': 10,
            'valid_records': 8,
            'missing_images': 2,
            'missing_ids': [1, 2]
        }
        mock_loader.return_value = mock_dataset_loader

        call_command(
            'make_cacao_crops',
            '--validate-only',
            stdout=self.stdout
        )

        output = self.stdout.getvalue()
        self.assertIn('Validación completada', output)
        mock_cropper.assert_not_called()

    @patch('api.management.commands.make_cacao_crops.CacaoDatasetLoader')
    @patch('api.management.commands.make_cacao_crops.create_cacao_cropper')
    def test_make_cacao_crops_process_images(self, mock_cropper, mock_loader):
        """Test processing images."""
        mock_dataset_loader = MagicMock()
        mock_dataset_loader.get_dataset_stats.return_value = {
            'total_records': 10,
            'valid_records': 8,
            'missing_images': 0,
            'missing_ids': []
        }
        mock_dataset_loader.get_valid_records.return_value = [
            {'id': 1, 'raw_image_path': '/path/to/image1.jpg'},
            {'id': 2, 'raw_image_path': '/path/to/image2.jpg'}
        ]
        mock_loader.return_value = mock_dataset_loader

        mock_cropper_instance = MagicMock()
        mock_cropper_instance.process_batch.return_value = {
            'total': 2,
            'processed': 2,
            'successful': 2,
            'failed': 0,
            'skipped': 0
        }
        mock_cropper.return_value = mock_cropper_instance

        call_command(
            'make_cacao_crops',
            '--limit', '2',
            '--conf', '0.5',
            stdout=self.stdout
        )

        mock_cropper_instance.process_batch.assert_called_once()

    @patch('api.management.commands.make_cacao_crops.CacaoDatasetLoader')
    def test_make_cacao_crops_no_valid_records(self, mock_loader):
        """Test when no valid records are found."""
        mock_dataset_loader = MagicMock()
        mock_dataset_loader.get_dataset_stats.return_value = {
            'total_records': 0,
            'valid_records': 0,
            'missing_images': 0,
            'missing_ids': []
        }
        mock_dataset_loader.get_valid_records.return_value = []
        mock_loader.return_value = mock_dataset_loader

        with self.assertRaises(CommandError):
            call_command(
                'make_cacao_crops',
                stdout=self.stdout,
                stderr=self.stderr
            )

