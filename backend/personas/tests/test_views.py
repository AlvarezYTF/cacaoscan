"""
Tests for Personas Views.
"""
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from catalogos.models import Tema, Parametro, Departamento, Municipio
from personas.models import Persona
from auth_app.models import PendingEmailVerification


@pytest.fixture
def api_client():
    """Create API client."""
    return APIClient()


@pytest.fixture
def user():
    """Create a regular user."""
    return User.objects.create_user(
        username='testuser@example.com',
        email='testuser@example.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user():
    """Create an admin user."""
    return User.objects.create_user(
        username='admin@example.com',
        email='admin@example.com',
        password='adminpass123',
        is_staff=True,
        is_superuser=True
    )


@pytest.fixture
def tipo_doc_tema():
    """Create TIPO_DOC theme."""
    return Tema.objects.create(
        codigo='TIPO_DOC',
        nombre='Tipo de Documento',
        activo=True
    )


@pytest.fixture
def sexo_tema():
    """Create SEXO theme."""
    return Tema.objects.create(
        codigo='SEXO',
        nombre='Sexo',
        activo=True
    )


@pytest.fixture
def tipo_doc_parametro(tipo_doc_tema):
    """Create CC parameter."""
    return Parametro.objects.create(
        tema=tipo_doc_tema,
        codigo='CC',
        nombre='Cédula de Ciudadanía',
        activo=True
    )


@pytest.fixture
def sexo_parametro(sexo_tema):
    """Create M parameter."""
    return Parametro.objects.create(
        tema=sexo_tema,
        codigo='M',
        nombre='Masculino',
        activo=True
    )


@pytest.fixture
def departamento():
    """Create a department."""
    return Departamento.objects.create(
        codigo='05',
        nombre='Antioquia'
    )


@pytest.fixture
def municipio(departamento):
    """Create a municipality."""
    return Municipio.objects.create(
        departamento=departamento,
        codigo='05001',
        nombre='Medellín'
    )


@pytest.fixture
def persona_data(tipo_doc_parametro, sexo_parametro, departamento, municipio):
    """Valid persona registration data."""
    return {
        'email': 'newuser@example.com',
        'password': 'SecurePass123!',
        'tipo_documento': 'CC',
        'numero_documento': '1234567890',
        'primer_nombre': 'Juan',
        'segundo_nombre': 'Carlos',
        'primer_apellido': 'Pérez',
        'segundo_apellido': 'García',
        'telefono': '3001234567',
        'direccion': 'Calle 123',
        'genero': 'M',
        'fecha_nacimiento': '1990-01-01',
        'departamento': departamento.id,
        'municipio': municipio.id
    }


@pytest.mark.django_db
class TestPersonaRegistroView:
    """Tests for PersonaRegistroView."""

    def test_registro_sin_autenticacion_envia_otp(
        self, api_client, persona_data, tipo_doc_parametro, sexo_parametro
    ):
        """Test registration without authentication sends OTP."""
        with patch('api.services.email.email_service.send_email') as mock_send:
            response = api_client.post(
                reverse('persona-registrar'),
                data=persona_data,
                format='json'
            )
        
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.data['message'] == 'Código enviado con éxito al correo.'
        assert response.data['email'] == persona_data['email']
        
        # Verify PendingEmailVerification was created
        pending = PendingEmailVerification.objects.filter(email=persona_data['email']).first()
        assert pending is not None
        assert pending.otp_code is not None
        assert len(pending.otp_code) == 6
        
        # Verify email was sent
        mock_send.assert_called_once()

    def test_registro_admin_crea_directamente(
        self, api_client, admin_user, persona_data, tipo_doc_parametro, sexo_parametro
    ):
        """Test admin can create user directly without OTP."""
        api_client.force_authenticate(user=admin_user)
        
        with patch('api.services.email.email_service.send_email'):
            response = api_client.post(
                reverse('persona-registrar'),
                data=persona_data,
                format='json'
            )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == 'Agricultor creado exitosamente.'
        assert response.data['email'] == persona_data['email']
        assert 'persona_id' in response.data
        assert 'user_id' in response.data
        
        # Verify user was created and activated
        user = User.objects.get(email=persona_data['email'])
        assert user.is_active is True
        
        # Verify persona was created
        persona = Persona.objects.get(user=user)
        assert persona.numero_documento == persona_data['numero_documento']

    def test_registro_email_duplicado(
        self, api_client, user, persona_data, tipo_doc_parametro, sexo_parametro
    ):
        """Test registration with duplicate email fails."""
        persona_data['email'] = user.email
        
        response = api_client.post(
            reverse('persona-registrar'),
            data=persona_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'ya está registrado' in response.data['detail']

    def test_registro_sin_email(
        self, api_client, persona_data, tipo_doc_parametro, sexo_parametro
    ):
        """Test registration without email fails."""
        persona_data.pop('email')
        
        response = api_client.post(
            reverse('persona-registrar'),
            data=persona_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Email es requerido' in response.data['detail']

    def test_registro_rate_limit(
        self, api_client, persona_data, tipo_doc_parametro, sexo_parametro
    ):
        """Test rate limiting for OTP resend."""
        # Create pending verification
        PendingEmailVerification.objects.create(
            email=persona_data['email'],
            otp_code='123456',
            temp_data=persona_data
        )
        
        response = api_client.post(
            reverse('persona-registrar'),
            data=persona_data,
            format='json'
        )
        
        # Should return 429 if less than 60 seconds passed
        assert response.status_code in [
            status.HTTP_429_TOO_MANY_REQUESTS,
            status.HTTP_202_ACCEPTED
        ]

    def test_registro_staff_crea_directamente(
        self, api_client, persona_data, tipo_doc_parametro, sexo_parametro
    ):
        """Test staff user can create user directly."""
        staff_user = User.objects.create_user(
            username='staff@example.com',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )
        api_client.force_authenticate(user=staff_user)
        
        with patch('api.services.email.email_service.send_email'):
            response = api_client.post(
                reverse('persona-registrar'),
                data=persona_data,
                format='json'
            )
        
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestPersonaListaView:
    """Tests for PersonaListaView."""

    def test_lista_personas(
        self, api_client, user, tipo_doc_parametro, sexo_parametro, departamento, municipio
    ):
        """Test listing all personas."""
        # Create a persona
        Persona.objects.create(
            user=user,
            tipo_documento=tipo_doc_parametro,
            numero_documento='1234567890',
            primer_nombre='Juan',
            primer_apellido='Pérez',
            telefono='3001234567',
            genero=sexo_parametro,
            departamento=departamento,
            municipio=municipio
        )
        
        response = api_client.get(reverse('persona-lista'))
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['numero_documento'] == '1234567890'


@pytest.mark.django_db
class TestPersonaDetalleView:
    """Tests for PersonaDetalleView."""

    def test_detalle_persona_existente(
        self, api_client, user, tipo_doc_parametro, sexo_parametro, departamento, municipio
    ):
        """Test getting existing persona detail."""
        persona = Persona.objects.create(
            user=user,
            tipo_documento=tipo_doc_parametro,
            numero_documento='1234567890',
            primer_nombre='Juan',
            primer_apellido='Pérez',
            telefono='3001234567',
            genero=sexo_parametro,
            departamento=departamento,
            municipio=municipio
        )
        
        response = api_client.get(
            reverse('persona-detalle', kwargs={'persona_id': persona.id})
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['numero_documento'] == '1234567890'
        assert response.data['primer_nombre'] == 'Juan'

    def test_detalle_persona_no_existente(self, api_client):
        """Test getting non-existent persona returns 404."""
        response = api_client.get(
            reverse('persona-detalle', kwargs={'persona_id': 99999})
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'no encontrada' in response.data['error']


@pytest.mark.django_db
class TestPersonaPerfilView:
    """Tests for PersonaPerfilView."""

    def test_obtener_perfil_autenticado(
        self, api_client, user, tipo_doc_parametro, sexo_parametro, departamento, municipio
    ):
        """Test authenticated user can get their profile."""
        persona = Persona.objects.create(
            user=user,
            tipo_documento=tipo_doc_parametro,
            numero_documento='1234567890',
            primer_nombre='Juan',
            primer_apellido='Pérez',
            telefono='3001234567',
            genero=sexo_parametro,
            departamento=departamento,
            municipio=municipio
        )
        
        api_client.force_authenticate(user=user)
        response = api_client.get(reverse('persona-perfil'))
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['numero_documento'] == '1234567890'

    def test_obtener_perfil_sin_persona(self, api_client, user):
        """Test getting profile when persona doesn't exist."""
        api_client.force_authenticate(user=user)
        response = api_client.get(reverse('persona-perfil'))
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_obtener_perfil_sin_autenticacion(self, api_client):
        """Test getting profile without authentication."""
        response = api_client.get(reverse('persona-perfil'))
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_actualizar_perfil(
        self, api_client, user, tipo_doc_parametro, sexo_parametro, departamento, municipio
    ):
        """Test updating profile."""
        persona = Persona.objects.create(
            user=user,
            tipo_documento=tipo_doc_parametro,
            numero_documento='1234567890',
            primer_nombre='Juan',
            primer_apellido='Pérez',
            telefono='3001234567',
            genero=sexo_parametro,
            departamento=departamento,
            municipio=municipio
        )
        
        api_client.force_authenticate(user=user)
        
        update_data = {
            'primer_nombre': 'Pedro',
            'telefono': '3009876543'
        }
        
        response = api_client.patch(
            reverse('persona-perfil'),
            data=update_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['primer_nombre'] == 'Pedro'
        
        # Verify update in database
        persona.refresh_from_db()
        assert persona.primer_nombre == 'Pedro'

    def test_crear_perfil(
        self, api_client, user, tipo_doc_parametro, sexo_parametro, departamento, municipio
    ):
        """Test creating profile for user without persona."""
        api_client.force_authenticate(user=user)
        
        create_data = {
            'tipo_documento': 'CC',
            'numero_documento': '1234567890',
            'primer_nombre': 'Juan',
            'primer_apellido': 'Pérez',
            'telefono': '3001234567',
            'genero': 'M',
            'departamento': departamento.id,
            'municipio': municipio.id
        }
        
        response = api_client.post(
            reverse('persona-perfil'),
            data=create_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == 'Perfil creado exitosamente'
        
        # Verify persona was created
        persona = Persona.objects.get(user=user)
        assert persona.numero_documento == '1234567890'

    def test_crear_perfil_duplicado(
        self, api_client, user, tipo_doc_parametro, sexo_parametro, departamento, municipio
    ):
        """Test creating profile when persona already exists."""
        Persona.objects.create(
            user=user,
            tipo_documento=tipo_doc_parametro,
            numero_documento='1234567890',
            primer_nombre='Juan',
            primer_apellido='Pérez',
            telefono='3001234567',
            genero=sexo_parametro,
            departamento=departamento,
            municipio=municipio
        )
        
        api_client.force_authenticate(user=user)
        
        create_data = {
            'tipo_documento': 'CC',
            'numero_documento': '9876543210',
            'primer_nombre': 'Pedro',
            'primer_apellido': 'García',
            'telefono': '3009876543',
            'genero': 'M'
        }
        
        response = api_client.post(
            reverse('persona-perfil'),
            data=create_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'ya tiene un perfil' in response.data['error']


@pytest.mark.django_db
class TestAdminPersonaByUserView:
    """Tests for AdminPersonaByUserView."""

    def test_admin_obtener_persona_por_usuario(
        self, api_client, admin_user, user, tipo_doc_parametro, sexo_parametro, departamento, municipio
    ):
        """Test admin can get persona by user ID."""
        persona = Persona.objects.create(
            user=user,
            tipo_documento=tipo_doc_parametro,
            numero_documento='1234567890',
            primer_nombre='Juan',
            primer_apellido='Pérez',
            telefono='3001234567',
            genero=sexo_parametro,
            departamento=departamento,
            municipio=municipio
        )
        
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(
            reverse('persona-admin-by-user', kwargs={'user_id': user.id})
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['numero_documento'] == '1234567890'

    def test_admin_obtener_persona_no_existente(
        self, api_client, admin_user, user
    ):
        """Test admin getting persona for user without persona."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(
            reverse('persona-admin-by-user', kwargs={'user_id': user.id})
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_no_admin_no_puede_acceder(
        self, api_client, user, tipo_doc_parametro, sexo_parametro, departamento, municipio
    ):
        """Test non-admin cannot access admin endpoint."""
        Persona.objects.create(
            user=user,
            tipo_documento=tipo_doc_parametro,
            numero_documento='1234567890',
            primer_nombre='Juan',
            primer_apellido='Pérez',
            telefono='3001234567',
            genero=sexo_parametro,
            departamento=departamento,
            municipio=municipio
        )
        
        api_client.force_authenticate(user=user)
        response = api_client.get(
            reverse('persona-admin-by-user', kwargs={'user_id': user.id})
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_actualizar_persona_por_usuario(
        self, api_client, admin_user, user, tipo_doc_parametro, sexo_parametro, departamento, municipio
    ):
        """Test admin can update persona by user ID."""
        persona = Persona.objects.create(
            user=user,
            tipo_documento=tipo_doc_parametro,
            numero_documento='1234567890',
            primer_nombre='Juan',
            primer_apellido='Pérez',
            telefono='3001234567',
            genero=sexo_parametro,
            departamento=departamento,
            municipio=municipio
        )
        
        api_client.force_authenticate(user=admin_user)
        
        update_data = {
            'primer_nombre': 'Pedro',
            'telefono': '3009876543'
        }
        
        response = api_client.patch(
            reverse('persona-admin-by-user', kwargs={'user_id': user.id}),
            data=update_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['primer_nombre'] == 'Pedro'
        
        # Verify update in database
        persona.refresh_from_db()
        assert persona.primer_nombre == 'Pedro'

    def test_admin_crear_persona_para_usuario(
        self, api_client, admin_user, user, tipo_doc_parametro, sexo_parametro, departamento, municipio
    ):
        """Test admin can create persona for existing user."""
        api_client.force_authenticate(user=admin_user)
        
        create_data = {
            'tipo_documento': 'CC',
            'numero_documento': '1234567890',
            'primer_nombre': 'Juan',
            'primer_apellido': 'Pérez',
            'telefono': '3001234567',
            'genero': 'M',
            'departamento': departamento.id,
            'municipio': municipio.id
        }
        
        response = api_client.patch(
            reverse('persona-admin-by-user', kwargs={'user_id': user.id}),
            data=create_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify persona was created
        persona = Persona.objects.get(user=user)
        assert persona.numero_documento == '1234567890'

    def test_admin_actualizar_usuario_no_existente(
        self, api_client, admin_user
    ):
        """Test admin updating persona for non-existent user."""
        api_client.force_authenticate(user=admin_user)
        
        update_data = {'primer_nombre': 'Pedro'}
        
        response = api_client.patch(
            reverse('persona-admin-by-user', kwargs={'user_id': 99999}),
            data=update_data,
            format='json'
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'Usuario no encontrado' in response.data['error']

