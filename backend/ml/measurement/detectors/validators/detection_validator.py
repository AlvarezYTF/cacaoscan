"""
Validador de detecciones de granos de cacao.

Este módulo valida la calidad y precisión de detecciones,
siguiendo el principio de Responsabilidad Única.
"""
from typing import Dict, Any, List
import numpy as np

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.measurement.detectors.validators")


class DetectionValidator:
    """
    Validador de detecciones de granos de cacao.
    
    Valida que las detecciones cumplan con los criterios mínimos de calidad
    para medición precisa de granos de cacao.
    """
    
    def __init__(
        self,
        min_confidence: float = 0.5,
        min_area: int = 100,
        min_bbox_size: int = 10
    ):
        """
        Inicializa el validador.
        
        Args:
            min_confidence: Confianza mínima requerida para detección válida
            min_area: Área mínima en píxeles para grano de cacao válido
            min_bbox_size: Tamaño mínimo del bounding box en píxeles
        """
        self.min_confidence = min_confidence
        self.min_area = min_area
        self.min_bbox_size = min_bbox_size
    
    def validate(self, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida una detección de grano de cacao.
        
        Args:
            detection_result: Resultado de detección a validar
            
        Returns:
            Diccionario con resultado de validación:
            - valid: bool - Si la detección es válida
            - errors: List[str] - Lista de errores encontrados
            - warnings: List[str] - Lista de advertencias
        """
        errors: List[str] = []
        warnings: List[str] = []
        
        if not detection_result.get('success', False):
            errors.append("La detección no fue exitosa")
            return {
                'valid': False,
                'errors': errors,
                'warnings': warnings
            }
        
        confidence = detection_result.get('confidence', 0.0)
        if confidence < self.min_confidence:
            errors.append(
                f"Confianza muy baja: {confidence:.2f} < {self.min_confidence}"
            )
        elif confidence < 0.7:
            warnings.append(
                f"Confianza moderada: {confidence:.2f} (recomendado > 0.7)"
            )
        
        bbox = detection_result.get('bbox')
        if bbox is not None:
            if len(bbox) != 4:
                errors.append(f"Bounding box inválido: debe tener 4 valores, tiene {len(bbox)}")
            else:
                x, y, w, h = bbox
                if w < self.min_bbox_size or h < self.min_bbox_size:
                    errors.append(
                        f"Bounding box muy pequeño: {w}x{h} píxeles "
                        f"(mínimo: {self.min_bbox_size}x{self.min_bbox_size})"
                    )
                if w <= 0 or h <= 0:
                    errors.append(f"Bounding box con dimensiones inválidas: {w}x{h}")
        
        mask = detection_result.get('mask')
        if mask is not None:
            if not isinstance(mask, np.ndarray):
                errors.append("La máscara debe ser un array de numpy")
            else:
                area = int(np.sum(mask > 0))
                if area < self.min_area:
                    errors.append(
                        f"Área de máscara muy pequeña: {area} píxeles "
                        f"(mínimo: {self.min_area})"
                    )
                elif area < self.min_area * 2:
                    warnings.append(
                        f"Área de máscara pequeña: {area} píxeles "
                        f"(recomendado: > {self.min_area * 2})"
                    )
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def set_thresholds(
        self,
        min_confidence: float = None,
        min_area: int = None,
        min_bbox_size: int = None
    ) -> None:
        """
        Actualiza los umbrales de validación.
        
        Args:
            min_confidence: Nueva confianza mínima (opcional)
            min_area: Nueva área mínima (opcional)
            min_bbox_size: Nuevo tamaño mínimo de bbox (opcional)
        """
        if min_confidence is not None:
            if not 0.0 <= min_confidence <= 1.0:
                raise ValueError(f"min_confidence debe estar entre 0.0 y 1.0, recibido: {min_confidence}")
            self.min_confidence = min_confidence
        
        if min_area is not None:
            if min_area < 0:
                raise ValueError(f"min_area debe ser >= 0, recibido: {min_area}")
            self.min_area = min_area
        
        if min_bbox_size is not None:
            if min_bbox_size < 0:
                raise ValueError(f"min_bbox_size debe ser >= 0, recibido: {min_bbox_size}")
            self.min_bbox_size = min_bbox_size

