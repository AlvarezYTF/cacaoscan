"""
Servicio de emails para CacaoScan.
Maneja el envío de emails usando SMTP y SendGrid como alternativas.
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.core.mail.backends.smtp import EmailBackend
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
import base64
import json
from datetime import datetime, timedelta

logger = logging.getLogger("cacaoscan.email")


class EmailService:
    """
    Servicio principal para el envío de emails en CacaoScan.
    Soporta tanto SMTP como SendGrid como backends.
    """
    
    def __init__(self):
        self.smtp_backend = None
        self.sendgrid_client = None
        self._initialize_backends()
    
    def _initialize_backends(self):
        """Inicializa los backends de email disponibles."""
        try:
            # Inicializar backend SMTP
            if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
                self.smtp_backend = EmailBackend(
                    host=settings.EMAIL_HOST,
                    port=settings.EMAIL_PORT,
                    username=settings.EMAIL_HOST_USER,
                    password=settings.EMAIL_HOST_PASSWORD,
                    use_tls=settings.EMAIL_USE_TLS,
                    use_ssl=settings.EMAIL_USE_SSL,
                    timeout=settings.EMAIL_TIMEOUT,
                    fail_silently=False
                )
                logger.info("Backend SMTP inicializado correctamente")
            
            # Inicializar SendGrid si está configurado
            if settings.SENDGRID_API_KEY:
                self.sendgrid_client = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
                logger.info("Cliente SendGrid inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando backends de email: {e}")
    
    def send_email(
        self,
        to_emails: Union[str, List[str]],
        subject: str,
        html_content: str = None,
        text_content: str = None,
        from_email: str = None,
        attachments: List[Dict[str, Any]] = None,
        use_sendgrid: bool = False,
        template_name: str = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Envía un email usando el backend especificado.
        
        Args:
            to_emails: Email(s) destinatario(s)
            subject: Asunto del email
            html_content: Contenido HTML del email
            text_content: Contenido de texto plano
            from_email: Email remitente
            attachments: Lista de archivos adjuntos
            use_sendgrid: Si usar SendGrid en lugar de SMTP
            template_name: Nombre del template a usar
            context: Contexto para el template
            
        Returns:
            Dict con el resultado del envío
        """
        try:
            # Preparar emails destinatarios
            if isinstance(to_emails, str):
                to_emails = [to_emails]
            
            # Usar email por defecto si no se especifica
            if not from_email:
                from_email = settings.DEFAULT_FROM_EMAIL
            
            # Renderizar template si se especifica
            if template_name and context:
                html_content, text_content = self._render_template(template_name, context)
            
            # Generar contenido de texto si no se proporciona
            if html_content and not text_content:
                text_content = strip_tags(html_content)
            
            # Elegir backend
            if use_sendgrid and self.sendgrid_client:
                return self._send_with_sendgrid(
                    to_emails, subject, html_content, text_content, 
                    from_email, attachments
                )
            elif self.smtp_backend:
                return self._send_with_smtp(
                    to_emails, subject, html_content, text_content, 
                    from_email, attachments
                )
            else:
                return {
                    'success': False,
                    'error': 'No hay backends de email configurados',
                    'backend_used': None
                }
                
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            return {
                'success': False,
                'error': str(e),
                'backend_used': 'sendgrid' if use_sendgrid else 'smtp'
            }
    
    def _send_with_smtp(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: str,
        from_email: str,
        attachments: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Envía email usando SMTP con EmailMultiAlternatives (Django)."""
        try:
            # Construir EmailMultiAlternatives para que Django EmailBackend lo procese correctamente
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content or strip_tags(html_content or ''),
                from_email=from_email,
                to=to_emails,
            )

            # Adjuntar versión HTML si existe
            if html_content:
                email.attach_alternative(html_content, "text/html")

            # Adjuntar archivos si vienen
            if attachments:
                for attachment in attachments:
                    filename = attachment.get('filename')
                    content = attachment.get('content')
                    content_type = attachment.get('content_type', 'application/octet-stream')
                    if isinstance(content, str):
                        content = content.encode('utf-8')
                    email.attach(filename, content, content_type)

            # Enviar usando el backend SMTP
            connection = get_connection(backend='django.core.mail.backends.smtp.EmailBackend')
            connection.open()
            try:
                connection.send_messages([email])
                logger.info(f"Email enviado exitosamente a {to_emails} via SMTP")
                return {
                    'success': True,
                    'backend_used': 'smtp',
                    'recipients': to_emails,
                    'timestamp': datetime.now().isoformat()
                }
            finally:
                connection.close()

        except Exception as e:
            logger.error(f"Error enviando email via SMTP: {e}")
            return {
                'success': False,
                'error': str(e),
                'backend_used': 'smtp'
            }
    
    def _send_with_sendgrid(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: str,
        from_email: str,
        attachments: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Envía email usando SendGrid."""
        try:
            # Crear objeto Mail
            from_email_obj = Email(from_email)
            to_emails_obj = [To(email) for email in to_emails]
            
            # Crear contenido
            if html_content and text_content:
                mail = Mail(
                    from_email=from_email_obj,
                    to_emails=to_emails_obj,
                    subject=subject,
                    plain_text_content=text_content,
                    html_content=html_content
                )
            elif html_content:
                mail = Mail(
                    from_email=from_email_obj,
                    to_emails=to_emails_obj,
                    subject=subject,
                    html_content=html_content
                )
            else:
                mail = Mail(
                    from_email=from_email_obj,
                    to_emails=to_emails_obj,
                    subject=subject,
                    plain_text_content=text_content
                )
            
            # Agregar archivos adjuntos
            if attachments:
                for attachment in attachments:
                    self._add_sendgrid_attachment(mail, attachment)
            
            # Enviar email
            response = self.sendgrid_client.send(mail)
            
            logger.info(f"Email enviado exitosamente a {to_emails} via SendGrid")
            return {
                'success': True,
                'backend_used': 'sendgrid',
                'recipients': to_emails,
                'sendgrid_status_code': response.status_code,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error enviando email via SendGrid: {e}")
            return {
                'success': False,
                'error': str(e),
                'backend_used': 'sendgrid'
            }
    
    def _render_template(self, template_name: str, context: Dict[str, Any]) -> tuple:
        """Renderiza un template de email."""
        try:
            # Template HTML
            html_template = f"emails/{template_name}.html"
            html_content = render_to_string(html_template, context)
            
            # Template de texto
            text_template = f"emails/{template_name}.txt"
            try:
                text_content = render_to_string(text_template, context)
            except:
                # Si no existe template de texto, generar desde HTML
                text_content = strip_tags(html_content)
            
            return html_content, text_content
            
        except Exception as e:
            logger.error(f"Error renderizando template {template_name}: {e}")
            raise
    
    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]):
        """Agrega un archivo adjunto al mensaje SMTP."""
        try:
            filename = attachment.get('filename')
            content = attachment.get('content')
            content_type = attachment.get('content_type', 'application/octet-stream')
            
            if isinstance(content, str):
                content = content.encode('utf-8')
            
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(content)
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            msg.attach(part)
            
        except Exception as e:
            logger.error(f"Error agregando adjunto: {e}")
    
    def _add_sendgrid_attachment(self, mail: Mail, attachment: Dict[str, Any]):
        """Agrega un archivo adjunto al mensaje SendGrid."""
        try:
            filename = attachment.get('filename')
            content = attachment.get('content')
            content_type = attachment.get('content_type', 'application/octet-stream')
            
            if isinstance(content, str):
                content = content.encode('utf-8')
            
            encoded_content = base64.b64encode(content).decode()
            
            attachment_obj = Attachment(
                FileContent(encoded_content),
                FileName(filename),
                FileType(content_type),
                Disposition('attachment')
            )
            
            mail.add_attachment(attachment_obj)
            
        except Exception as e:
            logger.error(f"Error agregando adjunto SendGrid: {e}")


