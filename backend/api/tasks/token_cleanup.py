"""
Celery task for cleaning up expired JWT tokens.

This task should be scheduled to run periodically (recommended: every hour)
using Celery Beat. Add to your celery beat schedule:

from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    'cleanup-expired-tokens': {
        'task': 'api.tasks.token_cleanup.cleanup_expired_tokens',
        'schedule': crontab(minute=0),  # Run every hour
    },
}

Or run manually:
    celery -A cacaoscan call api.tasks.token_cleanup.cleanup_expired_tokens
"""
import logging
from celery import shared_task
from django.utils import timezone
from django.db import OperationalError, ProgrammingError

logger = logging.getLogger("cacaoscan.api")


@shared_task(name='api.tasks.token_cleanup.cleanup_expired_tokens')
def cleanup_expired_tokens() -> dict:
    """
    Clean up expired JWT tokens from blacklist and outstanding tokens.
    
    This task removes:
    - Expired BlacklistedToken entries
    - Expired OutstandingToken entries
    
    Returns:
        dict: Summary of cleanup operation with counts of deleted tokens
        
    Example return:
        {
            'blacklisted_deleted': 10,
            'outstanding_deleted': 5,
            'success': True
        }
    """
    result = {
        'blacklisted_deleted': 0,
        'outstanding_deleted': 0,
        'success': False,
        'error': None
    }
    
    try:
        # Import here to avoid circular imports
        from rest_framework_simplejwt.token_blacklist.models import (
            BlacklistedToken,
            OutstandingToken
        )
        
        # Clean up expired blacklisted tokens
        expired_blacklisted = BlacklistedToken.objects.filter(
            token__expires_at__lt=timezone.now()
        )
        blacklisted_count = expired_blacklisted.count()
        if blacklisted_count > 0:
            expired_blacklisted.delete()
            result['blacklisted_deleted'] = blacklisted_count
            logger.info(f"Cleaned up {blacklisted_count} expired blacklisted tokens")
        
        # Clean up expired outstanding tokens
        expired_outstanding = OutstandingToken.objects.filter(
            expires_at__lt=timezone.now()
        )
        outstanding_count = expired_outstanding.count()
        if outstanding_count > 0:
            expired_outstanding.delete()
            result['outstanding_deleted'] = outstanding_count
            logger.info(f"Cleaned up {outstanding_count} expired outstanding tokens")
        
        result['success'] = True
        logger.debug(
            f"Token cleanup completed: {result['blacklisted_deleted']} blacklisted, "
            f"{result['outstanding_deleted']} outstanding tokens deleted"
        )
        
    except (OperationalError, ProgrammingError) as e:
        # Tables might not exist during initial deployment
        error_msg = str(e).lower()
        if 'does not exist' in error_msg or 'relation' in error_msg:
            logger.debug(
                "Token blacklist tables not yet created, will be created with migrations"
            )
            result['success'] = True  # Not an error, just not ready yet
        else:
            logger.warning(f"Database error during token cleanup: {e}")
            result['error'] = str(e)
            
    except Exception as e:
        logger.error(f"Error during token cleanup: {e}", exc_info=True)
        result['error'] = str(e)
    
    return result

