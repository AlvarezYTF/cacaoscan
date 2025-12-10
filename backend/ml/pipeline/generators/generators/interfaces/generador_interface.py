"""
Interfaz para generadores de recortes.

Define el contrato que deben cumplir todas las implementaciones
de generadores, siguiendo el principio de Dependency Inversion.
"""
from typing import Protocol, Dict, List, Any


class IGeneradorRecorte(Protocol):
    """
    Interfaz para generadores de recortes.
    
    Define los métodos que debe implementar cualquier clase
    que genere recortes de imágenes.
    """
    
    def generate_crops(
        self,
        records: List[Dict[str, Any]],
        overwrite: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Genera recortes para registros.
        
        Args:
            records: Lista de registros a procesar
            overwrite: Si se deben sobrescribir recortes existentes
            
        Returns:
            Lista de registros con recortes generados
        """
        ...

