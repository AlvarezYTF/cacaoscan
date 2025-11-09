"""
Comando de gestión para subir imágenes locales al bucket S3.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pathlib import Path
from images_app.models import CacaoImage
import mimetypes


class Command(BaseCommand):
    help = 'Sube imágenes locales al bucket S3 (o almacenamiento configurado)'

    def add_arguments(self, parser):
        parser.add_argument(
            'folder',
            type=str,
            help='Ruta de la carpeta que contiene las imágenes a subir'
        )
        parser.add_argument(
            '--user',
            type=str,
            default=None,
            help='Username del usuario propietario de las imágenes (default: primer superusuario)'
        )
        parser.add_argument(
            '--finca-id',
            type=int,
            default=None,
            help='ID de la finca a asociar con las imágenes'
        )
        parser.add_argument(
            '--extensions',
            type=str,
            nargs='+',
            default=['.png', '.jpg', '.jpeg', '.webp'],
            help='Extensiones de archivo permitidas (default: .png .jpg .jpeg .webp)'
        )

    def handle(self, *args, **options):
        folder_path = Path(options['folder'])
        
        if not folder_path.exists():
            self.stdout.write(
                self.style.ERROR(f'[ERROR] La carpeta {folder_path} no existe')
            )
            return
        
        if not folder_path.is_dir():
            self.stdout.write(
                self.style.ERROR(f'[ERROR] {folder_path} no es una carpeta')
            )
            return

        # Obtener usuario
        user = None
        if options['user']:
            try:
                user = User.objects.get(username=options['user'])
            except User.DoesNotExist:
                username = options['user']
                self.stdout.write(
                    self.style.ERROR(f'[ERROR] Usuario {username} no encontrado')
                )
                return
        else:
            # Usar el primer superusuario disponible
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                self.stdout.write(
                    self.style.ERROR('[ERROR] No se encontró ningún superusuario. Use --user para especificar un usuario.')
                )
                return

        self.stdout.write(f'👤 Usuario: {user.username}')

        # Obtener finca si se especifica
        finca = None
        if options['finca_id']:
            try:
                from fincas_app.models import Finca
                finca = Finca.objects.get(id=options['finca_id'])
                self.stdout.write(f'🏡 Finca: {finca.nombre}')
            except Finca.DoesNotExist:
                finca_id = options['finca_id']
                self.stdout.write(
                    self.style.WARNING(f'[WARN]  Finca con ID {finca_id} no encontrada. Continuando sin finca...')
                )

        # Buscar imágenes
        extensions = options['extensions']
        image_files = []
        for ext in extensions:
            image_files.extend(folder_path.glob(f'*{ext}'))
            image_files.extend(folder_path.glob(f'*{ext.upper()}'))

        if not image_files:
            self.stdout.write(
                self.style.WARNING(f'[WARN]  No se encontraron imágenes con extensiones {extensions} en {folder_path}')
            )
            return

        self.stdout.write(f'📸 Encontradas {len(image_files)} imágenes')
        self.stdout.write('📤 Subiendo imágenes...')

        uploaded_count = 0
        error_count = 0

        for idx, img_path in enumerate(image_files, 1):
            try:
                # Determinar content type
                content_type, _ = mimetypes.guess_type(str(img_path))
                if not content_type:
                    content_type = 'image/jpeg'  # Default

                # Abrir y crear imagen
                with open(img_path, 'rb') as f:
                    cacao_image = CacaoImage(
                        user=user,
                        image=f,
                        file_name=img_path.name,
                        file_size=img_path.stat().st_size,
                        file_type=content_type,
                        processed=False
                    )
                    
                    if finca:
                        cacao_image.finca = finca
                    
                    cacao_image.save()
                    
                    uploaded_count += 1
                    
                    if idx % 10 == 0:
                        self.stdout.write(f'  ✅ Procesadas {idx}/{len(image_files)} imágenes...')

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'  [ERROR] Error procesando {img_path.name}: {str(e)}')
                )

        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Proceso completado!\n'
                f'   📸 Imágenes subidas: {uploaded_count}\n'
                f'   [ERROR] Errores: {error_count}'
            )
        )

