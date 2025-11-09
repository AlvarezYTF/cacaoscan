"""
Comando de Django para corregir la foreign key de fincas_app_lote.
Ejecutar con: python manage.py fix_lote_foreign_key
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Corrige la foreign key de fincas_app_lote para que apunte a api_finca en lugar de fincas_app_finca'

    def handle(self, *args, **options):
        self.stdout.write('=' * 60)
        self.stdout.write('Corrigiendo foreign key de fincas_app_lote')
        self.stdout.write('=' * 60)
        
        with connection.cursor() as cursor:
            # 1. Buscar todas las foreign keys en fincas_app_lote que apuntan a fincas_app_finca
            cursor.execute("""
                SELECT 
                    tc.constraint_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_name = 'fincas_app_lote'
                    AND kcu.column_name = 'finca_id';
            """)
            
            fks = cursor.fetchall()
            
            if not fks:
                self.stdout.write(self.style.WARNING('No se encontró foreign key en fincas_app_lote.finca_id'))
                return
            
            self.stdout.write(f'\nForeign keys encontradas: {len(fks)}')
            
            # 2. Verificar si api_finca existe
            cursor.execute("""
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_finca'
            """)
            
            if not cursor.fetchone():
                self.stdout.write(self.style.ERROR('[ERROR] La tabla api_finca no existe'))
                return
            
            # 3. Buscar y corregir foreign keys incorrectas
            fixed = False
            for fk in fks:
                constraint_name, column_name, foreign_table = fk
                self.stdout.write(f'\nFK encontrada: {constraint_name}')
                self.stdout.write(f'  Columna: {column_name}')
                self.stdout.write(f'  Tabla referenciada: {foreign_table}')
                
                if foreign_table == 'api_finca':
                    self.stdout.write(self.style.SUCCESS(f'  ✅ FK correcta: apunta a {foreign_table}'))
                    continue
                
                if foreign_table == 'fincas_app_finca':
                    self.stdout.write(self.style.WARNING(f'  [WARN]  FK incorrecta: apunta a {foreign_table}, corrigiendo...'))
                    
                    # Eliminar FK incorrecta
                    try:
                        cursor.execute(f'ALTER TABLE fincas_app_lote DROP CONSTRAINT IF EXISTS "{constraint_name}"')
                        self.stdout.write(self.style.SUCCESS(f'  ✅ Eliminada FK incorrecta: {constraint_name}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  [ERROR] Error eliminando FK: {e}'))
                        continue
                    
                    # Crear nueva FK correcta
                    new_constraint_name = 'fincas_app_lote_finca_id_api_finca_fk'
                    try:
                        # Primero verificar si ya existe una FK correcta
                        cursor.execute("""
                            SELECT constraint_name 
                            FROM information_schema.table_constraints
                            WHERE constraint_type = 'FOREIGN KEY'
                                AND table_name = 'fincas_app_lote'
                                AND constraint_name = %s;
                        """, [new_constraint_name])
                        
                        if cursor.fetchone():
                            self.stdout.write(self.style.WARNING(f'  [WARN]  FK correcta ya existe: {new_constraint_name}'))
                        else:
                            cursor.execute(f"""
                                ALTER TABLE fincas_app_lote
                                ADD CONSTRAINT "{new_constraint_name}"
                                FOREIGN KEY (finca_id)
                                REFERENCES api_finca(id)
                                ON DELETE CASCADE
                            """)
                            self.stdout.write(self.style.SUCCESS(f'  ✅ Creada FK correcta: {new_constraint_name}'))
                            fixed = True
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  [ERROR] Error creando FK: {e}'))
                else:
                    self.stdout.write(self.style.WARNING(f'  [WARN]  FK apunta a tabla desconocida: {foreign_table}'))
            
            # 4. Verificar y limpiar lotes huérfanos
            cursor.execute("""
                SELECT l.id, l.finca_id, l.identificador
                FROM fincas_app_lote l
                LEFT JOIN api_finca f ON l.finca_id = f.id
                WHERE f.id IS NULL;
            """)
            
            orphaned_lotes = cursor.fetchall()
            
            if orphaned_lotes:
                self.stdout.write(self.style.WARNING(f'\n[WARN]  Advertencia: {len(orphaned_lotes)} lotes huérfanos (sin finca válida)'))
                for lote_id, finca_id, identificador in orphaned_lotes:
                    self.stdout.write(f'  - Lote ID: {lote_id}, finca_id: {finca_id}, identificador: {identificador}')
                
                # Preguntar si se deben eliminar
                self.stdout.write(self.style.WARNING('\n💡 Estos lotes deben eliminarse o corregirse manualmente'))
                
                # Intentar eliminar lotes huérfanos que no tienen imágenes asociadas
                cursor.execute("""
                    DELETE FROM fincas_app_lote 
                    WHERE id IN (
                        SELECT l.id 
                        FROM fincas_app_lote l
                        LEFT JOIN api_finca f ON l.finca_id = f.id
                        LEFT JOIN images_app_cacaoimage img ON img.lote_id = l.id
                        WHERE f.id IS NULL AND img.id IS NULL
                    );
                """)
                deleted = cursor.rowcount
                if deleted > 0:
                    self.stdout.write(self.style.SUCCESS(f'✅ Eliminados {deleted} lotes huérfanos sin imágenes asociadas'))
            else:
                self.stdout.write(self.style.SUCCESS('\n✅ No se encontraron lotes huérfanos'))
            
            # 5. Verificar que la corrección funcionó
            cursor.execute("""
                SELECT 
                    tc.constraint_name,
                    ccu.table_name AS foreign_table_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_name = 'fincas_app_lote'
                    AND kcu.column_name = 'finca_id';
            """)
            
            final_fks = cursor.fetchall()
            
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write('Verificación final')
            self.stdout.write('=' * 60)
            
            all_correct = True
            for fk in final_fks:
                constraint_name, foreign_table = fk
                status = '✅' if foreign_table == 'api_finca' else '[ERROR]'
                self.stdout.write(f'{status} {constraint_name} -> {foreign_table}')
                if foreign_table != 'api_finca':
                    all_correct = False
            
            if all_correct:
                self.stdout.write(self.style.SUCCESS('\n✅ Todas las foreign keys están correctamente configuradas'))
            else:
                self.stdout.write(self.style.ERROR('\n[ERROR] Aún hay foreign keys incorrectas'))
            
            if fixed:
                self.stdout.write(self.style.SUCCESS('\n✅ Foreign key corregida exitosamente'))
                self.stdout.write('Ahora deberías poder crear lotes correctamente.')

