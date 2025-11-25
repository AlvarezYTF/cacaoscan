"""
Celery tasks for statistics operations in CacaoScan.
Handles heavy statistics calculations asynchronously.
"""
import logging
from typing import Dict, Any
from celery import shared_task

from ..services.stats.stats_service import StatsService

logger = logging.getLogger("cacaoscan.api.tasks.stats")


@shared_task(bind=True, name='api.tasks.stats.calculate_admin_stats')
def calculate_admin_stats_task(self) -> Dict[str, Any]:
    """
    Calculate admin statistics asynchronously.
    
    Returns:
        Dictionary with all system statistics
    """
    try:
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'Calculating user statistics...'
            }
        )
        
        stats_service = StatsService()
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'Calculating image statistics...'
            }
        )
        
        stats = stats_service.get_all_stats()
        
        return {
            'status': 'completed',
            'stats': stats
        }
        
    except Exception as e:
        logger.error(f"Error calculating admin stats: {e}", exc_info=True)
        stats_service = StatsService()
        return {
            'status': 'error',
            'stats': stats_service.get_empty_stats(),
            'error': str(e)
        }

