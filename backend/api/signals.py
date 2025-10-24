"""
Signals para notificaciones automáticas en CacaoScan.
"""
import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Notification, CacaoPrediction, TrainingJob, Finca, Lote
from .realtime_service import realtime_service

logger = logging.getLogger("cacaoscan.api")


@receiver(post_save, sender=CacaoPrediction)
def notify_prediction_completed(sender, instance, created, **kwargs):
    """
    Notificar cuando se completa una predicción de análisis.
    """
    if created:
        try:
            # Determinar el tipo de notificación basado en la calidad
            if instance.average_confidence >= 0.8:
                tipo = 'success'
                titulo = 'Análisis Completado - Alta Calidad'
                mensaje = f'Tu análisis de granos de cacao ha sido completado con alta calidad (confianza: {instance.average_confidence:.1%}). Los resultados están disponibles.'
            elif instance.average_confidence >= 0.6:
                tipo = 'info'
                titulo = 'Análisis Completado - Calidad Estándar'
                mensaje = f'Tu análisis de granos de cacao ha sido completado con calidad estándar (confianza: {instance.average_confidence:.1%}). Revisa los resultados.'
            else:
                tipo = 'warning'
                titulo = 'Análisis Completado - Calidad Baja'
                mensaje = f'Tu análisis de granos de cacao ha sido completado con baja confianza ({instance.average_confidence:.1%}). Considera repetir el análisis.'
            
            # Crear notificación y enviar en tiempo real
            datos_extra = {
                'prediction_id': instance.id,
                'image_id': instance.image.id,
                'confidence': float(instance.average_confidence),
                'quality_metrics': {
                    'alto_mm': float(instance.alto_mm),
                    'ancho_mm': float(instance.ancho_mm),
                    'grosor_mm': float(instance.grosor_mm),
                    'peso_g': float(instance.peso_g),
                }
            }
            
            notification = realtime_service.create_and_send_notification(
                user_id=instance.image.user.id,
                tipo=tipo,
                titulo=titulo,
                mensaje=mensaje,
                datos_extra=datos_extra
            )
            
            # Enviar email de notificación si está habilitado
            try:
                from .email_service import send_email_notification
                
                email_context = {
                    'user_name': instance.image.user.get_full_name() or instance.image.user.username,
                    'user_email': instance.image.user.email,
                    'analysis_id': instance.id,
                    'confidence': round(instance.average_confidence * 100, 1),
                    'confidence_level': tipo,
                    'alto_mm': instance.alto_mm,
                    'ancho_mm': instance.ancho_mm,
                    'grosor_mm': instance.grosor_mm,
                    'peso_g': instance.peso_g,
                    'processing_time_ms': instance.processing_time_ms,
                    'analysis_date': instance.created_at.strftime('%d/%m/%Y %H:%M'),
                    'crop_url': getattr(instance, 'crop_url', ''),
                    'defects_detected': []  # TODO: Implementar detección de defectos
                }
                
                email_result = send_email_notification(
                    user_email=instance.image.user.email,
                    notification_type='analysis_complete',
                    context=email_context
                )
                
                if email_result['success']:
                    logger.info(f"Email de análisis completado enviado a {instance.image.user.email}")
                else:
                    logger.warning(f"Error enviando email de análisis: {email_result.get('error')}")
                    
            except Exception as e:
                logger.error(f"Error en envío de email de análisis: {e}")
            
            logger.info(f"Notificación de análisis completado enviada a usuario {instance.image.user.username}")
            
        except Exception as e:
            logger.error(f"Error enviando notificación de análisis completado: {e}")


