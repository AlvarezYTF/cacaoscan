"""
MÃ³dulo de calibraciÃ³n con OpenCV para mediciÃ³n precisa de granos de cacao.
Permite convertir mediciones en pÃ­xeles a mediciones reales en milÃ­metros.

CaracterÃ­sticas:
- DetecciÃ³n automÃ¡tica de objetos de referencia (monedas, reglas, etc.)
- CalibraciÃ³n manual con puntos de referencia
- ValidaciÃ³n de precisiÃ³n de calibraciÃ³n
- IntegraciÃ³n con el sistema de predicciÃ³n existente
- Persistencia de parÃ¡metros de calibraciÃ³n
"""

import cv2
import numpy as np
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass
from enum import Enum
import math

from ..utils.paths import get_regressors_artifacts_dir, ensure_dir_exists
from ..utils.logs import get_ml_logger
from ..utils.io import save_json, load_json

logger = get_ml_logger("cacaoscan.ml.measurement")


class CalibrationMethod(Enum):
    """MÃ©todos de calibraciÃ³n disponibles."""
    COIN_DETECTION = "coin_detection"
    RULER_DETECTION = "ruler_detection"
    MANUAL_POINTS = "manual_points"
    AUTO_REFERENCE = "auto_reference"


class ReferenceObject(Enum):
    """Objetos de referencia conocidos."""
    COIN_1000_COP = {"diameter_mm": 23.0, "name": "Moneda 1000 COP"}
    COIN_500_COP = {"diameter_mm": 21.0, "name": "Moneda 500 COP"}
    COIN_200_COP = {"diameter_mm": 17.0, "name": "Moneda 200 COP"}
    COIN_100_COP = {"diameter_mm": 15.0, "name": "Moneda 100 COP"}
    RULER_1CM = {"length_mm": 10.0, "name": "Regla 1cm"}
    RULER_2CM = {"length_mm": 20.0, "name": "Regla 2cm"}
    RULER_5CM = {"length_mm": 50.0, "name": "Regla 5cm"}


@dataclass
class CalibrationResult:
    """Resultado de una calibraciÃ³n."""
    success: bool
    pixels_per_mm: float
    confidence: float
    method: CalibrationMethod
    reference_object: Optional[ReferenceObject]
    detected_points: List[Tuple[int, int]]
    error_message: Optional[str] = None
    calibration_image_path: Optional[str] = None


@dataclass
class CalibrationParams:
    """ParÃ¡metros de calibraciÃ³n."""
    pixels_per_mm: float
    method: CalibrationMethod
    reference_object: Optional[ReferenceObject]
    confidence: float
    timestamp: str
    image_dimensions: Tuple[int, int]
    validation_score: Optional[float] = None


