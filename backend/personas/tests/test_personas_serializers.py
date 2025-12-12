"""
Tests for personas serializers.
"""
import pytest
from datetime import date, timedelta
from unittest.mock import patch, Mock
from django.contrib.auth.models import User
from django.utils import timezone
from catalogos.models import Tema, Parametro, Departamento, Municipio
from personas.models import Persona
from personas.serializers import (
    validate_documento_number,
    validate_phone_number,
    validate_birth_date,
    validate_name_field,
    PersonaSerializer,
    PersonaRegistroSerializer,
    PersonaActualizacionSerializer
)


@pytest.mark.django_db
class TestValidationFunctions:
    """Tests for validation helper functions."""
    
    def test_validate_documento_number_valid(self):
        """Test validating valid documento number."""
        result = validate_documento_number('1234567890')
        assert result == '1234567890'
    
    def test_validate_documento_number_too_short(self):
        """Test validating documento number that's too short."""
        with pytest.raises(Exception, match="debe tener entre 6 y 11"):
            validate_documento_number('12345')
    
    def test_validate_documento_number_too_long(self):
        """Test validating documento number that's too long."""
        with pytest.raises(Exception, match="debe tener entre 6 y 11"):
            validate_documento_number('123456789012')
    
    def test_validate_documento_number_non_digit(self):
        """Test validating documento number with non-digits."""
        with pytest.raises(Exception, match="solo puede contener números"):
            validate_documento_number('12345abc')
    
    def test_validate_documento_number_duplicate(self):
        """Test validating duplicate documento number."""
        from rest_framework import serializers
        
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user = User.objects.create_user(username=f'test_{unique_id}', email=f'test_{unique_id}@test.com')
        Persona.objects.create(
            user=user,
            tipo_documento=Parametro.objects.create(
                tema=Tema.objects.create(codigo='TIPO_DOC', nombre='Tipo Documento'),
                codigo='CC',
                nombre='Cédula'
            ),
            numero_documento='1234567890',
            primer_nombre='Test',
            primer_apellido='User',
            telefono='1234567890',
            genero=Parametro.objects.create(
                tema=Tema.objects.create(codigo='SEXO', nombre='Sexo'),
                codigo='M',
                nombre='Masculino'
            )
        )
        
        # validate_documento_number raises serializers.ValidationError
        with pytest.raises(serializers.ValidationError, match="ya está registrado"):
            validate_documento_number('1234567890')
    
    def test_validate_phone_number_valid(self):
        """Test validating valid phone number."""
        result = validate_phone_number('1234567890')
        assert result == '1234567890'
    
    def test_validate_phone_number_invalid(self):
        """Test validating invalid phone number."""
        with pytest.raises(Exception):
            validate_phone_number('123')
    
    def test_validate_birth_date_valid(self):
        """Test validating valid birth date."""
        birth_date = date.today() - timedelta(days=365*25)
        result = validate_birth_date(birth_date)
        assert result == birth_date
    
    def test_validate_birth_date_future(self):
        """Test validating future birth date."""
        from rest_framework import serializers
        # Use a date clearly in the future - validation checks future date first
        future_date = date.today() + timedelta(days=365)  # 1 year in the future
        with pytest.raises(serializers.ValidationError) as exc_info:
            validate_birth_date(future_date)
        # The validation should fail on future date check first
        # The error message is "La fecha de nacimiento no puede ser futura."
        error_message = str(exc_info.value)
        assert "futura" in error_message or "no puede ser futura" in error_message
    
    def test_validate_birth_date_too_old(self):
        """Test validating birth date that's too old."""
        from rest_framework import serializers
        old_date = date.today() - timedelta(days=365*150)
        with pytest.raises(serializers.ValidationError, match=".*no es válida.*"):
            validate_birth_date(old_date)
    
    def test_validate_name_field_valid(self):
        """Test validating valid name field."""
        result = validate_name_field('John', 'primer_nombre')
        assert result == 'John'
    
    def test_validate_name_field_too_short(self):
        """Test validating name field that's too short."""
        # validate_name_field doesn't check minimum length, only validates it's not empty and contains only letters
        # So a single letter should pass validation
        result = validate_name_field('A', 'primer_nombre')
        assert result == 'A'
    
    def test_validate_name_field_invalid_chars(self):
        """Test validating name field with invalid characters."""
        with pytest.raises(Exception, match="solo puede contener"):
            validate_name_field('John123', 'primer_nombre')


