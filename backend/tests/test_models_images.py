"""
Unit tests for images_app models (CacaoImage, CacaoPrediction).
Tests cover model creation, properties, methods, and relationships.
"""
import pytest
from decimal import Decimal
from datetime import date
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image as PILImage
import io

from images_app.models import CacaoImage, CacaoPrediction
from fincas_app.models import Finca, Lote


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def finca(user):
    """Create a test finca."""
    return Finca.objects.create(
        nombre='Finca Test',
        ubicacion='Test',
        municipio='Test',
        departamento='Test',
        hectareas=Decimal('10.00'),
        agricultor=user
    )


@pytest.fixture
def lote(finca):
    """Create a test lote."""
    return Lote.objects.create(
        finca=finca,
        identificador='LOTE-001',
        variedad='Criollo',
        fecha_plantacion=date(2020, 1, 15),
        area_hectareas=Decimal('2.50'),
        estado='activo'
    )


@pytest.fixture
def test_image():
    """Create a test image file."""
    img = PILImage.new('RGB', (100, 100), color='red')
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    return SimpleUploadedFile(
        name='test_image.jpg',
        content=img_io.read(),
        content_type='image/jpeg'
    )


@pytest.fixture
def cacao_image(user, finca, lote, test_image):
    """Create a test cacao image."""
    return CacaoImage.objects.create(
        user=user,
        image=test_image,
        finca=finca,
        lote=lote,
        finca_nombre='Finca Test',
        region='Antioquia',
        variedad='Criollo',
        fecha_cosecha=date(2023, 6, 20),
        notas='Test image',
        file_name='test_image.jpg',
        file_size=1024,
        file_type='image/jpeg',
        processed=False
    )


class TestCacaoImage:
    """Tests for CacaoImage model."""
    
    def test_cacao_image_creation(self, user, test_image):
        """Test basic cacao image creation."""
        image = CacaoImage.objects.create(
            user=user,
            image=test_image
        )
        
        assert image.user == user
        assert image.image is not None
        assert image.uploaded_at is not None
        assert image.processed is False
        assert image.created_at is not None
        assert image.updated_at is not None
    
    def test_cacao_image_str_representation(self, cacao_image):
        """Test string representation of cacao image."""
        expected = f"Imagen {cacao_image.id} - {cacao_image.user.username} ({cacao_image.uploaded_at.strftime('%Y-%m-%d')})"
        assert str(cacao_image) == expected
    
    def test_cacao_image_inherits_timestamped_model(self, cacao_image):
        """Test that CacaoImage inherits from TimeStampedModel."""
        from core.models import TimeStampedModel
        assert isinstance(cacao_image, TimeStampedModel)
    
    def test_cacao_image_file_size_mb_property_with_size(self, cacao_image):
        """Test file_size_mb property when size exists."""
        cacao_image.file_size = 5 * 1024 * 1024  # 5 MB
        cacao_image.save()
        
        assert cacao_image.file_size_mb == 5.0
    
    def test_cacao_image_file_size_mb_property_no_size(self, user, test_image):
        """Test file_size_mb property when no size."""
        image = CacaoImage.objects.create(
            user=user,
            image=test_image
        )
        
        assert image.file_size_mb is None
    
    def test_cacao_image_file_size_mb_property_rounding(self, cacao_image):
        """Test file_size_mb property rounds correctly."""
        cacao_image.file_size = 5 * 1024 * 1024 + 512 * 1024  # 5.5 MB
        cacao_image.save()
        
        assert cacao_image.file_size_mb == 5.5
    
    def test_cacao_image_has_prediction_property_no_prediction(self, cacao_image):
        """Test has_prediction property when no prediction exists."""
        assert cacao_image.has_prediction is False
    
    def test_cacao_image_has_prediction_property_with_prediction(self, cacao_image):
        """Test has_prediction property when prediction exists."""
        CacaoPrediction.objects.create(
            image=cacao_image,
            alto_mm=Decimal('20.5'),
            ancho_mm=Decimal('15.3'),
            grosor_mm=Decimal('10.2'),
            peso_g=Decimal('5.5'),
            processing_time_ms=100
        )
        
        cacao_image.refresh_from_db()
        assert cacao_image.has_prediction is True
    
    def test_cacao_image_relationship_with_finca(self, user, finca, test_image):
        """Test relationship with Finca."""
        image = CacaoImage.objects.create(
            user=user,
            image=test_image,
            finca=finca
        )
        
        assert image.finca == finca
        assert image in finca.cacao_images.all()
    
    def test_cacao_image_relationship_with_lote(self, user, finca, lote, test_image):
        """Test relationship with Lote."""
        image = CacaoImage.objects.create(
            user=user,
            image=test_image,
            finca=finca,
            lote=lote
        )
        
        assert image.lote == lote
        assert image in lote.cacao_images.all()
    
    def test_cacao_image_set_null_on_finca_delete(self, user, finca, test_image):
        """Test that finca is set to null when finca is deleted."""
        image = CacaoImage.objects.create(
            user=user,
            image=test_image,
            finca=finca
        )
        image_id = image.id
        
        finca.delete()
        
        image.refresh_from_db()
        assert image.finca is None
        assert image.id == image_id  # Image should still exist
    
    def test_cacao_image_set_null_on_lote_delete(self, user, finca, lote, test_image):
        """Test that lote is set to null when lote is deleted."""
        image = CacaoImage.objects.create(
            user=user,
            image=test_image,
            finca=finca,
            lote=lote
        )
        image_id = image.id
        
        lote.delete()
        
        image.refresh_from_db()
        assert image.lote is None
        assert image.id == image_id  # Image should still exist
    
    def test_cacao_image_cascade_delete_with_user(self, user, test_image):
        """Test that images are deleted when user is deleted."""
        image = CacaoImage.objects.create(
            user=user,
            image=test_image
        )
        image_id = image.id
        
        user.delete()
        
        assert not CacaoImage.objects.filter(id=image_id).exists()
    
    def test_cacao_image_ordering(self, user, test_image):
        """Test that images are ordered by created_at descending."""
        image1 = CacaoImage.objects.create(
            user=user,
            image=test_image
        )
        
        import time
        time.sleep(0.01)
        
        image2 = CacaoImage.objects.create(
            user=user,
            image=test_image
        )
        
        images = list(CacaoImage.objects.filter(user=user))
        assert images[0].id == image2.id
        assert images[1].id == image1.id
    
    def test_cacao_image_blank_fields(self, user, test_image):
        """Test that optional fields can be blank."""
        image = CacaoImage.objects.create(
            user=user,
            image=test_image
        )
        
        assert image.finca is None
        assert image.finca_nombre == ''
        assert image.region == ''
        assert image.lote is None
        assert image.variedad == ''
        assert image.notas == ''
        assert image.file_name == ''
        assert image.file_size == 0
        assert image.file_type == ''


