"""
Consumers de WebSockets para CacaoScan.
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

from .models import Notification, ActivityLog, LoginHistory

logger = logging.getLogger("cacaoscan.websockets")


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Consumer para notificaciones en tiempo real.
    """
    
    async def connect(self):
        """Conectar usuario al WebSocket."""
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.user_group_name = f'notifications_{self.user_id}'
        
        # Verificar que el usuario existe
        user = await self.get_user(self.user_id)
        if not user:
            await self.close()
            return
        
        # Unirse al grupo de notificaciones del usuario
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Enviar notificaciones pendientes
        await self.send_pending_notifications(user)
        
        logger.info(f"Usuario {user.username} conectado a notificaciones WebSocket")
    
    async def disconnect(self, close_code):
        """Desconectar usuario del WebSocket."""
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
        
        logger.info(f"Usuario {self.user_id} desconectado de notificaciones WebSocket")
    
    async def receive(self, text_data):
        """Recibir mensaje del cliente."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': timezone.now().isoformat()
                }))
            elif message_type == 'mark_read':
                notification_id = data.get('notification_id')
                await self.mark_notification_read(notification_id)
            elif message_type == 'mark_all_read':
                await self.mark_all_notifications_read()
            elif message_type == 'get_stats':
                await self.send_notification_stats()
            
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Formato JSON inválido'
            }))
        except Exception as e:
            logger.error(f"Error procesando mensaje WebSocket: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Error interno del servidor'
            }))
    
    async def notification_message(self, event):
        """Enviar notificación al cliente."""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'data': event['data']
        }))
    
    async def notification_update(self, event):
        """Enviar actualización de notificación al cliente."""
        await self.send(text_data=json.dumps({
            'type': 'notification_update',
            'data': event['data']
        }))
    
    async def notification_stats_update(self, event):
        """Enviar actualización de estadísticas al cliente."""
        await self.send(text_data=json.dumps({
            'type': 'stats_update',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def get_user(self, user_id):
        """Obtener usuario por ID."""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    
    @database_sync_to_async
    def send_pending_notifications(self, user):
        """Enviar notificaciones pendientes al usuario."""
        notifications = Notification.objects.filter(
            user=user,
            leida=False
        ).order_by('-fecha_creacion')[:10]
        
        for notification in notifications:
            self.send(text_data=json.dumps({
                'type': 'pending_notification',
                'data': {
                    'id': notification.id,
                    'tipo': notification.tipo,
                    'titulo': notification.titulo,
                    'mensaje': notification.mensaje,
                    'fecha_creacion': notification.fecha_creacion.isoformat(),
                    'datos_extra': notification.datos_extra
                }
            }))
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Marcar notificación como leída."""
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user_id=self.user_id
            )
            notification.mark_as_read()
            
            # Enviar confirmación
            self.send(text_data=json.dumps({
                'type': 'notification_read',
                'notification_id': notification_id
            }))
            
        except Notification.DoesNotExist:
            self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Notificación no encontrada'
            }))
    
    @database_sync_to_async
    def mark_all_notifications_read(self):
        """Marcar todas las notificaciones como leídas."""
        user = User.objects.get(id=self.user_id)
        Notification.mark_all_as_read(user)
        
        # Enviar confirmación
        self.send(text_data=json.dumps({
            'type': 'all_notifications_read'
        }))
    
    @database_sync_to_async
    def send_notification_stats(self):
        """Enviar estadísticas de notificaciones."""
        user = User.objects.get(id=self.user_id)
        
        total_notifications = Notification.objects.filter(user=user).count()
        unread_count = Notification.get_unread_count(user)
        
        notifications_by_type = {}
        for tipo, _ in Notification.TIPO_CHOICES:
            count = Notification.objects.filter(user=user, tipo=tipo).count()
            notifications_by_type[tipo] = count
        
        stats = {
            'total_notifications': total_notifications,
            'unread_count': unread_count,
            'notifications_by_type': notifications_by_type
        }
        
        self.send(text_data=json.dumps({
            'type': 'notification_stats',
            'data': stats
        }))


