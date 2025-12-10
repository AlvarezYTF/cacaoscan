"""
Interfaz para validadores de recortes.

Define el contrato que deben cumplir todas las implementaciones
de validadores, siguiendo el principio de Dependency Inversion.
"""
from typing import Protocol, Dict, List, Any, Tuple


class IValidadorRecorte(Protocol):
    """
    Interfaz para validadores de recortes.
    
    Define los métodos que debe implementar cualquier clase
    que valide recortes.
    """
    
    def validar_recorte_unico(self, record: Dict[str, Any]) -> bool:
        """
        Valida un recorte individual.
        
        Args:
            record: Registro que contiene crop_image_path
            
        Returns:
            True si el recorte es válido, False en caso contrario
        """
        ...
    
    def validar_lote(
        self,
        crop_records: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Valida la calidad de recortes para un lote de registros.
        
        Args:
            crop_records: Lista de registros con recortes
            
        Returns:
            Tupla de (registros_válidos, registros_inválidos)
        """
        ...