class TestCacaoPrediction:
    """Tests for CacaoPrediction model."""
    
    def test_prediction_creation(self, cacao_image):
        """Test basic prediction creation."""
        prediction = CacaoPrediction.objects.create(
            image=cacao_image,
            alto_mm=Decimal('20.5'),
            ancho_mm=Decimal('15.3'),
            grosor_mm=Decimal('10.2'),
            peso_g=Decimal('5.5'),
            confidence_alto=Decimal('0.85'),
            confidence_ancho=Decimal('0.90'),
            confidence_grosor=Decimal('0.88'),
            confidence_peso=Decimal('0.92'),
            processing_time_ms=100,
            model_version='v1.0',
            device_used='cpu'
        )
        
        assert prediction.image == cacao_image
        assert prediction.alto_mm == Decimal('20.5')
        assert prediction.ancho_mm == Decimal('15.3')
        assert prediction.grosor_mm == Decimal('10.2')
        assert prediction.peso_g == Decimal('5.5')
        assert prediction.confidence_alto == Decimal('0.85')
        assert prediction.confidence_ancho == Decimal('0.90')
        assert prediction.confidence_grosor == Decimal('0.88')
        assert prediction.confidence_peso == Decimal('0.92')
        assert prediction.processing_time_ms == 100
        assert prediction.model_version == 'v1.0'
        assert prediction.device_used == 'cpu'
        assert prediction.created_at is not None
    
    def test_prediction_str_representation(self, cacao_image):
        """Test string representation of prediction."""
        prediction = CacaoPrediction.objects.create(
            image=cacao_image,
            alto_mm=Decimal('20.5'),
            ancho_mm=Decimal('15.3'),
            grosor_mm=Decimal('10.2'),
            peso_g=Decimal('5.5'),
            processing_time_ms=100
        )
        
        expected = f"Predicción {prediction.id} - {cacao_image.user.username} ({prediction.created_at.strftime('%Y-%m-%d %H:%M')})"
        assert str(prediction) == expected
    
    def test_prediction_default_confidence_values(self, cacao_image):
        """Test default confidence values."""
        prediction = CacaoPrediction.objects.create(
            image=cacao_image,
            alto_mm=Decimal('20.5'),
            ancho_mm=Decimal('15.3'),
            grosor_mm=Decimal('10.2'),
            peso_g=Decimal('5.5'),
            processing_time_ms=100
        )
        
        assert prediction.confidence_alto == Decimal('0.0')
        assert prediction.confidence_ancho == Decimal('0.0')
        assert prediction.confidence_grosor == Decimal('0.0')
        assert prediction.confidence_peso == Decimal('0.0')
    
    def test_prediction_default_model_version(self, cacao_image):
        """Test default model_version."""
        prediction = CacaoPrediction.objects.create(
            image=cacao_image,
            alto_mm=Decimal('20.5'),
            ancho_mm=Decimal('15.3'),
            grosor_mm=Decimal('10.2'),
            peso_g=Decimal('5.5'),
            processing_time_ms=100
        )
        
        assert prediction.model_version == 'v1.0'
    
    def test_prediction_default_device_used(self, cacao_image):
        """Test default device_used."""
        prediction = CacaoPrediction.objects.create(
            image=cacao_image,
            alto_mm=Decimal('20.5'),
            ancho_mm=Decimal('15.3'),
            grosor_mm=Decimal('10.2'),
            peso_g=Decimal('5.5'),
            processing_time_ms=100
        )
        
        assert prediction.device_used == 'cpu'
    
    def test_prediction_average_confidence_property(self, cacao_image):
        """Test average_confidence property."""
        prediction = CacaoPrediction.objects.create(
            image=cacao_image,
            alto_mm=Decimal('20.5'),
            ancho_mm=Decimal('15.3'),
            grosor_mm=Decimal('10.2'),
            peso_g=Decimal('5.5'),
            confidence_alto=Decimal('0.85'),
            confidence_ancho=Decimal('0.90'),
            confidence_grosor=Decimal('0.88'),
            confidence_peso=Decimal('0.92'),
            processing_time_ms=100
        )
        
        expected = (0.85 + 0.90 + 0.88 + 0.92) / 4
        assert abs(float(prediction.average_confidence) - expected) < 0.001
    
    def test_prediction_average_confidence_property_zero(self, cacao_image):
        """Test average_confidence property with zero confidences."""
        prediction = CacaoPrediction.objects.create(
            image=cacao_image,
            alto_mm=Decimal('20.5'),
            ancho_mm=Decimal('15.3'),
            grosor_mm=Decimal('10.2'),
            peso_g=Decimal('5.5'),
            processing_time_ms=100
        )
        
        assert prediction.average_confidence == Decimal('0.0')
    
    def test_prediction_volume_cm3_property(self, cacao_image):
        """Test volume_cm3 property."""
        prediction = CacaoPrediction.objects.create(
            image=cacao_image,
            alto_mm=Decimal('20.0'),  # 2.0 cm
            ancho_mm=Decimal('15.0'),  # 1.5 cm
            grosor_mm=Decimal('10.0'),  # 1.0 cm
            peso_g=Decimal('5.5'),
            processing_time_ms=100
        )
        
        # Volume = (4/3) * π * a * b * c
        # = (4/3) * π * 2.0 * 1.5 * 1.0
        # ≈ 12.566
        volume = prediction.volume_cm3
        assert isinstance(volume, float)
        assert volume > 0
        assert abs(volume - 12.566) < 1.0  # Allow some tolerance
    
    def test_prediction_density_g_cm3_property(self, cacao_image):
        """Test density_g_cm3 property."""
        prediction = CacaoPrediction.objects.create(
            image=cacao_image,
            alto_mm=Decimal('20.0'),
            ancho_mm=Decimal('15.0'),
            grosor_mm=Decimal('10.0'),
            peso_g=Decimal('5.5'),
            processing_time_ms=100
        )
        
        density = prediction.density_g_cm3
        assert isinstance(density, float)
        assert density > 0
    
    def test_prediction_density_g_cm3_property_zero_volume(self, cacao_image):
        """Test density_g_cm3 property with zero volume."""
        prediction = CacaoPrediction.objects.create(
            image=cacao_image,
            alto_mm=Decimal('0.0'),
            ancho_mm=Decimal('0.0'),
            grosor_mm=Decimal('0.0'),
            peso_g=Decimal('5.5'),
            processing_time_ms=100
        )
        
        assert prediction.density_g_cm3 is None
    
    def test_prediction_device_used_choices(self, cacao_image):
        """Test that device_used accepts valid choices."""
        valid_devices = ['cpu', 'cuda', 'mps']
        
        for device in valid_devices:
            prediction = CacaoPrediction.objects.create(
                image=cacao_image,
                alto_mm=Decimal('20.5'),
                ancho_mm=Decimal('15.3'),
                grosor_mm=Decimal('10.2'),
                peso_g=Decimal('5.5'),
                processing_time_ms=100,
                device_used=device
            )
            assert prediction.device_used == device
    
    def test_prediction_one_to_one_relationship(self, cacao_image):
        """Test one-to-one relationship with CacaoImage."""
        prediction = CacaoPrediction.objects.create(
            image=cacao_image,
            alto_mm=Decimal('20.5'),
            ancho_mm=Decimal('15.3'),
            grosor_mm=Decimal('10.2'),
            peso_g=Decimal('5.5'),
            processing_time_ms=100
        )
        
        # Image should have access to prediction via related_name
        assert hasattr(cacao_image, 'prediction')
        assert cacao_image.prediction == prediction
    
    def test_prediction_cascade_delete_with_image(self, cacao_image):
        """Test that predictions are deleted when image is deleted."""
        prediction = CacaoPrediction.objects.create(
            image=cacao_image,
            alto_mm=Decimal('20.5'),
            ancho_mm=Decimal('15.3'),
            grosor_mm=Decimal('10.2'),
            peso_g=Decimal('5.5'),
            processing_time_ms=100
        )
        prediction_id = prediction.id
        
        cacao_image.delete()
        
        assert not CacaoPrediction.objects.filter(id=prediction_id).exists()
    
    def test_prediction_ordering(self, user, finca, lote, test_image):
        """Test that predictions are ordered by created_at descending."""
        image1 = CacaoImage.objects.create(
            user=user,
            image=test_image,
            finca=finca,
            lote=lote
        )
        prediction1 = CacaoPrediction.objects.create(
            image=image1,
            alto_mm=Decimal('20.5'),
            ancho_mm=Decimal('15.3'),
            grosor_mm=Decimal('10.2'),
            peso_g=Decimal('5.5'),
            processing_time_ms=100
        )
        
        import time
        time.sleep(0.01)
        
        image2 = CacaoImage.objects.create(
            user=user,
            image=test_image,
            finca=finca,
            lote=lote
        )
        prediction2 = CacaoPrediction.objects.create(
            image=image2,
            alto_mm=Decimal('21.0'),
            ancho_mm=Decimal('15.5'),
            grosor_mm=Decimal('10.3'),
            peso_g=Decimal('5.6'),
            processing_time_ms=110
        )
        
        predictions = list(CacaoPrediction.objects.all())
        assert predictions[0].id == prediction2.id
        assert predictions[1].id == prediction1.id
    
    def test_prediction_crop_url_field(self, cacao_image):
        """Test crop_url field can be null/blank."""
        prediction = CacaoPrediction.objects.create(
            image=cacao_image,
            alto_mm=Decimal('20.5'),
            ancho_mm=Decimal('15.3'),
            grosor_mm=Decimal('10.2'),
            peso_g=Decimal('5.5'),
            processing_time_ms=100,
            crop_url='https://example.com/crop.jpg'
        )
        
        assert prediction.crop_url == 'https://example.com/crop.jpg'
    
    def test_prediction_crop_url_field_blank(self, cacao_image):
        """Test crop_url field can be blank."""
        prediction = CacaoPrediction.objects.create(
            image=cacao_image,
            alto_mm=Decimal('20.5'),
            ancho_mm=Decimal('15.3'),
            grosor_mm=Decimal('10.2'),
            peso_g=Decimal('5.5'),
            processing_time_ms=100
        )
        
        assert prediction.crop_url is None or prediction.crop_url == ''

