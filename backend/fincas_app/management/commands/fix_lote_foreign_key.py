"""
Comando de Django para corregir la foreign key de fincas_app_lote.
Ejecutar con: python manage.py fix_lote_foreign_key
"""
import re
from psycopg2 import sql
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Corrige la foreign key de fincas_app_lote para que apunte a api_finca en lugar de fincas_app_finca'
    
    def _validate_sql_identifier(self, identifier: str) -> str:
        """
        Valida un identificador SQL para prevenir SQL injection.
        
        Args:
            identifier: Nombre del objeto SQL (tabla, constraint, columna, etc.)
            
        Returns:
            Identificador validado (sin escapar, se escapará con quote_name)
            
        Raises:
            ValueError: Si el identificador contiene caracteres no permitidos
        """
        if not identifier:
            raise ValueError('El identificador SQL no puede estar vacío')
        
        if not isinstance(identifier, str):
            raise ValueError('El identificador SQL debe ser una cadena de texto')
        
        # Limitar longitud para prevenir ataques (PostgreSQL limita a 63 caracteres)
        if len(identifier) > 63:
            raise ValueError(f'Identificador SQL demasiado largo (máximo 63 caracteres): {identifier}')
        
        # Solo permitir letras, números, guiones bajos y guiones
        # Debe comenzar con letra o guion bajo
        if not re.match(r'^[a-zA-Z_]\w*$', identifier):
            raise ValueError(f'Identificador SQL inválido: {identifier}. Solo se permiten letras, números y guiones bajos, y debe comenzar con letra o guion bajo.')
        
        return identifier
    
    def _find_foreign_keys(self, cursor):
        """Busca todas las foreign keys en fincas_app_lote."""
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
        return cursor.fetchall()
    
    def _verify_api_finca_exists(self, cursor) -> bool:
        """Verifica si la tabla api_finca existe."""
        cursor.execute("""
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'api_finca'
        """)
        return cursor.fetchone() is not None
    
    def _drop_incorrect_foreign_key(self, cursor, constraint_name: str) -> bool:
        """Elimina una foreign key incorrecta."""
        try:
            validated_constraint = self._validate_sql_identifier(constraint_name)
            query = sql.SQL(
                'ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {constraint}'
            ).format(
                table=sql.Identifier('fincas_app_lote'),
                constraint=sql.Identifier(validated_constraint),
            )
            cursor.execute(query)
            return True
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f'  [ERROR] Nombre de constraint inválido: {e}'))
            return False
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  [ERROR] Error eliminando FK: {e}'))
            return False
    
    def _create_correct_foreign_key(self, cursor, new_constraint_name: str) -> bool:
        """Crea una foreign key correcta."""
        try:
            validated_constraint = self._validate_sql_identifier(new_constraint_name)
            
            cursor.execute("""
                SELECT constraint_name 
                FROM information_schema.table_constraints
                WHERE constraint_type = 'FOREIGN KEY'
                    AND table_name = 'fincas_app_lote'
                    AND constraint_name = %s;
            """, [validated_constraint])
            
            if cursor.fetchone():
                self.stdout.write(self.style.WARNING(f'  [WARN]  FK correcta ya existe: {new_constraint_name}'))
                return False
            
            query = sql.SQL(
                'ALTER TABLE {table} '
                'ADD CONSTRAINT {constraint} '
                'FOREIGN KEY ({column}) '
                'REFERENCES {ref_table}({ref_column}) '
                'ON DELETE CASCADE'
            ).format(
                table=sql.Identifier('fincas_app_lote'),
                constraint=sql.Identifier(validated_constraint),
                column=sql.Identifier('finca_id'),
                ref_table=sql.Identifier('api_finca'),
                ref_column=sql.Identifier('id'),
            )
            cursor.execute(query)
            return True
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f'  [ERROR] Nombre de constraint inválido: {e}'))
            return False
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  [ERROR] Error creando FK: {e}'))
            return False
    
    def _fix_incorrect_foreign_key(self, cursor, constraint_name: str, foreign_table: str) -> bool:
        """Corrige una foreign key incorrecta."""
        if foreign_table != 'fincas_app_finca':
            return False
        
        self.stdout.write(self.style.WARNING(f'  [WARN]  FK incorrecta: apunta a {foreign_table}, corrigiendo...'))
        
        if not self._drop_incorrect_foreign_key(cursor, constraint_name):
            return False
        
        self.stdout.write(self.style.SUCCESS(f'  ✅ Eliminada FK incorrecta: {constraint_name}'))
        
        new_constraint_name = 'fincas_app_lote_finca_id_api_finca_fk'
        if self._create_correct_foreign_key(cursor, new_constraint_name):
            self.stdout.write(self.style.SUCCESS(f'  ✅ Creada FK correcta: {new_constraint_name}'))
            return True
        
        return False
    
    def _handle_orphaned_lotes(self, cursor):
        """Maneja los lotes huérfanos."""
        cursor.execute("""
            SELECT l.id, l.finca_id, l.identificador
            FROM fincas_app_lote l
            LEFT JOIN api_finca f ON l.finca_id = f.id
            WHERE f.id IS NULL;
        """)
        
        orphaned_lotes = cursor.fetchall()
        
        if not orphaned_lotes:
            self.stdout.write(self.style.SUCCESS('\n✅ No se encontraron lotes huérfanos'))
            return
        
        self.stdout.write(self.style.WARNING(f'\n[WARN]  Advertencia: {len(orphaned_lotes)} lotes huérfanos (sin finca válida)'))
        for lote_id, finca_id, identificador in orphaned_lotes:
            self.stdout.write(f'  - Lote ID: {lote_id}, finca_id: {finca_id}, identificador: {identificador}')
        
        self.stdout.write(self.style.WARNING('\n💡 Estos lotes deben eliminarse o corregirse manualmente'))
        
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
    
    def _verify_final_state(self, cursor):
        """Verifica el estado final de las foreign keys."""
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
        
        return all_correct
    
    def handle(self, *args, **options):
        self.stdout.write('=' * 60)
        self.stdout.write('Corrigiendo foreign key de fincas_app_lote')
        self.stdout.write('=' * 60)
        
        with connection.cursor() as cursor:
            fks = self._find_foreign_keys(cursor)
            
            if not fks:
                self.stdout.write(self.style.WARNING('No se encontró foreign key en fincas_app_lote.finca_id'))
                return
            
            self.stdout.write(f'\nForeign keys encontradas: {len(fks)}')
            
            if not self._verify_api_finca_exists(cursor):
                self.stdout.write(self.style.ERROR('[ERROR] La tabla api_finca no existe'))
                return
            
            fixed = False
            for fk in fks:
                constraint_name, column_name, foreign_table = fk
                self.stdout.write(f'\nFK encontrada: {constraint_name}')
                self.stdout.write(f'  Columna: {column_name}')
                self.stdout.write(f'  Tabla referenciada: {foreign_table}')
                
                if foreign_table == 'api_finca':
                    self.stdout.write(self.style.SUCCESS(f'  ✅ FK correcta: apunta a {foreign_table}'))
                    continue
                
                if self._fix_incorrect_foreign_key(cursor, constraint_name, foreign_table):
                    fixed = True
                else:
                    self.stdout.write(self.style.WARNING(f'  [WARN]  FK apunta a tabla desconocida: {foreign_table}'))
            
            self._handle_orphaned_lotes(cursor)
            self._verify_final_state(cursor)
            
            if fixed:
                self.stdout.write(self.style.SUCCESS('\n✅ Foreign key corregida exitosamente'))
                self.stdout.write('Ahora deberías poder crear lotes correctamente.')

