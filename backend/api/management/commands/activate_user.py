"""
Django management command to activate and verify a user.
"""
import logging
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction

logger = logging.getLogger("cacaoscan.management.activate_user")


class Command(BaseCommand):
    help = 'Activa y verifica un usuario. Útil para usuarios admin que no necesitan verificación de email.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Nombre de usuario a activar'
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email del usuario a activar'
        )

    def handle(self, *args, **options):
        username = options.get('username')
        email = options.get('email')
        
        if not username and not email:
            raise CommandError("Debe proporcionar --username o --email")
        
        try:
            with transaction.atomic():
                # Buscar usuario
                if username:
                    try:
                        user = User.objects.get(username=username)
                    except User.DoesNotExist:
                        raise CommandError(f"Usuario con username '{username}' no encontrado")
                elif email:
                    try:
                        user = User.objects.get(email=email)
                    except User.DoesNotExist:
                        raise CommandError(f"Usuario con email '{email}' no encontrado")
                    except User.MultipleObjectsReturned:
                        raise CommandError(f"Múltiples usuarios con email '{email}'. Use --username en su lugar")
                
                # Activar usuario
                user.is_active = True
                user.save()
                
                # Verificar email token si existe
                if hasattr(user, 'auth_email_token'):
                    user.auth_email_token.is_verified = True
                    user.auth_email_token.save()
                    logger.info(f"Email token verificado para usuario {user.username}")
                
                if hasattr(user, 'email_verification_token'):
                    user.email_verification_token.is_verified = True
                    user.email_verification_token.save()
                    logger.info(f"Email verification token verificado para usuario {user.username}")
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Usuario {user.username} activado y verificado exitosamente')
                )
                self.stdout.write(f'  Username: {user.username}')
                self.stdout.write(f'  Email: {user.email}')
                self.stdout.write(f'  is_active: {user.is_active}')
                self.stdout.write(f'  is_superuser: {user.is_superuser}')
                self.stdout.write(f'  is_staff: {user.is_staff}')
                
        except CommandError:
            raise
        except Exception as e:
            logger.error(f"Error activando usuario: {e}", exc_info=True)
            raise CommandError(f'Error al activar usuario: {str(e)}')