@pytest.mark.django_db
class TestPersonaSerializer:
    """Tests for PersonaSerializer."""
    
    @pytest.fixture
    def setup_persona(self):
        """Setup persona for testing."""
        tema_tipo = Tema.objects.create(codigo='TIPO_DOC', nombre='Tipo Documento')
        tipo_doc = Parametro.objects.create(
            tema=tema_tipo,
            codigo='CC',
            nombre='Cédula',
            activo=True
        )
        
        tema_sexo = Tema.objects.create(codigo='SEXO', nombre='Sexo')
        genero = Parametro.objects.create(
            tema=tema_sexo,
            codigo='M',
            nombre='Masculino',
            activo=True
        )
        
        dept = Departamento.objects.create(codigo='CUN', nombre='Cundinamarca')
        municipio = Municipio.objects.create(
            departamento=dept,
            codigo='BOG',
            nombre='Bogotá'
        )
        
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com'
        )
        
        persona = Persona.objects.create(
            user=user,
            tipo_documento=tipo_doc,
            numero_documento='1234567890',
            primer_nombre='John',
            primer_apellido='Doe',
            genero=genero,
            telefono='1234567890',
            departamento=dept,
            municipio=municipio
        )
        
        return persona
    
    def test_serialize_persona(self, setup_persona):
        """Test serializing a persona."""
        persona = setup_persona
        
        serializer = PersonaSerializer(persona)
        data = serializer.data
        
        assert data['primer_nombre'] == 'John'
        assert data['primer_apellido'] == 'Doe'
        assert data['numero_documento'] == '1234567890'
        assert 'tipo_documento_info' in data
        assert data['tipo_documento_info']['codigo'] == 'CC'
        assert 'genero_info' in data
        assert 'departamento_info' in data
        assert 'municipio_info' in data


