"""
Unit tests for personas serializers.
"""
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date

from rest_framework import serializers
from personas.serializers import (
    PersonaSerializer,
    PersonaRegistroSerializer,
    PersonaActualizacionSerializer
)
from catalogos.models import Parametro, Tema, Departamento, Municipio
from personas.models import Persona
from api.tests.test_constants import (
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
    TEST_USER_PASSWORD,
    TEST_WEAK_PASSWORD,
)


class PersonaSerializerTest(TestCase):
    """Tests for PersonaSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        
        # Create catalog data
        self.tema_tipo_doc = Tema.objects.create(codigo='TIPO_DOC', nombre='Tipo de Documento')
        self.tema_sexo = Tema.objects.create(codigo='SEXO', nombre='Sexo')
        
        self.tipo_doc_cc = Parametro.objects.create(
            codigo='CC',
            nombre='Cédula de Ciudadanía',
            tema=self.tema_tipo_doc,
            activo=True
        )
        
        self.genero_m = Parametro.objects.create(
            codigo='M',
            nombre='Masculino',
            tema=self.tema_sexo,
            activo=True
        )
        
        self.departamento = Departamento.objects.create(
            codigo='11',
            nombre='Cundinamarca'
        )
        
        self.municipio = Municipio.objects.create(
            codigo='11001',
            nombre='Bogotá',
            departamento=self.departamento
        )
        
        self.persona = Persona.objects.create(
            user=self.user,
            tipo_documento=self.tipo_doc_cc,
            numero_documento='1234567890',
            primer_nombre='Test',
            primer_apellido='User',
            telefono='1234567890',
            genero=self.genero_m,
            departamento=self.departamento,
            municipio=self.municipio
        )
    
    def test_persona_serialization_success(self):
        """Test successful persona serialization."""
        serializer = PersonaSerializer(self.persona)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('user', data)
        self.assertIn('email', data)
        self.assertIn('tipo_documento_info', data)
        self.assertIn('genero_info', data)
        self.assertIn('departamento_info', data)
        self.assertIn('municipio_info', data)
        self.assertEqual(data['email'], TEST_USER_EMAIL)
    
    def test_persona_serialization_without_catalogs(self):
        """Test persona serialization without catalog references."""
        persona = Persona.objects.create(
            user=User.objects.create_user(
                username='test2',
                email='test2@example.com',
                password=TEST_USER_PASSWORD
            ),
            numero_documento='0987654321',
            primer_nombre='Test',
            primer_apellido='User2',
            telefono='0987654321'
        )
        
        serializer = PersonaSerializer(persona)
        data = serializer.data
        
        self.assertIsNone(data['tipo_documento_info'])
        self.assertIsNone(data['genero_info'])


class PersonaRegistroSerializerTest(TestCase):
    """Tests for PersonaRegistroSerializer."""
    
    def setUp(self):
        """Set up test data."""
        # Create catalog data
        self.tema_tipo_doc = Tema.objects.create(codigo='TIPO_DOC', nombre='Tipo de Documento')
        self.tema_sexo = Tema.objects.create(codigo='SEXO', nombre='Sexo')
        
        self.tipo_doc_cc = Parametro.objects.create(
            codigo='CC',
            nombre='Cédula de Ciudadanía',
            tema=self.tema_tipo_doc,
            activo=True
        )
        
        self.genero_m = Parametro.objects.create(
            codigo='M',
            nombre='Masculino',
            tema=self.tema_sexo,
            activo=True
        )
        
        self.departamento = Departamento.objects.create(
            codigo='11',
            nombre='Cundinamarca'
        )
        
        self.municipio = Municipio.objects.create(
            codigo='11001',
            nombre='Bogotá',
            departamento=self.departamento
        )
    
    def test_persona_registro_success(self):
        """Test successful persona registration."""
        serializer = PersonaRegistroSerializer(data={
            'email': 'newuser@example.com',
            'password': TEST_USER_PASSWORD,
            'tipo_documento': 'CC',
            'numero_documento': '1234567890',
            'primer_nombre': 'New',
            'primer_apellido': 'User',
            'telefono': '1234567890',
            'genero': 'M',
            'departamento': self.departamento.id,
            'municipio': self.municipio.id
        })
        self.assertTrue(serializer.is_valid())
    
    def test_persona_registro_duplicate_email(self):
        """Test persona registration with duplicate email."""
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password=TEST_USER_PASSWORD
        )
        
        serializer = PersonaRegistroSerializer(data={
            'email': 'existing@example.com',
            'password': TEST_USER_PASSWORD,
            'tipo_documento': 'CC',
            'numero_documento': '1234567890',
            'primer_nombre': 'New',
            'primer_apellido': 'User',
            'telefono': '1234567890',
            'genero': 'M'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_persona_registro_invalid_email_format(self):
        """Test persona registration with invalid email format."""
        serializer = PersonaRegistroSerializer(data={
            'email': 'invalid-email',
            'password': TEST_USER_PASSWORD,
            'tipo_documento': 'CC',
            'numero_documento': '1234567890',
            'primer_nombre': 'New',
            'primer_apellido': 'User',
            'telefono': '1234567890',
            'genero': 'M'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    def test_persona_registro_weak_password(self):
        """Test persona registration with weak password."""
        serializer = PersonaRegistroSerializer(data={
            'email': 'newuser@example.com',
            'password': TEST_WEAK_PASSWORD,
            'tipo_documento': 'CC',
            'numero_documento': '1234567890',
            'primer_nombre': 'New',
            'primer_apellido': 'User',
            'telefono': '1234567890',
            'genero': 'M'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
    
    def test_persona_registro_invalid_document_number(self):
        """Test persona registration with invalid document number."""
        serializer = PersonaRegistroSerializer(data={
            'email': 'newuser@example.com',
            'password': TEST_USER_PASSWORD,
            'tipo_documento': 'CC',
            'numero_documento': '12345',  # Too short
            'primer_nombre': 'New',
            'primer_apellido': 'User',
            'telefono': '1234567890',
            'genero': 'M'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('numero_documento', serializer.errors)
    
    def test_persona_registro_invalid_phone(self):
        """Test persona registration with invalid phone."""
        serializer = PersonaRegistroSerializer(data={
            'email': 'newuser@example.com',
            'password': TEST_USER_PASSWORD,
            'tipo_documento': 'CC',
            'numero_documento': '1234567890',
            'primer_nombre': 'New',
            'primer_apellido': 'User',
            'telefono': '123',  # Too short
            'genero': 'M'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('telefono', serializer.errors)
    
    def test_persona_registro_invalid_tipo_documento(self):
        """Test persona registration with invalid tipo_documento."""
        serializer = PersonaRegistroSerializer(data={
            'email': 'newuser@example.com',
            'password': TEST_USER_PASSWORD,
            'tipo_documento': 'INVALID',
            'numero_documento': '1234567890',
            'primer_nombre': 'New',
            'primer_apellido': 'User',
            'telefono': '1234567890',
            'genero': 'M'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('tipo_documento', serializer.errors)
    
    def test_persona_registro_invalid_genero(self):
        """Test persona registration with invalid genero."""
        serializer = PersonaRegistroSerializer(data={
            'email': 'newuser@example.com',
            'password': TEST_USER_PASSWORD,
            'tipo_documento': 'CC',
            'numero_documento': '1234567890',
            'primer_nombre': 'New',
            'primer_apellido': 'User',
            'telefono': '1234567890',
            'genero': 'INVALID'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('genero', serializer.errors)
    
    def test_persona_registro_invalid_birth_date(self):
        """Test persona registration with invalid birth date."""
        serializer = PersonaRegistroSerializer(data={
            'email': 'newuser@example.com',
            'password': TEST_USER_PASSWORD,
            'tipo_documento': 'CC',
            'numero_documento': '1234567890',
            'primer_nombre': 'New',
            'primer_apellido': 'User',
            'telefono': '1234567890',
            'genero': 'M',
            'fecha_nacimiento': date(2030, 1, 1)  # Future date
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('fecha_nacimiento', serializer.errors)
    
    def test_persona_registro_invalid_name_characters(self):
        """Test persona registration with invalid name characters."""
        serializer = PersonaRegistroSerializer(data={
            'email': 'newuser@example.com',
            'password': TEST_USER_PASSWORD,
            'tipo_documento': 'CC',
            'numero_documento': '1234567890',
            'primer_nombre': 'New123',  # Contains numbers
            'primer_apellido': 'User',
            'telefono': '1234567890',
            'genero': 'M'
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn('primer_nombre', serializer.errors)
    
    @patch('personas.serializers.send_custom_email')
    def test_persona_registro_creates_user_and_persona(self, mock_send_email):
        """Test that persona registration creates both user and persona."""
        serializer = PersonaRegistroSerializer(data={
            'email': 'newuser@example.com',
            'password': TEST_USER_PASSWORD,
            'tipo_documento': 'CC',
            'numero_documento': '1234567890',
            'primer_nombre': 'New',
            'primer_apellido': 'User',
            'telefono': '1234567890',
            'genero': 'M',
            'departamento': self.departamento.id,
            'municipio': self.municipio.id
        })
        self.assertTrue(serializer.is_valid())
        
        persona = serializer.save()
        
        self.assertIsNotNone(persona)
        self.assertIsNotNone(persona.user)
        self.assertEqual(persona.user.email, 'newuser@example.com')
        self.assertEqual(persona.numero_documento, '1234567890')


class PersonaActualizacionSerializerTest(TestCase):
    """Tests for PersonaActualizacionSerializer."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD
        )
        
        # Create catalog data
        self.tema_tipo_doc = Tema.objects.create(codigo='TIPO_DOC', nombre='Tipo de Documento')
        self.tema_sexo = Tema.objects.create(codigo='SEXO', nombre='Sexo')
        
        self.tipo_doc_cc = Parametro.objects.create(
            codigo='CC',
            nombre='Cédula de Ciudadanía',
            tema=self.tema_tipo_doc,
            activo=True
        )
        
        self.genero_m = Parametro.objects.create(
            codigo='M',
            nombre='Masculino',
            tema=self.tema_sexo,
            activo=True
        )
        
        self.departamento = Departamento.objects.create(
            codigo='11',
            nombre='Cundinamarca'
        )
        
        self.municipio = Municipio.objects.create(
            codigo='11001',
            nombre='Bogotá',
            departamento=self.departamento
        )
        
        self.persona = Persona.objects.create(
            user=self.user,
            tipo_documento=self.tipo_doc_cc,
            numero_documento='1234567890',
            primer_nombre='Test',
            primer_apellido='User',
            telefono='1234567890',
            genero=self.genero_m
        )
    
    def test_persona_actualizacion_success(self):
        """Test successful persona update."""
        serializer = PersonaActualizacionSerializer(
            data={
                'primer_nombre': 'Updated',
                'telefono': '9876543210'
            },
            context={'persona': self.persona}
        )
        self.assertTrue(serializer.is_valid())
        
        updated_persona = serializer.update(self.persona, serializer.validated_data)
        
        self.assertEqual(updated_persona.primer_nombre, 'Updated')
        self.assertEqual(updated_persona.telefono, '9876543210')
    
    def test_persona_actualizacion_duplicate_document(self):
        """Test persona update with duplicate document number."""
        other_persona = Persona.objects.create(
            user=User.objects.create_user(
                username='other',
                email='other@example.com',
                password=TEST_USER_PASSWORD
            ),
            tipo_documento=self.tipo_doc_cc,
            numero_documento='0987654321',
            primer_nombre='Other',
            primer_apellido='User',
            telefono='0987654321'
        )
        
        serializer = PersonaActualizacionSerializer(
            data={
                'numero_documento': '0987654321'
            },
            context={'persona': self.persona}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('numero_documento', serializer.errors)
    
    def test_persona_actualizacion_duplicate_phone(self):
        """Test persona update with duplicate phone."""
        other_persona = Persona.objects.create(
            user=User.objects.create_user(
                username='other',
                email='other@example.com',
                password=TEST_USER_PASSWORD
            ),
            tipo_documento=self.tipo_doc_cc,
            numero_documento='0987654321',
            primer_nombre='Other',
            primer_apellido='User',
            telefono='0987654321'
        )
        
        serializer = PersonaActualizacionSerializer(
            data={
                'telefono': '0987654321'
            },
            context={'persona': self.persona}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('telefono', serializer.errors)
    
    def test_persona_actualizacion_invalid_tipo_documento(self):
        """Test persona update with invalid tipo_documento."""
        serializer = PersonaActualizacionSerializer(
            data={
                'tipo_documento': 'INVALID'
            },
            context={'persona': self.persona}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('tipo_documento', serializer.errors)
    
    def test_persona_actualizacion_invalid_genero(self):
        """Test persona update with invalid genero."""
        serializer = PersonaActualizacionSerializer(
            data={
                'genero': 'INVALID'
            },
            context={'persona': self.persona}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('genero', serializer.errors)
    
    def test_persona_actualizacion_invalid_municipio(self):
        """Test persona update with invalid municipio."""
        serializer = PersonaActualizacionSerializer(
            data={
                'municipio': 99999  # Non-existent
            },
            context={'persona': self.persona}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('municipio', serializer.errors)

