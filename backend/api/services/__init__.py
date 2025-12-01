"""
Servicios para CacaoScan API.
"""

# Importar clases base
from .base import (
    BaseService, 
    ServiceResult, 
    ServiceError, 
    ValidationServiceError, 
    PermissionServiceError, 
    NotFoundServiceError
)

# Importar servicios específicos
from .auth import LoginService, RegistrationService, PasswordService, VerificationService, ProfileService
from .analysis_service import AnalysisService

# Importar servicios desde apps modulares (wrappers de compatibilidad)
from fincas_app.services import FincaService, LoteService
from reports.services import ReportService
from images_app.services import ImageProcessingService, ImageStorageService, ImageManagementService

# Training services are imported lazily to avoid circular import
# They are available in __all__ but imported on demand
MLService = None
PredictionService = None

def _lazy_import_training_services():
    """Lazy import of training services to avoid circular dependency."""
    global MLService, PredictionService
    if MLService is None or PredictionService is None:
        from training.services import MLService as _MLService, PredictionService as _PredictionService
        MLService = _MLService
        PredictionService = _PredictionService
    return MLService, PredictionService

# Crear instancias de servicios para uso fácil
login_service = LoginService()
registration_service = RegistrationService()
password_service = PasswordService()
verification_service = VerificationService()
profile_service = ProfileService()
# analysis_service is created lazily to avoid circular import
analysis_service = None
image_service = ImageManagementService()
finca_service = FincaService()
lote_service = LoteService()
report_service = ReportService()

# Exportar todo
__all__ = [
    # Clases base
    'BaseService',
    'ServiceResult', 
    'ServiceError',
    'ValidationServiceError',
    'PermissionServiceError',
    'NotFoundServiceError',
    
    # Servicios específicos
    'LoginService',
    'RegistrationService',
    'PasswordService',
    'VerificationService',
    'ProfileService',
    'AnalysisService', 
    'ImageManagementService',
    'FincaService',
    'LoteService',
    'ReportService',
    
    # Servicios por dominio
    'PredictionService',
    'MLService',
    'ImageProcessingService',
    'ImageStorageService',
    
    # Instancias de servicios
    'login_service',
    'registration_service',
    'password_service',
    'verification_service',
    'profile_service',
    'analysis_service',
    'image_service', 
    'finca_service',
    'lote_service',
    'report_service'
]


def __getattr__(name: str):
    """Lazy import/creation for services to avoid circular dependency."""
    global analysis_service
    
    if name in ('MLService', 'PredictionService'):
        _lazy_import_training_services()
        if name == 'MLService':
            return MLService
        elif name == 'PredictionService':
            return PredictionService
    elif name == 'analysis_service':
        if analysis_service is None:
            analysis_service = AnalysisService()
        return analysis_service
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


