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
from .auth_service import AuthenticationService
from .analysis_service import AnalysisService
from .image_service import ImageManagementService
from .finca_service import FincaService
from .lote_service import LoteService
from .report_service import ReportService

# Importar servicios por dominio
from .ml.prediction_service import PredictionService
from .image.processing_service import ImageProcessingService
from .image.storage_service import ImageStorageService

# Crear instancias de servicios para uso fácil
auth_service = AuthenticationService()
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
    'AuthenticationService',
    'AnalysisService', 
    'ImageManagementService',
    'FincaService',
    'LoteService',
    'ReportService',
    
    # Servicios por dominio
    'PredictionService',
    'ImageProcessingService',
    'ImageStorageService',
    
    # Instancias de servicios
    'auth_service',
    'analysis_service',
    'image_service', 
    'finca_service',
    'lote_service',
    'report_service'
]


