"""
CRUD views for Persona model.
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth.models import User

from api.views.mixins import AdminPermissionMixin, PaginationMixin
from api.serializers import ErrorResponseSerializer
from personas.models import Persona
from personas.serializers import (
    PersonaSerializer,
    PersonaActualizacionSerializer
)

logger = logging.getLogger("cacaoscan.personas")


class PersonaCreateView(AdminPermissionMixin, APIView):
    """
    Vista para crear una nueva persona.
    Solo administradores pueden crear personas directamente.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Crea una nueva persona (solo administradores)",
        operation_summary="Crear persona",
        request_body=PersonaActualizacionSerializer,
        responses={
            201: openapi.Response(
                description="Persona creada exitosamente",
                schema=PersonaSerializer
            ),
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
        tags=['Personas']
    )
    def post(self, request):
        """Crear nueva persona."""
        try:
            if not self.is_admin_user(request.user):
                return self.admin_permission_denied('No tienes permisos para crear personas')
            
            # Obtener user_id del request
            user_id = request.data.get('user_id')
            if not user_id:
                return Response({
                    'error': 'user_id es requerido',
                    'details': 'Debes proporcionar el ID del usuario para asociar la persona'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar que el usuario existe
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({
                    'error': 'Usuario no encontrado',
                    'details': f'El usuario con ID {user_id} no existe'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Verificar que el usuario no tenga ya una persona
            if Persona.objects.filter(user=user).exists():
                return Response({
                    'error': 'El usuario ya tiene una persona asociada',
                    'details': f'El usuario {user.username} ya tiene un perfil de persona'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear persona usando el serializer
            serializer = PersonaActualizacionSerializer(
                data=request.data,
                context={'persona': None}
            )
            
            if serializer.is_valid():
                validated_data = serializer.validated_data
                persona = self._create_persona_from_validated_data(user, validated_data)
                persona.save()
                
                logger.info(f"Persona {persona.id} creada por administrador {request.user.username} para usuario {user.id}")
                
                response_serializer = PersonaSerializer(persona)
                return Response(
                    {
                        'message': 'Persona creada exitosamente',
                        'data': response_serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                logger.error(f"Errores de validación al crear persona: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error creando persona: {str(e)}", exc_info=True)
            return Response({
                'error': 'Error interno del servidor',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _create_persona_from_validated_data(self, user, validated_data):
        """Create Persona instance from validated data."""
        persona = Persona(user=user)
        
        # Asignar catálogos
        if 'tipo_documento_obj' in validated_data:
            persona.tipo_documento = validated_data['tipo_documento_obj']
        if 'genero_obj' in validated_data:
            persona.genero = validated_data['genero_obj']
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


class PersonaUpdateView(AdminPermissionMixin, APIView):
    """
    Vista para actualizar una persona existente.
    Solo administradores pueden actualizar personas.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Actualiza una persona existente (solo administradores)",
        operation_summary="Actualizar persona",
        request_body=PersonaActualizacionSerializer,
        responses={
            200: openapi.Response(
                description="Persona actualizada exitosamente",
                schema=PersonaSerializer
            ),
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Personas']
    )
    def patch(self, request, persona_id):
        """Actualizar persona parcialmente."""
        try:
            if not self.is_admin_user(request.user):
                return self.admin_permission_denied('No tienes permisos para actualizar personas')
            
            try:
                persona = Persona.objects.select_related(
                    'tipo_documento__tema',
                    'genero__tema',
                    'municipio__departamento',
                    'municipio',
                    'user'
                ).get(id=persona_id)
            except Persona.DoesNotExist:
                return Response({
                    'error': 'Persona no encontrada',
                    'details': f'La persona con ID {persona_id} no existe'
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = PersonaActualizacionSerializer(
                instance=persona,
                data=request.data,
                partial=True,
                context={'persona': persona}
            )
            
            if serializer.is_valid():
                serializer.save()
                logger.info(f"Persona {persona.id} actualizada por administrador {request.user.username}")
                
                response_serializer = PersonaSerializer(persona)
                return Response(
                    {
                        'message': 'Persona actualizada exitosamente',
                        'data': response_serializer.data
                    },
                    status=status.HTTP_200_OK
                )
            else:
                logger.error(f"Errores de validación al actualizar persona: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error actualizando persona: {str(e)}", exc_info=True)
            return Response({
                'error': 'Error interno del servidor',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request, persona_id):
        """Actualizar persona completamente (usa PATCH internamente)."""
        return self.patch(request, persona_id)


class PersonaDeleteView(AdminPermissionMixin, APIView):
    """
    Vista para eliminar una persona.
    Solo administradores pueden eliminar personas.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Elimina una persona (solo administradores)",
        operation_summary="Eliminar persona",
        responses={
            204: openapi.Response(description="Persona eliminada exitosamente"),
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Personas']
    )
    def delete(self, request, persona_id):
        """Eliminar persona."""
        try:
            if not self.is_admin_user(request.user):
                return self.admin_permission_denied('No tienes permisos para eliminar personas')
            
            try:
                persona = Persona.objects.get(id=persona_id)
            except Persona.DoesNotExist:
                return Response({
                    'error': 'Persona no encontrada',
                    'details': f'La persona con ID {persona_id} no existe'
                }, status=status.HTTP_404_NOT_FOUND)
            
            persona_id_backup = persona.id
            persona.delete()
            
            logger.info(f"Persona {persona_id_backup} eliminada por administrador {request.user.username}")
            
            return Response(
                {'message': 'Persona eliminada exitosamente'},
                status=status.HTTP_204_NO_CONTENT
            )
                
        except Exception as e:
            logger.error(f"Error eliminando persona: {str(e)}", exc_info=True)
            return Response({
                'error': 'Error interno del servidor',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

