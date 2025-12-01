"""
Unit tests for personas models (Persona, PendingRegistration).
Tests cover model creation, properties, methods, validations, and relationships.
"""
import pytest
import uuid
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
def tipo_documento_tema():
    """Create TIPO_DOC theme."""
    return Tema.objects.create(
        codigo='TIPO_DOC',
        nombre='Tipo de Documento',
        descripcion='Tipos de documentos de identidad',
        activo=True
    )


@pytest.fixture
def tipo_documento_param(tipo_documento_tema):
    """Create CC parameter."""
    return Parametro.objects.create(
        tema=tipo_documento_tema,
        codigo='CC',
        nombre='Cédula de Ciudadanía',
        activo=True
    )


@pytest.fixture
def sexo_tema():
    """Create SEXO theme."""
    return Tema.objects.create(
        codigo='SEXO',
        nombre='Sexo',
        descripcion='Género',
        activo=True
    )


@pytest.fixture
def sexo_param(sexo_tema):
    """Create M parameter."""
    return Parametro.objects.create(
        tema=sexo_tema,
        codigo='M',
        nombre='Masculino',
        activo=True
    )


@pytest.fixture
def departamento():
    """Create test department."""
    return Departamento.objects.create(
        codigo='05',
        nombre='Antioquia'
    )


@pytest.fixture
def municipio(departamento):
    """Create test municipality."""
    return Municipio.objects.create(
        departamento=departamento,
        codigo='05001',
        nombre='Medellín'
    )


@pytest.fixture
def persona(user, tipo_documento_param, sexo_param, departamento, municipio):
    """Create a test persona."""
    return Persona.objects.create(
        user=user,
        tipo_documento=tipo_documento_param,
        numero_documento='1234567890',
        primer_nombre='Juan',
        segundo_nombre='Carlos',
        primer_apellido='Pérez',
        segundo_apellido='García',
        telefono='3001234567',
        direccion='Calle 123 #45-67',
        genero=sexo_param,
        fecha_nacimiento=date(1990, 5, 15),
        departamento=departamento,
        municipio=municipio
    )


