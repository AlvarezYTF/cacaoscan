"""
Django management command to create a superuser if it doesn't exist.

This command reads configuration from environment variables and only creates
the superuser if explicitly enabled and the user doesn't already exist.

Environment variables:
    DJANGO_CREATE_SUPERUSER: Must be "true" to enable creation (default: disabled)
    DJANGO_SUPERUSER_USERNAME: Username for the superuser (required if enabled)
    DJANGO_SUPERUSER_EMAIL: Email for the superuser (required if enabled)
    DJANGO_SUPERUSER_PASSWORD: Password for the superuser (required if enabled)

This command is idempotent and safe to run multiple times.
It will not create duplicate users or overwrite existing users.
"""
import os
import logging
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

logger = logging.getLogger("cacaoscan.management.createsuperuser_if_not_exists")

User = get_user_model()


class Command(BaseCommand):
    help = (
        "Creates a superuser if it doesn't exist. "
        "Configured via environment variables. Safe to run multiple times."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-if-exists',
            action='store_true',
            help='Skip creation silently if user already exists (default behavior)',
        )

    def handle(self, *args, **options):
        # Read environment variables
        create_superuser = os.environ.get('DJANGO_CREATE_SUPERUSER', '').lower()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', '').strip()
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '').strip()
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '').strip()

        # Check if creation is enabled
        if create_superuser != 'true':
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  DJANGO_CREATE_SUPERUSER is not set to "true". Skipping superuser creation.'
                )
            )
            logger.info("Superuser creation skipped: DJANGO_CREATE_SUPERUSER != 'true'")
            return

        # Validate required environment variables
        if not username:
            self.stdout.write(
                self.style.ERROR(
                    '❌ DJANGO_SUPERUSER_USERNAME is required when DJANGO_CREATE_SUPERUSER=true'
                )
            )
            logger.error("Superuser creation failed: DJANGO_SUPERUSER_USERNAME not provided")
            return

        if not email:
            self.stdout.write(
                self.style.ERROR(
                    '❌ DJANGO_SUPERUSER_EMAIL is required when DJANGO_CREATE_SUPERUSER=true'
                )
            )
            logger.error("Superuser creation failed: DJANGO_SUPERUSER_EMAIL not provided")
            return

        if not password:
            self.stdout.write(
                self.style.ERROR(
                    '❌ DJANGO_SUPERUSER_PASSWORD is required when DJANGO_CREATE_SUPERUSER=true'
                )
            )
            logger.error("Superuser creation failed: DJANGO_SUPERUSER_PASSWORD not provided")
            return

        # Validate password length (Django minimum requirement)
        if len(password) < 8:
            self.stdout.write(
                self.style.ERROR(
                    '❌ DJANGO_SUPERUSER_PASSWORD must be at least 8 characters long'
                )
            )
            logger.error("Superuser creation failed: Password too short")
            return

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Superuser "{username}" already exists. Skipping creation.'
                )
            )
            logger.info(f"Superuser '{username}' already exists, skipping creation")
            return

        # Check if email is already in use by another user
        if User.objects.filter(email=email).exists():
            existing_user = User.objects.get(email=email)
            self.stdout.write(
                self.style.WARNING(
                    f'⚠️  Email "{email}" is already in use by user "{existing_user.username}". '
                    f'Skipping superuser creation to avoid conflicts.'
                )
            )
            logger.warning(
                f"Superuser creation skipped: Email '{email}' already in use by user '{existing_user.username}'"
            )
            return

        # Create the superuser
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_superuser=True,
                is_staff=True,
                is_active=True
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Superuser "{username}" created successfully!'
                )
            )
            self.stdout.write(f'   Username: {user.username}')
            self.stdout.write(f'   Email: {user.email}')
            self.stdout.write(f'   is_superuser: {user.is_superuser}')
            self.stdout.write(f'   is_staff: {user.is_staff}')
            self.stdout.write(f'   is_active: {user.is_active}')
            logger.info(f"Superuser '{username}' created successfully")

        except Exception as e:
            error_msg = f'❌ Error creating superuser: {str(e)}'
            self.stdout.write(self.style.ERROR(error_msg))
            logger.error(f"Error creating superuser: {e}", exc_info=True)
            raise CommandError(error_msg)

