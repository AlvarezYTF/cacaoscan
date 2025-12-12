"""
Gestor de calibración para medición precisa de granos de cacao.

REFACTORIZADO: Aplicando principios SOLID
- Separación de responsabilidades: calibrators, storage, converters, validators
- Enfocado exclusivamente en granos de cacao usando pixel_calibration.json
"""
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from ..utils.paths import get_regressors_artifacts_dir, ensure_dir_exists
from ..utils.logs import get_ml_logger
from .models import (
    CalibrationMethod,
    CalibrationResult,
    CalibrationParams
)
from .calibrators import ManualCalibrator
from .storage import CalibrationStorage
from .converters import ConvertidorUnidades

logger = get_ml_logger("cacaoscan.ml.measurement")


class GestorCalibracion:
    """Gestor principal de calibración para granos de cacao."""
    
    def __init__(self, calibration_dir: Optional[Path] = None):
        """
        Inicializa el gestor de calibración.
        
        Args:
            calibration_dir: Directorio para archivos de calibración
        """
        self._calibration_dir: Optional[Path] = calibration_dir
        self._initialized_dir: bool = False
        
        # Inicializar componentes (storage se inicializará con directorio lazy)
        self.manual_calibrator = ManualCalibrator()
        self._storage: Optional[CalibrationStorage] = None
        self.converter = ConvertidorUnidades()
        
        self.current_calibration: Optional[CalibrationParams] = None
        
        logger.info(f"GestorCalibracion inicializado")
    
    @property
    def storage(self) -> CalibrationStorage:
        """
        Obtiene el almacenamiento de calibración, inicializándolo si es necesario.
        
        Returns:
            Almacenamiento de calibración
        """
        if self._storage is None:
            self._storage = CalibrationStorage(self.calibration_dir)
        return self._storage
    
    @property
    def calibration_dir(self) -> Path:
        """
        Obtiene el directorio de calibración, inicializándolo si es necesario.
        
        Returns:
            Directorio de calibración
        """
        if not self._initialized_dir:
            if self._calibration_dir is None:
                try:
                    self._calibration_dir = get_regressors_artifacts_dir() / "calibration"
                except Exception as e:
                    # Si Django no está configurado, usar directorio temporal
                    from pathlib import Path
                    import tempfile
                    temp_dir = Path(tempfile.gettempdir()) / "cacaoscan_calibration"
                    self._calibration_dir = temp_dir
                    logger.warning(f"No se pudo obtener directorio de artefactos, usando temporal: {temp_dir}. Error: {e}")
            
            ensure_dir_exists(self._calibration_dir)
            self._initialized_dir = True
            logger.info(f"Directorio de calibración: {self._calibration_dir}")
        
        return self._calibration_dir
    
    def calibrar_imagen(
        self,
        image: np.ndarray,
        method: CalibrationMethod = CalibrationMethod.DATASET_CALIBRATION,
        manual_points: Optional[List[Tuple[int, int]]] = None
    ) -> CalibrationResult:
        """
        Calibra imagen usando el método especificado.
        
        Args:
            image: Imagen en formato BGR
            method: Método de calibración a usar
            manual_points: Puntos manuales para calibración (solo para MANUAL_POINTS)
            
        Returns:
            Resultado de calibración
        """
        logger.info(f"Iniciando calibración con método: {method.value}")
        
        try:
            if method == CalibrationMethod.DATASET_CALIBRATION:
                # La calibración basada en dataset se maneja mediante pixel_calibration.json
                # Este método no requiere procesamiento de imagen aquí
                logger.info("Calibración basada en dataset (pixel_calibration.json) - no requiere procesamiento de imagen")
                return CalibrationResult(
                    success=True,
                    pixels_per_mm=0.0,  # Se obtiene del dataset
                    confidence=1.0,
                    method=method,
                    detected_points=[],
                    error_message=None
                )
            elif method == CalibrationMethod.MANUAL_POINTS:
                if not manual_points:
                    raise ValueError("Se requieren puntos manuales para calibración manual")
                return self.manual_calibrator.calibrate(manual_points)
            else:
                raise ValueError(f"Método de calibración no soportado: {method}")
                
        except Exception as e:
            logger.error(f"Error en calibración: {e}")
            return CalibrationResult(
                success=False,
                pixels_per_mm=0.0,
                confidence=0.0,
                method=method,
                detected_points=[],
                error_message=str(e)
            )
    
    def guardar_calibracion(self, calibration_result: CalibrationResult) -> None:
        """Guarda parámetros de calibración."""
        if not calibration_result.success:
            raise ValueError("No se puede guardar una calibración fallida")
        
        calibration_params = CalibrationParams(
            pixels_per_mm=calibration_result.pixels_per_mm,
            method=calibration_result.method,
            confidence=calibration_result.confidence,
            timestamp=str(int(time.time())),
            image_dimensions=(0, 0),  # Se actualizaría con dimensiones reales
            validation_score=None
        )
        
        self.current_calibration = calibration_params
        self.converter.set_calibration(calibration_params)
        self.storage.save(calibration_params)
    
    def cargar_calibracion(self) -> Optional[CalibrationParams]:
        """Carga parámetros de calibración guardados."""
        calibration_params = self.storage.load()
        
        if calibration_params:
            self.current_calibration = calibration_params
            self.converter.set_calibration(calibration_params)
        
        return calibration_params
    
    def convertir_pixeles_a_mm(self, pixels: float) -> float:
        """
        Convierte píxeles a milímetros usando la calibración actual.
        
        Args:
            pixels: Valor en píxeles
            
        Returns:
            Valor en milímetros
        """
        return self.converter.convert_pixels_to_mm(pixels)
    
    def convertir_mm_a_pixeles(self, mm: float) -> float:
        """
        Convierte milímetros a píxeles usando la calibración actual.
        
        Args:
            mm: Valor en milímetros
            
        Returns:
            Valor en píxeles
        """
        return self.converter.convert_mm_to_pixels(mm)
    
    # Métodos de compatibilidad hacia atrás
    def calibrate_image(
        self,
        image: np.ndarray,
        method: CalibrationMethod = CalibrationMethod.DATASET_CALIBRATION,
        manual_points: Optional[List[Tuple[int, int]]] = None
    ) -> CalibrationResult:
        """Alias de compatibilidad hacia atrás para calibrar_imagen."""
        return self.calibrar_imagen(image, method, manual_points)
    
    def save_calibration(self, calibration_result: CalibrationResult) -> None:
        """Alias de compatibilidad hacia atrás para guardar_calibracion."""
        return self.guardar_calibracion(calibration_result)
    
    def load_calibration(self) -> Optional[CalibrationParams]:
        """Alias de compatibilidad hacia atrás para cargar_calibracion."""
        return self.cargar_calibracion()
    
    def convert_pixels_to_mm(self, pixels: float) -> float:
        """Alias de compatibilidad hacia atrás para convertir_pixeles_a_mm."""
        return self.convertir_pixeles_a_mm(pixels)
    
    def convert_mm_to_pixels(self, mm: float) -> float:
        """Alias de compatibilidad hacia atrás para convertir_mm_a_pixeles."""
        return self.convertir_mm_a_pixeles(mm)


