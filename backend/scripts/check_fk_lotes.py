"""
Script para verificar y corregir la foreign key de fincas_app_lote.
Ejecutar con: python manage.py shell < scripts/check_fk_lotes.py
o directamente: python scripts/check_fk_lotes.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')
django.setup()

from django.db import connection
from fincas_app.models import Finca, Lote


def _validate_identifier(identifier: str) -> str:
    """
    Valida y escapa un identificador SQL para prevenir inyección SQL.
    Solo permite caracteres alfanuméricos, guiones bajos y guiones.
    
    Args:
        identifier: El identificador a validar
        
    Returns:
        El identificador escapado de forma segura
        
    Raises:
        ValueError: Si el identificador contiene caracteres inválidos
    """
    if not identifier or not isinstance(identifier, str):
        raise ValueError("Identifier must be a non-empty string")
    
    # Solo permitir caracteres alfanuméricos, guiones bajos y guiones
    if not identifier.replace('_', '').replace('-', '').isalnum():
        raise ValueError(f"Invalid identifier: {identifier} contains invalid characters")
    
    # Escapar comillas dobles en el identificador (PostgreSQL escape)
    escaped = identifier.replace('"', '""')
    return escaped


def _build_drop_constraint_query(table_name: str, constraint_name: str) -> str:
    """
    Construye una consulta DDL segura para eliminar una constraint.
    Valida y escapa los identificadores antes de construir la consulta.
    
    SECURITY NOTE: DDL statements (ALTER TABLE, CREATE, etc.) cannot use parameterized
    queries for identifiers (table names, column names, constraint names) because these
    are not supported by PostgreSQL. Instead, we use strict validation and proper
    escaping with double quotes to prevent SQL injection.
    
    Args:
        table_name: Nombre de la tabla
        constraint_name: Nombre de la constraint
        
    Returns:
        Consulta SQL segura
        
    Raises:
        ValueError: Si algún identificador contiene caracteres inválidos
    """
    safe_table_name = _validate_identifier(table_name)
    safe_constraint_name = _validate_identifier(constraint_name)
    
    # Build query using string concatenation with validated and escaped identifiers
    # This is safe because:
    # 1. Both identifiers are validated to only contain whitelisted characters (alphanumeric, _, -)
    # 2. Double quotes are properly escaped ("" -> """")
    # 3. Identifiers are wrapped in double quotes for PostgreSQL
    query = 'ALTER TABLE "' + safe_table_name + '" DROP CONSTRAINT IF EXISTS "' + safe_constraint_name + '"'
    return query


def _build_add_constraint_query(table_name: str, constraint_name: str, 
                                column_name: str, ref_table: str, ref_column: str) -> str:
    """
    Construye una consulta DDL segura para agregar una foreign key constraint.
    Valida y escapa todos los identificadores antes de construir la consulta.
    
    SECURITY NOTE: DDL statements (ALTER TABLE, CREATE, etc.) cannot use parameterized
    queries for identifiers (table names, column names, constraint names) because these
    are not supported by PostgreSQL. Instead, we use strict validation and proper
    escaping with double quotes to prevent SQL injection.
    
    Args:
        table_name: Nombre de la tabla
        constraint_name: Nombre de la constraint
        column_name: Nombre de la columna
        ref_table: Nombre de la tabla referenciada
        ref_column: Nombre de la columna referenciada
        
    Returns:
        Consulta SQL segura
        
    Raises:
        ValueError: Si algún identificador contiene caracteres inválidos
    """
    safe_table_name = _validate_identifier(table_name)
    safe_constraint_name = _validate_identifier(constraint_name)
    safe_column_name = _validate_identifier(column_name)
    safe_ref_table = _validate_identifier(ref_table)
    safe_ref_column = _validate_identifier(ref_column)
    
    # Build query using string concatenation with validated and escaped identifiers
    # This is safe because:
    # 1. All identifiers are validated to only contain whitelisted characters (alphanumeric, _, -)
    # 2. Double quotes are properly escaped ("" -> """")
    # 3. Identifiers are wrapped in double quotes for PostgreSQL
    query = (
        'ALTER TABLE "' + safe_table_name + '" '
        'ADD CONSTRAINT "' + safe_constraint_name + '" '
        'FOREIGN KEY ("' + safe_column_name + '") '
        'REFERENCES "' + safe_ref_table + '"("' + safe_ref_column + '") '
        'ON DELETE CASCADE'
    )
    return query


