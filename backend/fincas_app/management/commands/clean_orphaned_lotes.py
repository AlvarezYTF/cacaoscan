"""
Comando para limpiar lotes huérfanos que no tienen finca válida.
Ejecutar con: python manage.py clean_orphaned_lotes
"""
from django.core.management.base import BaseCommand
from django.db import connection
from fincas_app.models import Lote, Finca


class Command(BaseCommand):
    help = 'Elimina lotes huérfanos que no tienen finca válida en api_finca'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué se eliminaría sin hacer cambios',
        )

    def _get_image_count(self, cursor, lote_id: int) -> int:
        """Get image count for a lote."""
        cursor.execute("""
            SELECT COUNT(*) 
            FROM images_app_cacaoimage 
            WHERE lote_id = %s;
        """, [lote_id])
        return cursor.fetchone()[0]
    
    def _check_and_display_lotes(self, cursor, orphaned_lotes):
        """Check and display orphaned lotes with their image counts."""
        self.stdout.write(f'\n[WARN]  Encontrados {len(orphaned_lotes)} lotes huérfanos:')
        for lote_id, finca_id, identificador, variedad in orphaned_lotes:
            self.stdout.write(f'  - Lote ID: {lote_id}, finca_id: {finca_id}, identificador: {identificador}, variedad: {variedad}')
        
        for lote_id, finca_id, identificador, variedad in orphaned_lotes:
            image_count = self._get_image_count(cursor, lote_id)
            
            if image_count > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f'  [WARN]  Lote {lote_id} ({identificador}) tiene {image_count} imagen(es) asociada(s) - NO se eliminará'
                    )
                )
            else:
                self.stdout.write(f'  ✅ Lote {lote_id} ({identificador}) no tiene imágenes - puede eliminarse')
    
    def _delete_orphaned_lotes(self, cursor, orphaned_lotes) -> int:
        """Delete orphaned lotes without images. Returns deleted count."""
        deleted_count = 0
        for lote_id, finca_id, identificador, variedad in orphaned_lotes:
            image_count = self._get_image_count(cursor, lote_id)
            
            if image_count == 0:
                try:
                    cursor.execute("DELETE FROM fincas_app_lote WHERE id = %s", [lote_id])
                    deleted_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✅ Eliminado lote {lote_id} ({identificador})')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  [ERROR] Error eliminando lote {lote_id}: {e}')
                    )
        return deleted_count

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write('=' * 60)
        self.stdout.write('Limpiando lotes huérfanos')
        self.stdout.write('=' * 60)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('[WARN]  MODO DRY-RUN: No se realizarán cambios'))
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT l.id, l.finca_id, l.identificador, l.variedad
                FROM fincas_app_lote l
                LEFT JOIN api_finca f ON l.finca_id = f.id
                WHERE f.id IS NULL;
            """)
            
            orphaned_lotes = cursor.fetchall()
            
            if not orphaned_lotes:
                self.stdout.write(self.style.SUCCESS('\n✅ No se encontraron lotes huérfanos'))
                return
            
            self._check_and_display_lotes(cursor, orphaned_lotes)
            
            if dry_run:
                self.stdout.write(self.style.WARNING('\n💡 Ejecuta sin --dry-run para eliminar los lotes sin imágenes'))
                return
            
            deleted_count = self._delete_orphaned_lotes(cursor, orphaned_lotes)
            
            if deleted_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n✅ Se eliminaron {deleted_count} lotes huérfanos sin imágenes'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        '\n[WARN]  No se eliminó ningún lote (todos tienen imágenes asociadas)'
                    )
                )
            
            finca_count = Finca.objects.count()
            self.stdout.write(f'\n📊 Fincas disponibles en api_finca: {finca_count}')

