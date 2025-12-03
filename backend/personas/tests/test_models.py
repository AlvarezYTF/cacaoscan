"""
Tests for Personas Models.
"""
import pytest
from datetime import date, timedelta
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from personas.models import Persona, PendingRegistration
from catalogos.models import Tema, Parametro, Departamento, Municipio


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def tipo_documento():
    """Create tipo documento parameter."""
    tema = Tema.objects.create(codigo='TIPO_DOC', nombre='Tipo de Documento')
    return Parametro.objects.create(
        tema=tema,
        codigo='CC',
        nombre='Cédula de Ciudadanía'
    )


@pytest.fixture
def genero():
    """Create genero parameter."""
    tema = Tema.objects.create(codigo='SEXO', nombre='Sexo')
    return Parametro.objects.create(
        tema=tema,
        codigo='M',
        nombre='Masculino'
    )


@pytest.fixture
def departamento():
    """Create a test department."""
    return Departamento.objects.create(
        codigo='05',
        nombre='Antioquia'
    )


@pytest.fixture
def municipio(departamento):
    """Create a test municipality."""
    return Municipio.objects.create(
        departamento=departamento,
        codigo='001',
        nombre='Medellín'
    )


@pytest.mark.django_db
class TestPersona:
    """Tests for Persona model."""

    def test_create_persona(self, user, tipo_documento, genero, departamento, municipio):
        """Test creating a persona."""
        persona = Persona.objects.create(
            user=user,
            tipo_documento=tipo_documento,
            numero_documento='1234567890',
            primer_nombre='Juan',
            segundo_nombre='Carlos',
            primer_apellido='Pérez',
            segundo_apellido='García',
            telefono='3001234567',
            direccion='Calle 123',
            genero=genero,
            fecha_nacimiento=date(1990, 1, 1),
            departamento=departamento,
            municipio=municipio
        )
        
        assert persona.user == user
        assert persona.numero_documento == '1234567890'
        assert persona.primer_nombre == 'Juan'

    def test_persona_str_representation(self, user, tipo_documento, genero):
        """Test string representation."""
        persona = Persona.objects.create(
            user=user,
            tipo_documento=tipo_documento,
            numero_documento='1234567890',
            primer_nombre='Juan',
            primer_apellido='Pérez',
            telefono='3001234567',
            genero=genero
        )
        
        assert 'Juan' in str(persona)
        assert 'Pérez' in str(persona)

    def test_nombre_completo_property(self, user, tipo_documento, genero):
        """Test nombre_completo property."""
        persona = Persona.objects.create(
            user=user,
            tipo_documento=tipo_documento,
            numero_documento='1234567890',
            primer_nombre='Juan',
            segundo_nombre='Carlos',
            primer_apellido='Pérez',
            segundo_apellido='García',
            telefono='3001234567',
            genero=genero
        )
        
        assert persona.nombre_completo == str(persona)
        assert 'Juan' in persona.nombre_completo
        assert 'Pérez' in persona.nombre_completo

    def test_edad_property(self, user, tipo_documento, genero):
        """Test edad property."""
        birth_date = date(1990, 1, 1)
        persona = Persona.objects.create(
            user=user,
            tipo_documento=tipo_documento,
            numero_documento='1234567890',
            primer_nombre='Juan',
            primer_apellido='Pérez',
            telefono='3001234567',
            genero=genero,
            fecha_nacimiento=birth_date
        )
        
        expected_age = (timezone.now().date() - birth_date).days // 365
        assert abs(persona.edad - expected_age) <= 1  # Allow 1 year difference

    def test_edad_property_none(self, user, tipo_documento, genero):
        """Test edad property when fecha_nacimiento is None."""
        persona = Persona.objects.create(
            user=user,
            tipo_documento=tipo_documento,
            numero_documento='1234567890',
            primer_nombre='Juan',
            primer_apellido='Pérez',
            telefono='3001234567',
            genero=genero
        )
        
        assert persona.edad is None

    def test_validate_document_number_valid(self, user, tipo_documento, genero):
        """Test document number validation with valid number."""
        persona = Persona(
            user=user,
            tipo_documento=tipo_documento,
            numero_documento='1234567890',
            primer_nombre='Juan',
            primer_apellido='Pérez',
            telefono='3001234567',
            genero=genero
        )
        
        # Should not raise exception
        persona.full_clean()

    def test_validate_document_number_invalid_length(self, user, tipo_documento, genero):
        """Test document number validation with invalid length."""
        persona = Persona(
            user=user,
            tipo_documento=tipo_documento,
            numero_documento='12345',  # Too short
            primer_nombre='Juan',
            primer_apellido='Pérez',
            telefono='3001234567',
            genero=genero
        )
        
        with pytest.raises(ValidationError):
            persona.full_clean()

    def test_validate_document_number_non_digit(self, user, tipo_documento, genero):
        """Test document number validation with non-digit characters."""
        persona = Persona(
            user=user,
            tipo_documento=tipo_documento,
            numero_documento='12345ABC',
            primer_nombre='Juan',
            primer_apellido='Pérez',
            telefono='3001234567',
            genero=genero
        )
        
        with pytest.raises(ValidationError):
            persona.full_clean()

    def test_validate_phone_valid(self, user, tipo_documento, genero):
        """Test phone validation with valid number."""
        persona = Persona(
            user=user,
            tipo_documento=tipo_documento,
            numero_documento='1234567890',
            primer_nombre='Juan',
            primer_apellido='Pérez',
            telefono='3001234567',
            genero=genero
        )
        
        # Should not raise exception
        persona.full_clean()

    def test_validate_phone_invalid_length(self, user, tipo_documento, genero):
        """Test phone validation with invalid length."""
        persona = Persona(
            user=user,
            tipo_documento=tipo_documento,
            numero_documento='1234567890',
            primer_nombre='Juan',
            primer_apellido='Pérez',
            telefono='12345',  # Too short
            genero=genero
        )
        
        with pytest.raises(ValidationError):
            persona.full_clean()

    def test_validate_birth_date_future(self, user, tipo_documento, genero):
        """Test birth date validation with future date."""
        future_date = date.today() + timedelta(days=1)
        persona = Persona(
            user=user,
            tipo_documento=tipo_documento,
            numero_documento='1234567890',
            primer_nombre='Juan',
            primer_apellido='Pérez',
            telefono='3001234567',
            genero=genero,
            fecha_nacimiento=future_date
        )
        
        with pytest.raises(ValidationError):
            persona.full_clean()

    def test_validate_birth_date_too_young(self, user, tipo_documento, genero):
        """Test birth date validation with person too young."""
        young_date = date.today() - timedelta(days=365 * 10)  # 10 years old
        persona = Persona(
            user=user,
            tipo_documento=tipo_documento,
            numero_documento='1234567890',
            primer_nombre='Juan',
            primer_apellido='Pérez',
            telefono='3001234567',
            genero=genero,
            fecha_nacimiento=young_date
        )
        
        with pytest.raises(ValidationError):
            persona.full_clean()

    def test_validate_municipality_department(self, user, tipo_documento, genero, departamento):
        """Test municipality belongs to department validation."""
        other_departamento = Departamento.objects.create(codigo='11', nombre='Bogotá')
        other_municipio = Municipio.objects.create(
            departamento=other_departamento,
            codigo='001',
            nombre='Bogotá'
        )
        
        persona = Persona(
            user=user,
            tipo_documento=tipo_documento,
            numero_documento='1234567890',
            primer_nombre='Juan',
            primer_apellido='Pérez',
            telefono='3001234567',
            genero=genero,
            departamento=departamento,
            municipio=other_municipio  # Wrong department
        )
        
        with pytest.raises(ValidationError):
            persona.full_clean()

    def test_unique_numero_documento(self, user, tipo_documento, genero):
        """Test that numero_documento must be unique."""
        Persona.objects.create(
            user=user,
            tipo_documento=tipo_documento,
            numero_documento='1234567890',
            primer_nombre='Juan',
            primer_apellido='Pérez',
            telefono='3001234567',
            genero=genero
        )
        
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='pass123'
        )
        
        with pytest.raises(Exception):  # IntegrityError or ValidationError
            Persona.objects.create(
                user=other_user,
                tipo_documento=tipo_documento,
                numero_documento='1234567890',  # Duplicate
                primer_nombre='Pedro',
                primer_apellido='García',
                telefono='3007654321',
                genero=genero
            )


