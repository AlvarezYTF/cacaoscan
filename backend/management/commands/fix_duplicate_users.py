from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from collections import Counter

User = get_user_model()


class Command(BaseCommand):
    help = 'Encuentra y elimina usuarios duplicados por email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo mostrar usuarios duplicados sin eliminarlos',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Eliminar usuarios duplicados (mantiene el mÃ¡s reciente)',
        )

    def handle(self, *args, **options):
        # Encontrar emails duplicados
        emails = Counter(User.objects.values_list('email', flat=True))
        duplicates = {email: count for email, count in emails.items() if count > 1}
        
        if not duplicates:
            self.stdout.write(self.style.SUCCESS('âœ“ No hay usuarios duplicados'))
            return
        
        self.stdout.write(self.style.WARNING(f'âš  Se encontraron {len(duplicates)} emails duplicados:\n'))
        
        total_to_delete = 0
        for email, count in duplicates.items():
            users = User.objects.filter(email=email).order_by('-date_joined')
            self.stdout.write(f'\nðŸ“§ Email: {email} ({count} usuarios)')
            
            # Mostrar informaciÃ³n de cada usuario
            for i, user in enumerate(users):
                status = 'âœ“ MANTENER' if i == 0 else 'âœ— ELIMINAR'
                role = user.role if hasattr(user, 'role') else 'N/A'
                self.stdout.write(
                    f'  [{status}] ID: {user.id}, Username: {user.username}, '
                    f'Role: {role}, Fecha: {user.date_joined.strftime("%Y-%m-%d %H:%M")}'
                )
            
            total_to_delete += count - 1
        
        # Si es --dry-run, no eliminar
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(f'\nâš  DRY RUN: {total_to_delete} usuarios serÃ­an eliminados')
            )
            self.stdout.write('   Ejecuta con --delete para eliminar duplicados')
            return
        
        # Si no es --delete, no eliminar
        if not options['delete']:
            self.stdout.write(
                self.style.ERROR('\nâœ— No se eliminaron usuarios. Agrega --delete para confirmar')
            )
            return
        
        # Eliminar duplicados (mantener el mÃ¡s reciente de cada email)
        deleted_count = 0
        for email in duplicates.keys():
            users = User.objects.filter(email=email).order_by('-date_joined')
            # Mantener el primero (mÃ¡s reciente), eliminar los demÃ¡s
            for user in users[1:]:
                username = user.username
                user.delete()
                deleted_count += 1
                self.stdout.write(f'âœ“ Eliminado: {username} (ID: {user.id})')
        
        self.stdout.write(
            self.style.SUCCESS(f'\nâœ“ Eliminados {deleted_count} usuarios duplicados')
        )


