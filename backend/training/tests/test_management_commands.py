"""
Tests for training management commands.
"""
import pytest
from io import StringIO
from unittest.mock import patch, MagicMock
from django.core.management import call_command
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestFixDuplicateUsersCommand:
    """Tests for fix_duplicate_users command."""
    
    def test_no_duplicates(self):
        """Test command with no duplicate users."""
        out = StringIO()
        call_command('fix_duplicate_users', '--dry-run', stdout=out)
        
        output = out.getvalue()
        assert 'No hay usuarios duplicados' in output or 'duplicados' in output.lower()
    
    def test_dry_run_with_duplicates(self):
        """Test dry run with duplicate users."""
        # Create duplicate users
        User.objects.create_user(
            username='user1',
            email='duplicate@test.com',
            password='testpass'
        )
        User.objects.create_user(
            username='user2',
            email='duplicate@test.com',
            password='testpass'
        )
        
        out = StringIO()
        call_command('fix_duplicate_users', '--dry-run', stdout=out)
        
        output = out.getvalue()
        assert 'duplicate@test.com' in output
        # Check for DRY-RUN in a case-insensitive way, handling encoding issues
        output_lower = output.lower()
        assert 'dry-run' in output_lower or 'dry run' in output_lower or 'se encontraron' in output_lower
    
    def test_delete_duplicates(self):
        """Test deleting duplicate users."""
        # Create duplicate users
        user1 = User.objects.create_user(
            username='user1',
            email='duplicate@test.com',
            password='testpass'
        )
        user2 = User.objects.create_user(
            username='user2',
            email='duplicate@test.com',
            password='testpass'
        )
        
        initial_count = User.objects.filter(email='duplicate@test.com').count()
        assert initial_count == 2
        
        out = StringIO()
        call_command('fix_duplicate_users', '--delete', stdout=out)
        
        final_count = User.objects.filter(email='duplicate@test.com').count()
        assert final_count == 1
        
        output = out.getvalue()
        assert 'eliminados' in output.lower() or 'eliminado' in output.lower()
    
    def test_no_delete_without_flag(self):
        """Test that users are not deleted without --delete flag."""
        # Create duplicate users
        User.objects.create_user(
            username='user1',
            email='duplicate@test.com',
            password='testpass'
        )
        User.objects.create_user(
            username='user2',
            email='duplicate@test.com',
            password='testpass'
        )
        
        initial_count = User.objects.filter(email='duplicate@test.com').count()
        
        out = StringIO()
        call_command('fix_duplicate_users', stdout=out)
        
        final_count = User.objects.filter(email='duplicate@test.com').count()
        assert final_count == initial_count
        
        output = out.getvalue()
        assert '--delete' in output or 'No se eliminaron' in output


@pytest.mark.django_db
class TestInitApiCommand:
    """Tests for init_api command."""
    
    @patch('training.management.commands.init_api.load_artifacts')
    def test_init_api_skip_models(self, mock_load_artifacts):
        """Test init_api command with --skip-models."""
        out = StringIO()
        call_command('init_api', '--skip-models', stdout=out)
        
        output = out.getvalue()
        assert 'Inicializando' in output or 'inicializado' in output.lower()
        assert not mock_load_artifacts.called
    
    @patch('training.management.commands.init_api.load_artifacts')
    def test_init_api_with_models(self, mock_load_artifacts):
        """Test init_api command loading models."""
        mock_load_artifacts.return_value = True
        
        out = StringIO()
        call_command('init_api', stdout=out)
        
        output = out.getvalue()
        assert 'Inicializando' in output or 'inicializado' in output.lower()
        mock_load_artifacts.assert_called_once()
    
    @patch('training.management.commands.init_api.load_artifacts')
    def test_init_api_check_artifacts(self, mock_load_artifacts):
        """Test init_api command with --check-artifacts."""
        out = StringIO()
        call_command('init_api', '--check-artifacts', '--skip-models', stdout=out)
        
        output = out.getvalue()
        assert 'artefactos' in output.lower() or 'artifacts' in output.lower()

