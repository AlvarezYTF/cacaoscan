"""
Modelos de la API.

Este módulo re-exporta modelos desde apps modulares para compatibilidad hacia atrás.
Los modelos se importan de forma lazy para evitar dependencias circulares durante el setup de Django.

Para usar modelos, se recomienda importar directamente desde sus apps:
    from auth_app.models import UserProfile, EmailVerificationToken
    from fincas_app.models import Finca, Lote
    from images_app.models import CacaoImage, CacaoPrediction
    from notifications.models import Notification
    from audit.models import ActivityLog, LoginHistory
    from training.models import TrainingJob, ModelMetrics
    from reports.models import ReporteGenerado
    from core.models import SystemSettings
"""

# Lazy imports to avoid circular dependencies during Django setup
def __getattr__(name: str):
    """
    Lazy import of models for backward compatibility.
    This avoids circular dependencies during Django setup.
    """
    from .utils.model_imports import get_model_safely
    
    # Map of model names to their module paths
    model_paths = {
        'EmailVerificationToken': 'auth_app.models.EmailVerificationToken',
        'UserProfile': 'auth_app.models.UserProfile',
        'Finca': 'fincas_app.models.Finca',
        'Lote': 'fincas_app.models.Lote',
        'CacaoImage': 'images_app.models.CacaoImage',
        'CacaoPrediction': 'images_app.models.CacaoPrediction',
        'Notification': 'notifications.models.Notification',
        'ActivityLog': 'audit.models.ActivityLog',
        'LoginHistory': 'audit.models.LoginHistory',
        'TrainingJob': 'training.models.TrainingJob',
        'ModelMetrics': 'training.models.ModelMetrics',
        'SystemSettings': 'core.models.SystemSettings',
        'ReporteGenerado': 'reports.models.ReporteGenerado',
    }
    
    if name in model_paths:
        model = get_model_safely(model_paths[name])
        if model is not None:
            # Cache the model in globals for future access
            globals()[name] = model
            return model
        else:
            raise ImportError(f"Could not import {name} from {model_paths[name]}")
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