class EmailNotificationService:
    """
    Servicio especializado para notificaciones por email.
    """
    
    def __init__(self):
        self.email_service = EmailService()
        self.notification_types = settings.EMAIL_NOTIFICATION_TYPES
    
    def send_notification_email(
        self,
        user_email: str,
        notification_type: str,
        context: Dict[str, Any],
        subject_override: str = None
    ) -> Dict[str, Any]:
        """
        Envía un email de notificación específico.
        
        Args:
            user_email: Email del usuario
            notification_type: Tipo de notificación
            context: Contexto para el template
            subject_override: Asunto personalizado
            
        Returns:
            Resultado del envío
        """
        if not settings.EMAIL_NOTIFICATIONS_ENABLED:
            return {
                'success': False,
                'error': 'Notificaciones por email deshabilitadas',
                'skipped': True
            }
        
        if notification_type not in self.notification_types:
            return {
                'success': False,
                'error': f'Tipo de notificación no soportado: {notification_type}',
                'skipped': True
            }
        
        try:
            # Preparar contexto base
            base_context = {
                'site_name': 'CacaoScan',
                'site_url': 'https://cacaoscan.com',
                'current_year': datetime.now().year,
                'timestamp': datetime.now().isoformat(),
                **context
            }
            
            # Determinar asunto
            if subject_override:
                subject = subject_override
            else:
                subject = self._get_default_subject(notification_type, context)
            
            # Enviar email
            result = self.email_service.send_email(
                to_emails=[user_email],
                subject=subject,
                template_name=notification_type,
                context=base_context,
                use_sendgrid=bool(settings.SENDGRID_API_KEY)
            )
            
            if result['success']:
                logger.info(f"Notificación {notification_type} enviada a {user_email}")
            else:
                logger.error(f"Error enviando notificación {notification_type} a {user_email}: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error en servicio de notificaciones: {e}")
            return {
                'success': False,
                'error': str(e),
                'notification_type': notification_type
            }
    
    def _get_default_subject(self, notification_type: str, context: Dict[str, Any]) -> str:
        """Obtiene el asunto por defecto para un tipo de notificación."""
        subjects = {
            'welcome': f"¡Bienvenido a CacaoScan, {context.get('user_name', 'Usuario')}!",
            'password_reset': "Restablecimiento de contraseña - CacaoScan",
            'password_reset_success': "Contrasea restablecida exitosamente - CacaoScan",
            'analysis_complete': "Análisis completado - CacaoScan",
            'report_ready': "Reporte listo - CacaoScan",
            'training_complete': "Entrenamiento completado - CacaoScan",
            'defect_alert': "Alerta de defectos detectados - CacaoScan",
            'system_alert': "Alerta del sistema - CacaoScan",
            'weekly_summary': "Resumen semanal - CacaoScan"
        }
        
        return subjects.get(notification_type, "Notificación - CacaoScan")
    
    def send_bulk_notification(
        self,
        user_emails: List[str],
        notification_type: str,
        context: Dict[str, Any],
        batch_size: int = None
    ) -> Dict[str, Any]:
        """
        Envía notificaciones masivas por email.
        
        Args:
            user_emails: Lista de emails de usuarios
            notification_type: Tipo de notificación
            context: Contexto para el template
            batch_size: Tamaño del lote (por defecto usa configuración)
            
        Returns:
            Resultado del envío masivo
        """
        if not batch_size:
            batch_size = settings.EMAIL_BATCH_SIZE
        
        results = {
            'total_emails': len(user_emails),
            'successful': 0,
            'failed': 0,
            'errors': [],
            'batches_processed': 0
        }
        
        # Procesar en lotes
        for i in range(0, len(user_emails), batch_size):
            batch = user_emails[i:i + batch_size]
            results['batches_processed'] += 1
            
            for email in batch:
                try:
                    result = self.send_notification_email(email, notification_type, context)
                    if result['success']:
                        results['successful'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append({
                            'email': email,
                            'error': result.get('error', 'Error desconocido')
                        })
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append({
                        'email': email,
                        'error': str(e)
                    })
        
        logger.info(f"Envio masivo completado: {results['successful']}/{results['total_emails']} exitosos")
        return results


# Instancias globales del servicio
email_service = EmailService()
email_notification_service = EmailNotificationService()


def send_email_notification(
    user_email: str,
    notification_type: str,
    context: Dict[str, Any],
    subject_override: str = None
) -> Dict[str, Any]:
    """
    Enva notificaciones por correo (recuperacin, verificacin, etc.) usando Gmail SMTP.
    Mejorada para evitar bloqueos y filtrado en SPAM.
    
    Args:
        user_email: Email del destinatario
        notification_type: Tipo de notificacin (password_reset, welcome, etc.)
        context: Contexto para renderizar templates
        subject_override: Asunto personalizado (opcional)
        
    Returns:
        Dict con 'success': True/False y detalles del envo
    """
    try:
        # === Seguridad: validar campos mnimos ===
        if not user_email or '@' not in user_email:
            logger.error(f"[EMAIL] Direccin invlida: {user_email}")
            return {"success": False, "error": "Correo invlido"}

        # === Configurar asunto y plantillas ===
        subject_prefix = getattr(settings, "EMAIL_SUBJECT_PREFIX", "[CacaoScan] ")
        
        # Usar subject_override si se proporciona, sino usar el predeterminado del servicio
        if subject_override:
            subject = subject_override
        else:
            # Intentar obtener asunto del servicio de notificaciones
            try:
                subject = email_notification_service._get_default_subject(notification_type, context)
            except:
                subject = f"{subject_prefix} Notificacin de CacaoScan"

        # Seleccin automtica de template
        html_template = f"emails/{notification_type}.html"
        text_template = f"emails/{notification_type}.txt"

        try:
            html_content = render_to_string(html_template, context)
            text_content = render_to_string(text_template, context)
        except Exception as e:
            logger.error(f"[EMAIL] Error renderizando templates: {e}")
            return {"success": False, "error": f"Error renderizando templates: {str(e)}"}

        # === Configurar remitente profesional ===
        # Usar el mismo email que el usuario autenticado en SMTP para evitar bloqueos de Gmail
        from_email = getattr(
            settings, "DEFAULT_FROM_EMAIL",
            f"CacaoScan <{settings.EMAIL_HOST_USER}>"
        )

        # === Conexin SMTP segura ===
        connection = get_connection(
            backend='django.core.mail.backends.smtp.EmailBackend',
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS,
            timeout=30,
        )

        # === Construir correo ===
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[user_email],
            connection=connection,
            headers={
                "Reply-To": "cacaoscan.soporte@gmail.com",
                "X-Mailer": "CacaoScanMailer",
                "X-Priority": "3",
            },
        )

        email.attach_alternative(html_content, "text/html")

        # === Logs de depuracin ===
        logger.info(f"[DEBUG EMAIL] Intentando enviar a {user_email}")
        logger.info(f"[DEBUG EMAIL] Template HTML: {html_template}")
        logger.info(f"[DEBUG EMAIL] Template TXT: {text_template}")
        logger.info(f"[DEBUG EMAIL] Remitente (from_email): {from_email}")
        logger.info(f"[DEBUG EMAIL] SMTP User: {settings.EMAIL_HOST_USER}")
        logger.info(f"[DEBUG EMAIL] SMTP Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        logger.info(f"[DEBUG EMAIL] TLS habilitado: {settings.EMAIL_USE_TLS}")
        logger.info(f"[DEBUG EMAIL] Asunto: {subject}")
        logger.info(f"[DEBUG EMAIL] Contexto recibido: {list(context.keys())}")

        # === Enviar correo ===
        logger.info(f"[DEBUG EMAIL] Abriendo conexin SMTP...")
        sent_count = email.send(fail_silently=False)
        logger.info(f"[DEBUG EMAIL] Email enviado. Contador: {sent_count}")

        if sent_count:
            logger.info(f"[EMAIL]  Correo '{notification_type}' enviado a {user_email}")
            return {
                "success": True,
                "sent_to": user_email,
                "timestamp": timezone.now().isoformat()
            }
        else:
            logger.warning(f"[EMAIL] [ERROR] Correo no enviado a {user_email}")
            return {"success": False, "error": "No se envi el correo"}

    except Exception as e:
        logger.error(f"[EMAIL] [WARN] Error al enviar correo a {user_email}: {e}", exc_info=True)
        logger.error(f"[DEBUG EMAIL] Tipo de excepcin: {type(e).__name__}")
        logger.error(f"[DEBUG EMAIL] Detalles del error: {str(e)}")
        # Log adicional para errores SMTP especficos
        if hasattr(e, 'smtp_code'):
            logger.error(f"[DEBUG EMAIL] Cdigo SMTP: {e.smtp_code}")
        if hasattr(e, 'smtp_error'):
            logger.error(f"[DEBUG EMAIL] Error SMTP: {e.smtp_error}")

        # === Fallback de emergencia ===
        try:
            # Si Gmail falla, imprimir en consola para debugging
            subject_fallback = subject if 'subject' in locals() else "Notificacin de CacaoScan"
            text_fallback = text_content if 'text_content' in locals() else "Error al renderizar contenido"
            print(f"\n[EMAIL Fallback] --- Envo simulado ---\n"
                  f"Para: {user_email}\n"
                  f"Asunto: {subject_fallback}\n"
                  f"Contenido:\n{text_fallback}\n")
        except Exception:
            pass

        return {"success": False, "error": str(e)}


def send_bulk_email_notification(
    user_emails: List[str],
    notification_type: str,
    context: Dict[str, Any],
    batch_size: int = None
) -> Dict[str, Any]:
    """
    Función helper para enviar notificaciones masivas por email.
    """
    return email_notification_service.send_bulk_notification(
        user_emails, notification_type, context, batch_size
    )


def send_custom_email(
    to_emails: Union[str, List[str]],
    subject: str,
    html_content: str = None,
    text_content: str = None,
    from_email: str = None,
    attachments: List[Dict[str, Any]] = None,
    use_sendgrid: bool = False
) -> Dict[str, Any]:
    """
    Función helper para enviar emails personalizados con fallback TLS/SSL.
    """
    # Intentar primero con TLS, si falla probar SSL
    try:
        return email_service.send_email(
            to_emails, subject, html_content, text_content,
            from_email, attachments, use_sendgrid
        )
    except Exception as e:
        # Si falla y está habilitado el fallback SSL, intentar SSL
        if settings.EMAIL_USE_SSL_FALLBACK and 'smtp' in str(e).lower():
            logger.warning(f"Error con TLS, intentando SSL: {e}")
            # Cambiar configuración temporalmente para SSL
            original_tls = settings.EMAIL_USE_TLS
            original_ssl = settings.EMAIL_USE_SSL
            original_port = settings.EMAIL_PORT
            
            settings.EMAIL_USE_TLS = False
            settings.EMAIL_USE_SSL = True
            settings.EMAIL_PORT = 465
            
            try:
                result = email_service.send_email(
                    to_emails, subject, html_content, text_content,
                    from_email, attachments, use_sendgrid
                )
                return result
            finally:
                # Restaurar configuración original
                settings.EMAIL_USE_TLS = original_tls
                settings.EMAIL_USE_SSL = original_ssl
                settings.EMAIL_PORT = original_port
        else:
            raise