@receiver(post_save, sender=TrainingJob)
def notify_training_completed(sender, instance, created, **kwargs):
    """
    Notificar cuando se completa un trabajo de entrenamiento.
    """
    if not created and instance.status == 'completed':
        try:
            # Notificar al usuario que creó el trabajo
            datos_extra = {
                'job_id': instance.job_id,
                'model_name': instance.model_name,
                'metrics': instance.metrics,
                'duration': instance.duration_formatted if hasattr(instance, 'duration_formatted') else None
            }
            
            notification = realtime_service.create_and_send_notification(
                user_id=instance.created_by.id,
                tipo='training_complete',
                titulo='Entrenamiento de Modelo Completado',
                mensaje=f'El entrenamiento del modelo "{instance.model_name}" ha sido completado exitosamente. El modelo está listo para usar.',
                datos_extra=datos_extra
            )
            
            # Enviar email de notificación si está habilitado
            try:
                from .email_service import send_email_notification
                
                email_context = {
                    'user_name': instance.created_by.get_full_name() or instance.created_by.username,
                    'user_email': instance.created_by.email,
                    'model_name': instance.model_name,
                    'job_id': instance.job_id,
                    'metrics': instance.metrics,
                    'duration': instance.duration_formatted if hasattr(instance, 'duration_formatted') else 'N/A',
                    'completion_date': instance.updated_at.strftime('%d/%m/%Y %H:%M'),
                    'status': instance.status
                }
                
                email_result = send_email_notification(
                    user_email=instance.created_by.email,
                    notification_type='training_complete',
                    context=email_context
                )
                
                if email_result['success']:
                    logger.info(f"Email de entrenamiento completado enviado a {instance.created_by.email}")
                else:
                    logger.warning(f"Error enviando email de entrenamiento: {email_result.get('error')}")
                    
            except Exception as e:
                logger.error(f"Error en envío de email de entrenamiento: {e}")
            
            # Si es un trabajo importante, también notificar a los administradores
            if instance.job_type in ['full_training', 'model_update']:
                admins = User.objects.filter(is_superuser=True)
                for admin in admins:
                    if admin != instance.created_by:  # No duplicar notificación
                        Notification.create_notification(
                            user=admin,
                            tipo='info',
                            titulo='Nuevo Modelo Entrenado',
                            mensaje=f'El usuario {instance.created_by.username} ha completado el entrenamiento del modelo "{instance.model_name}".',
                            datos_extra={
                                'job_id': instance.job_id,
                                'created_by': instance.created_by.username,
                                'model_name': instance.model_name
                            }
                        )
            
            logger.info(f"Notificación de entrenamiento completado enviada a usuario {instance.created_by.username}")
            
        except Exception as e:
            logger.error(f"Error enviando notificación de entrenamiento completado: {e}")


@receiver(post_save, sender=TrainingJob)
def notify_training_failed(sender, instance, created, **kwargs):
    """
    Notificar cuando falla un trabajo de entrenamiento.
    """
    if not created and instance.status == 'failed':
        try:
            datos_extra = {
                'job_id': instance.job_id,
                'model_name': instance.model_name,
                'error_message': instance.error_message
            }
            
            realtime_service.create_and_send_notification(
                user_id=instance.created_by.id,
                tipo='error',
                titulo='Error en Entrenamiento de Modelo',
                mensaje=f'El entrenamiento del modelo "{instance.model_name}" ha fallado. Error: {instance.error_message or "Error desconocido"}.',
                datos_extra=datos_extra
            )
            
            logger.info(f"Notificación de error de entrenamiento enviada a usuario {instance.created_by.username}")
            
        except Exception as e:
            logger.error(f"Error enviando notificación de error de entrenamiento: {e}")


@receiver(post_save, sender=User)
def notify_user_registered(sender, instance, created, **kwargs):
    """
    Notificar cuando se registra un nuevo usuario.
    """
    if created:
        try:
            # Notificación de bienvenida
            datos_extra = {
                'user_id': instance.id,
                'registration_date': timezone.now().isoformat(),
                'next_steps': [
                    'Completa tu perfil',
                    'Registra tu primera finca',
                    'Sube tu primera imagen para análisis'
                ]
            }
            
            realtime_service.create_and_send_notification(
                user_id=instance.id,
                tipo='welcome',
                titulo='¡Bienvenido a CacaoScan!',
                mensaje='Gracias por registrarte en CacaoScan. Tu cuenta ha sido creada exitosamente. Puedes comenzar a analizar granos de cacao subiendo imágenes.',
                datos_extra=datos_extra
            )
            
            logger.info(f"Notificación de bienvenida enviada a nuevo usuario {instance.username}")
            
        except Exception as e:
            logger.error(f"Error enviando notificación de bienvenida: {e}")


