#!/usr/bin/env python
"""
Script de configuración de desarrollo para CacaoScan.

Configura la base de datos PostgreSQL, crea migraciones iniciales
y configura usuarios de prueba para desarrollo.
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def setup_django():
    """Configura Django para el script."""
    try:
        django.setup()
        print("✅ Django configurado exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error configurando Django: {e}")
        return False

def test_database_connection():
    """Prueba la conexión a la base de datos."""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result[0] == 1:
                print("✅ Conexión a PostgreSQL exitosa")
                return True
    except Exception as e:
        print(f"❌ Error conectando a PostgreSQL: {e}")
        print("💡 Asegúrate de que PostgreSQL esté ejecutándose y la base de datos esté configurada")
        print("💡 Ejecuta: psql -U postgres -f setup_database.sql")
        return False

def create_migrations():
    """Crea y aplica migraciones."""
    try:
        from django.core.management import execute_from_command_line
        
        print("📦 Creando migraciones...")
        execute_from_command_line(['manage.py', 'makemigrations'])
        
        print("🚀 Aplicando migraciones...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        print("✅ Migraciones aplicadas exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error en migraciones: {e}")
        return False

def create_superuser():
    """Crea usuario administrador de prueba."""
    try:
        from apps.users.models import User
        
        # Verificar si ya existe un superusuario
        if User.objects.filter(is_superuser=True).exists():
            print("ℹ️  Ya existe un superusuario")
            return True
        
        # Crear superusuario
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@cacaoscan.com',
            password='admin123',
            first_name='Administrador',
            last_name='CacaoScan',
            role='admin',
            is_staff=True,
            is_superuser=True,
            is_verified=True
        )
        
        print("✅ Superusuario creado:")
        print(f"   📧 Email: {admin_user.email}")
        print(f"   🔑 Password: admin123")
        print(f"   👤 Role: {admin_user.role}")
        
        return True
    except Exception as e:
        print(f"❌ Error creando superusuario: {e}")
        return False

def create_test_users():
    """Crea usuarios de prueba para desarrollo."""
    try:
        from apps.users.models import User
        
        test_users = [
            {
                'username': 'agricultor1',
                'email': 'agricultor1@finca.com',
                'password': 'test123',
                'first_name': 'Juan',
                'last_name': 'Pérez',
                'role': 'farmer',
                'region': 'Huila',
                'municipality': 'Pitalito',
                'farm_name': 'Finca El Cacao',
            },
            {
                'username': 'agricultor2',
                'email': 'agricultor2@finca.com',
                'password': 'test123',
                'first_name': 'María',
                'last_name': 'González',
                'role': 'farmer',
                'region': 'Tolima',
                'municipality': 'Ibagué',
                'farm_name': 'Finca La Esperanza',
            },
            {
                'username': 'analista1',
                'email': 'analista@cacaoscan.com',
                'password': 'test123',
                'first_name': 'Carlos',
                'last_name': 'Rodríguez',
                'role': 'analyst',
            }
        ]
        
        created_count = 0
        for user_data in test_users:
            email = user_data['email']
            
            # Verificar si el usuario ya existe
            if User.objects.filter(email=email).exists():
                print(f"ℹ️  Usuario {email} ya existe")
                continue
            
            # Extraer datos del perfil
            profile_data = {
                'region': user_data.pop('region', ''),
                'municipality': user_data.pop('municipality', ''),
                'farm_name': user_data.pop('farm_name', ''),
            }
            
            # Crear usuario
            user = User.objects.create_user(**user_data)
            
            # Actualizar perfil si hay datos
            if any(profile_data.values()):
                for field, value in profile_data.items():
                    if value:
                        setattr(user.profile, field, value)
                user.profile.save()
            
            created_count += 1
            print(f"✅ Usuario creado: {email} ({user.role})")
        
        if created_count > 0:
            print(f"✅ {created_count} usuarios de prueba creados")
        
        return True
    except Exception as e:
        print(f"❌ Error creando usuarios de prueba: {e}")
        return False

def show_summary():
    """Muestra resumen de la configuración."""
    try:
        from apps.users.models import User
        
        print("\n" + "="*50)
        print("📊 RESUMEN DE LA CONFIGURACIÓN")
        print("="*50)
        
        total_users = User.objects.count()
        admins = User.objects.filter(role='admin').count()
        farmers = User.objects.filter(role='farmer').count()
        analysts = User.objects.filter(role='analyst').count()
        
        print(f"👥 Total usuarios: {total_users}")
        print(f"👑 Administradores: {admins}")
        print(f"🌱 Agricultores: {farmers}")
        print(f"📊 Analistas: {analysts}")
        
        print("\n🔗 URLs importantes:")
        print("   🌐 Admin: http://localhost:8000/admin/")
        print("   📖 API Docs: http://localhost:8000/api/docs/")
        print("   🔐 Auth API: http://localhost:8000/api/auth/")
        
        print("\n🚀 Para iniciar el servidor:")
        print("   python manage.py runserver")
        
        return True
    except Exception as e:
        print(f"❌ Error mostrando resumen: {e}")
        return False

def main():
    """Función principal del script."""
    print("🚀 CONFIGURACIÓN DE DESARROLLO - CACAOSCAN")
    print("=" * 50)
    
    # Paso 1: Configurar Django
    if not setup_django():
        return 1
    
    # Paso 2: Probar conexión a base de datos
    if not test_database_connection():
        return 1
    
    # Paso 3: Crear y aplicar migraciones
    if not create_migrations():
        return 1
    
    # Paso 4: Crear superusuario
    if not create_superuser():
        return 1
    
    # Paso 5: Crear usuarios de prueba
    if not create_test_users():
        return 1
    
    # Paso 6: Mostrar resumen
    if not show_summary():
        return 1
    
    print("\n✅ Configuración de desarrollo completada exitosamente!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