class TestPersona:
    """Tests for Persona model."""
    
    def test_persona_creation(self, user, tipo_documento_param, sexo_param, departamento, municipio):
        """Test basic persona creation."""
        persona = Persona.objects.create(
            user=user,
            tipo_documento=tipo_documento_param,
            numero_documento='1234567890',
            primer_nombre='María',
            primer_apellido='González',
            telefono='3009876543',
            genero=sexo_param,
            departamento=departamento,
            municipio=municipio
        )
        
        assert persona.user == user
        assert persona.tipo_documento == tipo_documento_param
        assert persona.numero_documento == '1234567890'
        assert persona.primer_nombre == 'María'
        assert persona.primer_apellido == 'González'
        assert persona.telefono == '3009876543'
        assert persona.genero == sexo_param
        assert persona.departamento == departamento
        assert persona.municipio == municipio
        assert persona.fecha_creacion is not None
    
    def test_persona_str_representation_full_name(self, persona):
        """Test string representation with full name."""
        expected = 'Juan Carlos Pérez García'
        assert str(persona) == expected
    
    def test_persona_str_representation_partial_name(self, user, tipo_documento_param, sexo_param):
        """Test string representation with partial name."""
        persona = Persona.objects.create(
            user=user,
            tipo_documento=tipo_documento_param,
            numero_documento='9876543210',
            primer_nombre='Ana',
            primer_apellido='López',
            telefono='3001112233',
            genero=sexo_param
        )
        
        assert str(persona) == 'Ana López'
    
    def test_persona_nombre_completo_property(self, persona):
        """Test nombre_completo property."""
        assert persona.nombre_completo == 'Juan Carlos Pérez García'
    
    def test_persona_edad_property(self, user, tipo_documento_param, sexo_param):
        """Test edad property."""
        birth_date = date(1990, 5, 15)
        persona = Persona.objects.create(
            user=user,
            tipo_documento=tipo_documento_param,
            numero_documento='1111111111',
            primer_nombre='Test',
            primer_apellido='User',
            telefono='3000000000',
            genero=sexo_param,
            fecha_nacimiento=birth_date
        )
        
        edad = persona.edad
        assert isinstance(edad, int)
        assert edad >= 30  # At least 30 years old
    
    def test_persona_edad_property_no_birth_date(self, persona):
        """Test edad property when no birth date."""
        persona.fecha_nacimiento = None
        persona.save()
        
        assert persona.edad is None
    
    def test_persona_validation_document_number_digits_only(self, user, tipo_documento_param, sexo_param):
        """Test validation: document number must contain only digits."""
        persona = Persona(
            user=user,
            tipo_documento=tipo_documento_param,
            numero_documento='12345ABC',
            primer_nombre='Test',
            primer_apellido='User',
            telefono='3000000000',
            genero=sexo_param
        )
        
        with pytest.raises(ValidationError):
            persona.full_clean()
    
    def test_persona_validation_document_number_length(self, user, tipo_documento_param, sexo_param):
        """Test validation: document number length."""
        # Too short
        persona = Persona(
            user=user,
            tipo_documento=tipo_documento_param,
            numero_documento='12345',
            primer_nombre='Test',
            primer_apellido='User',
            telefono='3000000000',
            genero=sexo_param
        )
        
        with pytest.raises(ValidationError):
            persona.full_clean()
        
        # Too long
        persona.numero_documento = '1' * 12
        
        with pytest.raises(ValidationError):
            persona.full_clean()
    
    def test_persona_validation_phone_digits_only(self, user, tipo_documento_param, sexo_param):
        """Test validation: phone must contain only digits (after cleaning)."""
        persona = Persona(
            user=user,
            tipo_documento=tipo_documento_param,
            numero_documento='1234567890',
            primer_nombre='Test',
            primer_apellido='User',
            telefono='300-123-4567',
            genero=sexo_param
        )
        
        # Should pass (cleaning removes dashes)
        persona.full_clean()
        persona.save()
        
        # But invalid characters should fail
        persona.telefono = '300-ABC-4567'
        
        with pytest.raises(ValidationError):
            persona.full_clean()
    
    def test_persona_validation_phone_length(self, user, tipo_documento_param, sexo_param):
        """Test validation: phone length."""
        # Too short
        persona = Persona(
            user=user,
            tipo_documento=tipo_documento_param,
            numero_documento='1234567890',
            primer_nombre='Test',
            primer_apellido='User',
            telefono='123456',
            genero=sexo_param
        )
        
        with pytest.raises(ValidationError):
            persona.full_clean()
    
    def test_persona_validation_birth_date_future(self, user, tipo_documento_param, sexo_param):
        """Test validation: birth date cannot be future."""
        future_date = date.today() + timedelta(days=1)
        persona = Persona(
            user=user,
            tipo_documento=tipo_documento_param,
            numero_documento='1234567890',
            primer_nombre='Test',
            primer_apellido='User',
            telefono='3001234567',
            genero=sexo_param,
            fecha_nacimiento=future_date
        )
        
        with pytest.raises(ValidationError):
            persona.full_clean()
    
    def test_persona_validation_birth_date_min_age(self, user, tipo_documento_param, sexo_param):
        """Test validation: minimum age is 14."""
        recent_date = date.today() - timedelta(days=365 * 13)  # 13 years old
        persona = Persona(
            user=user,
            tipo_documento=tipo_documento_param,
            numero_documento='1234567890',
            primer_nombre='Test',
            primer_apellido='User',
            telefono='3001234567',
            genero=sexo_param,
            fecha_nacimiento=recent_date
        )
        
        with pytest.raises(ValidationError):
            persona.full_clean()
    
    def test_persona_validation_birth_date_max_age(self, user, tipo_documento_param, sexo_param):
        """Test validation: maximum age is 120."""
        old_date = date.today() - timedelta(days=365 * 121)  # 121 years old
        persona = Persona(
            user=user,
            tipo_documento=tipo_documento_param,
            numero_documento='1234567890',
            primer_nombre='Test',
            primer_apellido='User',
            telefono='3001234567',
            genero=sexo_param,
            fecha_nacimiento=old_date
        )
        
        with pytest.raises(ValidationError):
            persona.full_clean()
    
    def test_persona_validation_names_letters_only(self, user, tipo_documento_param, sexo_param):
        """Test validation: names must contain only letters."""
        persona = Persona(
            user=user,
            tipo_documento=tipo_documento_param,
            numero_documento='1234567890',
            primer_nombre='Juan123',
            primer_apellido='Pérez',
            telefono='3001234567',
            genero=sexo_param
        )
        
        with pytest.raises(ValidationError):
            persona.full_clean()
    
    def test_persona_validation_municipality_department(self, user, tipo_documento_param, sexo_param, departamento):
        """Test validation: municipality must belong to department."""
        # Create another department
        otro_departamento = Departamento.objects.create(
            codigo='11',
            nombre='Bogotá'
        )
        otro_municipio = Municipio.objects.create(
            departamento=otro_departamento,
            codigo='11001',
            nombre='Bogotá'
        )
        
        persona = Persona(
            user=user,
            tipo_documento=tipo_documento_param,
            numero_documento='1234567890',
            primer_nombre='Test',
            primer_apellido='User',
            telefono='3001234567',
            genero=sexo_param,
            departamento=departamento,
            municipio=otro_municipio  # Wrong department
        )
        
        with pytest.raises(ValidationError):
            persona.full_clean()
    
    def test_persona_unique_document_number(self, user, tipo_documento_param, sexo_param):
        """Test that numero_documento is unique."""
        Persona.objects.create(
            user=user,
            tipo_documento=tipo_documento_param,
            numero_documento='1234567890',
            primer_nombre='Test',
            primer_apellido='User',
            telefono='3001234567',
            genero=sexo_param
        )
        
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        
        with pytest.raises(Exception):  # IntegrityError
            Persona.objects.create(
                user=user2,
                tipo_documento=tipo_documento_param,
                numero_documento='1234567890',  # Duplicate
                primer_nombre='Test2',
                primer_apellido='User2',
                telefono='3001234568',
                genero=sexo_param
            )
    
    def test_persona_unique_telefono(self, user, tipo_documento_param, sexo_param):
        """Test that telefono is unique."""
        Persona.objects.create(
            user=user,
            tipo_documento=tipo_documento_param,
            numero_documento='1234567890',
            primer_nombre='Test',
            primer_apellido='User',
            telefono='3001234567',
            genero=sexo_param
        )
        
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        
        with pytest.raises(Exception):  # IntegrityError
            Persona.objects.create(
                user=user2,
                tipo_documento=tipo_documento_param,
                numero_documento='9876543210',
                primer_nombre='Test2',
                primer_apellido='User2',
                telefono='3001234567',  # Duplicate
                genero=sexo_param
            )
    
    def test_persona_one_to_one_relationship(self, persona):
        """Test one-to-one relationship with User."""
        assert hasattr(persona.user, 'persona')
        assert persona.user.persona == persona
    
    def test_persona_cascade_delete_with_user(self, persona):
        """Test that persona is deleted when user is deleted."""
        persona_id = persona.id
        
        persona.user.delete()
        
        assert not Persona.objects.filter(id=persona_id).exists()
    
    def test_persona_protect_on_tipo_documento_delete(self, persona):
        """Test that tipo_documento is protected from deletion."""
        tipo_doc = persona.tipo_documento
        
        with pytest.raises(Exception):  # ProtectedError
            tipo_doc.delete()
    
    def test_persona_protect_on_genero_delete(self, persona):
        """Test that genero is protected from deletion."""
        genero = persona.genero
        
        with pytest.raises(Exception):  # ProtectedError
            genero.delete()
    
    def test_persona_set_null_on_departamento_delete(self, persona):
        """Test that departamento is set to null when deleted."""
        dept = persona.departamento
        persona_id = persona.id
        
        dept.delete()
        
        persona.refresh_from_db()
        assert persona.departamento is None
        assert persona.id == persona_id
    
    def test_persona_set_null_on_municipio_delete(self, persona):
        """Test that municipio is set to null when deleted."""
        mun = persona.municipio
        persona_id = persona.id
        
        mun.delete()
        
        persona.refresh_from_db()
        assert persona.municipio is None
        assert persona.id == persona_id


