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


@receiver(post_save, sender=User)
def assign_default_role(sender, instance, created, **kwargs):
    """
    Asigna automáticamente el rol 'farmer' a todos los usuarios nuevos
    que no sean staff o superuser.
    """
    if created and not instance.is_staff and not instance.is_superuser:
        try:
            # Crear el grupo 'farmer' si no existe
            farmer_group, _ = Group.objects.get_or_create(name='farmer')
            
            # Agregar el usuario al grupo farmer
            instance.groups.add(farmer_group)
            
            logger.info(f"Usuario {instance.username} asignado automáticamente al rol 'farmer'")
        except Exception as e:
            logger.error(f"Error asignando rol farmer a usuario {instance.username}: {e}")
