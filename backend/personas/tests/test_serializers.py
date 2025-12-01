"""
Unit tests for personas serializers (personas/serializers.py).
Tests all serializers: PersonaSerializer, PersonaRegistroSerializer, PersonaActualizacionSerializer
and validation functions.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta

from personas.models import Persona
from personas.serializers import (
    PersonaSerializer,
    PersonaRegistroSerializer,
    PersonaActualizacionSerializer,
    validate_documento_number,
    validate_phone_number,
    validate_birth_date,
    validate_name_field
)
from catalogos.models import Tema, Parametro, Departamento, Municipio
from api.tests.test_constants import (
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
    TEST_USER_PASSWORD
)


@pytest.fixture
def test_user():
    """Create a test user."""
    return User.objects.create_user(
        username=TEST_USER_USERNAME,
        email=TEST_USER_EMAIL,
        password=TEST_USER_PASSWORD
    )


@pytest.fixture
def tipo_doc_tema():
    """Create TIPO_DOC theme."""
    return Tema.objects.create(
        codigo='TIPO_DOC',
        nombre='Tipo de Documento',
        descripcion='Tipos de documentos de identidad'
    )


@pytest.fixture
def sexo_tema():
    """Create SEXO theme."""
    return Tema.objects.create(
        codigo='SEXO',
        nombre='Sexo',
        descripcion='Género o sexo'
    )


@pytest.fixture
def tipo_doc_cc(tipo_doc_tema):
    """Create CC parameter."""
    return Parametro.objects.create(
        tema=tipo_doc_tema,
        codigo='CC',
        nombre='Cédula de Ciudadanía',
        activo=True
    )


@pytest.fixture
def genero_m(sexo_tema):
    """Create M gender parameter."""
    return Parametro.objects.create(
        tema=sexo_tema,
        codigo='M',
        nombre='Masculino',
        activo=True
    )


@pytest.fixture
def test_departamento():
    """Create test department."""
    return Departamento.objects.create(
        codigo='11',
        nombre='Cundinamarca'
    )


@pytest.fixture
def test_municipio(test_departamento):
    """Create test municipality."""
    return Municipio.objects.create(
        departamento=test_departamento,
        codigo='11001',
        nombre='Bogotá'
    )


@pytest.fixture
def test_persona(test_user, tipo_doc_cc, genero_m, test_departamento, test_municipio):
    """Create test persona."""
    return Persona.objects.create(
        user=test_user,
        tipo_documento=tipo_doc_cc,
        numero_documento='1234567890',
        primer_nombre='Juan',
        segundo_nombre='Carlos',
        primer_apellido='Pérez',
        segundo_apellido='García',
        telefono='3001234567',
        direccion='Calle 123',
        genero=genero_m,
        fecha_nacimiento=date(1990, 1, 1),
        departamento=test_departamento,
        municipio=test_municipio
    )


class TestValidateDocumentoNumber:
    """Tests for validate_documento_number function."""
    
    def test_validate_documento_number_success(self):
        """Test successful documento number validation."""
        value = validate_documento_number('1234567890')
        assert value == '1234567890'
    
    def test_validate_documento_number_non_digit(self):
        """Test validation error with non-digit characters."""
        with pytest.raises(Exception):
            validate_documento_number('123456789a')
    
    def test_validate_documento_number_too_short(self):
        """Test validation error when too short."""
        with pytest.raises(Exception):
            validate_documento_number('12345')
    
    def test_validate_documento_number_too_long(self):
        """Test validation error when too long."""
        with pytest.raises(Exception):
            validate_documento_number('123456789012')
    
    def test_validate_documento_number_duplicate(self, test_persona):
        """Test validation error when duplicate."""
        with pytest.raises(Exception):
            validate_documento_number('1234567890')
    
    def test_validate_documento_number_exclude_id(self, test_persona):
        """Test validation success when excluding own ID."""
        value = validate_documento_number('1234567890', exclude_persona_id=test_persona.id)
        assert value == '1234567890'


class TestValidatePhoneNumber:
    """Tests for validate_phone_number function."""
    
    def test_validate_phone_number_success(self):
        """Test successful phone number validation."""
        value = validate_phone_number('3001234567')
        assert value == '3001234567'
    
    def test_validate_phone_number_with_spaces(self):
        """Test phone number validation with spaces."""
        value = validate_phone_number('300 123 4567')
        assert value == '300 123 4567'  # Original value preserved
    
    def test_validate_phone_number_with_plus(self):
        """Test phone number validation with plus sign."""
        value = validate_phone_number('+573001234567')
        assert value == '+573001234567'
    
    def test_validate_phone_number_non_digit(self):
        """Test validation error with non-digit characters."""
        with pytest.raises(Exception):
            validate_phone_number('300123456a')
    
    def test_validate_phone_number_too_short(self):
        """Test validation error when too short."""
        with pytest.raises(Exception):
            validate_phone_number('123456')
    
    def test_validate_phone_number_too_long(self):
        """Test validation error when too long."""
        with pytest.raises(Exception):
            validate_phone_number('1234567890123456')
    
    def test_validate_phone_number_duplicate(self, test_persona):
        """Test validation error when duplicate."""
        with pytest.raises(Exception):
            validate_phone_number('3001234567')
    
    def test_validate_phone_number_exclude_id(self, test_persona):
        """Test validation success when excluding own ID."""
        value = validate_phone_number('3001234567', exclude_persona_id=test_persona.id)
        assert value == '3001234567'


class TestValidateBirthDate:
    """Tests for validate_birth_date function."""
    
    def test_validate_birth_date_success(self):
        """Test successful birth date validation."""
        value = validate_birth_date(date(1990, 1, 1))
        assert value == date(1990, 1, 1)
    
    def test_validate_birth_date_none(self):
        """Test validation with None value."""
        value = validate_birth_date(None)
        assert value is None
    
    def test_validate_birth_date_future(self):
        """Test validation error with future date."""
        future_date = timezone.now().date() + timedelta(days=1)
        with pytest.raises(Exception):
            validate_birth_date(future_date)
    
    def test_validate_birth_date_too_young(self):
        """Test validation error when age < 14."""
        young_date = timezone.now().date() - timedelta(days=365 * 13)
        with pytest.raises(Exception):
            validate_birth_date(young_date)
    
    def test_validate_birth_date_too_old(self):
        """Test validation error when age > 120."""
        old_date = timezone.now().date() - timedelta(days=365 * 121)
        with pytest.raises(Exception):
            validate_birth_date(old_date)


class TestValidateNameField:
    """Tests for validate_name_field function."""
    
    def test_validate_name_field_success(self):
        """Test successful name field validation."""
        value = validate_name_field('Juan Carlos', 'primer nombre')
        assert value == 'Juan Carlos'
    
    def test_validate_name_field_empty(self):
        """Test validation error when empty."""
        with pytest.raises(Exception):
            validate_name_field('', 'primer nombre')
    
    def test_validate_name_field_non_alpha(self):
        """Test validation error with non-alphabetic characters."""
        with pytest.raises(Exception):
            validate_name_field('Juan123', 'primer nombre')
    
    def test_validate_name_field_with_spaces(self):
        """Test validation success with spaces."""
        value = validate_name_field('Juan Carlos', 'primer nombre')
        assert value == 'Juan Carlos'


class TestPersonaSerializer:
    """Tests for PersonaSerializer."""
    
    def test_serialize_persona_success(self, test_persona):
        """Test successful persona serialization."""
        serializer = PersonaSerializer(test_persona)
        data = serializer.data
        
        assert data['id'] == test_persona.id
        assert data['numero_documento'] == '1234567890'
        assert data['primer_nombre'] == 'Juan'
        assert 'tipo_documento_info' in data
        assert 'genero_info' in data
        assert 'departamento_info' in data
        assert 'municipio_info' in data
        assert 'email' in data
    
    def test_get_tipo_documento_info(self, test_persona):
        """Test get_tipo_documento_info method."""
        serializer = PersonaSerializer(test_persona)
        info = serializer.get_tipo_documento_info(test_persona)
        assert info['codigo'] == 'CC'
        assert info['nombre'] == 'Cédula de Ciudadanía'
    
    def test_get_tipo_documento_info_none(self, test_user, tipo_doc_cc, genero_m):
        """Test get_tipo_documento_info when tipo_documento is None."""
        persona = Persona.objects.create(
            user=test_user,
            tipo_documento=tipo_doc_cc,
            numero_documento='9999999999',
            primer_nombre='Test',
            primer_apellido='User',
            telefono='9999999999',
            genero=genero_m
        )
        persona.tipo_documento = None
        serializer = PersonaSerializer(persona)
        info = serializer.get_tipo_documento_info(persona)
        assert info is None
    
    def test_get_genero_info(self, test_persona):
        """Test get_genero_info method."""
        serializer = PersonaSerializer(test_persona)
        info = serializer.get_genero_info(test_persona)
        assert info['codigo'] == 'M'
        assert info['nombre'] == 'Masculino'
    
    def test_get_departamento_info(self, test_persona):
        """Test get_departamento_info method."""
        serializer = PersonaSerializer(test_persona)
        info = serializer.get_departamento_info(test_persona)
        assert info['codigo'] == '11'
        assert info['nombre'] == 'Cundinamarca'
    
    def test_get_municipio_info(self, test_persona):
        """Test get_municipio_info method."""
        serializer = PersonaSerializer(test_persona)
        info = serializer.get_municipio_info(test_persona)
        assert info['codigo'] == '11001'
        assert info['nombre'] == 'Bogotá'


class TestPersonaRegistroSerializer:
    """Tests for PersonaRegistroSerializer."""
    
    def test_validate_email_success(self):
        """Test successful email validation."""
        serializer = PersonaRegistroSerializer()
        value = serializer.validate_email('newuser@example.com')
        assert value == 'newuser@example.com'
    
    def test_validate_email_duplicate(self, test_user):
        """Test validation error when email is duplicate."""
        serializer = PersonaRegistroSerializer()
        with pytest.raises(Exception):
            serializer.validate_email(TEST_USER_EMAIL)
    
    def test_validate_email_invalid_format(self):
        """Test validation error with invalid email format."""
        serializer = PersonaRegistroSerializer()
        with pytest.raises(Exception):
            serializer.validate_email('invalid-email')
    
    def test_validate_tipo_documento_success(self, tipo_doc_tema, tipo_doc_cc):
        """Test successful tipo_documento validation."""
        serializer = PersonaRegistroSerializer()
        data = {'tipo_documento': 'CC'}
        serializer.validate(data)
        assert 'tipo_documento_obj' in data
        assert data['tipo_documento_obj'] == tipo_doc_cc
    
    def test_validate_tipo_documento_invalid(self, tipo_doc_tema):
        """Test validation error with invalid tipo_documento."""
        serializer = PersonaRegistroSerializer()
        data = {'tipo_documento': 'INVALID'}
        with pytest.raises(Exception):
            serializer.validate(data)
    
    def test_validate_genero_success(self, sexo_tema, genero_m):
        """Test successful genero validation."""
        serializer = PersonaRegistroSerializer()
        data = {'genero': 'M'}
        serializer.validate(data)
        assert 'genero_obj' in data
        assert data['genero_obj'] == genero_m
    
    def test_validate_municipio_belongs_to_departamento(self, test_departamento, test_municipio):
        """Test validation when municipio belongs to departamento."""
        serializer = PersonaRegistroSerializer()
        data = {
            'municipio': test_municipio.id,
            'departamento': test_departamento.id
        }
        serializer.validate(data)
        assert 'municipio_obj' in data
        assert data['municipio_obj'] == test_municipio
    
    def test_validate_municipio_not_belongs_to_departamento(self, test_departamento):
        """Test validation error when municipio doesn't belong to departamento."""
        other_departamento = Departamento.objects.create(codigo='05', nombre='Antioquia')
        other_municipio = Municipio.objects.create(
            departamento=other_departamento,
            codigo='05001',
            nombre='Medellín'
        )
        
        serializer = PersonaRegistroSerializer()
        data = {
            'municipio': other_municipio.id,
            'departamento': test_departamento.id
        }
        with pytest.raises(Exception):
            serializer.validate(data)
    
    @patch('personas.serializers.send_custom_email')
    @patch('personas.serializers.EmailVerificationToken')
    def test_create_persona_success(self, mock_token, mock_email, tipo_doc_cc, genero_m, test_departamento, test_municipio):
        """Test successful persona creation."""
        mock_token_instance = Mock()
        mock_token_instance.token = 'test-token'
        mock_token_instance.is_verified = False
        mock_token.create_for_user.return_value = mock_token_instance
        
        serializer = PersonaRegistroSerializer(data={
            'email': 'newuser@example.com',
            'password': 'StrongPass123',
            'tipo_documento': 'CC',
            'numero_documento': '9876543210',
            'primer_nombre': 'María',
            'primer_apellido': 'González',
            'telefono': '3009876543',
            'genero': 'M',
            'departamento': test_departamento.id,
            'municipio': test_municipio.id
        })
        assert serializer.is_valid()
        
        persona = serializer.create(serializer.validated_data)
        assert persona.numero_documento == '9876543210'
        assert persona.primer_nombre == 'María'
        assert persona.user.email == 'newuser@example.com'
        assert persona.user.is_active is False  # Inactive until verification
    
    def test_to_representation(self, test_persona):
        """Test to_representation method."""
        serializer = PersonaRegistroSerializer(test_persona)
        data = serializer.to_representation(test_persona)
        
        assert data['id'] == test_persona.id
        assert data['email'] == test_user.email
        assert 'verification_required' in data
        assert 'user' in data