class CoinDetector:
    """Detector de monedas colombianas usando OpenCV."""
    
    def __init__(self):
        """Inicializa el detector de monedas."""
        self.coin_templates = self._load_coin_templates()
        self.min_coin_area = 100  # Ãrea mÃ­nima en pÃ­xeles
        self.max_coin_area = 10000  # Ãrea mÃ¡xima en pÃ­xeles
        
    def _load_coin_templates(self) -> Dict[str, np.ndarray]:
        """Carga plantillas de monedas (implementaciÃ³n simplificada)."""
        # En una implementaciÃ³n real, se cargarÃ­an plantillas desde archivos
        return {
            "1000_cop": None,  # Se implementarÃ­a con plantillas reales
            "500_cop": None,
            "200_cop": None,
            "100_cop": None
        }
    
    def detect_coins(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detecta monedas en la imagen.
        
        Args:
            image: Imagen en formato BGR
            
        Returns:
            Lista de diccionarios con informaciÃ³n de monedas detectadas
        """
        # Convertir a escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Aplicar desenfoque gaussiano
        blurred = cv2.GaussianBlur(gray, (11, 11), 0)
        
        # Detectar cÃ­rculos usando HoughCircles
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=30,
            param1=50,
            param2=30,
            minRadius=10,
            maxRadius=100
        )
        
        detected_coins = []
        
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            
            for (x, y, r) in circles:
                # Validar Ã¡rea del cÃ­rculo
                area = math.pi * r * r
                if self.min_coin_area <= area <= self.max_coin_area:
                    # Clasificar moneda por tamaÃ±o
                    coin_type = self._classify_coin_by_size(r)
                    
                    detected_coins.append({
                        'center': (x, y),
                        'radius': r,
                        'diameter_pixels': 2 * r,
                        'area': area,
                        'coin_type': coin_type,
                        'confidence': 0.8  # Confianza estimada
                    })
        
        return detected_coins
    
    def _classify_coin_by_size(self, radius: int) -> Optional[ReferenceObject]:
        """Clasifica la moneda por su tamaÃ±o en pÃ­xeles."""
        diameter_pixels = 2 * radius
        
        # Rangos aproximados para diferentes monedas (se ajustarÃ­an con datos reales)
        if 40 <= diameter_pixels <= 50:  # ~23mm
            return ReferenceObject.COIN_1000_COP
        elif 35 <= diameter_pixels <= 45:  # ~21mm
            return ReferenceObject.COIN_500_COP
        elif 30 <= diameter_pixels <= 40:  # ~17mm
            return ReferenceObject.COIN_200_COP
        elif 25 <= diameter_pixels <= 35:  # ~15mm
            return ReferenceObject.COIN_100_COP
        
        return None


class RulerDetector:
    """Detector de reglas usando OpenCV."""
    
    def __init__(self):
        """Inicializa el detector de reglas."""
        self.min_line_length = 50  # Longitud mÃ­nima en pÃ­xeles
        self.max_line_length = 500  # Longitud mÃ¡xima en pÃ­xeles
        
    def detect_rulers(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detecta reglas en la imagen.
        
        Args:
            image: Imagen en formato BGR
            
        Returns:
            Lista de diccionarios con informaciÃ³n de reglas detectadas
        """
        # Convertir a escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Aplicar filtro Canny para detectar bordes
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Detectar lÃ­neas usando HoughLinesP
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi/180,
            threshold=100,
            minLineLength=self.min_line_length,
            maxLineGap=10
        )
        
        detected_rulers = []
        
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                
                # Calcular longitud de la lÃ­nea
                length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                
                if self.min_line_length <= length <= self.max_line_length:
                    # Clasificar regla por longitud
                    ruler_type = self._classify_ruler_by_length(length)
                    
                    detected_rulers.append({
                        'start_point': (x1, y1),
                        'end_point': (x2, y2),
                        'length_pixels': length,
                        'ruler_type': ruler_type,
                        'confidence': 0.7  # Confianza estimada
                    })
        
        return detected_rulers
    
    def _classify_ruler_by_length(self, length_pixels: float) -> Optional[ReferenceObject]:
        """Clasifica la regla por su longitud en pÃ­xeles."""
        # Rangos aproximados para diferentes reglas (se ajustarÃ­an con datos reales)
        if 200 <= length_pixels <= 300:  # ~50mm
            return ReferenceObject.RULER_5CM
        elif 80 <= length_pixels <= 120:  # ~20mm
            return ReferenceObject.RULER_2CM
        elif 40 <= length_pixels <= 60:  # ~10mm
            return ReferenceObject.RULER_1CM
        
        return None


