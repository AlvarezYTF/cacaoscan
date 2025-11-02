"""
Utilidades para logging del proyecto ML.
"""
import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str,
    log_file: Optional[Path] = None,
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Configura un logger con salida a consola y opcionalmente a archivo.
    
    Args:
        name: Nombre del logger
        log_file: Archivo de log opcional
        level: Nivel de logging
        format_string: Formato personalizado opcional
    
    Returns:
        Logger configurado
    """
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Limpiar handlers existentes
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Formatter
    formatter = logging.Formatter(format_string)
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo si se especifica
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_ml_logger(name: str = "cacaoscan.ml") -> logging.Logger:
    """Obtiene el logger principal para ML."""
    return setup_logger(name)


def log_processing_stats(
    logger: logging.Logger,
    total_items: int,
    processed_items: int,
    successful_items: int,
    failed_items: int,
    processing_time: float
) -> None:
    """Log de estadÃ­sticas de procesamiento."""
    success_rate = (successful_items / processed_items * 100) if processed_items > 0 else 0
    avg_time = processing_time / processed_items if processed_items > 0 else 0
    
    logger.info(f"Procesamiento completado:")
    logger.info(f"  Total items: {total_items}")
    logger.info(f"  Procesados: {processed_items}")
    logger.info(f"  Exitosos: {successful_items}")
    logger.info(f"  Fallidos: {failed_items}")
    logger.info(f"  Tasa de Ã©xito: {success_rate:.2f}%")
    logger.info(f"  Tiempo promedio por item: {avg_time:.3f}s")
    logger.info(f"  Tiempo total: {processing_time:.2f}s")


