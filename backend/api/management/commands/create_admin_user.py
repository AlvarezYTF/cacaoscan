"""
Django management command to create or update an admin user.
"""
import logging
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction

logger = logging.getLogger("cacaoscan.management.create_admin_user")


class Command(BaseCommand):
    help = 'Crea o actualiza un usuario administrador. Si el usuario ya existe, se actualiza con los nuevos valores.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Nombre de usuario del administrador (default: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@cacaoscan.com',
            help='Email del administrador (default: admin@cacaoscan.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Contraseña del administrador (default: admin123)'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            default='Admin',
            help='Nombre del administrador (default: Admin)'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            default='User',
            help='Apellido del administrador (default: User)'
        )
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='No solicitar confirmación interactiva'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']
        no_input = options['no_input']
        
        logger.info(f"Creating/updating admin user: {username}")
        
        try:
            with transaction.atomic():
                # Verificar si el usuario ya existe
                if User.objects.filter(username=username).exists():
                    user = User.objects.get(username=username)
                    logger.info(f"User {username} already exists, updating...")
                    
                    user.email = email
                    user.set_password(password)
                    user.first_name = first_name
                    user.last_name = last_name
                    user.is_superuser = True
                    user.is_staff = True
                    user.is_active = True
                    user.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Usuario {username} actualizado como administrador')
                    )
                    logger.info(f"User {username} updated successfully")
                else:
                    # Verificar si el email ya está en uso
                    if User.objects.filter(email=email).exists():
                        existing_user = User.objects.get(email=email)
                        raise CommandError(f'Email {email} already in use by user {existing_user.username}')
                    
                    # Crear nuevo usuario
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        is_superuser=True,
                        is_staff=True,
                        is_active=True
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS('✅ Usuario administrador creado exitosamente:')
                    )
                    logger.info(f"User {username} created successfully")
                
                # Mostrar información del usuario
                self.stdout.write(f'  Username: {user.username}')
                self.stdout.write(f'  Email: {user.email}')
                self.stdout.write(f'  Password: {password}')
                self.stdout.write(f'  is_superuser: {user.is_superuser}')
                self.stdout.write(f'  is_staff: {user.is_staff}')
                self.stdout.write(f'  is_active: {user.is_active}')
                
        except CommandError:
            raise
        except Exception as e:
            logger.error(f"Error creating/updating admin user: {e}", exc_info=True)
            raise CommandError(f'Error al crear/actualizar usuario administrador: {str(e)}')

