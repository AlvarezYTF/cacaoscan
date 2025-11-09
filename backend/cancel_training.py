"""
Script para cancelar un entrenamiento en ejecución.
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

if len(sys.argv) < 2:
    # Listar jobs corriendo si no se especifica job_id
    running_jobs = TrainingJob.objects.filter(status='running').order_by('-created_at')
    
    if running_jobs.exists():
        print("=" * 60)
        print("JOBS EN EJECUCIÓN:")
        print("=" * 60)
        for job in running_jobs:
            print(f"\nJob ID: {job.job_id}")
            print(f"Tipo: {job.get_job_type_display()}")
            print(f"Progreso: {job.progress_percentage:.1f}%")
            print(f"Épocas: {job.epochs}")
            print(f"\nPara cancelar, ejecuta:")
            print(f"  python cancel_training.py {job.job_id}")
    else:
        print("✅ No hay jobs en ejecución")
        sys.exit(0)
else:
    job_id = sys.argv[1]
    
    try:
        job = TrainingJob.objects.get(job_id=job_id)
        
        if job.status == 'running':
            print(f"[WARN]  Cancelando job {job_id}...")
            job.mark_cancelled()
            print(f"✅ Job {job_id} cancelado exitosamente")
            print("\n💡 NOTA: El worker de Celery seguirá procesando, pero el job")
            print("    quedará marcado como cancelado. Si necesitas detener")
            print("    el worker, presiona Ctrl+C en la terminal donde corre.")
        elif job.status == 'pending':
            print(f"[WARN]  Cancelando job pendiente {job_id}...")
            job.mark_cancelled()
            print(f"✅ Job {job_id} cancelado exitosamente")
        else:
            print(f"ℹ️  Job {job_id} tiene estado '{job.status}' y no puede cancelarse")
            
    except TrainingJob.DoesNotExist:
        print(f"[ERROR] Job {job_id} no encontrado")
        sys.exit(1)
