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
        """Dispara envío de OTP guardando el formulario en temp_data sin reenviar la request."""
        try:
            email = request.data.get('email')
            if not email:
                return Response({'detail': 'Email es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

            # Prevenir si ya existe usuario
            from django.contrib.auth import get_user_model
            User = get_user_model()
            if User.objects.filter(email=email).exists():
                return Response({'detail': 'El email ya está registrado.'}, status=status.HTTP_400_BAD_REQUEST)

            # Si el usuario es admin, crear directamente sin verificación
            if self._is_admin(request.user):
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Admin {request.user.username} creando usuario: {email}")

                # Validar y crear usando el serializer
                serializer = PersonaRegistroSerializer(
                    data=request.data,
                    context={'skip_email_verification': True}
                )
                if not serializer.is_valid():
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                # Crear usuario y persona directamente (sin verificación de email)
                # El serializer ya maneja la activación y verificación cuando skip_email_verification=True
                persona = serializer.save()

                logger.info(f"Usuario {email} creado exitosamente por admin {request.user.username}")

                return Response({
                    'message': 'Agricultor creado exitosamente.',
                    'email': email,
                    'persona_id': persona.id,
                    'user_id': persona.user.id
                }, status=status.HTTP_201_CREATED)

            # Si no es admin, seguir flujo OTP normal
            # Rate limit y creación/actualización del pending
            from auth_app.models import PendingEmailVerification
            existing = PendingEmailVerification.objects.filter(email=email).first()
            if existing:
                elapsed = (timezone.now() - existing.last_sent).total_seconds()
                if elapsed < 60:
                    return Response({
                        'detail': f'Espera {int(60 - elapsed)} segundos antes de reenviar el código.'
                    }, status=status.HTTP_429_TOO_MANY_REQUESTS)

            code = PendingEmailVerification.generate_code()
            PendingEmailVerification.objects.update_or_create(
                email=email,
                defaults={'otp_code': code, 'temp_data': request.data}
            )

            # Enviar email con servicio centralizado
            from api.services.email import email_service
            email_service.send_email(
                to_emails=[email],
                subject='Verificación de cuenta CacaoScan',
                html_content=f"""
                <html>
                <body style=\"font-family: Arial, sans-serif; line-height: 1.6; color: #333;\">
                    <div style=\"max-width: 600px; margin: 0 auto; padding: 20px;\">
                        <h2 style=\"color: #22c55e;\">Verificación de cuenta CacaoScan</h2>
                        <p>Hola ',</p>
                        <p>Tu código de verificación es:</p>
                        <div style=\"background-color: #f3f4f6; border: 2px solid #22c55e; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0;\">
                            <h1 style=\"color: #22c55e; font-size: 32px; margin: 0; letter-spacing: 5px;\">{code}</h1>
                        </div>
                        <p>Este código expirará en <strong>10 minutos</strong>.</p>
                        <p style=\"color: #6b7280; font-size: 14px;\">Si no solicitaste este código, puedes ignorar este email.</p>
                        <hr style=\"border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;\">
                        <p style=\"color: #6b7280; font-size: 12px;\">é {timezone.now().year} CacaoScan - Sistema de análisis de cacao</p>
                    </div>
                </body>
                </html>
                """,
                text_content=f"Hola, tu código de verificación es: {code}. Este código expirará en 10 minutos."
            )

            return Response({'message': 'Código enviado con éxito al correo.', 'email': email}, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error en registro: {str(e)}", exc_info=True)
            return Response({'detail': f'Error procesando registro: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
                logger.info(f"[OK] Perfil de persona creado exitosamente: {persona.id}")
                
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

