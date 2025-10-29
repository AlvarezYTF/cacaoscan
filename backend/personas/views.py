"""
Vistas para la app personas.

INTEGRACIÓN:
- Los catálogos están disponibles en /api/temas/ y /api/parametros/
- Las ubicaciones están disponibles en /api/departamentos/ y /api/municipios/
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from catalogos.models import Parametro, Departamento, Municipio
from .serializers import (
    PersonaRegistroSerializer, 
    PersonaSerializer,
    PersonaActualizacionSerializer
)
from .models import Persona


class PersonaRegistroView(APIView):
    """Vista para registrar usuario y persona en una sola petición."""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Crear usuario y persona.
        
        Requiere:
        - tipo_documento: Código del parámetro (ej: 'CC')
        - genero: Código del parámetro (ej: 'M')
        - departamento: ID del departamento (opcional)
        - municipio: ID del municipio (opcional)
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"📝 Datos recibidos en registro: {request.data}")
        
        serializer = PersonaRegistroSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                persona = serializer.save()
                logger.info(f"✅ Persona creada exitosamente: {persona.id}")
                return Response(
                    serializer.to_representation(persona),
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                logger.error(f"❌ Error al crear persona: {str(e)}")
                return Response(
                    {'error': f'Error al crear el usuario: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        logger.warning(f"⚠️ Errores de validación: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PersonaListaView(APIView):
    """Vista para listar todas las personas."""
    
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
        try:
            persona = Persona.objects.select_related(
                'tipo_documento__tema',
                'genero__tema',
                'departamento',
                'municipio',
                'user'
            ).get(user=request.user)
            serializer = PersonaSerializer(persona)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Persona.DoesNotExist:
            return Response(
                {'error': 'No se encontró información de perfil para este usuario'},
                status=status.HTTP_404_NOT_FOUND
            )
    
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
        
        logger.info(f"📝 Creando perfil de persona para usuario: {request.user.email}")
        
        # Crear persona usando el serializer de actualización
        serializer = PersonaActualizacionSerializer(
            data=request.data,
            context={'persona': None}
        )
        
        if serializer.is_valid():
            try:
                validated_data = serializer.validated_data
                
                # Crear la persona
                persona = Persona(user=request.user)
                
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
                
                persona.save()
                logger.info(f"✅ Perfil de persona creado exitosamente: {persona.id}")
                
                # Devolver los datos creados
                response_serializer = PersonaSerializer(persona)
                return Response(
                    {
                        'message': 'Perfil creado exitosamente',
                        'data': response_serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                logger.error(f"❌ Error al crear perfil: {str(e)}")
                return Response(
                    {'error': f'Error al crear el perfil: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        logger.warning(f"⚠️ Errores de validación: {serializer.errors}")
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
            
            logger.info(f"📝 Datos recibidos para actualización: {request.data}")
            
            serializer = PersonaActualizacionSerializer(
                instance=persona,
                data=request.data,
                partial=True,
                context={'persona': persona}
            )
            
            if serializer.is_valid():
                try:
                    serializer.save()
                    logger.info(f"✅ Perfil actualizado exitosamente: {persona.id}")
                    
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
                    logger.error(f"❌ Error al actualizar perfil: {str(e)}")
                    return Response(
                        {'error': f'Error al actualizar el perfil: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            logger.warning(f"⚠️ Errores de validación: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Persona.DoesNotExist:
            return Response(
                {'error': 'No se encontró información de perfil para este usuario. Usa POST para crear uno.'},
                status=status.HTTP_404_NOT_FOUND
            )