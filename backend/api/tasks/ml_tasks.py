"""
Celery tasks for ML operations in CacaoScan.
Handles heavy ML operations like dataset validation asynchronously.
"""
import logging
from typing import Dict, Any
from celery import shared_task
from django.core.cache import cache

from core.utils import get_cache_key
from ..utils.model_imports import get_model_safely

logger = logging.getLogger("cacaoscan.api.tasks.ml")

# Import CacaoDatasetLoader safely
CacaoDatasetLoader = get_model_safely('ml.data.dataset_loader.CacaoDatasetLoader')


@shared_task(bind=True, name='api.tasks.ml.validate_dataset')
def validate_dataset_task(self) -> Dict[str, Any]:
    """
    Validate dataset and return statistics asynchronously.
    
    Returns:
        Dictionary with validation results and statistics
    """
    def safe_update_state(state: str, meta: Dict[str, Any]) -> None:
        """Safely update task state, only if task_id exists (not in test mode)."""
        if not hasattr(self, 'request') or not getattr(self.request, 'id', None):
            # We are in test mode, return without using backend
            return
        if hasattr(self, 'update_state'):
            self.update_state(state=state, meta=meta)
    
    try:
        # Update task state
        safe_update_state(
            'PROGRESS',
            {
                'status': 'Loading dataset loader...'
            }
        )
        
        if CacaoDatasetLoader is None:
            return {
                'status': 'error',
                'valid': False,
                'error': 'Cargador de dataset no disponible'
            }
        
        # Update task state
        safe_update_state(
            'PROGRESS',
            {
                'status': 'Validating dataset...'
            }
        )
        
        loader = CacaoDatasetLoader()
        stats = loader.get_dataset_stats()
        
        response_data = {
            'valid': len(stats.get('missing_images', [])) == 0,
            'stats': stats,
            'status': 'success'
        }
        
        # Cache the result
        cache_key = get_cache_key('dataset_validation', 'stats')
        
        # Cache dinámico: timeout más largo si el dataset es válido y estable
        if response_data['valid'] and len(stats.get('missing_images', [])) == 0:
            cache_timeout = 60 * 15  # 15 minutos
        else:
            cache_timeout = 60 * 5  # 5 minutos
        
        cache.set(cache_key, response_data, cache_timeout)
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error validating dataset: {e}", exc_info=True)
        return {
            'status': 'error',
            'valid': False,
            'error': str(e)
        }

