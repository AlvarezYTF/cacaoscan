"""
Script para verificar el estado de entrenamientos en ejecución.
"""
import os
import sys
from pathlib import Path

# Configurar Django
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')

import django
django.setup()

from api.models import TrainingJob
from django.utils import timezone

# Buscar jobs en ejecución
running_jobs = TrainingJob.objects.filter(status='running').order_by('-created_at')
pending_jobs = TrainingJob.objects.filter(status='pending').order_by('-created_at')

print("=" * 60)
print("ESTADO DE ENTRENAMIENTOS")
print("=" * 60)

if running_jobs.exists():
    print(f"\n🚀 Jobs EN EJECUCIÓN: {running_jobs.count()}")
    for job in running_jobs:
        duration = (timezone.now() - job.created_at).total_seconds() if job.created_at else 0
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        
        print(f"\n  📋 Job ID: {job.job_id}")
        print(f"     Tipo: {job.get_job_type_display()}")
        print(f"     Progreso: {job.progress_percentage:.1f}%")
        print(f"     Épocas configuradas: {job.epochs}")
        print(f"     Tiempo transcurrido: {hours}h {minutes}m")
        print(f"     Creado: {job.created_at}")
        if job.logs:
            last_logs = job.logs.split('\n')[-3:]
            print(f"     Últimos logs:")
            for log in last_logs:
                print(f"       - {log[:80]}")
else:
    print("\n✅ No hay jobs en ejecución")

if pending_jobs.exists():
    print(f"\n⏳ Jobs PENDIENTES: {pending_jobs.count()}")
    for job in pending_jobs:
        print(f"  📋 Job ID: {job.job_id}")
        print(f"     Tipo: {job.get_job_type_display()}")
        print(f"     Épocas: {job.epochs}")
else:
    print("\n✅ No hay jobs pendientes")

print("\n" + "=" * 60)
print("RECOMENDACIÓN:")
print("=" * 60)

if running_jobs.exists():
    print("\n[WARN]  Tienes entrenamientos corriendo.")
    print("\n📌 OPCIONES:")
    print("\n1️⃣  CANCELAR el entrenamiento actual y empezar uno nuevo")
    print("   [OK] Usará las nuevas mejoras (150 épocas, validación de crops, etc.)")
    print("   [OK] Mejor confianza (>=80%)")
    print("   [OK] Validación automática de crops")
    print("\n2️⃣  DEJAR que termine el actual")
    print("   [FAIL] No usará las mejoras nuevas")
    print("   [FAIL] Confianza baja (29.9%)")
    print("\n💡 RECOMENDACIÓN: Cancelar y empezar nuevo entrenamiento")
    print("\nPara cancelar, usa:")
    print("   python cancel_training.py <job_id>")
else:
    print("\n✅ No hay entrenamientos corriendo. Puedes iniciar uno nuevo con:")
    print("   - Las nuevas mejoras ya están aplicadas")
    print("   - 150 épocas por defecto")
    print("   - Validación de crops automática")
    print("   - Confianza mejorada (>=80%)")

