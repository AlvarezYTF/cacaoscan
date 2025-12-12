"""
Interfaz base para convertidores de unidades de granos de cacao.

Este módulo define la interfaz base para todos los convertidores,
siguiendo el principio de Inversión de Dependencias (DIP).
"""
from abc import ABC, abstractmethod
from typing import Protocol

from ..models import CalibrationParams


class IConvertidor(Protocol):
    """Protocolo para convertidores de unidades de granos de cacao."""
    
    def convert(self, value: float) -> float:
        """
        Convierte un valor usando la calibración.
        
        Args:
            value: Valor a convertir
            
        Returns:
            Valor convertido
        """
        ...


class ConvertidorBase(ABC):
    """Clase base abstracta para convertidores de unidades de granos de cacao."""
    
    def __init__(self, calibration_params: CalibrationParams):
        """
        Inicializa el convertidor base.
        
        Args:
            calibration_params: Parámetros de calibración para granos de cacao
        """
        self.calibration_params = calibration_params
    
    @abstractmethod
    def convert(self, value: float) -> float:
        """
        Convierte un valor usando la calibración.
        
        Args:
            value: Valor a convertir
            
        Returns:
            Valor convertido
        """
        pass
    
    @property
    def pixels_per_mm(self) -> float:
        """Obtiene el factor de conversión píxeles por milímetro."""
        return self.calibration_params.pixels_per_mm


# Compatibilidad hacia atrás
IConverter = IConvertidor
BaseConverter = ConvertidorBase