# Instancia global del gestor de calibración
_gestor_calibracion: Optional[GestorCalibracion] = None
_calibration_manager: Optional[GestorCalibracion] = None  # Compatibilidad hacia atrás


def obtener_gestor_calibracion() -> GestorCalibracion:
    """Obtiene la instancia global del gestor de calibración."""
    global _gestor_calibracion
    if _gestor_calibracion is None:
        _gestor_calibracion = GestorCalibracion()
    return _gestor_calibracion


def get_calibration_manager() -> GestorCalibracion:
    """Alias de compatibilidad hacia atrás para obtener_gestor_calibracion."""
    global _calibration_manager
    if _calibration_manager is None:
        _calibration_manager = GestorCalibracion()
    return _calibration_manager


def calibrar_imagen(
    image: np.ndarray,
    method: CalibrationMethod = CalibrationMethod.DATASET_CALIBRATION,
    manual_points: Optional[List[Tuple[int, int]]] = None
) -> CalibrationResult:
    """
    Función de conveniencia para calibrar una imagen.
    
    Args:
        image: Imagen en formato BGR
        method: Método de calibración
        manual_points: Puntos manuales (solo para MANUAL_POINTS)
        
    Returns:
        Resultado de calibración
    """
    gestor = obtener_gestor_calibracion()
    return gestor.calibrar_imagen(image, method, manual_points)


def calibrate_image(
    image: np.ndarray,
    method: CalibrationMethod = CalibrationMethod.DATASET_CALIBRATION,
    manual_points: Optional[List[Tuple[int, int]]] = None
) -> CalibrationResult:
    """Alias de compatibilidad hacia atrás para calibrar_imagen."""
    return calibrar_imagen(image, method, manual_points)


def convertir_pixeles_a_mm(pixels: float) -> float:
    """
    Función de conveniencia para convertir píxeles a milímetros.
    
    Args:
        pixels: Valor en píxeles
        
    Returns:
        Valor en milímetros
    """
    gestor = obtener_gestor_calibracion()
    return gestor.convertir_pixeles_a_mm(pixels)


def convert_pixels_to_mm(pixels: float) -> float:
    """Alias de compatibilidad hacia atrás para convertir_pixeles_a_mm."""
    return convertir_pixeles_a_mm(pixels)


def convertir_mm_a_pixeles(mm: float) -> float:
    """
    Función de conveniencia para convertir milímetros a píxeles.
    
    Args:
        mm: Valor en milímetros
        
    Returns:
        Valor en píxeles
    """
    gestor = obtener_gestor_calibracion()
    return gestor.convertir_mm_a_pixeles(mm)


def convert_mm_to_pixels(mm: float) -> float:
    """Alias de compatibilidad hacia atrás para convertir_mm_a_pixeles."""
    return convertir_mm_a_pixeles(mm)

