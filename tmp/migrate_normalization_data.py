"""
Script de migración de datos para normalización 3NF.

Este script migra los datos existentes antes de aplicar los cambios de normalización:
- api_finca: municipio/departamento (texto) → municipio_id (FK)
- auth_app_userprofile: region/municipality (texto) → municipio_id (FK)

EJECUTAR ANTES de aplicar las sentencias SQL de ALTER TABLE.

Uso:
    python manage.py shell < tmp/migrate_normalization_data.py
    O ejecutar directamente: python tmp/migrate_normalization_data.py
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import transaction
from catalogos.models import Municipio, Departamento
from fincas_app.models import Finca
from auth_app.models import UserProfile


def normalize_string(text: str) -> str:
    """Normalize string for comparison (uppercase, trim, remove accents)."""
    if not text:
        return ""
    # Basic normalization: uppercase and trim
    normalized = text.upper().strip()
    # Remove common accents (basic approach)
    replacements = {
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'Ñ': 'N'
    }
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    return normalized


def find_municipio(municipio_nombre: str, departamento_nombre: str) -> Municipio | None:
    """
    Find municipio by name and department name.
    
    Args:
        municipio_nombre: Name of the municipality
        departamento_nombre: Name of the department
        
    Returns:
        Municipio instance or None if not found
    """
    if not municipio_nombre or not departamento_nombre:
        return None
    
    municipio_norm = normalize_string(municipio_nombre)
    departamento_norm = normalize_string(departamento_nombre)
    
    try:
        # Try exact match first
        municipio = Municipio.objects.filter(
            nombre__iexact=municipio_nombre,
            departamento__nombre__iexact=departamento_nombre
        ).first()
        
        if municipio:
            return municipio
        
        # Try normalized match
        municipios = Municipio.objects.select_related('departamento').all()
        for m in municipios:
            m_norm = normalize_string(m.nombre)
            d_norm = normalize_string(m.departamento.nombre)
            if m_norm == municipio_norm and d_norm == departamento_norm:
                return m
        
        return None
    except Exception as e:
        print(f"Error finding municipio: {e}")
        return None


@transaction.atomic
def migrate_fincas():
    """Migrate Finca records: municipio/departamento → municipio_id."""
    print("\n=== Migrando Fincas ===")
    
    fincas = Finca.objects.filter(municipio_id__isnull=True).exclude(
        municipio__isnull=True, 
        departamento__isnull=True
    )
    
    total = fincas.count()
    migrated = 0
    not_found = 0
    errors = 0
    
    print(f"Total de fincas a migrar: {total}")
    
    for finca in fincas:
        try:
            municipio = find_municipio(finca.municipio, finca.departamento)
            
            if municipio:
                finca.municipio_id = municipio.id
                finca.save(update_fields=['municipio_id'])
                migrated += 1
                if migrated % 10 == 0:
                    print(f"  Migradas: {migrated}/{total}")
            else:
                not_found += 1
                print(f"  ⚠️  No se encontró municipio para: {finca.municipio}, {finca.departamento} (Finca ID: {finca.id})")
        
        except Exception as e:
            errors += 1
            print(f"  ❌ Error migrando Finca ID {finca.id}: {e}")
    
    print(f"\n✅ Fincas migradas: {migrated}")
    print(f"⚠️  No encontradas: {not_found}")
    print(f"❌ Errores: {errors}")
    
    return {
        'total': total,
        'migrated': migrated,
        'not_found': not_found,
        'errors': errors
    }


@transaction.atomic
def migrate_user_profiles():
    """Migrate UserProfile records: region/municipality → municipio_id."""
    print("\n=== Migrando UserProfiles ===")
    
    profiles = UserProfile.objects.filter(municipio_id__isnull=True).exclude(
        municipality__isnull=True,
        region__isnull=True
    )
    
    total = profiles.count()
    migrated = 0
    not_found = 0
    errors = 0
    
    print(f"Total de perfiles a migrar: {total}")
    
    for profile in profiles:
        try:
            municipio = find_municipio(profile.municipality, profile.region)
            
            if municipio:
                profile.municipio_id = municipio.id
                profile.save(update_fields=['municipio_id'])
                migrated += 1
                if migrated % 10 == 0:
                    print(f"  Migrados: {migrated}/{total}")
            else:
                not_found += 1
                print(f"  ⚠️  No se encontró municipio para: {profile.municipality}, {profile.region} (Profile ID: {profile.id})")
        
        except Exception as e:
            errors += 1
            print(f"  ❌ Error migrando Profile ID {profile.id}: {e}")
    
    print(f"\n✅ Perfiles migrados: {migrated}")
    print(f"⚠️  No encontrados: {not_found}")
    print(f"❌ Errores: {errors}")
    
    return {
        'total': total,
        'migrated': migrated,
        'not_found': not_found,
        'errors': errors
    }


def verify_migration():
    """Verify migration results."""
    print("\n=== Verificando Migración ===")
    
    # Verificar Fincas
    fincas_sin_migrar = Finca.objects.filter(
        municipio_id__isnull=True
    ).exclude(
        municipio__isnull=True,
        departamento__isnull=True
    ).count()
    
    fincas_con_fk_invalida = Finca.objects.filter(
        municipio_id__isnull=False
    ).exclude(
        municipio__isnull=False
    ).count()
    
    print(f"Fincas sin migrar: {fincas_sin_migrar}")
    print(f"Fincas con FK inválida: {fincas_con_fk_invalida}")
    
    # Verificar UserProfiles
    profiles_sin_migrar = UserProfile.objects.filter(
        municipio_id__isnull=True
    ).exclude(
        municipality__isnull=True,
        region__isnull=True
    ).count()
    
    profiles_con_fk_invalida = UserProfile.objects.filter(
        municipio_id__isnull=False
    ).exclude(
        municipio__isnull=False
    ).count()
    
    print(f"Perfiles sin migrar: {profiles_sin_migrar}")
    print(f"Perfiles con FK inválida: {profiles_con_fk_invalida}")
    
    return {
        'fincas_sin_migrar': fincas_sin_migrar,
        'fincas_fk_invalida': fincas_con_fk_invalida,
        'profiles_sin_migrar': profiles_sin_migrar,
        'profiles_fk_invalida': profiles_con_fk_invalida
    }


def main():
    """Main migration function."""
    print("=" * 60)
    print("MIGRACIÓN DE DATOS PARA NORMALIZACIÓN 3NF")
    print("=" * 60)
    
    # Verificar que existen catálogos
    total_municipios = Municipio.objects.count()
    total_departamentos = Departamento.objects.count()
    
    print(f"\nCatálogos disponibles:")
    print(f"  - Departamentos: {total_departamentos}")
    print(f"  - Municipios: {total_municipios}")
    
    if total_municipios == 0:
        print("\n❌ ERROR: No hay municipios en el catálogo. Cargar catálogos primero.")
        return
    
    # Ejecutar migraciones
    fincas_result = migrate_fincas()
    profiles_result = migrate_user_profiles()
    
    # Verificar resultados
    verification = verify_migration()
    
    # Resumen final
    print("\n" + "=" * 60)
    print("RESUMEN FINAL")
    print("=" * 60)
    print(f"Fincas: {fincas_result['migrated']}/{fincas_result['total']} migradas")
    print(f"Perfiles: {profiles_result['migrated']}/{profiles_result['total']} migrados")
    
    if verification['fincas_sin_migrar'] > 0 or verification['profiles_sin_migrar'] > 0:
        print("\n⚠️  ADVERTENCIA: Hay registros sin migrar.")
        print("   Revisar los logs anteriores y corregir manualmente si es necesario.")
    
    if verification['fincas_fk_invalida'] > 0 or verification['profiles_fk_invalida'] > 0:
        print("\n❌ ERROR: Hay ForeignKeys inválidas. Revisar antes de continuar.")
    
    print("\n✅ Migración completada. Revisar resultados antes de aplicar cambios SQL.")


if __name__ == '__main__':
    main()

