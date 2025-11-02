"""
Signals para el manejo automÃ¡tico de usuarios en CacaoScan.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group


@receiver(post_save, sender=User)
def assign_default_role(sender, instance, created, **kwargs):
    """
    Asigna automÃ¡ticamente el rol 'farmer' a todos los usuarios nuevos
    que no sean staff o superuser.
    """
    if created and not instance.is_staff and not instance.is_superuser:
        # Crear el grupo 'farmer' si no existe
        farmer_group, created_group = Group.objects.get_or_create(name='farmer')
        
        # Agregar el usuario al grupo farmer
        instance.groups.add(farmer_group)
        
        print(f"âœ… Usuario {instance.username} asignado automÃ¡ticamente al rol 'farmer'")


@receiver(post_save, sender=User)
def ensure_user_active(sender, instance, created, **kwargs):
    """
    Asegura que los usuarios registrados estÃ©n activos por defecto.
    """
    if created:
        instance.is_active = True
        instance.save(update_fields=['is_active'])
        print(f"âœ… Usuario {instance.username} marcado como activo")