class TestPersonaActualizacionSerializer:
    """Tests for PersonaActualizacionSerializer."""
    
    def test_validate_numero_documento_exclude_self(self, test_persona):
        """Test validation success when updating own documento."""
        serializer = PersonaActualizacionSerializer(context={'persona': test_persona})
        value = serializer.validate_numero_documento('1234567890')
        assert value == '1234567890'
    
    def test_validate_numero_documento_duplicate(self, test_persona):
        """Test validation error when documento is duplicate."""
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password=TEST_USER_PASSWORD
        )
        other_persona = Persona.objects.create(
            user=other_user,
            tipo_documento=test_persona.tipo_documento,
            numero_documento='9999999999',
            primer_nombre='Other',
            primer_apellido='User',
            telefono='9999999998',
            genero=test_persona.genero
        )
        
        serializer = PersonaActualizacionSerializer(context={'persona': test_persona})
        with pytest.raises(Exception):
            serializer.validate_numero_documento('9999999999')
    
    def test_update_persona_success(self, test_persona, tipo_doc_cc, genero_m):
        """Test successful persona update."""
        serializer = PersonaActualizacionSerializer(
            test_persona,
            data={
                'primer_nombre': 'Updated',
                'telefono': '3001111111'
            },
            context={'persona': test_persona}
        )
        assert serializer.is_valid()
        
        updated_persona = serializer.update(test_persona, serializer.validated_data)
        assert updated_persona.primer_nombre == 'Updated'
        assert updated_persona.telefono == '3001111111'
    
    def test_update_tipo_documento(self, test_persona, tipo_doc_tema):
        """Test updating tipo_documento."""
        ce_param = Parametro.objects.create(
            tema=tipo_doc_tema,
            codigo='CE',
            nombre='Cédula de Extranjería',
            activo=True
        )
        
        serializer = PersonaActualizacionSerializer(
            test_persona,
            data={'tipo_documento': 'CE'},
            context={'persona': test_persona}
        )
        assert serializer.is_valid()
        
        updated_persona = serializer.update(test_persona, serializer.validated_data)
        assert updated_persona.tipo_documento == ce_param
    
    def test_validate_municipio_not_exists(self, test_persona):
        """Test validation error when municipio doesn't exist."""
        serializer = PersonaActualizacionSerializer(
            test_persona,
            data={'municipio': 99999},
            context={'persona': test_persona}
        )
        assert not serializer.is_valid()

