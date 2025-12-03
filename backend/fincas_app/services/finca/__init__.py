"""
Finca services module for CacaoScan.
"""
from .finca_crud_service import FincaCRUDService
from .finca_stats_service import FincaStatsService
from .finca_validation_service import FincaValidationService

# Backward compatibility: Create a combined service that delegates to individual services
from api.services.base import BaseService, ServiceResult


class FincaService(BaseService):
    """
    Combined finca service for backward compatibility.
    Delegates to individual specialized services.
    """
    
    def __init__(self):
        super().__init__()
        self.crud_service = FincaCRUDService()
        self.stats_service = FincaStatsService()
        from fincas_app.services.lote_service import LoteService
        self.lote_service = LoteService()
    
    # CRUD methods
    def create_finca(self, finca_data, user) -> ServiceResult:
        """Delegates to FincaCRUDService."""
        return self.crud_service.create_finca(finca_data, user)
    
    def get_user_fincas(self, user, page=1, page_size=20, filters=None) -> ServiceResult:
        """Delegates to FincaCRUDService."""
        return self.crud_service.get_user_fincas(user, page, page_size, filters)
    
    def get_finca_details(self, finca_id, user) -> ServiceResult:
        """Delegates to FincaCRUDService."""
        return self.crud_service.get_finca_details(finca_id, user)
    
    def update_finca(self, finca_id, *args, **kwargs) -> ServiceResult:
        """Delegates to FincaCRUDService. Handles both signatures for backward compatibility."""
        # Handle both signatures: (finca_id, finca_data, user) and (finca_id, user, finca_data)
        if len(args) == 2:
            arg1, arg2 = args
            # Check if arg1 is a User (old signature) or dict (new signature)
            from django.contrib.auth.models import User
            if isinstance(arg1, User):
                # Old signature: (finca_id, user, finca_data)
                user = arg1
                finca_data = arg2
            else:
                # New signature: (finca_id, finca_data, user)
                finca_data = arg1
                user = arg2
        elif len(args) == 1:
            # Assume new signature with user in kwargs
            finca_data = args[0]
            user = kwargs.get('user')
        else:
            # Use kwargs
            finca_data = kwargs.get('finca_data') or kwargs.get('update_data')
            user = kwargs.get('user')
        
        return self.crud_service.update_finca(finca_id, user, finca_data)
    
    def delete_finca(self, finca_id, user) -> ServiceResult:
        """Delegates to FincaCRUDService."""
        return self.crud_service.delete_finca(finca_id, user)
    
    # Statistics methods
    def get_finca_statistics(self, user, filters=None) -> ServiceResult:
        """Delegates to FincaStatsService."""
        return self.stats_service.get_finca_statistics(user, filters)
    
    # Serialization (for backward compatibility)
    def _serialize_finca(self, finca):
        """Delegates to FincaCRUDService."""
        return self.crud_service._serialize_finca(finca)

__all__ = [
    'FincaCRUDService',
    'FincaStatsService',
    'FincaValidationService',
    'FincaService',  # For backward compatibility
]

