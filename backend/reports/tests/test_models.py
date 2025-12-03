"""
Tests for Reports Models.
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


@pytest.mark.django_db
class TestReporteGenerado:
    """Tests for ReporteGenerado model."""

    def test_create_reporte(self, user):
        """Test creating a reporte."""
        reporte = ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='calidad',
            formato='pdf',
            titulo='Reporte de Calidad',
            descripcion='Reporte de calidad de granos',
            estado='pendiente'
        )
        
        assert reporte.usuario == user
        assert reporte.tipo_reporte == 'calidad'
        assert reporte.formato == 'pdf'
        assert reporte.estado == 'pendiente'

    def test_reporte_str_representation(self, user):
        """Test string representation."""
        reporte = ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='calidad',
            formato='pdf',
            nombre_archivo='reporte_calidad.pdf'
        )
        
        assert 'calidad' in str(reporte)
        assert 'reporte_calidad.pdf' in str(reporte)

    def test_tamano_archivo_mb_property(self, user):
        """Test tamano_archivo_mb property."""
        reporte = ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='calidad',
            formato='pdf',
            tamano_archivo=2 * 1024 * 1024  # 2MB
        )
        
        assert reporte.tamano_archivo_mb == 2.0

    def test_tamano_archivo_mb_none(self, user):
        """Test tamano_archivo_mb property when tamano_archivo is 0."""
        reporte = ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='calidad',
            formato='pdf',
            tamano_archivo=0
        )
        
        assert reporte.tamano_archivo_mb is None

    def test_archivo_url_property(self, user):
        """Test archivo_url property."""
        reporte = ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='calidad',
            formato='pdf'
        )
        
        # When no file, should return None
        assert reporte.archivo_url is None

    def test_tiempo_generacion_segundos_property(self, user):
        """Test tiempo_generacion_segundos property."""
        reporte = ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='calidad',
            formato='pdf',
            tiempo_generacion=timedelta(seconds=30)
        )
        
        assert reporte.tiempo_generacion_segundos == 30.0

    def test_tiempo_generacion_segundos_none(self, user):
        """Test tiempo_generacion_segundos property when tiempo_generacion is None."""
        reporte = ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='calidad',
            formato='pdf'
        )
        
        assert reporte.tiempo_generacion_segundos is None

    def test_esta_expirado_not_expired(self, user):
        """Test esta_expirado property when not expired."""
        future_date = timezone.now() + timedelta(days=1)
        reporte = ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='calidad',
            formato='pdf',
            fecha_expiracion=future_date
        )
        
        assert reporte.esta_expirado is False

    def test_esta_expirado_expired(self, user):
        """Test esta_expirado property when expired."""
        past_date = timezone.now() - timedelta(days=1)
        reporte = ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='calidad',
            formato='pdf',
            fecha_expiracion=past_date
        )
        
        assert reporte.esta_expirado is True

    def test_esta_expirado_no_fecha(self, user):
        """Test esta_expirado property when fecha_expiracion is None."""
        reporte = ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='calidad',
            formato='pdf'
        )
        
        assert reporte.esta_expirado is False

    def test_generar_reporte_static_method(self, user):
        """Test generar_reporte static method."""
        reporte = ReporteGenerado.generar_reporte(
            usuario=user,
            tipo_reporte='calidad',
            formato='pdf',
            titulo='Test Report',
            descripcion='Test Description',
            parametros={'param1': 'value1'},
            filtros={'filter1': 'value1'}
        )
        
        assert reporte.usuario == user
        assert reporte.tipo_reporte == 'calidad'
        assert reporte.formato == 'pdf'
        assert reporte.titulo == 'Test Report'
        assert reporte.estado == 'pendiente'
        assert reporte.parametros == {'param1': 'value1'}
        assert reporte.filtros_aplicados == {'filter1': 'value1'}

    def test_marcar_completado(self, user):
        """Test marcar_completado method."""
        reporte = ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='calidad',
            formato='pdf',
            estado='generando'
        )
        
        from django.core.files.uploadedfile import SimpleUploadedFile
        archivo = SimpleUploadedFile('test.pdf', b'content')
        tiempo = timedelta(seconds=10)
        
        reporte.marcar_completado(archivo, tiempo)
        
        assert reporte.estado == 'completado'
        assert reporte.archivo == archivo
        assert reporte.tiempo_generacion == tiempo

    def test_marcar_fallido(self, user):
        """Test marcar_fallido method."""
        reporte = ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='calidad',
            formato='pdf',
            estado='generando'
        )
        
        error_message = 'Error generating report'
        reporte.marcar_fallido(error_message)
        
        assert reporte.estado == 'fallido'
        assert reporte.mensaje_error == error_message

    def test_tipo_reporte_choices(self, user):
        """Test tipo_reporte choices."""
        valid_types = ['calidad', 'defectos', 'rendimiento', 'finca', 'lote', 
                      'usuario', 'auditoria', 'personalizado', 'analisis_periodo']
        
        for tipo in valid_types:
            reporte = ReporteGenerado.objects.create(
                usuario=user,
                tipo_reporte=tipo,
                formato='pdf'
            )
            assert reporte.tipo_reporte == tipo

    def test_formato_choices(self, user):
        """Test formato choices."""
        valid_formats = ['pdf', 'excel', 'csv', 'json']
        
        for formato in valid_formats:
            reporte = ReporteGenerado.objects.create(
                usuario=user,
                tipo_reporte='calidad',
                formato=formato
            )
            assert reporte.formato == formato

    def test_estado_choices(self, user):
        """Test estado choices."""
        valid_states = ['pendiente', 'generando', 'completado', 'fallido', 'expirado']
        
        for estado in valid_states:
            reporte = ReporteGenerado.objects.create(
                usuario=user,
                tipo_reporte='calidad',
                formato='pdf',
                estado=estado
            )
            assert reporte.estado == estado