class TestPendingRegistration:
    """Tests for PendingRegistration model."""
    
    def test_pending_registration_creation(self):
        """Test basic pending registration creation."""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        registration = PendingRegistration.objects.create(
            email='newuser@example.com',
            data=data
        )
        
        assert registration.email == 'newuser@example.com'
        assert registration.data == data
        assert registration.verification_token is not None
        assert isinstance(registration.verification_token, uuid.UUID)
        assert registration.is_verified is False
        assert registration.verified_at is None
        assert registration.created_at is not None
    
    def test_pending_registration_str_representation(self):
        """Test string representation of pending registration."""
        registration = PendingRegistration.objects.create(
            email='test@example.com',
            data={}
        )
        
        assert str(registration) == 'Registro pendiente: test@example.com'
    
    def test_pending_registration_is_expired_fresh(self):
        """Test is_expired method for fresh registration."""
        registration = PendingRegistration.objects.create(
            email='test@example.com',
            data={}
        )
        
        assert registration.is_expired() is False
    
    def test_pending_registration_is_expired_old(self):
        """Test is_expired method for old registration."""
        registration = PendingRegistration.objects.create(
            email='test@example.com',
            data={}
        )
        
        # Manually set created_at to past (more than 24 hours ago)
        registration.created_at = timezone.now() - timedelta(hours=25)
        registration.save()
        
        assert registration.is_expired() is True
    
    def test_pending_registration_verify_method(self):
        """Test verify method."""
        registration = PendingRegistration.objects.create(
            email='test@example.com',
            data={}
        )
        
        assert registration.is_verified is False
        assert registration.verified_at is None
        
        registration.verify()
        
        assert registration.is_verified is True
        assert registration.verified_at is not None
        assert isinstance(registration.verified_at, timezone.datetime)
    
    def test_pending_registration_unique_email(self):
        """Test that email field is unique."""
        PendingRegistration.objects.create(
            email='test@example.com',
            data={}
        )
        
        with pytest.raises(Exception):  # IntegrityError
            PendingRegistration.objects.create(
                email='test@example.com',
                data={}
            )
    
    def test_pending_registration_unique_verification_token(self):
        """Test that verification_token is unique."""
        token1 = uuid.uuid4()
        token2 = uuid.uuid4()
        
        PendingRegistration.objects.create(
            email='test1@example.com',
            data={},
            verification_token=token1
        )
        
        # Should work with different token
        PendingRegistration.objects.create(
            email='test2@example.com',
            data={},
            verification_token=token2
        )
        
        # Should fail with duplicate token
        with pytest.raises(Exception):  # IntegrityError
            PendingRegistration.objects.create(
                email='test3@example.com',
                data={},
                verification_token=token1
            )