def _check_existing_foreign_keys(cursor):
    """Check existing foreign keys for fincas_app_lote."""
    # Use parameterized query for string literals to prevent SQL injection
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
        WHERE tc.constraint_type = %s
            AND tc.table_name = %s
            AND kcu.column_name = %s;
    """, ['FOREIGN KEY', 'fincas_app_lote', 'finca_id'])
    return cursor.fetchall()


def _table_exists(cursor, table_name):
    """
    Check if a table exists in the database.
    
    Uses parameterized query with validated identifier to prevent SQL injection.
    The table_name is validated before being used in the query.
    """
    # Validate identifier to prevent SQL injection
    safe_table_name = _validate_identifier(table_name)
    # Use parameterized query for the table name value
    # Note: We still validate the identifier as an extra security layer
    cursor.execute(
        "SELECT 1 FROM information_schema.tables WHERE table_schema = %s AND table_name = %s",
        ['public', safe_table_name]
    )
    return cursor.fetchone() is not None


def _create_missing_foreign_key(cursor):
    """Create missing foreign key constraint."""
    print("\n[WARN]  No se encontró foreign key en fincas_app_lote.finca_id")
    print("Creando foreign key...")
    
    if not _table_exists(cursor, 'api_finca'):
        print("[ERROR] La tabla api_finca no existe")
        return False
    
    constraint_name = 'fincas_app_lote_finca_id_api_finca_fk'
    query = _build_add_constraint_query(
        table_name='fincas_app_lote',
        constraint_name=constraint_name,
        column_name='finca_id',
        ref_table='api_finca',
        ref_column='id'
    )
    cursor.execute(query)
    print(f"✅ Foreign key creada: {constraint_name}")
    return True


def _validate_fk_identifiers(constraint_name, table_name, column_name, foreign_table, foreign_column):
    """Validate all foreign key identifiers."""
    try:
        _validate_identifier(constraint_name)
        _validate_identifier(table_name)
        _validate_identifier(column_name)
        _validate_identifier(foreign_table)
        _validate_identifier(foreign_column)
        return True
    except ValueError as e:
        print(f"[ERROR] Identificador inválido encontrado en la base de datos: {e}")
        return False


def _fix_incorrect_foreign_key(cursor, constraint_name, foreign_table):
    """Fix foreign key pointing to wrong table."""
    print(f"\n[WARN]  PROBLEMA: FK apunta a '{foreign_table}' pero debería apuntar a 'api_finca'")
    print("Corrigiendo foreign key...")
    
    drop_query = _build_drop_constraint_query(
        table_name='fincas_app_lote',
        constraint_name=constraint_name
    )
    cursor.execute(drop_query)
    print(f"✅ Eliminada FK incorrecta: {constraint_name}")
    
    new_constraint_name = constraint_name.replace(foreign_table, 'api_finca')
    try:
        _validate_identifier(new_constraint_name)
    except ValueError as e:
        print(f"[ERROR] Nombre de constraint generado inválido: {e}")
        return
    
    add_query = _build_add_constraint_query(
        table_name='fincas_app_lote',
        constraint_name=new_constraint_name,
        column_name='finca_id',
        ref_table='api_finca',
        ref_column='id'
    )
    cursor.execute(add_query)
    print(f"✅ Creada FK correcta: {new_constraint_name}")


def _process_existing_foreign_keys(cursor, fks):
    """Process existing foreign keys."""
    print(f"\n📋 Foreign keys encontradas: {len(fks)}")
    for fk in fks:
        constraint_name, table_name, column_name, foreign_table, foreign_column = fk
        print(f"  - {constraint_name}: {table_name}.{column_name} -> {foreign_table}.{foreign_column}")
        
        if not _validate_fk_identifiers(constraint_name, table_name, column_name, foreign_table, foreign_column):
            continue
        
        if foreign_table != 'api_finca':
            _fix_incorrect_foreign_key(cursor, constraint_name, foreign_table)
        else:
            print(f"✅ FK correcta: apunta a {foreign_table}")


def _check_data_consistency():
    """Check data consistency between Finca and Lote."""
    print("\n" + "=" * 60)
    print("Verificando consistencia de datos")
    print("=" * 60)
    
    total_fincas = Finca.objects.count()
    print(f"\nTotal de fincas en BD: {total_fincas}")
    
    if total_fincas > 0:
        fincas_list = list(Finca.objects.values('id', 'nombre')[:10])
        print("Primeras fincas:")
        for f in fincas_list:
            print(f"  - ID: {f['id']}, Nombre: {f['nombre']}")
    
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
            print(f"\n[WARN]  Lotes huérfanos encontrados: {len(orphaned_lotes)}")
            print("Lotes sin finca válida:")
            for lote in orphaned_lotes:
                print(f"  - Lote ID: {lote[0]}, finca_id: {lote[1]}")
        else:
            print("\n✅ No se encontraron lotes huérfanos")


def check_and_fix_foreign_key():
    """Verificar y corregir la foreign key de lotes."""
    print("=" * 60)
    print("Verificando foreign key de fincas_app_lote")
    print("=" * 60)
    
    print(f"\nTabla Finca: {Finca._meta.db_table}")
    print(f"Tabla Lote: {Lote._meta.db_table}")
    
    with connection.cursor() as cursor:
        fks = _check_existing_foreign_keys(cursor)
        
        if not fks:
            if not _create_missing_foreign_key(cursor):
                return
        else:
            _process_existing_foreign_keys(cursor, fks)
    
    _check_data_consistency()
    
    print("\n" + "=" * 60)
    print("Verificación completada")
    print("=" * 60)

if __name__ == '__main__':
    check_and_fix_foreign_key()

