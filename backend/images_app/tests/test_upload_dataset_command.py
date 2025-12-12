"""
Tests for upload_dataset management command.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
from pathlib import Path
from django.core.management import call_command
from django.core.management.base import CommandError
from django.contrib.auth.models import User
from images_app.models import CacaoImage


@pytest.mark.django_db
class TestUploadDatasetCommand:
    """Tests for upload_dataset command."""
    
    @pytest.fixture
    def user(self, db):
        """Create test user with unique username and email."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123',
            is_superuser=True
        )
    
    @pytest.fixture
    def temp_folder(self, tmp_path):
        """Create temporary folder with test images."""
        folder = tmp_path / 'test_images'
        folder.mkdir()
        
        # Create test image files
        (folder / 'test1.png').write_bytes(b'fake png content')
        (folder / 'test2.jpg').write_bytes(b'fake jpg content')
        (folder / 'test3.jpeg').write_bytes(b'fake jpeg content')
        (folder / 'test4.webp').write_bytes(b'fake webp content')
        
        return folder
    
    def test_validate_folder_exists(self, user, temp_folder):
        """Test validating existing folder."""
        from images_app.management.commands.upload_dataset import Command
        
        command = Command()
        result = command._validate_folder(Path(temp_folder))
        
        assert result is True
    
    def test_validate_folder_not_exists(self, user):
        """Test validating non-existent folder."""
        from images_app.management.commands.upload_dataset import Command
        
        command = Command()
        out = StringIO()
        command.stdout = out
        
        result = command._validate_folder(Path('/nonexistent/folder'))
        
        assert result is False
        assert 'no existe' in out.getvalue()
    
    def test_validate_folder_not_directory(self, user, tmp_path):
        """Test validating file instead of folder."""
        from images_app.management.commands.upload_dataset import Command
        
        command = Command()
        out = StringIO()
        command.stdout = out
        
        file_path = tmp_path / 'test.txt'
        file_path.write_text('test')
        
        result = command._validate_folder(file_path)
        
        assert result is False
        assert 'no es una carpeta' in out.getvalue()
    
    def test_get_user_by_username(self, user):
        """Test getting user by username."""
        from images_app.management.commands.upload_dataset import Command
        
        command = Command()
        # Use the actual username from the fixture
        result = command._get_user(user.username)
        
        assert result == user
        assert result.username == user.username
    
    def test_get_user_not_found(self):
        """Test getting non-existent user."""
        from images_app.management.commands.upload_dataset import Command
        
        command = Command()
        out = StringIO()
        command.stdout = out
        
        result = command._get_user('nonexistent')
        
        assert result is None
        assert 'no encontrado' in out.getvalue()
    
    def test_get_user_default_superuser(self, user):
        """Test getting default superuser."""
        from images_app.management.commands.upload_dataset import Command
        
        command = Command()
        result = command._get_user(None)
        
        assert result == user
        assert result.is_superuser is True
    
    def test_get_finca_valid_id(self, user):
        """Test getting finca with valid ID."""
        from images_app.management.commands.upload_dataset import Command
        from fincas_app.models import Finca
        
        finca = Finca.objects.create(
            nombre='Test Finca',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=10.0,
            agricultor=user
        )
        
        command = Command()
        out = StringIO()
        command.stdout = out
        
        result = command._get_finca(finca.id)
        
        assert result == finca
        assert 'Finca:' in out.getvalue()
    
    def test_get_finca_invalid_id(self, user):
        """Test getting finca with invalid ID."""
        from images_app.management.commands.upload_dataset import Command
        
        command = Command()
        out = StringIO()
        command.stdout = out
        
        result = command._get_finca(999)
        
        assert result is None
        assert 'no encontrada' in out.getvalue()
    
    def test_get_finca_none(self, user):
        """Test getting finca with None."""
        from images_app.management.commands.upload_dataset import Command
        
        command = Command()
        result = command._get_finca(None)
        
        assert result is None
    
    def test_find_image_files(self, user, temp_folder):
        """Test finding image files."""
        from images_app.management.commands.upload_dataset import Command
        
        command = Command()
        extensions = ['.png', '.jpg', '.jpeg', '.webp']
        
        files = command._find_image_files(Path(temp_folder), extensions)
        
        assert len(files) == 4
        assert any('test1.png' in str(f) for f in files)
        assert any('test2.jpg' in str(f) for f in files)
        assert any('test3.jpeg' in str(f) for f in files)
        assert any('test4.webp' in str(f) for f in files)
    
    def test_find_image_files_case_insensitive(self, user, tmp_path):
        """Test finding image files case insensitive."""
        from images_app.management.commands.upload_dataset import Command
        
        folder = tmp_path / 'test_images'
        folder.mkdir()
        (folder / 'TEST.PNG').write_bytes(b'fake content')
        
        command = Command()
        extensions = ['.png']
        
        files = command._find_image_files(Path(folder), extensions)
        
        assert len(files) == 1
    
    def test_get_content_type(self, user, temp_folder):
        """Test getting content type."""
        from images_app.management.commands.upload_dataset import Command
        
        command = Command()
        img_path = Path(temp_folder) / 'test1.png'
        
        content_type = command._get_content_type(img_path)
        
        assert content_type == 'image/png'
    
    def test_upload_single_image_success(self, user, temp_folder):
        """Test uploading single image successfully."""
        from images_app.management.commands.upload_dataset import Command
        
        command = Command()
        out = StringIO()
        command.stdout = out
        
        img_path = Path(temp_folder) / 'test1.png'
        
        result = command._upload_single_image(img_path, user, None, 1, 1)
        
        assert result is True
        assert CacaoImage.objects.filter(file_name='test1.png').exists()
    
    def test_upload_single_image_with_finca(self, user, temp_folder):
        """Test uploading single image with finca."""
        from images_app.management.commands.upload_dataset import Command
        from fincas_app.models import Finca
        
        finca = Finca.objects.create(
            nombre='Test Finca',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=10.0,
            agricultor=user
        )
        
        command = Command()
        out = StringIO()
        command.stdout = out
        
        img_path = Path(temp_folder) / 'test1.png'
        
        result = command._upload_single_image(img_path, user, finca, 1, 1)
        
        assert result is True
        image = CacaoImage.objects.get(file_name='test1.png')
        assert image.finca == finca
    
    def test_upload_single_image_error(self, user, tmp_path):
        """Test uploading single image with error."""
        from images_app.management.commands.upload_dataset import Command
        
        command = Command()
        out = StringIO()
        command.stdout = out
        
        # Create invalid path
        img_path = Path(tmp_path) / 'nonexistent.png'
        
        result = command._upload_single_image(img_path, user, None, 1, 1)
        
        assert result is False
        assert 'ERROR' in out.getvalue()
    
    @pytest.mark.django_db
    def test_handle_command_success(self, user, temp_folder):
        """Test handling command successfully."""
        from images_app.management.commands.upload_dataset import Command
        
        out = StringIO()
        
        call_command(
            'upload_dataset',
            str(temp_folder),
            '--user', 'testuser',
            stdout=out
        )
        
        assert CacaoImage.objects.count() == 4
        assert 'completado' in out.getvalue().lower()
    
    @pytest.mark.django_db
    def test_handle_command_with_finca(self, user, temp_folder):
        """Test handling command with finca."""
        from fincas_app.models import Finca
        
        finca = Finca.objects.create(
            nombre='Test Finca',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=10.0,
            agricultor=user
        )
        
        out = StringIO()
        
        call_command(
            'upload_dataset',
            str(temp_folder),
            '--user', 'testuser',
            '--finca-id', str(finca.id),
            stdout=out
        )
        
        assert CacaoImage.objects.count() == 4
        images = CacaoImage.objects.all()
        assert all(img.finca == finca for img in images)
    
    @pytest.mark.django_db
    def test_handle_command_custom_extensions(self, user, tmp_path):
        """Test handling command with custom extensions."""
        folder = tmp_path / 'test_images'
        folder.mkdir()
        (folder / 'test1.bmp').write_bytes(b'fake bmp content')
        
        out = StringIO()
        
        call_command(
            'upload_dataset',
            str(folder),
            '--user', 'testuser',
            '--extensions', '.bmp',
            stdout=out
        )
        
        assert CacaoImage.objects.count() == 1
    
    def test_handle_command_no_images(self, user, tmp_path):
        """Test handling command with no images."""
        folder = tmp_path / 'test_images'
        folder.mkdir()
        
        out = StringIO()
        
        call_command(
            'upload_dataset',
            str(folder),
            '--user', 'testuser',
            stdout=out
        )
        
        assert CacaoImage.objects.count() == 0
        assert 'No se encontraron imágenes' in out.getvalue()


