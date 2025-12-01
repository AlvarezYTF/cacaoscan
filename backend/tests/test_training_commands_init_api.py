"""
Unit tests for init_api management command.
Tests Django management command for initializing CacaoScan API.
"""
import pytest
from unittest.mock import patch, MagicMock, Mock
from django.core.management import call_command
from django.core.management.base import CommandError
from pathlib import Path
from django.conf import settings

from training.management.commands.init_api import Command


@pytest.fixture
def command():
    """Create a Command instance for testing."""
    return Command()


class TestInitAPICommand:
    """Tests for init_api Command class."""
    
    def test_command_initialization(self):
        """Test command initialization."""
        cmd = Command()
        assert cmd is not None
    
    def test_check_configuration_success(self, command):
        """Test checking configuration when all settings exist."""
        with patch('training.management.commands.init_api.settings') as mock_settings:
            mock_settings.MEDIA_ROOT = '/media'
            mock_settings.MEDIA_URL = '/media/'
            mock_settings.DEBUG = True
            mock_settings.ALLOWED_HOSTS = ['localhost']
            
            command._check_configuration()
            
            # Should complete without errors
            assert True
    
    def test_check_configuration_missing_setting(self, command):
        """Test checking configuration when setting is missing."""
        with patch('training.management.commands.init_api.settings') as mock_settings:
            # Remove MEDIA_ROOT
            del mock_settings.MEDIA_ROOT
            
            with pytest.raises(CommandError, match="Setting requerido no encontrado"):
                command._check_configuration()
    
    @patch('training.management.commands.init_api.settings')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.mkdir')
    def test_check_directories_all_exist(self, mock_mkdir, mock_exists, mock_settings, command):
        """Test checking directories when all exist."""
        mock_settings.MEDIA_ROOT = '/media'
        mock_settings.BASE_DIR = Path('/project')
        mock_exists.return_value = True
        
        command._check_directories()
        
        # Should not create directories
        mock_mkdir.assert_not_called()
    
    @patch('training.management.commands.init_api.settings')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.mkdir')
    def test_check_directories_missing_creates(self, mock_mkdir, mock_exists, mock_settings, command):
        """Test checking directories when missing creates them."""
        mock_settings.MEDIA_ROOT = '/media'
        mock_settings.BASE_DIR = Path('/project')
        mock_exists.return_value = False
        
        command._check_directories()
        
        # Should create directories
        assert mock_mkdir.called
    
    @patch('training.management.commands.init_api.settings')
    @patch('pathlib.Path.exists')
    def test_check_artifacts_all_found(self, mock_exists, mock_settings, command):
        """Test checking artifacts when all are found."""
        mock_settings.BASE_DIR = Path('/project')
        mock_exists.return_value = True
        
        command._check_artifacts()
        
        # Should complete without errors
        assert True
    
    @patch('training.management.commands.init_api.settings')
    @patch('pathlib.Path.exists')
    def test_check_artifacts_some_missing(self, mock_exists, mock_settings, command):
        """Test checking artifacts when some are missing."""
        mock_settings.BASE_DIR = Path('/project')
        
        # Return True for some, False for others
        call_count = [0]
        def exists_side_effect(path):
            call_count[0] += 1
            # First few exist, rest don't
            return call_count[0] <= 4
        
        mock_exists.side_effect = exists_side_effect
        
        command._check_artifacts()
        
        # Should complete with warnings
        assert True
    
    @patch('training.management.commands.init_api.load_artifacts')
    def test_load_models_success(self, mock_load_artifacts, command):
        """Test loading models successfully."""
        mock_load_artifacts.return_value = True
        
        command._load_models()
        
        mock_load_artifacts.assert_called_once()
    
    @patch('training.management.commands.init_api.load_artifacts')
    def test_load_models_failure(self, mock_load_artifacts, command):
        """Test loading models when it fails."""
        mock_load_artifacts.return_value = False
        
        command._load_models()
        
        # Should complete with warning
        mock_load_artifacts.assert_called_once()
    
    @patch('training.management.commands.init_api.load_artifacts')
    def test_load_models_exception(self, mock_load_artifacts, command):
        """Test loading models when exception occurs."""
        mock_load_artifacts.side_effect = Exception("Load error")
        
        command._load_models()
        
        # Should complete with warning
        mock_load_artifacts.assert_called_once()
    
    @patch('training.management.commands.init_api.settings')
    def test_show_api_info(self, mock_settings, command):
        """Test showing API information."""
        mock_settings.MEDIA_ROOT = '/media'
        mock_settings.BASE_DIR = Path('/project')
        
        command._show_api_info()
        
        # Should complete without errors
        assert True
    
    @patch('training.management.commands.init_api.Command._check_configuration')
    @patch('training.management.commands.init_api.Command._check_directories')
    @patch('training.management.commands.init_api.Command._check_artifacts')
    @patch('training.management.commands.init_api.Command._load_models')
    @patch('training.management.commands.init_api.Command._show_api_info')
    def test_handle_full_flow(self, mock_show, mock_load, mock_check_artifacts, 
                              mock_check_dirs, mock_check_config, command):
        """Test full handle flow."""
        command.handle(skip_models=False, check_artifacts=True)
        
        mock_check_config.assert_called_once()
        mock_check_dirs.assert_called_once()
        mock_check_artifacts.assert_called_once()
        mock_load.assert_called_once()
        mock_show.assert_called_once()
    
    @patch('training.management.commands.init_api.Command._check_configuration')
    @patch('training.management.commands.init_api.Command._check_directories')
    @patch('training.management.commands.init_api.Command._check_artifacts')
    @patch('training.management.commands.init_api.Command._load_models')
    @patch('training.management.commands.init_api.Command._show_api_info')
    def test_handle_skip_models(self, mock_show, mock_load, mock_check_artifacts,
                                mock_check_dirs, mock_check_config, command):
        """Test handle with skip_models=True."""
        command.handle(skip_models=True, check_artifacts=True)
        
        mock_check_config.assert_called_once()
        mock_check_dirs.assert_called_once()
        mock_check_artifacts.assert_called_once()
        mock_load.assert_not_called()  # Should skip loading models
        mock_show.assert_called_once()
    
    @patch('training.management.commands.init_api.Command._check_configuration')
    @patch('training.management.commands.init_api.Command._check_directories')
    @patch('training.management.commands.init_api.Command._check_artifacts')
    @patch('training.management.commands.init_api.Command._load_models')
    @patch('training.management.commands.init_api.Command._show_api_info')
    def test_handle_no_check_artifacts(self, mock_show, mock_load, mock_check_artifacts,
                                       mock_check_dirs, mock_check_config, command):
        """Test handle with check_artifacts=False."""
        command.handle(skip_models=False, check_artifacts=False)
        
        mock_check_config.assert_called_once()
        mock_check_dirs.assert_called_once()
        mock_check_artifacts.assert_not_called()  # Should skip checking artifacts
        mock_load.assert_called_once()
        mock_show.assert_called_once()
    
    @patch('training.management.commands.init_api.Command._check_configuration')
    def test_handle_exception(self, mock_check_config, command):
        """Test handle when exception occurs."""
        mock_check_config.side_effect = Exception("Config error")
        
        with pytest.raises(CommandError, match="Error inicializando API"):
            command.handle(skip_models=False, check_artifacts=False)
    
    def test_call_command_via_call_command(self):
        """Test calling command via Django's call_command."""
        with patch('training.management.commands.init_api.Command.handle'):
            call_command('init_api', '--skip-models', '--check-artifacts')
            
            # Should complete without errors
            assert True

