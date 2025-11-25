"""
Django management command to check the status of training jobs.
"""
import logging
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from api.utils.model_imports import get_model_safely

logger = logging.getLogger("cacaoscan.management.check_training")

TrainingJob = get_model_safely('training.models.TrainingJob')


class Command(BaseCommand):
    help = 'Verifica el estado de entrenamientos en ejecución, pendientes y completados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--status',
            type=str,
            choices=['running', 'pending', 'completed', 'failed', 'cancelled', 'all'],
            default='all',
            help='Filtrar por estado específico (default: all)'
        )
        parser.add_argument(
            '--job-id',
            type=str,
            help='Mostrar detalles de un job específico'
        )

    def handle(self, *args, **options):
        if TrainingJob is None:
            logger.error("TrainingJob model not available")
            raise CommandError('TrainingJob no está disponible. Verifica que la app training esté instalada.')

        status_filter = options['status']
        job_id = options.get('job_id')

        logger.info(f"Checking training jobs status (filter: {status_filter})")

        try:
            # Si se especifica un job_id, mostrar detalles
            if job_id:
                try:
                    job = TrainingJob.objects.get(job_id=job_id)
                    self._display_job_details(job)
                    return
                except TrainingJob.DoesNotExist:
                    raise CommandError(f'Job {job_id} no encontrado')

            # Mostrar jobs según filtro
            self.stdout.write("=" * 60)
            self.stdout.write("ESTADO DE ENTRENAMIENTOS")
            self.stdout.write("=" * 60)

            if status_filter in ['running', 'all']:
                running_jobs = TrainingJob.objects.filter(status='running').order_by('-created_at')
                if running_jobs.exists():
                    self.stdout.write(f"\n🚀 Jobs EN EJECUCIÓN: {running_jobs.count()}")
                    for job in running_jobs:
                        self._display_job_summary(job, show_cancel=True)
                else:
                    self.stdout.write("\n✅ No hay jobs en ejecución")

            if status_filter in ['pending', 'all']:
                pending_jobs = TrainingJob.objects.filter(status='pending').order_by('-created_at')
                if pending_jobs.exists():
                    self.stdout.write(f"\n⏳ Jobs PENDIENTES: {pending_jobs.count()}")
                    for job in pending_jobs:
                        self._display_job_summary(job)
                else:
                    self.stdout.write("\n✅ No hay jobs pendientes")

            # Resumen general
            if status_filter == 'all':
                completed_jobs = TrainingJob.objects.filter(status='completed').count()
                failed_jobs = TrainingJob.objects.filter(status='failed').count()
                cancelled_jobs = TrainingJob.objects.filter(status='cancelled').count()

                self.stdout.write("\n" + "=" * 60)
                self.stdout.write("RESUMEN")
                self.stdout.write("=" * 60)
                self.stdout.write(f"  En ejecución: {TrainingJob.objects.filter(status='running').count()}")
                self.stdout.write(f"  Pendientes: {TrainingJob.objects.filter(status='pending').count()}")
                self.stdout.write(f"  Completados: {completed_jobs}")
                self.stdout.write(f"  Fallidos: {failed_jobs}")
                self.stdout.write(f"  Cancelados: {cancelled_jobs}")

        except CommandError:
            raise
        except Exception as e:
            logger.error(f"Error checking training jobs: {e}", exc_info=True)
            raise CommandError(f'Error al verificar entrenamientos: {str(e)}')

    def _display_job_summary(self, job, show_cancel=False):
        """Display a summary of a training job."""
        duration = (timezone.now() - job.created_at).total_seconds() if job.created_at else 0
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        
        self.stdout.write(f"\nJob ID: {job.job_id}")
        self.stdout.write(f"  Tipo: {job.get_job_type_display() if hasattr(job, 'get_job_type_display') else job.job_type}")
        if hasattr(job, 'progress_percentage') and job.progress_percentage is not None:
            self.stdout.write(f"  Progreso: {job.progress_percentage:.1f}%")
        self.stdout.write(f"  Duración: {hours}h {minutes}m")
        self.stdout.write(f"  Iniciado: {job.created_at}")
        if show_cancel:
            self.stdout.write(f"\n  Para cancelar:")
            self.stdout.write(f"   python manage.py cancel_training {job.job_id}")

    def _display_job_details(self, job):
        """Display detailed information about a training job."""
        self.stdout.write("=" * 60)
        self.stdout.write(f"DETALLES DEL JOB: {job.job_id}")
        self.stdout.write("=" * 60)
        self.stdout.write(f"  Tipo: {job.get_job_type_display() if hasattr(job, 'get_job_type_display') else job.job_type}")
        self.stdout.write(f"  Estado: {job.status}")
        if hasattr(job, 'progress_percentage') and job.progress_percentage is not None:
            self.stdout.write(f"  Progreso: {job.progress_percentage:.1f}%")
        self.stdout.write(f"  Creado: {job.created_at}")
        if hasattr(job, 'started_at') and job.started_at:
            self.stdout.write(f"  Iniciado: {job.started_at}")
        if hasattr(job, 'completed_at') and job.completed_at:
            self.stdout.write(f"  Completado: {job.completed_at}")
        if hasattr(job, 'created_by') and job.created_by:
            self.stdout.write(f"  Creado por: {job.created_by.username}")
        if hasattr(job, 'logs') and job.logs:
            self.stdout.write(f"\n  Últimas líneas del log:")
            log_lines = job.logs.split('\n')[-5:]
            for line in log_lines:
                self.stdout.write(f"    {line}")

