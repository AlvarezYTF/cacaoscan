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
            self.stdout.write(f"\n📋 Información de modelos:")
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
            
        except Exception as e:
            logger.error(f"Error checking FK constraints: {e}", exc_info=True)
            raise CommandError(f'Error al verificar foreign keys: {str(e)}')

    def _check_foreign_keys(self, fix: bool) -> bool:
        """Check and optionally fix foreign key constraints."""
        issues_found = False
        
        with connection.cursor() as cursor:
            # Verificar foreign keys actuales
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
            
            fks = cursor.fetchall()
            
            if not fks:
                self.stdout.write(self.style.WARNING("\n⚠️  No se encontró foreign key en fincas_app_lote.finca_id"))
                issues_found = True
                
                if fix:
                    self.stdout.write("🔧 Creando foreign key...")
                    try:
                        with transaction.atomic():
                            # Verificar si la tabla api_finca existe
                            cursor.execute("""
                                SELECT 1 FROM information_schema.tables 
                                WHERE table_schema = 'public' 
                                AND table_name = 'api_finca'
                            """)
                            
                            if cursor.fetchone():
                                constraint_name = 'fincas_app_lote_finca_id_api_finca_fk'
                                cursor.execute(f"""
                                    ALTER TABLE fincas_app_lote
                                    ADD CONSTRAINT "{constraint_name}"
                                    FOREIGN KEY (finca_id)
                                    REFERENCES api_finca(id)
                                    ON DELETE CASCADE
                                """)
                                self.stdout.write(self.style.SUCCESS(f"✅ Foreign key creada: {constraint_name}"))
                                logger.info(f"FK created: {constraint_name}")
                            else:
                                raise CommandError('La tabla api_finca no existe')
                    except Exception as e:
                        logger.error(f"Error creating FK: {e}", exc_info=True)
                        raise CommandError(f'Error al crear foreign key: {str(e)}')
            else:
                self.stdout.write(f"\n📋 Foreign keys encontradas: {len(fks)}")
                for fk in fks:
                    constraint_name, table_name, column_name, foreign_table, foreign_column = fk
                    self.stdout.write(f"  - {constraint_name}: {table_name}.{column_name} -> {foreign_table}.{foreign_column}")
                    
                    # Verificar si apunta a la tabla correcta
                    if foreign_table != 'api_finca':
                        self.stdout.write(
                            self.style.WARNING(
                                f"\n⚠️  PROBLEMA: FK apunta a '{foreign_table}' pero debería apuntar a 'api_finca'"
                            )
                        )
                        issues_found = True
                        
                        if fix:
                            self.stdout.write(f"🔧 Corrigiendo foreign key...")
                            try:
                                with transaction.atomic():
                                    # Eliminar FK incorrecta
                                    cursor.execute(f'ALTER TABLE fincas_app_lote DROP CONSTRAINT IF EXISTS "{constraint_name}"')
                                    self.stdout.write(self.style.SUCCESS(f"✅ Eliminada FK incorrecta: {constraint_name}"))
                                    logger.info(f"FK dropped: {constraint_name}")
                                    
                                    # Crear FK correcta
                                    new_constraint_name = constraint_name.replace(foreign_table, 'api_finca')
                                    cursor.execute(f"""
                                        ALTER TABLE fincas_app_lote
                                        ADD CONSTRAINT "{new_constraint_name}"
                                        FOREIGN KEY (finca_id)
                                        REFERENCES api_finca(id)
                                        ON DELETE CASCADE
                                    """)
                                    self.stdout.write(self.style.SUCCESS(f"✅ Creada FK correcta: {new_constraint_name}"))
                                    logger.info(f"FK created: {new_constraint_name}")
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