class CalibrationManager:
    """Gestor principal de calibraciÃ³n."""
    
    def __init__(self, calibration_dir: Optional[Path] = None):
        """
        Inicializa el gestor de calibraciÃ³n.
        
        Args:
            calibration_dir: Directorio para guardar parÃ¡metros de calibraciÃ³n
        """
        self.calibration_dir = calibration_dir or get_regressors_artifacts_dir() / "calibration"
        ensure_dir_exists(self.calibration_dir)
        
        self.coin_detector = CoinDetector()
        self.ruler_detector = RulerDetector()
        self.current_calibration: Optional[CalibrationParams] = None
        
        logger.info(f"CalibrationManager inicializado en {self.calibration_dir}")
    
    def calibrate_image(
        self,
        image: np.ndarray,
        method: CalibrationMethod = CalibrationMethod.COIN_DETECTION,
        reference_object: Optional[ReferenceObject] = None,
        manual_points: Optional[List[Tuple[int, int]]] = None
    ) -> CalibrationResult:
        """
        Calibra una imagen usando el mÃ©todo especificado.
        
        Args:
            image: Imagen en formato BGR
            method: MÃ©todo de calibraciÃ³n a usar
            reference_object: Objeto de referencia especÃ­fico
            manual_points: Puntos manuales para calibraciÃ³n
            
        Returns:
            Resultado de la calibraciÃ³n
        """
        logger.info(f"Iniciando calibraciÃ³n con mÃ©todo: {method.value}")
        
        try:
            if method == CalibrationMethod.COIN_DETECTION:
                return self._calibrate_with_coins(image, reference_object)
            elif method == CalibrationMethod.RULER_DETECTION:
                return self._calibrate_with_rulers(image, reference_object)
            elif method == CalibrationMethod.MANUAL_POINTS:
                return self._calibrate_with_manual_points(image, manual_points)
            elif method == CalibrationMethod.AUTO_REFERENCE:
                return self._calibrate_auto_reference(image)
            else:
                raise ValueError(f"MÃ©todo de calibraciÃ³n no soportado: {method}")
                
        except Exception as e:
            logger.error(f"Error en calibraciÃ³n: {e}")
            return CalibrationResult(
                success=False,
                pixels_per_mm=0.0,
                confidence=0.0,
                method=method,
                reference_object=reference_object,
                detected_points=[],
                error_message=str(e)
            )
    
    def _calibrate_with_coins(
        self,
        image: np.ndarray,
        reference_object: Optional[ReferenceObject] = None
    ) -> CalibrationResult:
        """Calibra usando detecciÃ³n de monedas."""
        detected_coins = self.coin_detector.detect_coins(image)
        
        if not detected_coins:
            return CalibrationResult(
                success=False,
                pixels_per_mm=0.0,
                confidence=0.0,
                method=CalibrationMethod.COIN_DETECTION,
                reference_object=reference_object,
                detected_points=[],
                error_message="No se detectaron monedas en la imagen"
            )
        
        # Usar la moneda con mayor confianza o la especificada
        best_coin = None
        if reference_object:
            for coin in detected_coins:
                if coin['coin_type'] == reference_object:
                    best_coin = coin
                    break
        
        if not best_coin:
            best_coin = max(detected_coins, key=lambda x: x['confidence'])
        
        # Calcular pixels por mm
        coin_type = best_coin['coin_type']
        diameter_mm = coin_type.value['diameter_mm']
        diameter_pixels = best_coin['diameter_pixels']
        
        pixels_per_mm = diameter_pixels / diameter_mm
        
        # Crear imagen de calibraciÃ³n
        calibration_image = self._create_calibration_image(image, detected_coins)
        
        return CalibrationResult(
            success=True,
            pixels_per_mm=pixels_per_mm,
            confidence=best_coin['confidence'],
            method=CalibrationMethod.COIN_DETECTION,
            reference_object=coin_type,
            detected_points=[best_coin['center']],
            calibration_image_path=str(self._save_calibration_image(calibration_image))
        )
    
    def _calibrate_with_rulers(
        self,
        image: np.ndarray,
        reference_object: Optional[ReferenceObject] = None
    ) -> CalibrationResult:
        """Calibra usando detecciÃ³n de reglas."""
        detected_rulers = self.ruler_detector.detect_rulers(image)
        
        if not detected_rulers:
            return CalibrationResult(
                success=False,
                pixels_per_mm=0.0,
                confidence=0.0,
                method=CalibrationMethod.RULER_DETECTION,
                reference_object=reference_object,
                detected_points=[],
                error_message="No se detectaron reglas en la imagen"
            )
        
        # Usar la regla con mayor confianza o la especificada
        best_ruler = None
        if reference_object:
            for ruler in detected_rulers:
                if ruler['ruler_type'] == reference_object:
                    best_ruler = ruler
                    break
        
        if not best_ruler:
            best_ruler = max(detected_rulers, key=lambda x: x['confidence'])
        
        # Calcular pixels por mm
        ruler_type = best_ruler['ruler_type']
        length_mm = ruler_type.value['length_mm']
        length_pixels = best_ruler['length_pixels']
        
        pixels_per_mm = length_pixels / length_mm
        
        # Crear imagen de calibraciÃ³n
        calibration_image = self._create_calibration_image(image, detected_rulers, is_ruler=True)
        
        return CalibrationResult(
            success=True,
            pixels_per_mm=pixels_per_mm,
            confidence=best_ruler['confidence'],
            method=CalibrationMethod.RULER_DETECTION,
            reference_object=ruler_type,
            detected_points=[best_ruler['start_point'], best_ruler['end_point']],
            calibration_image_path=str(self._save_calibration_image(calibration_image))
        )
    
    def _calibrate_with_manual_points(
        self,
        image: np.ndarray,
        manual_points: Optional[List[Tuple[int, int]]] = None
    ) -> CalibrationResult:
        """Calibra usando puntos manuales."""
        if not manual_points or len(manual_points) < 2:
            return CalibrationResult(
                success=False,
                pixels_per_mm=0.0,
                confidence=0.0,
                method=CalibrationMethod.MANUAL_POINTS,
                reference_object=None,
                detected_points=[],
                error_message="Se requieren al menos 2 puntos para calibraciÃ³n manual"
            )
        
        # Calcular distancia en pÃ­xeles
        point1, point2 = manual_points[0], manual_points[1]
        distance_pixels = math.sqrt(
            (point2[0] - point1[0])**2 + (point2[1] - point1[1])**2
        )
        
        # Para calibraciÃ³n manual, se requiere que el usuario especifique la distancia real
        # Por ahora, asumimos una distancia de referencia de 10mm
        distance_mm = 10.0  # Esto deberÃ­a venir del usuario
        
        pixels_per_mm = distance_pixels / distance_mm
        
        return CalibrationResult(
            success=True,
            pixels_per_mm=pixels_per_mm,
            confidence=0.9,  # Alta confianza para calibraciÃ³n manual
            method=CalibrationMethod.MANUAL_POINTS,
            reference_object=None,
            detected_points=manual_points
        )
    
    def _calibrate_auto_reference(self, image: np.ndarray) -> CalibrationResult:
        """Calibra automÃ¡ticamente detectando cualquier objeto de referencia."""
        # Intentar primero con monedas
        coin_result = self._calibrate_with_coins(image)
        if coin_result.success and coin_result.confidence > 0.7:
            return coin_result
        
        # Si falla, intentar con reglas
        ruler_result = self._calibrate_with_rulers(image)
        if ruler_result.success and ruler_result.confidence > 0.7:
            return ruler_result
        
        # Si ambos fallan, retornar el mejor resultado
        if coin_result.confidence > ruler_result.confidence:
            return coin_result
        else:
            return ruler_result
    
    def _create_calibration_image(
        self,
        image: np.ndarray,
        detected_objects: List[Dict[str, Any]],
        is_ruler: bool = False
    ) -> np.ndarray:
        """Crea una imagen con las detecciones marcadas."""
        calibration_image = image.copy()
        
        for obj in detected_objects:
            if is_ruler:
                # Dibujar lÃ­nea para regla
                cv2.line(
                    calibration_image,
                    obj['start_point'],
                    obj['end_point'],
                    (0, 255, 0),
                    3
                )
                # Marcar puntos
                cv2.circle(calibration_image, obj['start_point'], 5, (0, 0, 255), -1)
                cv2.circle(calibration_image, obj['end_point'], 5, (0, 0, 255), -1)
            else:
                # Dibujar cÃ­rculo para moneda
                cv2.circle(
                    calibration_image,
                    obj['center'],
                    obj['radius'],
                    (0, 255, 0),
                    3
                )
                cv2.circle(calibration_image, obj['center'], 3, (0, 0, 255), -1)
        
        return calibration_image
    
    def _save_calibration_image(self, image: np.ndarray) -> Path:
        """Guarda la imagen de calibraciÃ³n."""
        import time
        timestamp = int(time.time())
        filename = f"calibration_{timestamp}.jpg"
        filepath = self.calibration_dir / filename
        
        cv2.imwrite(str(filepath), image)
        return filepath
    
    def save_calibration(self, calibration_result: CalibrationResult) -> None:
        """Guarda los parÃ¡metros de calibraciÃ³n."""
        if not calibration_result.success:
            raise ValueError("No se puede guardar una calibraciÃ³n fallida")
        
        calibration_params = CalibrationParams(
            pixels_per_mm=calibration_result.pixels_per_mm,
            method=calibration_result.method,
            reference_object=calibration_result.reference_object,
            confidence=calibration_result.confidence,
            timestamp=str(int(time.time())),
            image_dimensions=(0, 0),  # Se actualizarÃ­a con dimensiones reales
            validation_score=None
        )
        
        self.current_calibration = calibration_params
        
        # Guardar en archivo JSON
        calibration_file = self.calibration_dir / "current_calibration.json"
        calibration_data = {
            'pixels_per_mm': calibration_params.pixels_per_mm,
            'method': calibration_params.method.value,
            'reference_object': calibration_params.reference_object.value['name'] if calibration_params.reference_object else None,
            'confidence': calibration_params.confidence,
            'timestamp': calibration_params.timestamp,
            'image_dimensions': calibration_params.image_dimensions,
            'validation_score': calibration_params.validation_score
        }
        
        save_json(calibration_data, calibration_file)
        logger.info(f"CalibraciÃ³n guardada: {calibration_params.pixels_per_mm:.3f} pixels/mm")
    
    def load_calibration(self) -> Optional[CalibrationParams]:
        """Carga los parÃ¡metros de calibraciÃ³n guardados."""
        calibration_file = self.calibration_dir / "current_calibration.json"
        
        if not calibration_file.exists():
            logger.warning("No se encontrÃ³ archivo de calibraciÃ³n")
            return None
        
        try:
            calibration_data = load_json(calibration_file)
            
            calibration_params = CalibrationParams(
                pixels_per_mm=calibration_data['pixels_per_mm'],
                method=CalibrationMethod(calibration_data['method']),
                reference_object=None,  # Se reconstruirÃ­a desde el nombre
                confidence=calibration_data['confidence'],
                timestamp=calibration_data['timestamp'],
                image_dimensions=tuple(calibration_data['image_dimensions']),
                validation_score=calibration_data.get('validation_score')
            )
            
            self.current_calibration = calibration_params
            logger.info(f"CalibraciÃ³n cargada: {calibration_params.pixels_per_mm:.3f} pixels/mm")
            
            return calibration_params
            
        except Exception as e:
            logger.error(f"Error cargando calibraciÃ³n: {e}")
            return None
    
    def convert_pixels_to_mm(self, pixels: float) -> float:
        """
        Convierte pÃ­xeles a milÃ­metros usando la calibraciÃ³n actual.
        
        Args:
            pixels: Valor en pÃ­xeles
            
        Returns:
            Valor en milÃ­metros
        """
        if not self.current_calibration:
            raise ValueError("No hay calibraciÃ³n cargada")
        
        return pixels / self.current_calibration.pixels_per_mm
    
    def convert_mm_to_pixels(self, mm: float) -> float:
        """
        Convierte milÃ­metros a pÃ­xeles usando la calibraciÃ³n actual.
        
        Args:
            mm: Valor en milÃ­metros
            
        Returns:
            Valor en pÃ­xeles
        """
        if not self.current_calibration:
            raise ValueError("No hay calibraciÃ³n cargada")
        
        return mm * self.current_calibration.pixels_per_mm
    
    def validate_calibration(self, test_image: np.ndarray) -> Dict[str, Any]:
        """
        Valida la precisiÃ³n de la calibraciÃ³n actual.
        
        Args:
            test_image: Imagen de prueba con objetos de referencia conocidos
            
        Returns:
            Diccionario con mÃ©tricas de validaciÃ³n
        """
        if not self.current_calibration:
            raise ValueError("No hay calibraciÃ³n para validar")
        
        # Realizar nueva calibraciÃ³n en la imagen de prueba
        test_result = self.calibrate_image(test_image, self.current_calibration.method)
        
        if not test_result.success:
            return {
                'valid': False,
                'error': 'No se pudo realizar calibraciÃ³n de prueba',
                'accuracy_score': 0.0
            }
        
        # Comparar con calibraciÃ³n actual
        pixels_per_mm_diff = abs(test_result.pixels_per_mm - self.current_calibration.pixels_per_mm)
        accuracy_score = max(0.0, 1.0 - (pixels_per_mm_diff / self.current_calibration.pixels_per_mm))
        
        validation_result = {
            'valid': accuracy_score > 0.8,  # Umbral de precisiÃ³n
            'accuracy_score': accuracy_score,
            'pixels_per_mm_current': self.current_calibration.pixels_per_mm,
            'pixels_per_mm_test': test_result.pixels_per_mm,
            'difference': pixels_per_mm_diff,
            'test_confidence': test_result.confidence
        }
        
        # Actualizar score de validaciÃ³n
        self.current_calibration.validation_score = accuracy_score
        
        return validation_result


