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
from training.services import MLService, PredictionService

# Crear instancias de servicios para uso fácil
login_service = LoginService()
registration_service = RegistrationService()
password_service = PasswordService()
verification_service = VerificationService()
profile_service = ProfileService()
analysis_service = AnalysisService()
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


