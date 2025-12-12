"""
Interfaz para filtros de registros.

Define el contrato que deben cumplir todas las implementaciones
de filtros, siguiendo el principio de Dependency Inversion.
"""
from typing import Protocol, Dict, List, Any, Tuple


class IFiltro(Protocol):
    """
    Interfaz para filtros de registros.
    
    Define los métodos que debe implementar cualquier clase
    que filtre registros.
    """
    
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
        ...

