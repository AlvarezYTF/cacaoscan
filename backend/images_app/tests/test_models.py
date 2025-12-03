"""
Tests for Images App Models.
"""
import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

from images_app.models import CacaoImage, CacaoPrediction


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def image_file():
    """Create a test image file."""
    img = Image.new('RGB', (100, 100), color='red')
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    return SimpleUploadedFile(
        name='test_image.jpg',
        content=img_io.read(),
        content_type='image/jpeg'
    )


@pytest.mark.django_db
class TestCacaoImage:
    """Tests for CacaoImage model."""

    def test_create_cacao_image(self, user, image_file):
        """Test creating a CacaoImage."""
        cacao_image = CacaoImage.objects.create(
            user=user,
            image=image_file,
            file_name='test_image.jpg',
            file_size=1024,
            file_type='image/jpeg'
        )
        
        assert cacao_image.user == user
        assert cacao_image.file_name == 'test_image.jpg'
        assert cacao_image.file_size == 1024
        assert cacao_image.processed is False

    def test_cacao_image_str_representation(self, user, image_file):
        """Test string representation."""
        cacao_image = CacaoImage.objects.create(
            user=user,
            image=image_file,
            file_name='test_image.jpg'
        )
        
        assert str(cacao_image.user.username) in str(cacao_image)

    def test_file_size_mb_property(self, user, image_file):
        """Test file_size_mb property."""
        cacao_image = CacaoImage.objects.create(
            user=user,
            image=image_file,
            file_size=2 * 1024 * 1024  # 2MB
        )
        
        assert cacao_image.file_size_mb == 2.0

    def test_file_size_mb_none(self, user, image_file):
        """Test file_size_mb property when file_size is None."""
        cacao_image = CacaoImage.objects.create(
            user=user,
            image=image_file,
            file_size=None
        )
        
        assert cacao_image.file_size_mb is None

    def test_has_prediction_property_false(self, user, image_file):
        """Test has_prediction property when no prediction."""
        cacao_image = CacaoImage.objects.create(
            user=user,
            image=image_file
        )
        
        assert cacao_image.has_prediction is False

    def test_has_prediction_property_true(self, user, image_file):
        """Test has_prediction property when prediction exists."""
        cacao_image = CacaoImage.objects.create(
            user=user,
            image=image_file
        )
        
        CacaoPrediction.objects.create(
            image=cacao_image,
            alto_mm=Decimal('20.5'),
            ancho_mm=Decimal('15.3'),
            grosor_mm=Decimal('10.2'),
            peso_g=Decimal('1.5')
        )
        
        assert cacao_image.has_prediction is True

    def test_filename_property(self, user, image_file):
        """Test filename property."""
        cacao_image = CacaoImage.objects.create(
            user=user,
            image=image_file,
            file_name='test_image.jpg'
        )
        
        assert cacao_image.filename == 'test_image.jpg'

    def test_filename_property_fallback(self, user, image_file):
        """Test filename property fallback to image.name."""
        cacao_image = CacaoImage.objects.create(
            user=user,
            image=image_file
            # No file_name set
        )
        
        # Should use image.name if file_name is empty
        assert cacao_image.filename is not None


@pytest.mark.django_db
class TestCacaoPrediction:
    """Tests for CacaoPrediction model."""

    def test_create_cacao_prediction(self, user, image_file):
        """Test creating a CacaoPrediction."""
        cacao_image = CacaoImage.objects.create(
            user=user,
            image=image_file
        )
        
        prediction = CacaoPrediction.objects.create(
            image=cacao_image,
            user=user,
            alto_mm=Decimal('20.5'),
            ancho_mm=Decimal('15.3'),
            grosor_mm=Decimal('10.2'),
            peso_g=Decimal('1.5'),
            confidence_alto=Decimal('0.9'),
            confidence_ancho=Decimal('0.85'),
            confidence_grosor=Decimal('0.88'),
            confidence_peso=Decimal('0.92')
        )
        
        assert prediction.alto_mm == Decimal('20.5')
        assert prediction.ancho_mm == Decimal('15.3')
        assert prediction.peso_g == Decimal('1.5')
        assert prediction.image == cacao_image

    def test_average_confidence_property(self, user, image_file):
        """Test average_confidence property."""
        cacao_image = CacaoImage.objects.create(
            user=user,
            image=image_file
        )
        
        prediction = CacaoPrediction.objects.create(
            image=cacao_image,
            confidence_alto=Decimal('0.9'),
            confidence_ancho=Decimal('0.85'),
            confidence_grosor=Decimal('0.88'),
            confidence_peso=Decimal('0.92')
        )
        
        expected_avg = (0.9 + 0.85 + 0.88 + 0.92) / 4
        assert abs(float(prediction.average_confidence) - expected_avg) < 0.01

    def test_average_confidence_zero_confidences(self, user, image_file):
        """Test average_confidence when all confidences are 0."""
        cacao_image = CacaoImage.objects.create(
            user=user,
            image=image_file
        )
        
        prediction = CacaoPrediction.objects.create(
            image=cacao_image,
            confidence_alto=Decimal('0.0'),
            confidence_ancho=Decimal('0.0'),
            confidence_grosor=Decimal('0.0'),
            confidence_peso=Decimal('0.0')
        )
        
        assert prediction.average_confidence == 0.0

    def test_created_alias(self, user, image_file):
        """Test created alias for backward compatibility."""
        cacao_image = CacaoImage.objects.create(
            user=user,
            image=image_file
        )
        
        prediction = CacaoPrediction.objects.create(
            image=cacao_image
        )
        
        assert prediction.created == prediction.created_at

    def test_prediction_one_to_one_relationship(self, user, image_file):
        """Test one-to-one relationship with CacaoImage."""
        cacao_image = CacaoImage.objects.create(
            user=user,
            image=image_file
        )
        
        prediction = CacaoPrediction.objects.create(
            image=cacao_image
        )
        
        # Should be accessible via related_name
        assert cacao_image.prediction == prediction

    def test_prediction_cascade_delete(self, user, image_file):
        """Test that prediction is deleted when image is deleted."""
        cacao_image = CacaoImage.objects.create(
            user=user,
            image=image_file
        )
        
        prediction = CacaoPrediction.objects.create(
            image=cacao_image
        )
        prediction_id = prediction.id
        
        cacao_image.delete()
        
        assert not CacaoPrediction.objects.filter(id=prediction_id).exists()

