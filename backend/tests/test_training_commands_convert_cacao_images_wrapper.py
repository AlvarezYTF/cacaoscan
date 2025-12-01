"""
Unit tests for convert_cacao_images wrapper command (training app).
Tests that the wrapper correctly imports and uses the unified command.
"""
import pytest
from unittest.mock import patch

from training.management.commands.convert_cacao_images import Command


class TestConvertCacaoImagesWrapper:
    """Tests for convert_cacao_images wrapper Command class."""
    
    def test_command_is_imported_from_unified(self):
        """Test that command is imported from unified command."""
        # The command should be the same class from api.management.commands
        from api.management.commands.convert_cacao_images import Command as UnifiedCommand
        
        assert Command is UnifiedCommand
    
    def test_command_initialization(self):
        """Test command initialization."""
        cmd = Command()
        assert cmd is not None
    
    def test_command_has_same_interface(self):
        """Test that wrapper has same interface as unified command."""
        cmd = Command()
        
        # Should have same methods
        assert hasattr(cmd, 'handle')
        assert hasattr(cmd, 'add_arguments')
        assert hasattr(cmd, '_process_files')
        assert hasattr(cmd, '_process_bmp_to_jpg')
        assert hasattr(cmd, '_process_jpg_to_png')

