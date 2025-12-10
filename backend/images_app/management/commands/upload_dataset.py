"""
Comando de gestión para subir imágenes locales al bucket S3.
"""
from typing import Optional
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files import File
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

    def _validate_folder(self, folder_path: Path) -> bool:
        """Valida que la carpeta existe y es un directorio."""
        if not folder_path.exists():
            self.stdout.write(
                self.style.ERROR(f'[ERROR] La carpeta {folder_path} no existe')
            )
            return False
        
        if not folder_path.is_dir():
            self.stdout.write(
                self.style.ERROR(f'[ERROR] {folder_path} no es una carpeta')
            )
            return False
        
        return True
    
    def _get_user(self, username: Optional[str]) -> Optional[User]:
        """Obtiene el usuario por username o el primer superusuario."""
        if username:
            try:
                return User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'[ERROR] Usuario {username} no encontrado')
                )
                return None
        
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            self.stdout.write(
                self.style.ERROR('[ERROR] No se encontró ningún superusuario. Use --user para especificar un usuario.')
            )
        return user
    
    def _get_finca(self, finca_id: Optional[int]):
        """Obtiene la finca si se especifica."""
        if not finca_id:
            return None
        
        try:
            from fincas_app.models import Finca
            finca = Finca.objects.get(id=finca_id)
            self.stdout.write(f'🏡 Finca: {finca.nombre}')
            return finca
        except Finca.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(f'[WARN]  Finca con ID {finca_id} no encontrada. Continuando sin finca...')
            )
            return None
    
    def _find_image_files(self, folder_path: Path, extensions: list) -> list:
        """Busca archivos de imagen en la carpeta."""
        image_files = []
        seen_paths = set()
        for ext in extensions:
            # Search for lowercase and uppercase extensions
            for pattern in [f'*{ext}', f'*{ext.upper()}']:
                for file_path in folder_path.glob(pattern):
                    # Use absolute resolved path to avoid duplicates on case-insensitive filesystems
                    abs_path = file_path.resolve()
                    if abs_path not in seen_paths:
                        seen_paths.add(abs_path)
                        image_files.append(file_path)
        return image_files
    
    def _get_content_type(self, img_path: Path) -> str:
        """Determina el content type del archivo."""
        content_type, _ = mimetypes.guess_type(str(img_path))
        return content_type if content_type else 'image/jpeg'
    
    def _upload_single_image(self, img_path: Path, user: User, finca, idx: int, total: int) -> bool:
        """Sube una sola imagen."""
        try:
            content_type = self._get_content_type(img_path)
            
            from images_app.utils import get_tipo_archivo_from_mime_type
            tipo_archivo = get_tipo_archivo_from_mime_type(content_type)
            
            with open(img_path, 'rb') as f:
                django_file = File(f, name=img_path.name)
                cacao_image = CacaoImage(
                    user=user,
                    image=django_file,
                    file_name=img_path.name,
                    file_size=img_path.stat().st_size,
                    file_type=tipo_archivo,
                    processed=False
                )
                
                if finca:
                    cacao_image.finca = finca
                
                cacao_image.save()
                
                if idx % 10 == 0:
                    self.stdout.write(f'  ✅ Procesadas {idx}/{total} imágenes...')
                
                return True
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  [ERROR] Error procesando {img_path.name}: {str(e)}')
            )
            return False
    
    def handle(self, *args, **options):
        folder_path = Path(options['folder'])
        
        if not self._validate_folder(folder_path):
            return
        
        user = self._get_user(options.get('user'))
        if not user:
            return
        
        self.stdout.write(f'👤 Usuario: {user.username}')
        
        finca = self._get_finca(options.get('finca_id'))
        
        extensions = options['extensions']
        image_files = self._find_image_files(folder_path, extensions)
        
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
            if self._upload_single_image(img_path, user, finca, idx, len(image_files)):
                uploaded_count += 1
            else:
                error_count += 1
        
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Proceso completado!\n'
                f'   📸 Imágenes subidas: {uploaded_count}\n'
                f'   [ERROR] Errores: {error_count}'
            )
        )