@receiver(post_save, sender=Finca)
def notify_finca_created(sender, instance, created, **kwargs):
    """
    Notificar cuando se crea una nueva finca.
    """
    if created:
        try:
            Notification.create_notification(
                user=instance.agricultor,
                tipo='success',
                titulo='Finca Registrada Exitosamente',
                mensaje=f'Tu finca "{instance.nombre}" ha sido registrada exitosamente en {instance.municipio}, {instance.departamento}.',
                datos_extra={
                    'finca_id': instance.id,
                    'finca_nombre': instance.nombre,
                    'ubicacion': instance.ubicacion_completa,
                    'hectareas': float(instance.hectareas)
                }
            )
            
            logger.info(f"Notificación de finca creada enviada a usuario {instance.agricultor.username}")
            
        except Exception as e:
            logger.error(f"Error enviando notificación de finca creada: {e}")


@receiver(post_save, sender=Lote)
def notify_lote_created(sender, instance, created, **kwargs):
    """
    Notificar cuando se crea un nuevo lote.
    """
    if created:
        try:
            Notification.create_notification(
                user=instance.finca.agricultor,
                tipo='info',
                titulo='Nuevo Lote Registrado',
                mensaje=f'Se ha registrado el lote "{instance.identificador}" de variedad {instance.variedad} en tu finca "{instance.finca.nombre}".',
                datos_extra={
                    'lote_id': instance.id,
                    'lote_identificador': instance.identificador,
                    'variedad': instance.variedad,
                    'finca_nombre': instance.finca.nombre,
                    'area_hectareas': float(instance.area_hectareas)
                }
            )
            
            logger.info(f"Notificación de lote creado enviada a usuario {instance.finca.agricultor.username}")
            
        except Exception as e:
            logger.error(f"Error enviando notificación de lote creado: {e}")


@receiver(post_save, sender=Lote)
def notify_lote_cosechado(sender, instance, created, **kwargs):
    """
    Notificar cuando se marca un lote como cosechado.
    """
    if not created and instance.estado == 'cosechado':
        try:
            Notification.create_notification(
                user=instance.finca.agricultor,
                tipo='success',
                titulo='Lote Cosechado',
                mensaje=f'El lote "{instance.identificador}" de variedad {instance.variedad} ha sido marcado como cosechado.',
                datos_extra={
                    'lote_id': instance.id,
                    'lote_identificador': instance.identificador,
                    'variedad': instance.variedad,
                    'fecha_cosecha': instance.fecha_cosecha.isoformat() if instance.fecha_cosecha else None,
                    'finca_nombre': instance.finca.nombre
                }
            )
            
            logger.info(f"Notificación de lote cosechado enviada a usuario {instance.finca.agricultor.username}")
            
        except Exception as e:
            logger.error(f"Error enviando notificación de lote cosechado: {e}")


def send_custom_notification(user, tipo, titulo, mensaje, datos_extra=None):
    """
    Función helper para enviar notificaciones personalizadas.
    
    Args:
        user: Usuario destinatario
        tipo: Tipo de notificación
        titulo: Título de la notificación
        mensaje: Mensaje de la notificación
        datos_extra: Datos adicionales en formato dict
    """
    try:
        notification = Notification.create_notification(
            user=user,
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            datos_extra=datos_extra or {}
        )
        
        logger.info(f"Notificación personalizada enviada a usuario {user.username}: {titulo}")
        return notification
        
    except Exception as e:
        logger.error(f"Error enviando notificación personalizada: {e}")
        return None


def send_bulk_notification(users, tipo, titulo, mensaje, datos_extra=None):
    """
    Función helper para enviar notificaciones masivas.
    
    Args:
        users: Lista de usuarios destinatarios
        tipo: Tipo de notificación
        titulo: Título de la notificación
        mensaje: Mensaje de la notificación
        datos_extra: Datos adicionales en formato dict
    """
    notifications_created = 0
    
    for user in users:
        try:
            Notification.create_notification(
                user=user,
                tipo=tipo,
                titulo=titulo,
                mensaje=mensaje,
                datos_extra=datos_extra or {}
            )
            notifications_created += 1
            
        except Exception as e:
            logger.error(f"Error enviando notificación masiva a usuario {user.username}: {e}")
    
    logger.info(f"Notificaciones masivas enviadas: {notifications_created}/{len(users)}")
    return notifications_created
