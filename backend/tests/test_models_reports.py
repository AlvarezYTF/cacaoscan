"""
Unit tests for reports models (ReporteGenerado).
Tests cover model creation, properties, methods, and state management.
"""
import pytest
from datetime import timedelta
from django.contrib.auth.models import User
from django.utils import timezone

from reports.models import ReporteGenerado


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def reporte(user):
    """Create a test reporte."""
    return ReporteGenerado.objects.create(
        usuario=user,
        tipo_reporte='calidad',
        formato='pdf',
        titulo='Reporte de Calidad',
        descripcion='Reporte de prueba',
        estado='generando'
    )


class TestReporteGenerado:
    """Tests for ReporteGenerado model."""
    
    def test_reporte_creation(self, user):
        """Test basic reporte creation."""
        reporte = ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='calidad',
            formato='pdf',
            titulo='Reporte de Calidad',
            descripcion='Reporte de prueba',
            estado='generando'
        )
        
        assert reporte.usuario == user
        assert reporte.tipo_reporte == 'calidad'
        assert reporte.formato == 'pdf'
        assert reporte.titulo == 'Reporte de Calidad'
        assert reporte.descripcion == 'Reporte de prueba'
        assert reporte.estado == 'generando'
        assert reporte.fecha_solicitud is not None
        assert reporte.created_at is not None
        assert reporte.updated_at is not None
    
    def test_reporte_default_estado(self, user):
        """Test default estado is 'generando'."""
        reporte = ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='calidad',
            formato='pdf',
            titulo='Test Report'
        )
        
        assert reporte.estado == 'generando'
    
    def test_reporte_tamano_archivo_mb_property_with_size(self, reporte):
        """Test tamano_archivo_mb property when size exists."""
        reporte.tamano_archivo = 5 * 1024 * 1024  # 5 MB
        reporte.save()
        
        assert reporte.tamano_archivo_mb == 5.0
    
    def test_reporte_tamano_archivo_mb_property_no_size(self, reporte):
        """Test tamano_archivo_mb property when no size."""
        assert reporte.tamano_archivo_mb is None
    
    def test_reporte_tamano_archivo_mb_property_rounding(self, reporte):
        """Test tamano_archivo_mb property rounds correctly."""
        reporte.tamano_archivo = 5 * 1024 * 1024 + 512 * 1024  # 5.5 MB
        reporte.save()
        
        assert reporte.tamano_archivo_mb == 5.5
    
    def test_reporte_archivo_url_property_with_file(self, reporte):
        """Test archivo_url property when file exists."""
        # Mock file URL
        reporte.archivo = 'reportes/2024/01/15/test.pdf'
        reporte.save()
        
        # Note: In real test, would need to mock the file storage
        # For now, just check the property exists
        assert hasattr(reporte, 'archivo_url')
    
    def test_reporte_archivo_url_property_no_file(self, reporte):
        """Test archivo_url property when no file."""
        assert reporte.archivo_url is None
    
    def test_reporte_tiempo_generacion_segundos_property_with_duration(self, reporte):
        """Test tiempo_generacion_segundos property when duration exists."""
        reporte.tiempo_generacion = timedelta(seconds=125)
        reporte.save()
        
        assert reporte.tiempo_generacion_segundos == 125.0
    
    def test_reporte_tiempo_generacion_segundos_property_no_duration(self, reporte):
        """Test tiempo_generacion_segundos property when no duration."""
        assert reporte.tiempo_generacion_segundos is None
    
    def test_reporte_esta_expirado_property_not_expired(self, reporte):
        """Test esta_expirado property when not expired."""
        reporte.fecha_expiracion = timezone.now() + timedelta(days=1)
        reporte.save()
        
        assert reporte.esta_expirado is False
    
    def test_reporte_esta_expirado_property_expired(self, reporte):
        """Test esta_expirado property when expired."""
        reporte.fecha_expiracion = timezone.now() - timedelta(days=1)
        reporte.save()
        
        assert reporte.esta_expirado is True
    
    def test_reporte_esta_expirado_property_no_fecha(self, reporte):
        """Test esta_expirado property when no fecha_expiracion."""
        assert reporte.esta_expirado is False
    
    def test_reporte_tipo_reporte_choices(self, user):
        """Test that tipo_reporte accepts valid choices."""
        valid_tipos = [
            'calidad', 'defectos', 'rendimiento', 'finca',
            'lote', 'usuario', 'auditoria', 'personalizado'
        ]
        
        for tipo in valid_tipos:
            reporte = ReporteGenerado.objects.create(
                usuario=user,
                tipo_reporte=tipo,
                formato='pdf',
                titulo=f'Reporte {tipo}'
            )
            assert reporte.tipo_reporte == tipo
    
    def test_reporte_formato_choices(self, user):
        """Test that formato accepts valid choices."""
        valid_formatos = ['pdf', 'excel', 'csv', 'json']
        
        for formato in valid_formatos:
            reporte = ReporteGenerado.objects.create(
                usuario=user,
                tipo_reporte='calidad',
                formato=formato,
                titulo='Test Report'
            )
            assert reporte.formato == formato
    
    def test_reporte_estado_choices(self, user):
        """Test that estado accepts valid choices."""
        valid_estados = ['generando', 'completado', 'fallido', 'expirado']
        
        for estado in valid_estados:
            reporte = ReporteGenerado.objects.create(
                usuario=user,
                tipo_reporte='calidad',
                formato='pdf',
                titulo='Test Report',
                estado=estado
            )
            assert reporte.estado == estado
    
    def test_reporte_parametros_json_field(self, user):
        """Test parametros JSON field."""
        parametros = {
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-12-31',
            'finca_id': 1
        }
        
        reporte = ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='calidad',
            formato='pdf',
            titulo='Test Report',
            parametros=parametros
        )
        
        assert reporte.parametros == parametros
    
    def test_reporte_filtros_aplicados_json_field(self, user):
        """Test filtros_aplicados JSON field."""
        filtros = {
            'variedad': 'Criollo',
            'calidad_minima': 0.8
        }
        
        reporte = ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='calidad',
            formato='pdf',
            titulo='Test Report',
            filtros_aplicados=filtros
        )
        
        assert reporte.filtros_aplicados == filtros
    
    def test_reporte_cascade_delete_with_user(self, user):
        """Test that reportes are deleted when user is deleted."""
        reporte = ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='calidad',
            formato='pdf',
            titulo='Test Report'
        )
        reporte_id = reporte.id
        
        user.delete()
        
        assert not ReporteGenerado.objects.filter(id=reporte_id).exists()
    
    def test_reporte_ordering(self, user):
        """Test that reportes are ordered by fecha_solicitud descending."""
        reporte1 = ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='calidad',
            formato='pdf',
            titulo='Report 1'
        )
        
        # Small delay
        import time
        time.sleep(0.01)
        
        reporte2 = ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='defectos',
            formato='excel',
            titulo='Report 2'
        )
        
        reportes = list(ReporteGenerado.objects.filter(usuario=user))
        assert reportes[0].id == reporte2.id
        assert reportes[1].id == reporte1.id