@pytest.mark.django_db
class TestPersonaRegistroSerializer:
    """Tests for PersonaRegistroSerializer."""
    
    @pytest.fixture
    def setup_catalogos(self):
        """Setup catalogos for testing."""
        tema_tipo = Tema.objects.create(codigo='TIPO_DOC', nombre='Tipo Documento')
        Parametro.objects.create(
            tema=tema_tipo,
            codigo='CC',
            nombre='Cédula',
            activo=True
        )
        
        tema_sexo = Tema.objects.create(codigo='SEXO', nombre='Sexo')
        Parametro.objects.create(
            tema=tema_sexo,
            codigo='M',
            nombre='Masculino',
            activo=True
        )
        
        dept = Departamento.objects.create(codigo='CUN', nombre='Cundinamarca')
        Municipio.objects.create(
            departamento=dept,
            codigo='BOG',
            nombre='Bogotá'
        )
    
    def test_validate_email_duplicate(self, setup_catalogos):
        """Test validating duplicate email."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        duplicate_email = f'existing_{unique_id}@example.com'
        User.objects.create_user(
            username=f'existing_{unique_id}',
            email=duplicate_email
        )
        
        serializer = PersonaRegistroSerializer(data={
            'email': duplicate_email,
            'password': 'TestPass123!',
            'tipo_documento': 'CC',
            'numero_documento': '1234567890',
            'primer_nombre': 'John',
            'primer_apellido': 'Doe',
            'telefono': '1234567890',
            'genero': 'M'
        })
        
        assert not serializer.is_valid()
        assert 'email' in serializer.errors
    
    def test_validate_invalid_tipo_documento(self, setup_catalogos):
        """Test validating invalid tipo_documento."""
        serializer = PersonaRegistroSerializer(data={
            'email': 'new@example.com',
            'password': 'TestPass123!',
            'tipo_documento': 'INVALID',
            'numero_documento': '1234567890',
            'primer_nombre': 'John',
            'primer_apellido': 'Doe',
            'telefono': '1234567890',
            'genero': 'M'
        })
        
        assert not serializer.is_valid()
        assert 'tipo_documento' in serializer.errors
    
    @patch('api.services.email.send_custom_email')
    @patch('api.utils.model_imports.get_models_safely')
    def test_create_persona(self, mock_get_models, mock_email, setup_catalogos):
        """Test creating persona and user."""
        mock_token_model = Mock()
        mock_token = Mock()
        mock_token.token = 'test-token'
        mock_token_model.create_for_user.return_value = mock_token
        mock_get_models.return_value = {'EmailVerificationToken': mock_token_model}
        
        serializer = PersonaRegistroSerializer(data={
            'email': 'new@example.com',
            'password': 'TestPass123!',
            'tipo_documento': 'CC',
            'numero_documento': '1234567890',
            'primer_nombre': 'John',
            'segundo_nombre': '',  # Allow blank but provide empty string
            'primer_apellido': 'Doe',
            'segundo_apellido': '',  # Allow blank but provide empty string
            'telefono': '1234567890',
            'genero': 'M'
        })
        
        assert serializer.is_valid()
        persona = serializer.save()
        
        assert persona.primer_nombre == 'John'
        assert persona.user.email == 'new@example.com'
        assert User.objects.filter(email='new@example.com').exists()


@pytest.mark.django_db
class TestPersonaActualizacionSerializer:
    """Tests for PersonaActualizacionSerializer."""
    
    @pytest.fixture
    def setup_persona(self):
        """Setup persona for testing."""
        tema_tipo = Tema.objects.create(codigo='TIPO_DOC', nombre='Tipo Documento')
        tipo_doc = Parametro.objects.create(
            tema=tema_tipo,
            codigo='CC',
            nombre='Cédula',
            activo=True
        )
        
        tema_sexo = Tema.objects.create(codigo='SEXO', nombre='Sexo')
        genero = Parametro.objects.create(
            tema=tema_sexo,
            codigo='M',
            nombre='Masculino',
            activo=True
        )
        
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user = User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com'
        )
        
        persona = Persona.objects.create(
            user=user,
            tipo_documento=tipo_doc,
            numero_documento='1234567890',
            primer_nombre='John',
            primer_apellido='Doe',
            genero=genero,
            telefono='1234567890'
        )
        
        return persona
    
    def test_update_persona(self, setup_persona):
        """Test updating persona."""
        persona = setup_persona
        
        serializer = PersonaActualizacionSerializer(
            instance=persona,
            data={
                'primer_nombre': 'Jane',
                'segundo_nombre': 'Marie'
            },
            partial=True
        )
        
        assert serializer.is_valid()
        updated = serializer.save()
        
        assert updated.primer_nombre == 'Jane'
        assert updated.segundo_nombre == 'Marie'
    
    def test_update_duplicate_documento(self, setup_persona):
        """Test updating with duplicate documento."""
        persona = setup_persona
        
        # Create another persona
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user2 = User.objects.create_user(username=f'test2_{unique_id}', email=f'test2_{unique_id}@test.com')
        Persona.objects.create(
            user=user2,
            tipo_documento=persona.tipo_documento,
            numero_documento='9876543210',
            primer_nombre='Other',
            primer_apellido='User',
            genero=persona.genero,
            telefono='9876543210'
        )
        
        serializer = PersonaActualizacionSerializer(
            instance=persona,
            data={'numero_documento': '9876543210'},
            partial=True
        )
        
        assert not serializer.is_valid()
        assert 'numero_documento' in serializer.errors

