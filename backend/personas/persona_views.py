"""
Vistas para la app personas.

INTEGRACI"N:
- Los catálogos están disponibles en /api/temas/ y /api/parametros/
- Las ubicaciones están disponibles en /api/departamentos/ y /api/municipios/
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.utils import timezone
from catalogos.models import Parametro, Departamento, Municipio
from .serializers import (
    PersonaRegistroSerializer, 
    PersonaSerializer,
    PersonaActualizacionSerializer
)
from .models import Persona

# Import CRUD views
from .views.crud_views import (
    PersonaCreateView,
    PersonaUpdateView,
    PersonaDeleteView
)


class PersonaRegistroView(APIView):
    """
    Endpoint para registro de usuario y persona.
    - Si el usuario está autenticado y es admin/staff: crea el usuario directamente sin verificación
    - Si no está autenticado o no es admin: inicia flujo de verificación por OTP
    """
    permission_classes = [AllowAny]

    def _is_admin(self, user):
        """Verificar si el usuario es administrador."""
        if not user or not user.is_authenticated:
            return False
        return user.is_superuser or user.is_staff

    def post(self, request):
        """Crea usuario y persona directamente sin verificación de email, generando tokens JWT."""
        try:
            email = request.data.get('email')
            if not email:
                return Response({'detail': 'Email es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

            # Prevenir si ya existe usuario
            from django.contrib.auth import get_user_model
            user_model = get_user_model()
            if user_model.objects.filter(email=email).exists():
                return Response({'detail': 'El email ya está registrado.'}, status=status.HTTP_400_BAD_REQUEST)

            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Creando usuario sin verificación de email: {email}")

            # Validar y crear usando el serializer con skip_email_verification=True
            serializer = PersonaRegistroSerializer(
                data=request.data,
                context={'skip_email_verification': True}
            )
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Crear usuario y persona directamente (sin verificación de email)
            persona = serializer.save()

            # Asegurar que el rol farmer esté asignado (el signal debería hacerlo, pero lo verificamos)
            from django.contrib.auth.models import Group
            user = persona.user
            user.refresh_from_db()  # Refrescar para obtener los grupos asignados por el signal
            
            # Verificar si tiene el rol farmer, si no, asignarlo explícitamente
            farmer_group, _ = Group.objects.get_or_create(name="farmer")
            if not user.groups.filter(name="farmer").exists():
                user.groups.add(farmer_group)
                user.refresh_from_db()  # Refrescar nuevamente para cargar el grupo
                logger.info(f"Rol 'farmer' asignado explícitamente a usuario {email}")
            
            # Obtener el rol del usuario usando la misma lógica que UserSerializer
            if user.is_superuser or user.is_staff:
                user_role = 'admin'
            elif user.groups.filter(name="analyst").exists():
                user_role = 'analyst'
            else:
                user_role = 'farmer'  # Por defecto para usuarios nuevos

            # Generar tokens JWT para login automático
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            logger.info(f"Usuario {email} creado exitosamente con tokens JWT y rol {user_role}")

            return Response({
                'success': True,
                'message': 'Usuario registrado exitosamente.',
                'email': email,
                'persona_id': persona.id,
                'user_id': user.id,
                'access': str(access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_active': user.is_active,
                    'role': user_role
                },
                'verification_required': False
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error en registro: {str(e)}", exc_info=True)
            return Response({'detail': f'Error procesando registro: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PersonaListaView(APIView):
    """Vista para listar todas las personas."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Listar todas las personas."""
        personas = Persona.objects.select_related(
            'tipo_documento__tema',
            'genero__tema',
            'departamento',
            'municipio'
        ).all()
        serializer = PersonaSerializer(personas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PersonaDetalleView(APIView):
    """Vista para obtener, actualizar o eliminar una persona específica."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, persona_id):
        """Obtener una persona específica."""
        try:
            persona = Persona.objects.select_related(
                'tipo_documento__tema',
                'genero__tema',
                'departamento',
                'municipio'
            ).get(id=persona_id)
            serializer = PersonaSerializer(persona)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Persona.DoesNotExist:
            return Response(
                {'error': 'Persona no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )


class PersonaPerfilView(APIView):
    """
    Vista para obtener y actualizar los datos del perfil del usuario autenticado.
    El email no se puede modificar desde aquí.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Obtener los datos de la persona del usuario autenticado."""
        user = request.user
        
        # 🔥 FIX 1: Garantizar que UserProfile exista para evitar errores 500
        from auth_app.models import UserProfile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'login_provider': 'local'}
        )
        
        # 🔥 FIX 2: login_provider SIEMPRE debe venir del perfil
        login_provider = getattr(profile, 'login_provider', 'local')
        
        # 🔥 FIX 3: password_allowed = false si es Google
        password_allowed = (login_provider != 'google')
        
        try:
            # 🔥 FIX: departamento NO es una relación directa, es una propiedad
            # Usar municipio__departamento para optimizar la consulta
            persona = Persona.objects.select_related(
                'tipo_documento__tema',
                'genero__tema',
                'municipio__departamento',  # Corregido: departamento viene de municipio
                'user'
            ).get(user=user)
            
            # Serializar persona con contexto para incluir login_provider
            serializer = PersonaSerializer(persona, context={'user': user})
            data = serializer.data
            
            # 🔥 FIX 4: SIEMPRE insertar flags en la respuesta (nivel superior)
            data['login_provider'] = login_provider
            data['password_allowed'] = password_allowed
            
            # También incluir has_password
            data['has_password'] = user.has_usable_password()
            
            return Response(data, status=status.HTTP_200_OK)
        except Persona.DoesNotExist:
            # Si no existe Persona, devolver solo datos de usuario con flags
            from api.serializers import UserSerializer
            user_data = UserSerializer(user).data
            
            return Response({
                'error': 'No se encontró información de perfil de persona para este usuario',
                'login_provider': login_provider,
                'password_allowed': password_allowed,
                'has_password': user.has_usable_password(),
                'user': user_data
            }, status=status.HTTP_200_OK)  # Cambiado a 200 para que el frontend no entre en catch
        except Exception as e:
            # 🔥 FIX: Capturar cualquier otro error y devolver respuesta controlada
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error en PersonaPerfilView.get(): {str(e)}", exc_info=True)
            
            # Devolver datos del usuario con flags aunque haya error
            from api.serializers import UserSerializer
            user_data = UserSerializer(user).data
            
            return Response({
                'error': 'Error al obtener perfil de persona',
                'login_provider': login_provider,
                'password_allowed': password_allowed,
                'has_password': user.has_usable_password(),
                'user': user_data
            }, status=status.HTTP_200_OK)  # 200 para que el frontend no entre en catch
    
    def post(self, request):
        """
        Crear perfil de persona para un usuario existente.
        Útil para usuarios creados antes de la implementación del módulo de personas.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Verificar si ya existe persona para este usuario
        if Persona.objects.filter(user=request.user).exists():
            return Response(
                {'error': 'Este usuario ya tiene un perfil de persona. Usa PATCH para actualizar.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logger.info(f"[INFO] Creando perfil de persona para usuario: {request.user.email}")
        
        # Crear persona usando el serializer de actualización
        serializer = PersonaActualizacionSerializer(
            data=request.data,
            context={'persona': None}
        )
        
        if serializer.is_valid():
            try:
                validated_data = serializer.validated_data
                persona = self._create_persona_from_validated_data(request.user, validated_data)
                persona.save()
                
                logger.info(f"[OK] Perfil de persona creado exitosamente: {persona.id}")
                
                response_serializer = PersonaSerializer(persona)
                return Response(
                    {
                        'message': 'Perfil creado exitosamente',
                        'data': response_serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                logger.error(f"[ERROR] Error al crear perfil: {str(e)}")
                return Response(
                    {'error': f'Error al crear el perfil: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        logger.warning(f"[WARN] Errores de validacin: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        """
        Actualizar parcialmente los datos de la persona del usuario autenticado.
        No permite modificar el email.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            persona = Persona.objects.select_related(
                'tipo_documento__tema',
                'genero__tema',
                'departamento',
                'municipio',
                'user'
            ).get(user=request.user)
            
            logger.info(f"[INFO] Datos recibidos para actualizacin: {request.data}")
            
            serializer = PersonaActualizacionSerializer(
                instance=persona,
                data=request.data,
                partial=True,
                context={'persona': persona}
            )
            
            if serializer.is_valid():
                try:
                    serializer.save()
                    logger.info(f"[OK] Perfil actualizado exitosamente: {persona.id}")
                    
                    # Devolver los datos actualizados
                    response_serializer = PersonaSerializer(persona)
                    return Response(
                        {
                            'message': 'Perfil actualizado exitosamente',
                            'data': response_serializer.data
                        },
                        status=status.HTTP_200_OK
                    )
                except Exception as e:
                    logger.error(f"[ERROR] Error al actualizar perfil: {str(e)}")
                    return Response(
                        {'error': f'Error al actualizar el perfil: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            logger.warning(f"[WARN] Errores de validacin: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Persona.DoesNotExist:
            return Response(
                {'error': 'No se encontró información de perfil para este usuario. Usa POST para crear uno.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _create_persona_from_validated_data(self, user, validated_data):
        """Create Persona instance from validated data."""
        persona = Persona(user=user)
        
        # Asignar catálogos
        if 'tipo_documento_obj' in validated_data:
            persona.tipo_documento = validated_data['tipo_documento_obj']
        if 'genero_obj' in validated_data:
            persona.genero = validated_data['genero_obj']
        if 'departamento_obj' in validated_data:
            persona.departamento = validated_data['departamento_obj']
        if 'municipio_obj' in validated_data:
            persona.municipio = validated_data['municipio_obj']
        
        # Asignar campos simples
        simple_fields = [
            'numero_documento', 'primer_nombre', 'segundo_nombre',
            'primer_apellido', 'segundo_apellido', 'telefono',
            'direccion', 'fecha_nacimiento'
        ]
        
        for field in simple_fields:
            if field in validated_data:
                setattr(persona, field, validated_data[field])
        
        return persona


class AdminPersonaByUserView(APIView):
    """Permite a un administrador obtener/crear/actualizar la persona de un usuario específico."""
    permission_classes = [IsAuthenticated]

    def _is_admin(self, user):
        return user.is_superuser or user.is_staff

    def get(self, request, user_id):
        if not self._is_admin(request.user):
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)

        persona = Persona.objects.select_related(
            'tipo_documento__tema', 'genero__tema', 'departamento', 'municipio', 'user'
        ).filter(user_id=user_id).first()
        if not persona:
            return Response({'error': 'Persona no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        return Response(PersonaSerializer(persona).data, status=status.HTTP_200_OK)

    def patch(self, request, user_id):
        if not self._is_admin(request.user):
            return Response({'error': 'No autorizado'}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        persona = Persona.objects.filter(user=user).first()

        serializer = PersonaActualizacionSerializer(
            instance=persona,
            data=request.data,
            partial=True,
            context={'persona': persona}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if persona is None:
            # Crear persona si no existe
            persona = Persona(user=user)
        serializer.instance = persona
        serializer.save()

        return Response(PersonaSerializer(persona).data, status=status.HTTP_200_OK)