class SystemStatusConsumer(AsyncWebsocketConsumer):
    """
    Consumer para estado del sistema en tiempo real.
    """
    
    async def connect(self):
        """Conectar al WebSocket de estado del sistema."""
        self.system_group_name = 'system_status'
        
        # Unirse al grupo de estado del sistema
        await self.channel_layer.group_add(
            self.system_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Enviar estado inicial
        await self.send_system_status()
        
        logger.info("Cliente conectado a WebSocket de estado del sistema")
    
    async def disconnect(self, close_code):
        """Desconectar del WebSocket."""
        await self.channel_layer.group_discard(
            self.system_group_name,
            self.channel_name
        )
        
        logger.info("Cliente desconectado de WebSocket de estado del sistema")
    
    async def receive(self, text_data):
        """Recibir mensaje del cliente."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': timezone.now().isoformat()
                }))
            elif message_type == 'get_status':
                await self.send_system_status()
            
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Formato JSON inválido'
            }))
        except Exception as e:
            logger.error(f"Error procesando mensaje WebSocket: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Error interno del servidor'
            }))
    
    async def system_status_update(self, event):
        """Enviar actualización de estado del sistema."""
        await self.send(text_data=json.dumps({
            'type': 'system_status',
            'data': event['data']
        }))
    
    async def system_alert(self, event):
        """Enviar alerta del sistema."""
        await self.send(text_data=json.dumps({
            'type': 'system_alert',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def send_system_status(self):
        """Enviar estado actual del sistema."""
        # Obtener estadísticas del sistema
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        
        # Estadísticas de notificaciones
        total_notifications = Notification.objects.count()
        unread_notifications = Notification.objects.filter(leida=False).count()
        
        # Estadísticas de actividad
        today_activities = ActivityLog.objects.filter(
            timestamp__date=timezone.now().date()
        ).count()
        
        today_logins = LoginHistory.objects.filter(
            login_time__date=timezone.now().date()
        ).count()
        
        status = {
            'timestamp': timezone.now().isoformat(),
            'system_status': 'online',
            'users': {
                'total': total_users,
                'active': active_users
            },
            'notifications': {
                'total': total_notifications,
                'unread': unread_notifications
            },
            'activity': {
                'today_activities': today_activities,
                'today_logins': today_logins
            },
            'websocket_connections': {
                'notifications': 0,  # Se actualizará dinámicamente
                'system_status': 1,
                'audit': 0
            }
        }
        
        self.send(text_data=json.dumps({
            'type': 'system_status',
            'data': status
        }))


class AuditConsumer(AsyncWebsocketConsumer):
    """
    Consumer para auditoría en tiempo real.
    """
    
    async def connect(self):
        """Conectar usuario al WebSocket de auditoría."""
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.audit_group_name = f'audit_{self.user_id}'
        
        # Verificar que el usuario existe y es admin
        user = await self.get_user(self.user_id)
        if not user or not (user.is_superuser or user.is_staff):
            await self.close()
            return
        
        # Unirse al grupo de auditoría del usuario
        await self.channel_layer.group_add(
            self.audit_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        logger.info(f"Admin {user.username} conectado a auditoría WebSocket")
    
    async def disconnect(self, close_code):
        """Desconectar usuario del WebSocket."""
        await self.channel_layer.group_discard(
            self.audit_group_name,
            self.channel_name
        )
        
        logger.info(f"Usuario {self.user_id} desconectado de auditoría WebSocket")
    
    async def receive(self, text_data):
        """Recibir mensaje del cliente."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': timezone.now().isoformat()
                }))
            elif message_type == 'get_audit_stats':
                await self.send_audit_stats()
            elif message_type == 'get_recent_activity':
                await self.send_recent_activity()
            
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Formato JSON inválido'
            }))
        except Exception as e:
            logger.error(f"Error procesando mensaje WebSocket: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Error interno del servidor'
            }))
    
    async def audit_activity(self, event):
        """Enviar nueva actividad de auditoría."""
        await self.send(text_data=json.dumps({
            'type': 'audit_activity',
            'data': event['data']
        }))
    
    async def audit_login(self, event):
        """Enviar nuevo login."""
        await self.send(text_data=json.dumps({
            'type': 'audit_login',
            'data': event['data']
        }))
    
    async def audit_stats_update(self, event):
        """Enviar actualización de estadísticas de auditoría."""
        await self.send(text_data=json.dumps({
            'type': 'audit_stats_update',
            'data': event['data']
        }))
    
    @database_sync_to_async
    def get_user(self, user_id):
        """Obtener usuario por ID."""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    
    @database_sync_to_async
    def send_audit_stats(self):
        """Enviar estadísticas de auditoría."""
        # Estadísticas de ActivityLog
        total_activities = ActivityLog.objects.count()
        activities_today = ActivityLog.objects.filter(
            timestamp__date=timezone.now().date()
        ).count()
        
        # Estadísticas de LoginHistory
        total_logins = LoginHistory.objects.count()
        successful_logins = LoginHistory.objects.filter(success=True).count()
        failed_logins = LoginHistory.objects.filter(success=False).count()
        
        # Actividades por tipo
        activities_by_action = {}
        for accion, _ in ActivityLog.ACCION_CHOICES:
            count = ActivityLog.objects.filter(accion=accion).count()
            activities_by_action[accion] = count
        
        stats = {
            'timestamp': timezone.now().isoformat(),
            'activities': {
                'total': total_activities,
                'today': activities_today,
                'by_action': activities_by_action
            },
            'logins': {
                'total': total_logins,
                'successful': successful_logins,
                'failed': failed_logins,
                'success_rate': (successful_logins / total_logins * 100) if total_logins > 0 else 0
            }
        }
        
        self.send(text_data=json.dumps({
            'type': 'audit_stats',
            'data': stats
        }))
    
    @database_sync_to_async
    def send_recent_activity(self):
        """Enviar actividad reciente."""
        recent_activities = ActivityLog.objects.select_related('usuario').order_by('-timestamp')[:20]
        recent_logins = LoginHistory.objects.select_related('usuario').order_by('-login_time')[:20]
        
        activities_data = []
        for activity in recent_activities:
            activities_data.append({
                'id': activity.id,
                'usuario': activity.usuario.username if activity.usuario else 'Usuario Anónimo',
                'accion': activity.accion,
                'accion_display': activity.get_accion_display(),
                'modelo': activity.modelo,
                'descripcion': activity.descripcion,
                'timestamp': activity.timestamp.isoformat(),
                'ip_address': activity.ip_address
            })
        
        logins_data = []
        for login in recent_logins:
            logins_data.append({
                'id': login.id,
                'usuario': login.usuario.username,
                'ip_address': login.ip_address,
                'success': login.success,
                'login_time': login.login_time.isoformat(),
                'failure_reason': login.failure_reason
            })
        
        self.send(text_data=json.dumps({
            'type': 'recent_activity',
            'data': {
                'activities': activities_data,
                'logins': logins_data
            }
        }))
