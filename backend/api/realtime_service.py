"""
Servicio para notificaciones en tiempo real usando WebSockets.
"""
import json
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings

from .models import LoginHistory
try:
    from notifications.models import Notification
except ImportError:
    Notification = None
try:
    from audit.models import ActivityLog
except ImportError:
    ActivityLog = None

logger = logging.getLogger("cacaoscan.websockets")


class RealtimeNotificationService:
    """
    Servicio para enviar notificaciones en tiempo real a travÃ©s de WebSockets.
    """
    
    def __init__(self):
        self.channel_layer = get_channel_layer()
    
    def send_notification_to_user(self, user_id, notification_data):
        """
        Enviar notificaciÃ³n a un usuario especÃ­fico.
        
        Args:
            user_id (int): ID del usuario
            notification_data (dict): Datos de la notificaciÃ³n
        """
        if not settings.REALTIME_NOTIFICATIONS_ENABLED:
            return
        
        try:
            group_name = f'notifications_{user_id}'
            
            async_to_sync(self.channel_layer.group_send)(
                group_name,
                {
                    'type': 'notification_message',
                    'data': notification_data
                }
            )
            
            logger.info(f"NotificaciÃ³n enviada a usuario {user_id}: {notification_data.get('titulo', 'Sin tÃ­tulo')}")
            
        except Exception as e:
            logger.error(f"Error enviando notificaciÃ³n a usuario {user_id}: {e}")
    
    def send_notification_to_all_users(self, notification_data):
        """
        Enviar notificaciÃ³n a todos los usuarios conectados.
        
        Args:
            notification_data (dict): Datos de la notificaciÃ³n
        """
        if not settings.NOTIFICATION_BROADCAST_ENABLED:
            return
        
        try:
            # Obtener todos los usuarios activos
            active_users = User.objects.filter(is_active=True)
            
            for user in active_users:
                self.send_notification_to_user(user.id, notification_data)
            
            logger.info(f"NotificaciÃ³n broadcast enviada a {active_users.count()} usuarios")
            
        except Exception as e:
            logger.error(f"Error enviando notificaciÃ³n broadcast: {e}")
    
    def send_notification_to_admins(self, notification_data):
        """
        Enviar notificaciÃ³n solo a administradores.
        
        Args:
            notification_data (dict): Datos de la notificaciÃ³n
        """
        try:
            admin_users = User.objects.filter(
                is_active=True,
                is_superuser=True
            )
            
            for admin in admin_users:
                self.send_notification_to_user(admin.id, notification_data)
            
            logger.info(f"NotificaciÃ³n enviada a {admin_users.count()} administradores")
            
        except Exception as e:
            logger.error(f"Error enviando notificaciÃ³n a administradores: {e}")
    
    def update_notification_stats(self, user_id):
        """
        Actualizar estadÃ­sticas de notificaciones para un usuario.
        
        Args:
            user_id (int): ID del usuario
        """
        if Notification is None:
            logger.debug("Servicio de notificaciones no disponible; se omite actualizaciÃ³n de estadÃ­sticas")
            return
        try:
            user = User.objects.get(id=user_id)
            
            total_notifications = Notification.objects.filter(user=user).count()
            unread_count = Notification.get_unread_count(user)
            
            notifications_by_type = {}
            for tipo, _ in Notification.TIPO_CHOICES:
                count = Notification.objects.filter(user=user, tipo=tipo).count()
                notifications_by_type[tipo] = count
            
            stats = {
                'total_notifications': total_notifications,
                'unread_count': unread_count,
                'notifications_by_type': notifications_by_type,
                'timestamp': timezone.now().isoformat()
            }
            
            group_name = f'notifications_{user_id}'
            
            async_to_sync(self.channel_layer.group_send)(
                group_name,
                {
                    'type': 'notification_stats_update',
                    'data': stats
                }
            )
            
        except User.DoesNotExist:
            logger.error(f"Usuario {user_id} no encontrado para actualizar estadÃ­sticas")
        except Exception as e:
            logger.error(f"Error actualizando estadÃ­sticas de notificaciones: {e}")
    
    def send_activity_log(self, activity_data):
        """
        Enviar nueva actividad de auditorÃ­a a administradores.
        
        Args:
            activity_data (dict): Datos de la actividad
        """
        try:
            admin_users = User.objects.filter(
                is_active=True,
                is_superuser=True
            )
            
            for admin in admin_users:
                group_name = f'audit_{admin.id}'
                
                async_to_sync(self.channel_layer.group_send)(
                    group_name,
                    {
                        'type': 'audit_activity',
                        'data': activity_data
                    }
                )
            
            logger.info(f"Actividad de auditorÃ­a enviada a {admin_users.count()} administradores")
            
        except Exception as e:
            logger.error(f"Error enviando actividad de auditorÃ­a: {e}")
    
    def send_login_activity(self, login_data):
        """
        Enviar nueva actividad de login a administradores.
        
        Args:
            login_data (dict): Datos del login
        """
        try:
            admin_users = User.objects.filter(
                is_active=True,
                is_superuser=True
            )
            
            for admin in admin_users:
                group_name = f'audit_{admin.id}'
                
                async_to_sync(self.channel_layer.group_send)(
                    group_name,
                    {
                        'type': 'audit_login',
                        'data': login_data
                    }
                )
            
            logger.info(f"Actividad de login enviada a {admin_users.count()} administradores")
            
        except Exception as e:
            logger.error(f"Error enviando actividad de login: {e}")
    
    def send_system_status_update(self, status_data):
        """
        Enviar actualizaciÃ³n de estado del sistema.
        
        Args:
            status_data (dict): Datos del estado del sistema
        """
        try:
            async_to_sync(self.channel_layer.group_send)(
                'system_status',
                {
                    'type': 'system_status_update',
                    'data': status_data
                }
            )
            
            logger.info("ActualizaciÃ³n de estado del sistema enviada")
            
        except Exception as e:
            logger.error(f"Error enviando actualizaciÃ³n de estado del sistema: {e}")
    
    def send_system_alert(self, alert_data):
        """
        Enviar alerta del sistema.
        
        Args:
            alert_data (dict): Datos de la alerta
        """
        try:
            # Enviar a todos los usuarios conectados al estado del sistema
            async_to_sync(self.channel_layer.group_send)(
                'system_status',
                {
                    'type': 'system_alert',
                    'data': alert_data
                }
            )
            
            # TambiÃ©n enviar como notificaciÃ³n a administradores
            self.send_notification_to_admins({
                'tipo': 'error',
                'titulo': alert_data.get('title', 'Alerta del Sistema'),
                'mensaje': alert_data.get('message', 'Se ha detectado una alerta del sistema'),
                'datos_extra': alert_data
            })
            
            logger.info(f"Alerta del sistema enviada: {alert_data.get('title', 'Sin tÃ­tulo')}")
            
        except Exception as e:
            logger.error(f"Error enviando alerta del sistema: {e}")
    
    def create_and_send_notification(self, user_id, tipo, titulo, mensaje, datos_extra=None):
        """
        Crear notificaciÃ³n en la base de datos y enviarla en tiempo real.
        
        Args:
            user_id (int): ID del usuario
            tipo (str): Tipo de notificaciÃ³n
            titulo (str): TÃ­tulo de la notificaciÃ³n
            mensaje (str): Mensaje de la notificaciÃ³n
            datos_extra (dict): Datos adicionales
        """
        if Notification is None:
            logger.debug("Servicio de notificaciones no disponible; no se crea notificaciÃ³n")
            return None
        try:
            user = User.objects.get(id=user_id)
            
            # Crear notificaciÃ³n en la base de datos
            notification = Notification.create_notification(
                user=user,
                tipo=tipo,
                titulo=titulo,
                mensaje=mensaje,
                datos_extra=datos_extra
            )
            
            # Enviar en tiempo real
            notification_data = {
                'id': notification.id,
                'tipo': notification.tipo,
                'titulo': notification.titulo,
                'mensaje': notification.mensaje,
                'fecha_creacion': notification.fecha_creacion.isoformat(),
                'datos_extra': notification.datos_extra
            }
            
            self.send_notification_to_user(user_id, notification_data)
            
            # Actualizar estadÃ­sticas
            self.update_notification_stats(user_id)
            
            logger.info(f"NotificaciÃ³n creada y enviada: {titulo}")
            
            return notification
            
        except User.DoesNotExist:
            logger.error(f"Usuario {user_id} no encontrado para crear notificaciÃ³n")
            return None
        except Exception as e:
            logger.error(f"Error creando y enviando notificaciÃ³n: {e}")
            return None


# Instancia global del servicio
realtime_service = RealtimeNotificationService()