# Instancia global del gestor de calibraciÃ³n
_calibration_manager: Optional[CalibrationManager] = None


def get_calibration_manager() -> CalibrationManager:
    """Obtiene la instancia global del gestor de calibraciÃ³n."""
    global _calibration_manager
    if _calibration_manager is None:
        _calibration_manager = CalibrationManager()
    return _calibration_manager


def calibrate_image(
    image: np.ndarray,
    method: CalibrationMethod = CalibrationMethod.COIN_DETECTION,
    reference_object: Optional[ReferenceObject] = None
) -> CalibrationResult:
    """
    FunciÃ³n de conveniencia para calibrar una imagen.
    
    Args:
        image: Imagen en formato BGR
        method: MÃ©todo de calibraciÃ³n
        reference_object: Objeto de referencia especÃ­fico
        
    Returns:
        Resultado de la calibraciÃ³n
    """
    manager = get_calibration_manager()
    return manager.calibrate_image(image, method, reference_object)


def convert_pixels_to_mm(pixels: float) -> float:
    """
    FunciÃ³n de conveniencia para convertir pÃ­xeles a milÃ­metros.
    
    Args:
        pixels: Valor en pÃ­xeles
        
    Returns:
        Valor en milÃ­metros
    """
    manager = get_calibration_manager()
    return manager.convert_pixels_to_mm(pixels)


def convert_mm_to_pixels(mm: float) -> float:
    """
    FunciÃ³n de conveniencia para convertir milÃ­metros a pÃ­xeles.
    
    Args:
        mm: Valor en milÃ­metros
        
    Returns:
        Valor en pÃ­xeles
    """
    manager = get_calibration_manager()
    return manager.convert_mm_to_pixels(mm)


