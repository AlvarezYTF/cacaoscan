"""
Interfaz para generadores de recortes.

Define el contrato que deben cumplir todas las implementaciones
de generadores, siguiendo el principio de Dependency Inversion.
"""
from typing import Protocol, Dict, List, Any, Tuple


class IGeneradorRecorte(Protocol):
    """
    Interfaz para generadores de recortes.
    
    Define los métodos que debe implementar cualquier clase
    que gestione la generación de recortes.
    """
    
    def filter_records_by_crops(
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
        ...
    
    def generate_crops_for_missing(
        self,
        missing_records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Genera recortes para registros que no los tienen.
        
        Args:
            missing_records: Lista de registros sin recortes
            
        Returns:
            Lista de registros con recortes generados
        """
        ...

