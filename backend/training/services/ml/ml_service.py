"""
ML Service for managing ML model loading and lifecycle in CacaoScan.
Implements singleton pattern with thread-safe lazy loading to ensure models
are loaded only once across the application.
"""
import logging
import threading
from typing import Optional, Dict, Any
from enum import Enum

from api.services.base import BaseService, ServiceResult, ValidationServiceError

logger = logging.getLogger("cacaoscan.services.ml")

# Success message constants
MSG_PREDICTOR_OBTAINED = "Predictor obtained successfully"


class ModelLoadState(Enum):
    """Enum for model loading states."""
    NOT_LOADED = "not_loaded"
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"


class MLService(BaseService):
    """
    Service for managing ML model lifecycle.
    
    Responsibilities:
    - Centralized model loading with singleton pattern
    - Thread-safe lazy loading
    - Preventing multiple concurrent loads
    - Managing model state and availability
    
    This service ensures models are loaded only once, even across multiple requests.
    """
    
    _instance: Optional['MLService'] = None
    _lock = threading.Lock()
    _predictor_instance = None
    _load_state = ModelLoadState.NOT_LOADED
    _load_error: Optional[str] = None
    
    def __new__(cls):
        """
        Singleton pattern: ensure only one instance exists.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(MLService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """
        Initialize the ML service.
        Note: __init__ may be called multiple times due to singleton pattern,
        so we only initialize once.
        """
        if hasattr(self, '_initialized'):
            return
        
        super().__init__()
        self._initialized = True
        self._load_lock = threading.Lock()
    
    def _import_predictor_modules(self):
        """Import predictor modules, returning error result if import fails."""
        try:
            from ml.prediction import get_predictor as _get_predictor, load_artifacts
            return _get_predictor, load_artifacts, None
        except ImportError:
            error = ServiceResult.error(
                ValidationServiceError(
                    "ML prediction module not available",
                    details={"module": "ml.prediction"}
                )
            )
            return None, None, error
    
    def _handle_already_loaded_predictor(self):
        """Handle case when predictor is already loaded."""
        return ServiceResult.success(
            data=self._predictor_instance,
            message=f"{MSG_PREDICTOR_OBTAINED} (already loaded)"
        )
    
    def _handle_loading_state(self, get_predictor):
        """Handle case when models are currently loading."""
        self.log_info("Models are currently loading, waiting...")
        predictor = get_predictor()
        if predictor.models_loaded:
            self._predictor_instance = predictor
            self._load_state = ModelLoadState.LOADED
            return ServiceResult.success(
                data=predictor,
                message=MSG_PREDICTOR_OBTAINED
            )
        return None
    
    def _load_models_with_lock(self, get_predictor, load_artifacts, force_reload):
        """Load models while holding the load lock."""
        with self._load_lock:
            if not force_reload and self._load_state == ModelLoadState.LOADED:
                return ServiceResult.success(
                    data=self._predictor_instance,
                    message=f"{MSG_PREDICTOR_OBTAINED} (loaded by another thread)"
                )
            
            return self._perform_model_loading(get_predictor, load_artifacts)
    
    def _perform_model_loading(self, get_predictor, load_artifacts):
        """Perform the actual model loading logic."""
        self._load_state = ModelLoadState.LOADING
        self._load_error = None
        
        try:
            self.log_info("Loading ML models (first time or forced reload)...")
            predictor = get_predictor()
            
            if predictor.models_loaded:
                return self._complete_loading(predictor, "Models already loaded in predictor instance")
            
            return self._load_artifacts_and_verify(get_predictor, load_artifacts)
            
        except Exception as e:
            return self._handle_loading_error(e)
    
    def _complete_loading(self, predictor, log_message):
        """Complete the loading process and return success."""
        self._predictor_instance = predictor
        self._load_state = ModelLoadState.LOADED
        self.log_info(log_message)
        return ServiceResult.success(
            data=predictor,
            message=MSG_PREDICTOR_OBTAINED
        )
    
    def _load_artifacts_and_verify(self, get_predictor, load_artifacts):
        """Load artifacts and verify they loaded correctly."""
        self.log_info("Models not loaded, loading artifacts...")
        success = load_artifacts()
        
        if not success:
            return self._create_artifacts_error()
        
        predictor = get_predictor()
        if not predictor.models_loaded:
            return self._create_verification_error()
        
        return self._complete_loading(predictor, "ML models loaded successfully")
    
    def _create_artifacts_error(self):
        """Create error result for failed artifact loading."""
        self._load_state = ModelLoadState.ERROR
        self._load_error = "Failed to load artifacts"
        return ServiceResult.error(
            ValidationServiceError(
                "Models not available. Run automatic initialization first.",
                details={
                    "suggestion": "POST /api/v1/auto-initialize/ to initialize the system",
                    "or": "POST /api/v1/models/load/ to load models manually"
                }
            )
        )
    
    def _create_verification_error(self):
        """Create error result for verification failure."""
        self._load_state = ModelLoadState.ERROR
        self._load_error = "Models failed to load after load_artifacts()"
        return ServiceResult.error(
            ValidationServiceError("Error loading models after load_artifacts()")
        )
    
    def _handle_loading_error(self, error):
        """Handle errors during model loading."""
        self._load_state = ModelLoadState.ERROR
        self._load_error = str(error)
        self.log_error(f"Error loading models: {str(error)}")
        return ServiceResult.error(
            ValidationServiceError(
                "Internal error loading models",
                details={"original_error": str(error)}
            )
        )
    
    def get_predictor(self, force_reload: bool = False) -> ServiceResult:
        """
        Gets the ML predictor instance with lazy loading.
        
        Models are loaded only once, on first access. Subsequent calls
        return the same instance without reloading.
        
        Args:
            force_reload: If True, force reload of models even if already loaded.
                         Use with caution as this is expensive.
        
        Returns:
            ServiceResult with predictor instance
        """
        try:
            get_predictor, load_artifacts, import_error = self._import_predictor_modules()
            if import_error:
                return import_error
            
            if not force_reload and self._predictor_instance is not None:
                if self._load_state == ModelLoadState.LOADED:
                    return self._handle_already_loaded_predictor()
                
                if self._load_state == ModelLoadState.LOADING:
                    result = self._handle_loading_state(get_predictor)
                    if result:
                        return result
            
            return self._load_models_with_lock(get_predictor, load_artifacts, force_reload)
        
        except Exception as e:
            self.log_error(f"Error getting predictor: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError(
                    "Internal error getting predictor",
                    details={"original_error": str(e)}
                )
            )
    
    def load_models(self, force: bool = False) -> ServiceResult:
        """
        Explicitly loads ML models.
        
        This method ensures models are loaded. If models are already loaded
        and force=False, it returns success without reloading.
        
        Args:
            force: If True, force reload even if models are already loaded.
        
        Returns:
            ServiceResult indicating success or failure
        """
        result = self.get_predictor(force_reload=force)
        
        if result.success:
            return ServiceResult.success(
                message="Models loaded successfully"
            )
        else:
            return result
    
    def get_model_status(self) -> ServiceResult:
        """
        Gets the current status of ML models.
        
        Returns:
            ServiceResult with model status information
        """
        try:
            try:
                from ml.prediction import get_predictor as _get_predictor
            except ImportError:
                return ServiceResult.error(
                    ValidationServiceError(
                        "ML prediction module not available",
                        details={"module": "ml.prediction"}
                    )
                )
            
            predictor = _get_predictor()
            model_info = predictor.get_model_info()
            
            status_data = {
                'load_state': self._load_state.value,
                'models_loaded': predictor.models_loaded,
                'status': model_info.get('status', 'not_loaded'),
                'device': model_info.get('device', 'unknown'),
                'model': model_info.get('model', 'HybridCacaoRegression'),
                'model_details': model_info.get('model_details', {}),
                'scalers': model_info.get('scalers', 'not_loaded'),
                'load_error': self._load_error
            }
            
            return ServiceResult.success(
                data=status_data,
                message="Model status obtained successfully"
            )
            
        except Exception as e:
            self.log_error(f"Error getting model status: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError(
                    "Internal error getting model status",
                    details={"original_error": str(e)}
                )
            )
    
    def reload_models(self) -> ServiceResult:
        """
        Forces reload of ML models.
        
        This is expensive and should only be used when models have been updated.
        
        Returns:
            ServiceResult indicating success or failure
        """
        self.log_info("Forcing reload of ML models...")
        
        # Reset state
        with self._load_lock:
            self._predictor_instance = None
            self._load_state = ModelLoadState.NOT_LOADED
            self._load_error = None
        
        # Load models
        return self.load_models(force=True)

