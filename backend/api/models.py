"""
Modelos de la API - Importar desde apps modulares.

Este archivo actúa como un punto de acceso para evitar conflictos de importación.
En lugar de definir modelos aquí, importamos desde las apps modulares correspondientes.
"""

# Import models from modular apps to avoid duplication
# Note: These imports are for type hints and re-exports, not for direct use
# Direct model usage should use get_model_safely from utils.model_imports
from .utils.model_imports import get_models_safely

# Import models safely (for re-export purposes)
_models = get_models_safely({
    'EmailVerificationToken': 'auth_app.models.EmailVerificationToken',
    'UserProfile': 'auth_app.models.UserProfile',
    'Finca': 'fincas_app.models.Finca',
    'Lote': 'fincas_app.models.Lote',
    'CacaoImage': 'images_app.models.CacaoImage',
    'CacaoPrediction': 'images_app.models.CacaoPrediction',
    'Notification': 'notifications.models.Notification',
    'ActivityLog': 'audit.models.ActivityLog',
    'TrainingJob': 'training.models.TrainingJob',
    'SystemSettings': 'core.models.SystemSettings'
})
# Re-export for backward compatibility
EmailVerificationToken = _models['EmailVerificationToken']
UserProfile = _models['UserProfile']
Finca = _models['Finca']
Lote = _models['Lote']
CacaoImage = _models['CacaoImage']
CacaoPrediction = _models['CacaoPrediction']
Notification = _models['Notification']
ActivityLog = _models['ActivityLog']
TrainingJob = _models['TrainingJob']
SystemSettings = _models['SystemSettings']

# Import models that were moved to modular apps (for backward compatibility)
# These models are now in their respective apps:
# - LoginHistory → audit.models
# - ReporteGenerado → reports.models
# - ModelMetrics → training.models
_models_moved = get_models_safely({
    'LoginHistory': 'audit.models.LoginHistory',
    'ReporteGenerado': 'reports.models.ReporteGenerado',
    'ModelMetrics': 'training.models.ModelMetrics'
})

# Re-export moved models for backward compatibility
LoginHistory = _models_moved['LoginHistory']
ReporteGenerado = _models_moved['ReporteGenerado']
ModelMetrics = _models_moved['ModelMetrics']


