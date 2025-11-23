"""
Vistas para gestión de emails en CacaoScan.
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.services.email import (
    email_service, 
    email_notification_service,
    send_email_notification,
    send_bulk_email_notification,
    send_custom_email
)
from core.utils import create_success_response, create_error_response
from api.serializers import ErrorResponseSerializer

logger = logging.getLogger("cacaoscan.email")


class EmailStatusView(APIView):
    """
    Endpoint para consultar el estado del sistema de emails.
    """
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="Obtiene el estado actual del sistema de emails",
        operation_summary="Estado del sistema de emails",
        responses={
            200: openapi.Response(
                description="Estado del sistema obtenido",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'email_enabled': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'smtp_configured': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'sendgrid_configured': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'notifications_enabled': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'supported_types': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                        'backend_status': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            403: ErrorResponseSerializer,
        },
        tags=['Emails']
    )
    def get(self, request):
        """Obtiene el estado del sistema de emails."""
        try:
            from django.conf import settings
            
            status_info = {
                'email_enabled': settings.EMAIL_NOTIFICATIONS_ENABLED,
                'smtp_configured': bool(settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD),
                'sendgrid_configured': bool(settings.SENDGRID_API_KEY),
                'notifications_enabled': settings.EMAIL_NOTIFICATIONS_ENABLED,
                'supported_types': settings.EMAIL_NOTIFICATION_TYPES,
                'backend_status': {
                    'smtp_available': email_service.smtp_backend is not None,
                    'sendgrid_available': email_service.sendgrid_client is not None,
                    'default_from_email': settings.DEFAULT_FROM_EMAIL,
                    'email_host': settings.EMAIL_HOST,
                    'email_port': settings.EMAIL_PORT
                }
            }
            
            return create_success_response(
                message='Estado del sistema de emails obtenido',
                data=status_info
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo estado de emails: {e}")
            return create_error_response(
                message='Error obteniendo estado del sistema de emails',
                error_type='server_error',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SendTestEmailView(APIView):
    """
    Endpoint para enviar email de prueba.
    """
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="Envía un email de prueba para verificar la configuración",
        operation_summary="Enviar email de prueba",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'to_email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                'use_sendgrid': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False)
            },
            required=['to_email']
        ),
        responses={
            200: openapi.Response(
                description="Email de prueba enviado",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'backend_used': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
        tags=['Emails']
    )
    def post(self, request):
        """Envía un email de prueba."""
        to_email = request.data.get('to_email')
        use_sendgrid = request.data.get('use_sendgrid', False)
        
        if not to_email:
            return create_error_response(
                message='Email destinatario es requerido',
                error_type='validation_error',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Preparar contenido del email de prueba
            subject = " Email de Prueba - CacaoScan"
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #8B4513; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1> CacaoScan</h1>
                    <h2>Email de Prueba</h2>
                </div>
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px;">
                    <p>¡Hola!</p>
                    <p>Este es un email de prueba enviado desde el sistema CacaoScan.</p>
                    <p><strong>Detalles del envío:</strong></p>
                    <ul>
                        <li><strong>Fecha:</strong> {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}</li>
                        <li><strong>Backend:</strong> {'SendGrid' if use_sendgrid else 'SMTP'}</li>
                        <li><strong>Enviado por:</strong> {request.user.username}</li>
                    </ul>
                    <p>Si recibes este email, significa que la configuración de emails está funcionando correctamente.</p>
                    <hr style="margin: 20px 0;">
                    <p style="color: #666; font-size: 12px;">
                        Este es un email automático del sistema CacaoScan.<br>
                        é {datetime.now().year} CacaoScan. Todos los derechos reservados.
                    </p>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            CacaoScan - Email de Prueba
            
            ¡Hola!
            
            Este es un email de prueba enviado desde el sistema CacaoScan.
            
            Detalles del envío:
            - Fecha: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}
            - Backend: {'SendGrid' if use_sendgrid else 'SMTP'}
            - Enviado por: {request.user.username}
            
            Si recibes este email, significa que la configuración de emails está funcionando correctamente.
            
            ---
            Este es un email automático del sistema CacaoScan.
            é {datetime.now().year} CacaoScan. Todos los derechos reservados.
            """
            
            # Enviar email
            result = send_custom_email(
                to_emails=[to_email],
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                use_sendgrid=use_sendgrid
            )
            
            if result['success']:
                logger.info(f"Email de prueba enviado exitosamente a {to_email} via {result['backend_used']}")
                return create_success_response(
                    message=f'Email de prueba enviado exitosamente a {to_email}',
                    data={
                        'backend_used': result['backend_used'],
                        'timestamp': result.get('timestamp'),
                        'recipient': to_email
                    }
                )
            else:
                logger.error(f"Error enviando email de prueba: {result.get('error')}")
                return create_error_response(
                    message=f'Error enviando email de prueba: {result.get("error")}',
                    error_type='email_error',
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Error en envío de email de prueba: {e}")
            return create_error_response(
                message='Error interno enviando email de prueba',
                error_type='server_error',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SendBulkNotificationView(APIView):
    """
    Endpoint para enviar notificaciones masivas por email.
    """
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="Envía notificaciones masivas por email a múltiples usuarios",
        operation_summary="Enviar notificaciones masivas",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'notification_type': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['welcome', 'password_reset', 'analysis_complete', 'report_ready', 'training_complete', 'defect_alert', 'system_alert', 'weekly_summary']
                ),
                'user_emails': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING, format='email')
                ),
                'subject_override': openapi.Schema(type=openapi.TYPE_STRING),
                'context': openapi.Schema(type=openapi.TYPE_OBJECT),
                'batch_size': openapi.Schema(type=openapi.TYPE_INTEGER, default=50)
            },
            required=['notification_type', 'user_emails']
        ),
        responses={
            200: openapi.Response(
                description="Notificaciones masivas enviadas",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_emails': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'successful': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'failed': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'batches_processed': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'errors': openapi.Schema(type=openapi.TYPE_ARRAY)
                    }
                )
            ),
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
        tags=['Emails']
    )
    def post(self, request):
        """Envía notificaciones masivas por email."""
        notification_type = request.data.get('notification_type')
        user_emails = request.data.get('user_emails', [])
        subject_override = request.data.get('subject_override')
        context = request.data.get('context', {})
        batch_size = request.data.get('batch_size', 50)
        
        if not notification_type:
            return create_error_response(
                message='Tipo de notificación es requerido',
                error_type='validation_error',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if not user_emails or not isinstance(user_emails, list):
            return create_error_response(
                message='Lista de emails es requerida',
                error_type='validation_error',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Preparar contexto base
            base_context = {
                'site_name': 'CacaoScan',
                'site_url': 'https://cacaoscan.com',
                'current_year': datetime.now().year,
                'timestamp': datetime.now().isoformat(),
                **context
            }
            
            # Enviar notificaciones masivas
            result = send_bulk_email_notification(
                user_emails=user_emails,
                notification_type=notification_type,
                context=base_context,
                batch_size=batch_size
            )
            
            logger.info(f"Notificaciones masivas enviadas: {result['successful']}/{result['total_emails']} exitosas")
            
            return create_success_response(
                message=f'Notificaciones masivas procesadas: {result["successful"]}/{result["total_emails"]} exitosas',
                data=result
            )
            
        except Exception as e:
            logger.error(f"Error enviando notificaciones masivas: {e}")
            return create_error_response(
                message='Error enviando notificaciones masivas',
                error_type='server_error',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EmailTemplatePreviewView(APIView):
    """
    Endpoint para previsualizar templates de email.
    """
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="Previsualiza un template de email con datos de ejemplo",
        operation_summary="Previsualizar template de email",
        manual_parameters=[
            openapi.Parameter(
                'template_type',
                openapi.IN_QUERY,
                description="Tipo de template a previsualizar",
                type=openapi.TYPE_STRING,
                enum=['welcome', 'password_reset', 'analysis_complete', 'report_ready', 'training_complete', 'defect_alert', 'system_alert', 'weekly_summary'],
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Template previsualizado",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'template_type': openapi.Schema(type=openapi.TYPE_STRING),
                        'html_content': openapi.Schema(type=openapi.TYPE_STRING),
                        'text_content': openapi.Schema(type=openapi.TYPE_STRING),
                        'subject': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
        tags=['Emails']
    )
    def get(self, request):
        """Previsualiza un template de email."""
        template_type = request.query_params.get('template_type')
        
        if not template_type:
            return create_error_response(
                message='Tipo de template es requerido',
                error_type='validation_error',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Datos de ejemplo para el template
            sample_context = {
                'user_name': 'Juan Pérez',
                'user_email': 'juan.perez@ejemplo.com',
                'site_name': 'CacaoScan',
                'site_url': 'https://cacaoscan.com',
                'current_year': datetime.now().year,
                'timestamp': datetime.now().isoformat(),
                'verification_token': 'abc123-def456-ghi789',
                'verification_url': 'https://cacaoscan.com/auth/verify-email/?token=abc123-def456-ghi789',
                'reset_url': 'https://cacaoscan.com/auth/reset-password/?token=abc123-def456-ghi789',
                'token_expiry_hours': 24,
                'analysis_id': '12345',
                'confidence': 85.5,
                'confidence_level': 'high',
                'alto_mm': 22.8,
                'ancho_mm': 10.2,
                'grosor_mm': 16.3,
                'peso_g': 1.72,
                'confidence_alto': 92.0,
                'confidence_ancho': 88.0,
                'confidence_grosor': 85.0,
                'confidence_peso': 90.0,
                'processing_time_ms': 1250,
                'model_version': 'v2.0_calibrated',
                'analysis_date': '15/10/2024 14:30',
                'crop_url': '/media/cacao_images/crops_runtime/sample.png',
                'defects_detected': ['Mancha oscura', 'Grieta superficial'],
                'report_type': 'Análisis Mensual',
                'period_start': '01/10/2024',
                'period_end': '31/10/2024',
                'generation_date': '15/10/2024 15:00',
                'file_size': '2.5 MB',
                'file_format': 'PDF',
                'download_url': 'https://cacaoscan.com/reports/download/12345',
                'download_expiry_days': 7,
                'report_id': 'RPT-2024-001',
                'summary_stats': [
                    {'label': 'Total Análisis', 'value': '150'},
                    {'label': 'Promedio Peso', 'value': '1.8g'},
                    {'label': 'Calidad Alta', 'value': '85%'}
                ],
                'report_sections': [
                    'Resumen Ejecutivo',
                    'Análisis de Dimensiones',
                    'Distribución de Peso',
                    'Detección de Defectos',
                    'Recomendaciones'
                ],
                'recommendations': [
                    'Mejorar condiciones de almacenamiento',
                    'Implementar control de calidad más estricto'
                ]
            }
            
            # Renderizar template
            html_content, text_content = email_notification_service.email_service._render_template(
                template_type, sample_context
            )
            
            # Obtener asunto por defecto
            subject = email_notification_service._get_default_subject(template_type, sample_context)
            
            return create_success_response(
                message=f'Template {template_type} previsualizado',
                data={
                    'template_type': template_type,
                    'html_content': html_content,
                    'text_content': text_content,
                    'subject': subject
                }
            )
            
        except Exception as e:
            logger.error(f"Error previsualizando template {template_type}: {e}")
            return create_error_response(
                message=f'Error previsualizando template: {str(e)}',
                error_type='template_error',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EmailLogsView(APIView):
    """
    Endpoint para consultar logs de emails enviados.
    """
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="Obtiene logs de emails enviados en un período específico",
        operation_summary="Logs de emails",
        manual_parameters=[
            openapi.Parameter(
                'start_date',
                openapi.IN_QUERY,
                description="Fecha de inicio (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format='date',
                required=False
            ),
            openapi.Parameter(
                'end_date',
                openapi.IN_QUERY,
                description="Fecha de fin (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format='date',
                required=False
            ),
            openapi.Parameter(
                'notification_type',
                openapi.IN_QUERY,
                description="Filtrar por tipo de notificación",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description="Filtrar por estado (success, failed)",
                type=openapi.TYPE_STRING,
                enum=['success', 'failed'],
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="Logs de emails obtenidos",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'total_emails': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'successful': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'failed': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'logs': openapi.Schema(type=openapi.TYPE_ARRAY)
                    }
                )
            ),
            403: ErrorResponseSerializer,
        },
        tags=['Emails']
    )
    def get(self, request):
        """Obtiene logs de emails enviados."""
        try:
            # TODO: Implementar sistema de logging de emails
            # Por ahora retornamos datos de ejemplo
            
            logs_data = {
                'total_emails': 0,
                'successful': 0,
                'failed': 0,
                'logs': [],
                'message': 'Sistema de logs de emails en desarrollo'
            }
            
            return create_success_response(
                message='Logs de emails obtenidos',
                data=logs_data
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo logs de emails: {e}")
            return create_error_response(
                message='Error obteniendo logs de emails',
                error_type='server_error',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


