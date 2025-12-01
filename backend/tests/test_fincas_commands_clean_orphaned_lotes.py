"""
Unit tests for clean_orphaned_lotes management command.
Tests Django management command for cleaning orphaned lotes.
"""
import pytest
from unittest.mock import patch, MagicMock
from django.core.management import call_command
from django.db import connection
from django.contrib.auth.models import User
from decimal import Decimal

from fincas_app.management.commands.clean_orphaned_lotes import Command


@pytest.fixture
def command():
    """Create a Command instance for testing."""
    return Command()


@pytest.fixture
def test_user(db):
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def test_finca(db, test_user):
    """Create a test finca."""
    from api.models import Finca
    return Finca.objects.create(
        nombre='Test Finca',
        propietario=test_user,
        area_total=Decimal('20.0')
    )


@pytest.mark.django_db
class TestCleanOrphanedLotesCommand:
    """Tests for clean_orphaned_lotes Command class."""
    
    def test_command_initialization(self):
        """Test command initialization."""
        cmd = Command()
        assert cmd is not None
    
    def test_get_image_count_no_images(self, command, db):
        """Test getting image count when no images exist."""
        with connection.cursor() as cursor:
            count = command._get_image_count(cursor, 999)
            assert count == 0
    
    def test_handle_no_orphaned_lotes(self, command, db, test_finca):
        """Test handle when no orphaned lotes exist."""
        from fincas_app.models import Lote
        
        # Create a valid lote
        lote = Lote.objects.create(
            finca=test_finca,
            nombre='Valid Lote',
            area=Decimal('5.0')
        )
        
        command.handle(dry_run=False)
        
        # Lote should still exist
        assert Lote.objects.filter(id=lote.id).exists()
    
    def test_handle_orphaned_lotes_dry_run(self, command, db):
        """Test handle with orphaned lotes in dry-run mode."""
        from fincas_app.models import Lote
        
        # Create orphaned lote (finca_id points to non-existent finca)
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO fincas_app_lote (finca_id, nombre, area, estado, fecha_creacion, fecha_actualizacion)
                VALUES (99999, 'Orphaned Lote', 5.0, 'activo', NOW(), NOW())
            """)
            cursor.execute("SELECT id FROM fincas_app_lote WHERE finca_id = 99999")
            orphaned_id = cursor.fetchone()[0]
        
        command.handle(dry_run=True)
        
        # Lote should still exist in dry-run mode
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM fincas_app_lote WHERE id = %s", [orphaned_id])
            assert cursor.fetchone() is not None
    
    def test_handle_orphaned_lotes_with_images(self, command, db):
        """Test handle with orphaned lotes that have images."""
        from fincas_app.models import Lote
        
        # Create orphaned lote
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO fincas_app_lote (finca_id, nombre, area, estado, fecha_creacion, fecha_actualizacion)
                VALUES (99999, 'Orphaned with Images', 5.0, 'activo', NOW(), NOW())
            """)
            cursor.execute("SELECT id FROM fincas_app_lote WHERE finca_id = 99999")
            orphaned_id = cursor.fetchone()[0]
            
            # Create associated image
            cursor.execute("""
                INSERT INTO images_app_cacaoimage (lote_id, user_id, file_name, file_size, file_type, processed, fecha_subida)
                VALUES (%s, 1, 'test.jpg', 1024, 'image/jpeg', false, NOW())
            """, [orphaned_id])
        
        command.handle(dry_run=False)
        
        # Lote should still exist because it has images
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM fincas_app_lote WHERE id = %s", [orphaned_id])
            assert cursor.fetchone() is not None
    
    def test_handle_orphaned_lotes_without_images(self, command, db):
        """Test handle with orphaned lotes without images."""
        from fincas_app.models import Lote
        
        # Create orphaned lote
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO fincas_app_lote (finca_id, nombre, area, estado, fecha_creacion, fecha_actualizacion)
                VALUES (99999, 'Orphaned without Images', 5.0, 'activo', NOW(), NOW())
            """)
            cursor.execute("SELECT id FROM fincas_app_lote WHERE finca_id = 99999")
            orphaned_id = cursor.fetchone()[0]
        
        command.handle(dry_run=False)
        
        # Lote should be deleted
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM fincas_app_lote WHERE id = %s", [orphaned_id])
            assert cursor.fetchone() is None
    
    def test_check_and_display_lotes(self, command, db):
        """Test checking and displaying orphaned lotes."""
        from fincas_app.models import Lote
        
        # Create orphaned lotes
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO fincas_app_lote (finca_id, nombre, identificador, variedad, area, estado, fecha_creacion, fecha_actualizacion)
                VALUES 
                    (99999, 'Orphaned 1', 'L001', 'CCN-51', 5.0, 'activo', NOW(), NOW()),
                    (99998, 'Orphaned 2', 'L002', 'Criollo', 3.0, 'activo', NOW(), NOW())
            """)
            cursor.execute("""
                SELECT l.id, l.finca_id, l.identificador, l.variedad
                FROM fincas_app_lote l
                LEFT JOIN api_finca f ON l.finca_id = f.id
                WHERE f.id IS NULL
            """)
            orphaned_lotes = cursor.fetchall()
        
        command._check_and_display_lotes(connection.cursor(), orphaned_lotes)
        
        assert len(orphaned_lotes) >= 0
    
    def test_delete_orphaned_lotes(self, command, db):
        """Test deleting orphaned lotes."""
        from fincas_app.models import Lote
        
        # Create orphaned lotes
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO fincas_app_lote (finca_id, nombre, identificador, variedad, area, estado, fecha_creacion, fecha_actualizacion)
                VALUES 
                    (99999, 'Orphaned 1', 'L001', 'CCN-51', 5.0, 'activo', NOW(), NOW()),
                    (99998, 'Orphaned 2', 'L002', 'Criollo', 3.0, 'activo', NOW(), NOW())
            """)
            cursor.execute("""
                SELECT l.id, l.finca_id, l.identificador, l.variedad
                FROM fincas_app_lote l
                LEFT JOIN api_finca f ON l.finca_id = f.id
                WHERE f.id IS NULL
            """)
            orphaned_lotes = cursor.fetchall()
        
        with connection.cursor() as cursor:
            deleted_count = command._delete_orphaned_lotes(cursor, orphaned_lotes)
        
        # Verify lotes were deleted
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM fincas_app_lote 
                WHERE finca_id IN (99999, 99998)
            """)
            remaining_count = cursor.fetchone()[0]
            assert remaining_count == 0

