"""
Django management command to cancel a training job.
"""
import logging
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from api.utils.model_imports import get_model_safely

logger = logging.getLogger("cacaoscan.management.cancel_training")

TrainingJob = get_model_safely('training.models.TrainingJob')


class Command(BaseCommand):
    help = 'Cancela un trabajo de entrenamiento en ejecución o pendiente. Si no se especifica job_id, lista los trabajos disponibles.'

    def add_arguments(self, parser):
        parser.add_argument(
            'job_id',
            type=str,
            nargs='?',
            help='ID del trabajo a cancelar (opcional, lista trabajos si no se especifica)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar cancelación incluso si el job está en estado completed o failed'
        )

    def handle(self, *args, **options):
        if TrainingJob is None:
            logger.error("TrainingJob model not available")
            raise CommandError('TrainingJob no está disponible. Verifica que la app training esté instalada.')

        job_id = options.get('job_id')
        force = options.get('force', False)
        
        if not job_id:
            # Listar jobs corriendo si no se especifica job_id
            self._list_running_jobs()
            return
        
        # Cancelar trabajo específico
        logger.info(f"Cancelling training job: {job_id}")
        
        try:
            with transaction.atomic():
                try:
                    job = TrainingJob.objects.select_for_update().get(job_id=job_id)
                except TrainingJob.DoesNotExist:
                    raise CommandError(f'Trabajo {job_id} no encontrado')
                
                # Verificar estado
                if job.status not in ['pending', 'running']:
                    if not force:
                        raise CommandError(
                            f"El trabajo {job_id} no está en estado 'pending' o 'running' "
                            f"(estado actual: {job.status}). Usa --force para cancelar de todos modos."
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"⚠️  Cancelando trabajo {job_id} con estado '{job.status}' (--force activado)"
                            )
                        )
                
                # Cancelar job
                job.status = 'cancelled'
                if hasattr(job, 'completed_at'):
                    job.completed_at = timezone.now()
                job.save()
                
                logger.info(f"Job {job_id} cancelled successfully")
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Trabajo {job_id} cancelado exitosamente')
                )
                
        except CommandError:
            raise
        except Exception as e:
            logger.error(f"Error cancelling training job {job_id}: {e}", exc_info=True)
            raise CommandError(f'Error al cancelar trabajo {job_id}: {str(e)}')

    def _list_running_jobs(self):
        """List all running and pending jobs."""
        try:
            running_jobs = TrainingJob.objects.filter(status='running').order_by('-created_at')
            pending_jobs = TrainingJob.objects.filter(status='pending').order_by('-created_at')
            
            if not running_jobs.exists() and not pending_jobs.exists():
                self.stdout.write(self.style.WARNING("No hay trabajos en ejecución o pendientes"))
                return
            
            self.stdout.write("=" * 60)
            self.stdout.write("JOBS DISPONIBLES PARA CANCELAR:")
            self.stdout.write("=" * 60)
            
            if running_jobs.exists():
                self.stdout.write(f"\n🚀 Jobs EN EJECUCIÓN: {running_jobs.count()}")
                for job in running_jobs:
                    self.stdout.write(f"\nJob ID: {job.job_id}")
                    self.stdout.write(f"  Tipo: {job.get_job_type_display() if hasattr(job, 'get_job_type_display') else job.job_type}")
                    if hasattr(job, 'progress_percentage') and job.progress_percentage is not None:
                        self.stdout.write(f"  Progreso: {job.progress_percentage:.1f}%")
                    self.stdout.write(f"  Iniciado: {job.created_at}")
                    self.stdout.write(f"\n  Para cancelar:")
                    self.stdout.write(f"    python manage.py cancel_training {job.job_id}")
            
            if pending_jobs.exists():
                self.stdout.write(f"\n⏳ Jobs PENDIENTES: {pending_jobs.count()}")
                for job in pending_jobs:
                    self.stdout.write(f"\nJob ID: {job.job_id}")
                    self.stdout.write(f"  Tipo: {job.get_job_type_display() if hasattr(job, 'get_job_type_display') else job.job_type}")
                    self.stdout.write(f"  Creado: {job.created_at}")
                    self.stdout.write(f"\n  Para cancelar:")
                    self.stdout.write(f"    python manage.py cancel_training {job.job_id}")
                    
        except Exception as e:
            logger.error(f"Error listing running jobs: {e}", exc_info=True)
            raise CommandError(f'Error al listar trabajos: {str(e)}')