@pytest.mark.django_db
class TestPendingRegistration:
    """Tests for PendingRegistration model."""

    def test_create_pending_registration(self):
        """Test creating a pending registration."""
        registration = PendingRegistration.objects.create(
            email='test@example.com',
            data={'username': 'testuser', 'password': 'testpass'}
        )
        
        assert registration.email == 'test@example.com'
        assert registration.is_verified is False
        assert registration.verification_token is not None

    def test_pending_registration_str_representation(self):
        """Test string representation."""
        registration = PendingRegistration.objects.create(
            email='test@example.com',
            data={}
        )
        
        assert 'test@example.com' in str(registration)

    def test_is_expired_not_expired(self):
        """Test is_expired when not expired."""
        registration = PendingRegistration.objects.create(
            email='test@example.com',
            data={}
        )
        
        assert registration.is_expired() is False

    def test_is_expired_when_verified(self):
        """Test is_expired when already verified."""
        registration = PendingRegistration.objects.create(
            email='test@example.com',
            data={}
        )
        registration.verify()
        
        assert registration.is_expired() is False

    def test_verify_registration(self):
        """Test verifying a registration."""
        registration = PendingRegistration.objects.create(
            email='test@example.com',
            data={}
        )
        
        assert registration.is_verified is False
        assert registration.verified_at is None
        
        registration.verify()
        
        assert registration.is_verified is True
        assert registration.verified_at is not None

    def test_unique_email(self):
        """Test that email must be unique."""
        PendingRegistration.objects.create(
            email='test@example.com',
            data={}
        )
        
        with pytest.raises(Exception):  # IntegrityError
            PendingRegistration.objects.create(
                email='test@example.com',  # Duplicate
                data={}
            )

