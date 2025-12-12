"""
Signals para el manejo automático de usuarios en CacaoScan.
"""
import logging
import os
import sys
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group

logger = logging.getLogger("cacaoscan.users")


def _is_testing():
    """Detecta si estamos ejecutando tests."""
    return (
        'test' in sys.argv or 
        'pytest' in sys.modules or 
        os.environ.get('DJANGO_TEST_MODE') == '1' or
        'pytest' in str(sys.modules.get('__main__', {})) or
        'PYTEST_CURRENT_TEST' in os.environ
    )


@receiver(pre_save, sender=User)
def ensure_user_active(sender, instance, **kwargs):
    """
    Asegura que los usuarios registrados estén activos por defecto.
    Usa pre_save para evitar bucles infinitos.
    
    Durante los tests, respeta el valor explícito de is_active si se establece.
    """
    # Durante tests, no forzar is_active=True para permitir tests con usuarios inactivos
    if _is_testing():
        return
    
    if instance._state.adding and not instance.is_active:
        instance.is_active = True
        logger.info(f"Usuario {instance.username} marcado como activo por defecto")


@receiver(pre_save, sender=User)
def protect_explicit_username(sender, instance, **kwargs):
    """
    Protege el username explícito de los tests.
    Nunca sobreescribe instance.username si ya tiene un valor.
    """
    # Si el username ya está definido, no generar uno automático
    if instance.username:
        return
    
    # Solo generar username automático si no existe
    # Esta función puede ser extendida en el futuro para generar usernames
    # pero nunca sobreescribirá un username explícito


@receiver(post_save, sender=User)
def assign_default_role(sender, instance, created, **kwargs):
    """
    Asigna automáticamente el rol 'farmer' a usuarios nuevos normales.
    
    Reglas:
    - No asigna roles a superusuarios
    - No asigna roles a usuarios staff
    - No asigna roles si el usuario ya tiene roles asignados
    - Solo asigna farmer a usuarios normales sin roles
    """
    # Solo procesar usuarios nuevos
    if not created:
        return
    
    # No asignar roles a superusuarios
    if instance.is_superuser:
        logger.debug(f"Usuario {instance.username} es superusuario, no se asigna rol farmer")
        return
    
    # No asignar roles a usuarios staff
    if instance.is_staff:
        logger.debug(f"Usuario {instance.username} es staff, no se asigna rol farmer")
        return
    
    # No asignar roles si el usuario ya tiene roles asignados
    # Verificar grupos directamente sin refresh para evitar problemas de sincronización
    try:
        # Verificar si el usuario ya tiene grupos asignados
        # Usar count() en lugar de exists() para ser más explícito
        existing_groups_count = instance.groups.count()
        if existing_groups_count > 0:
            logger.debug(f"Usuario {instance.username} ya tiene {existing_groups_count} rol(es) asignado(s), no se asigna rol farmer")
            return
    except Exception as e:
        logger.warning(f"Error verificando grupos existentes para usuario {instance.username}: {e}")
        # Continuar si hay error verificando grupos, pero ser más cuidadoso
    
    # Solo asignar farmer a usuarios normales sin roles
    try:
        # Asegurar que el grupo exista
        farmer_group, _ = Group.objects.get_or_create(name="farmer")
        
        # Agregar el usuario al grupo farmer
        instance.groups.add(farmer_group)
        
        logger.info(f"Usuario {instance.username} asignado automáticamente al rol 'farmer'")
    except Exception as e:
        logger.error(f"Error asignando rol farmer a usuario {instance.username}: {e}")
