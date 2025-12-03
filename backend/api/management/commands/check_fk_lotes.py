"""
Django management command to check and fix foreign key constraints for Lote model.
"""
import logging
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from api.utils.model_imports import get_models_safely

logger = logging.getLogger("cacaoscan.management.check_fk_lotes")

models = get_models_safely({
    'Finca': 'fincas_app.models.Finca',
    'Lote': 'fincas_app.models.Lote'
})
Finca = models['Finca']
Lote = models['Lote']


class Command(BaseCommand):
    help = 'Verifica y corrige la foreign key de fincas_app_lote.finca_id. Verifica consistencia de datos y detecta lotes huérfanos.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Corregir automáticamente las foreign keys incorrectas'
        )
        parser.add_argument(
            '--check-orphans',
            action='store_true',
            help='Verificar y reportar lotes huérfanos (sin finca válida)'
        )

    def handle(self, *args, **options):
        if Finca is None or Lote is None:
            logger.error("Finca or Lote models not available")
            raise CommandError('Modelos Finca o Lote no están disponibles. Verifica que la app fincas_app esté instalada.')

        fix = options.get('fix', False)
        check_orphans = options.get('check_orphans', True)
        
        logger.info(f"Checking FK constraints for Lote model (fix={fix}, check_orphans={check_orphans})")
        
        try:
            self.stdout.write("=" * 60)
            self.stdout.write("Verificando foreign key de fincas_app_lote")
            self.stdout.write("=" * 60)
            
            # Información del modelo
            self.stdout.write("\n📋 Información de modelos:")
            self.stdout.write(f"   Tabla Finca: {Finca._meta.db_table}")
            self.stdout.write(f"   Tabla Lote: {Lote._meta.db_table}")
            
            # Verificar foreign keys
            fk_issues = self._check_foreign_keys(fix)
            
            # Verificar consistencia de datos
            if check_orphans:
                self._check_data_consistency()
            
            # Resumen
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("Verificación completada")
            self.stdout.write("=" * 60)
            
            if fk_issues:
                if fix:
                    self.stdout.write(self.style.SUCCESS("\n✅ Foreign keys corregidas"))
                else:
                    self.stdout.write(self.style.WARNING("\n⚠️  Se encontraron problemas. Usa --fix para corregirlos automáticamente."))
            else:
                self.stdout.write(self.style.SUCCESS("\n✅ No se encontraron problemas con las foreign keys"))
            
        except CommandError:
            raise
        except Exception as e:
            logger.error(f"Error checking FK constraints: {e}", exc_info=True)
            raise CommandError(f'Error al verificar foreign keys: {str(e)}')

    def _get_foreign_keys(self, cursor) -> list:
        """Obtiene las foreign keys de la tabla fincas_app_lote."""
        cursor.execute("""
            SELECT 
                tc.constraint_name,
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
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
    
    def _check_table_exists(self, cursor, table_name: str) -> bool:
        """Verifica si una tabla existe."""
        cursor.execute("""
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        """, [table_name])
        return cursor.fetchone() is not None
    
    def _validate_identifier(self, identifier: str) -> str:
        """
        Valida y escapa un identificador SQL para prevenir inyección SQL.
        Solo permite caracteres alfanuméricos, guiones bajos y guiones.
        """
        if identifier is None:
            raise ValueError("Identifier must be a non-empty string")
        
        if not isinstance(identifier, str):
            raise ValueError("Identifier must be a non-empty string")
        
        if not identifier:
            raise ValueError("Identifier must be a non-empty string")
        
        # Solo permitir caracteres alfanuméricos, guiones bajos y guiones
        # No permitir guiones (solo guiones bajos)
        if not identifier.replace('_', '').isalnum():
            raise ValueError(f"Invalid identifier: {identifier} contains invalid characters")
        
        # Escapar comillas dobles en el identificador (PostgreSQL escape)
        escaped = identifier.replace('"', '""')
        return escaped
    
    def _build_drop_constraint_query(self, table_name: str, constraint_name: str) -> str:
        """
        Construye una consulta DDL segura para eliminar una constraint.
        Valida y escapa los identificadores antes de construir la consulta.
        """
        safe_table_name = self._validate_identifier(table_name)
        safe_constraint_name = self._validate_identifier(constraint_name)
        
        # Build query using string concatenation with validated identifiers
        # This is safe because both identifiers are validated to only contain whitelisted characters
        query = 'ALTER TABLE "' + safe_table_name + '" DROP CONSTRAINT IF EXISTS "' + safe_constraint_name + '"'
        return query
    
    def _build_add_constraint_query(self, table_name: str, constraint_name: str, 
                                    column_name: str, ref_table: str, ref_column: str) -> str:
        """
        Construye una consulta DDL segura para agregar una foreign key constraint.
        Valida y escapa todos los identificadores antes de construir la consulta.
        """
        safe_table_name = self._validate_identifier(table_name)
        safe_constraint_name = self._validate_identifier(constraint_name)
        safe_column_name = self._validate_identifier(column_name)
        safe_ref_table = self._validate_identifier(ref_table)
        safe_ref_column = self._validate_identifier(ref_column)
        
        # Build query using string concatenation with validated identifiers
        # This is safe because all identifiers are validated to only contain whitelisted characters
        query = (
            'ALTER TABLE "' + safe_table_name + '" '
            'ADD CONSTRAINT "' + safe_constraint_name + '" '
            'FOREIGN KEY ("' + safe_column_name + '") '
            'REFERENCES "' + safe_ref_table + '"("' + safe_ref_column + '") '
            'ON DELETE CASCADE'
        )
        return query
    
    def _create_foreign_key(self, cursor, constraint_name: str):
        """
        Crea una foreign key.
        El nombre de la constraint se valida y escapa antes de usarse en la consulta DDL.
        """
        # Build safe DDL query using validated identifiers
        query = self._build_add_constraint_query(
            table_name='fincas_app_lote',
            constraint_name=constraint_name,
            column_name='finca_id',
            ref_table='api_finca',
            ref_column='id'
        )
        cursor.execute(query)
    
    def _handle_missing_foreign_key(self, cursor, fix: bool) -> bool:
        """Maneja el caso cuando no se encuentra foreign key."""
        self.stdout.write(self.style.WARNING("\n⚠️  No se encontró foreign key en fincas_app_lote.finca_id"))
        
        if not fix:
            return True
        
        self.stdout.write("🔧 Creando foreign key...")
        try:
            with transaction.atomic():
                if not self._check_table_exists(cursor, 'api_finca'):
                    raise CommandError('La tabla api_finca no existe')
                
                constraint_name = 'fincas_app_lote_finca_id_api_finca_fk'
                self._create_foreign_key(cursor, constraint_name)
                self.stdout.write(self.style.SUCCESS(f"✅ Foreign key creada: {constraint_name}"))
                logger.info(f"FK created: {constraint_name}")
                return False
        except CommandError:
            raise
        except Exception as e:
            logger.error(f"Error creating FK: {e}", exc_info=True)
            raise CommandError(f'Error al crear foreign key: {str(e)}')
    
    def _fix_incorrect_foreign_key(self, cursor, constraint_name: str, foreign_table: str):
        """Corrige una foreign key incorrecta."""
        self.stdout.write("🔧 Corrigiendo foreign key...")
        with transaction.atomic():
            # Build safe DDL query using validated identifiers
            drop_query = self._build_drop_constraint_query(
                table_name='fincas_app_lote',
                constraint_name=constraint_name
            )
            cursor.execute(drop_query)
            self.stdout.write(self.style.SUCCESS(f"✅ Eliminada FK incorrecta: {constraint_name}"))
            logger.info(f"FK dropped: {constraint_name}")
            
            # Build new constraint name safely
            new_constraint_name = constraint_name.replace(foreign_table, 'api_finca')
            # Validate the new constraint name before using it
            self._validate_identifier(new_constraint_name)
            
            self._create_foreign_key(cursor, new_constraint_name)
            self.stdout.write(self.style.SUCCESS(f"✅ Creada FK correcta: {new_constraint_name}"))
            logger.info(f"FK created: {new_constraint_name}")
    
    def _check_foreign_keys(self, fix: bool) -> bool:
        """Check and optionally fix foreign key constraints."""
        issues_found = False
        
        with connection.cursor() as cursor:
            fks = self._get_foreign_keys(cursor)
            
            if not fks:
                return self._handle_missing_foreign_key(cursor, fix)
            
            self.stdout.write(f"\n📋 Foreign keys encontradas: {len(fks)}")
            for fk in fks:
                constraint_name, table_name, column_name, foreign_table, foreign_column = fk
                self.stdout.write(f"  - {constraint_name}: {table_name}.{column_name} -> {foreign_table}.{foreign_column}")
                
                if foreign_table != 'api_finca':
                    self.stdout.write(
                        self.style.WARNING(
                            f"\n⚠️  PROBLEMA: FK apunta a '{foreign_table}' pero debería apuntar a 'api_finca'"
                        )
                    )
                    issues_found = True
                    
                    if fix:
                        try:
                            self._fix_incorrect_foreign_key(cursor, constraint_name, foreign_table)
                        except CommandError:
                            raise
                        except Exception as e:
                            logger.error(f"Error fixing FK: {e}", exc_info=True)
                            raise CommandError(f'Error al corregir foreign key: {str(e)}')
                    else:
                        self.stdout.write("   Usa --fix para corregir automáticamente")
                else:
                    self.stdout.write(self.style.SUCCESS(f"   ✅ FK correcta: apunta a {foreign_table}"))
        
        return issues_found

    def _check_data_consistency(self):
        """Check data consistency and orphaned records."""
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("Verificando consistencia de datos")
        self.stdout.write("=" * 60)
        
        # Contar fincas
        try:
            total_fincas = Finca.objects.count()
            self.stdout.write(f"\n📊 Total de fincas en BD: {total_fincas}")
            
            if total_fincas > 0:
                fincas_list = list(Finca.objects.values('id', 'nombre')[:10])
                self.stdout.write("   Primeras fincas:")
                for f in fincas_list:
                    self.stdout.write(f"     - ID: {f['id']}, Nombre: {f['nombre']}")
        except Exception as e:
            logger.warning(f"Error counting fincas: {e}")
            self.stdout.write(self.style.WARNING(f"   ⚠️  Error al contar fincas: {e}"))
        
        # Verificar lotes huérfanos
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT l.id, l.finca_id, f.id as finca_exists
                    FROM fincas_app_lote l
                    LEFT JOIN api_finca f ON l.finca_id = f.id
                    WHERE f.id IS NULL
                    LIMIT 10;
                """)
                
                orphaned_lotes = cursor.fetchall()
                
                if orphaned_lotes:
                    self.stdout.write(
                        self.style.WARNING(f"\n⚠️  Lotes huérfanos encontrados: {len(orphaned_lotes)}")
                    )
                    self.stdout.write("   Lotes sin finca válida:")
                    for lote in orphaned_lotes:
                        self.stdout.write(f"     - Lote ID: {lote[0]}, finca_id: {lote[1]}")
                    logger.warning(f"Found {len(orphaned_lotes)} orphaned lotes")
                else:
                    self.stdout.write(self.style.SUCCESS("\n✅ No se encontraron lotes huérfanos"))
        except Exception as e:
            logger.error(f"Error checking orphaned lotes: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR(f"   ❌ Error al verificar lotes huérfanos: {e}"))

