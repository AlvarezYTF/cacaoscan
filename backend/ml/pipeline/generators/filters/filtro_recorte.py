"""
Filtro de registros por disponibilidad de recortes.

Este módulo maneja el filtrado de registros por disponibilidad de recortes,
siguiendo principios SOLID:
- Single Responsibility: solo filtrado, no normalización ni verificación
- Dependency Inversion: implementa IFiltro
"""
from pathlib import Path
from typing import Dict, List, Any, Tuple

from ....utils.logs import get_ml_logger
from .normalizadores import NormalizadorPath
from .verificadores import VerificadorExistencia

logger = get_ml_logger("cacaoscan.ml.pipeline.generators.filters")


class FiltroRecorte:
    """
    Filtro de registros por disponibilidad de recortes.
    
    Responsabilidad única: filtrar registros por disponibilidad de recortes.
    La normalización de rutas está delegada a NormalizadorPath (SRP).
    La verificación de existencia está delegada a VerificadorExistencia (SRP).
    """
    
    def __init__(self):
        """Inicializa el filtro de recortes."""
        self.normalizador = NormalizadorPath()
        self.verificador = VerificadorExistencia()
    
    def filtrar_por_recortes(
        self,
        valid_records: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Filtra registros por disponibilidad de recortes.
        
        Args:
            valid_records: Lista de registros a filtrar
            
        Returns:
            Tupla de (registros_con_recortes, registros_sin_recortes)
        """
        registros_con_recortes: List[Dict[str, Any]] = []
        registros_sin_recortes: List[Dict[str, Any]] = []
        
        for record in valid_records:
            crop_path_value = record.get("crop_image_path")
            crop_path = self.normalizador.normalizar_path(crop_path_value)
            
            # Actualizar el registro con la ruta normalizada
            record["crop_image_path"] = crop_path
            
            if self.verificador.existe(crop_path):
                registros_con_recortes.append(record)
            else:
                registros_sin_recortes.append(record)
        
        logger.info(f"Registros con recortes disponibles: {len(registros_con_recortes)}")
        logger.info(f"Registros sin recortes: {len(registros_sin_recortes)}")
        
        return registros_con_recortes, registros_sin_recortes
    
    def filter_by_crops(
        self,
        valid_records: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Alias de compatibilidad hacia atrás para filtrar_por_recortes."""
        return self.filtrar_por_recortes(valid_records)

