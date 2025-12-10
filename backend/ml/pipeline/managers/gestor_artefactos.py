"""
Gestor de artefactos de entrenamiento para granos de cacao.

Este módulo maneja el guardado, carga y verificación de artefactos de entrenamiento
(modelos, scalers, checkpoints), siguiendo principios SOLID:
- Single Responsibility: gestión de artefactos
- Dependency Inversion: implementa IGestorArtefactos
"""
from pathlib import Path
from typing import Dict, List, Optional, Any
import torch

from ...utils.logs import get_ml_logger
from ...utils.paths import get_regressors_artifacts_dir
from ...regression.scalers import save_scalers, CacaoScalers
from ...regression.models import TARGETS
from .interfaces import IGestorArtefactos

logger = get_ml_logger("cacaoscan.ml.pipeline.managers")


class GestorArtefactos(IGestorArtefactos):
    """
    Gestor de artefactos de entrenamiento (modelos, scalers, checkpoints).
    
    Responsabilidad única: gestión de artefactos de entrenamiento.
    """
    
    # Constantes de nombres de archivos de modelos
    MODELO_HIBRIDO = "hybrid.pt"
    MODELO_MULTIHEAD = "multihead.pt"
    # Compatibilidad hacia atrás
    MODEL_HYBRID = MODELO_HIBRIDO
    MODEL_MULTIHEAD = MODELO_MULTIHEAD
    
    def __init__(self, artifacts_dir: Optional[Path] = None):
        """
        Inicializa el gestor de artefactos.
        
        Args:
            artifacts_dir: Directorio para artefactos (por defecto regressors_artifacts_dir)
        """
        self.artifacts_dir = artifacts_dir or get_regressors_artifacts_dir()
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"GestorArtefactos inicializado (dir={self.artifacts_dir})")
    
    def guardar_scalers(self, scalers: CacaoScalers) -> bool:
        """
        Guarda scalers en disco.
        
        Args:
            scalers: Instancia de CacaoScalers a guardar
            
        Returns:
            True si se guardó exitosamente, False en caso contrario
        """
        try:
            save_scalers(scalers)
            logger.info("Scalers guardados exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error guardando scalers: {e}", exc_info=True)
            return False
    
    def verificar_archivo_modelo(
        self,
        model_name: str,
        archivos_faltantes: Optional[List[str]] = None
    ) -> bool:
        """
        Verifica si existe un archivo de modelo.
        
        Args:
            model_name: Nombre del archivo del modelo (ej: "hybrid.pt", "alto.pt")
            archivos_faltantes: Lista opcional para agregar nombres de archivos faltantes
            
        Returns:
            True si el archivo existe, False en caso contrario
        """
        model_path = self.artifacts_dir / model_name
        exists = model_path.exists()
        
        if not exists:
            if archivos_faltantes is not None:
                archivos_faltantes.append(model_name)
            logger.warning(f"Archivo de modelo no encontrado: {model_name}")
        
        return exists
    
    def verificar_archivos_scalers(
        self,
        archivos_faltantes: Optional[List[str]] = None
    ) -> bool:
        """
        Verifica si todos los archivos de scalers existen.
        
        Args:
            archivos_faltantes: Lista opcional para agregar nombres de archivos faltantes
            
        Returns:
            True si todos los scalers existen, False en caso contrario
        """
        all_exist = True
        
        for target in TARGETS:
            scaler_path = self.artifacts_dir / f"{target}_scaler.pkl"
            if not scaler_path.exists():
                all_exist = False
                if archivos_faltantes is not None:
                    archivos_faltantes.append(f"{target}_scaler.pkl")
                logger.warning(f"Archivo de scaler no encontrado: {target}_scaler.pkl")
        
        return all_exist
    
    def registrar_resumen_artefactos_hibridos(self) -> None:
        """Registra resumen de artefactos de modelo híbrido."""
        archivos_faltantes: List[str] = []
        
        self.verificar_archivo_modelo(self.MODELO_HIBRIDO, archivos_faltantes)
        self.verificar_archivos_scalers(archivos_faltantes)
        
        if archivos_faltantes:
            logger.warning(
                f"Resumen de artefactos híbridos: {len(archivos_faltantes)} archivos faltantes: {archivos_faltantes}"
            )
        else:
            logger.info("Resumen de artefactos híbridos: Todos los archivos presentes")
            logger.info(f"  - Modelo: {self.MODELO_HIBRIDO}")
            logger.info(f"  - Scalers: {len(TARGETS)} archivos")
    
    def registrar_resumen_artefactos_individuales(self) -> None:
        """Registra resumen de artefactos de modelos individuales."""
        archivos_faltantes: List[str] = []
        
        for target in TARGETS:
            self.verificar_archivo_modelo(f"{target}.pt", archivos_faltantes)
        
        self.verificar_archivos_scalers(archivos_faltantes)
        
        if archivos_faltantes:
            logger.warning(
                f"Resumen de artefactos individuales: {len(archivos_faltantes)} archivos faltantes: {archivos_faltantes}"
            )
        else:
            logger.info("Resumen de artefactos individuales: Todos los archivos presentes")
            logger.info(f"  - Modelos: {len(TARGETS)} archivos ({', '.join(TARGETS)})")
            logger.info(f"  - Scalers: {len(TARGETS)} archivos")
    
    def verificar_artefactos_guardados(
        self,
        is_hybrid: bool = False,
        is_multi_head: bool = False
    ) -> bool:
        """
        Verifica que todos los artefactos requeridos estén guardados.
        
        Args:
            is_hybrid: Si se entrenó modelo híbrido
            is_multi_head: Si se entrenó modelo multi-head
            
        Returns:
            True si todos los artefactos están presentes, False en caso contrario
        """
        archivos_faltantes: List[str] = []
        
        if is_hybrid:
            self.verificar_archivo_modelo(self.MODELO_HIBRIDO, archivos_faltantes)
        elif is_multi_head:
            self.verificar_archivo_modelo(self.MODELO_MULTIHEAD, archivos_faltantes)
        else:
            # Modelos individuales
            for target in TARGETS:
                self.verificar_archivo_modelo(f"{target}.pt", archivos_faltantes)
        
        # Siempre verificar scalers
        self.verificar_archivos_scalers(archivos_faltantes)
        
        if archivos_faltantes:
            logger.error(
                f"Verificación de artefactos falló: {len(archivos_faltantes)} archivos faltantes: {archivos_faltantes}"
            )
            return False
        
        logger.info("Verificación de artefactos exitosa: Todos los archivos requeridos presentes")
        return True
    
    def guardar_checkpoint_modelo(
        self,
        model: torch.nn.Module,
        model_name: str,
        model_info: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Guarda checkpoint de modelo en disco.
        
        Args:
            model: Modelo PyTorch a guardar
            model_name: Nombre del archivo del modelo (ej: "hybrid.pt")
            model_info: Información adicional del modelo (opcional)
            
        Returns:
            True si se guardó exitosamente, False en caso contrario
        """
        try:
            model_path = self.artifacts_dir / model_name
            
            save_dict = {
                'model_state_dict': model.state_dict(),
                'model_info': model_info or {}
            }
            
            torch.save(save_dict, model_path)
            
            if model_path.exists() and model_path.stat().st_size > 0:
                logger.info(f"Checkpoint de modelo guardado: {model_path}")
                return True
            else:
                logger.error(f"Archivo de checkpoint de modelo no creado o vacío: {model_path}")
                return False
                
        except Exception as e:
            logger.error(f"Error guardando checkpoint de modelo: {e}", exc_info=True)
            return False
    
    def obtener_directorio_artefactos(self) -> Path:
        """
        Obtiene el directorio de artefactos.
        
        Returns:
            Ruta al directorio de artefactos
        """
        return self.artifacts_dir
    
    # Métodos de compatibilidad hacia atrás
    def save_scalers(self, scalers: CacaoScalers) -> bool:
        """Alias de compatibilidad hacia atrás para guardar_scalers."""
        return self.guardar_scalers(scalers)
    
    def check_model_file(
        self,
        model_name: str,
        missing_files: Optional[List[str]] = None
    ) -> bool:
        """Alias de compatibilidad hacia atrás para verificar_archivo_modelo."""
        return self.verificar_archivo_modelo(model_name, missing_files)
    
    def check_scaler_files(
        self,
        missing_files: Optional[List[str]] = None
    ) -> bool:
        """Alias de compatibilidad hacia atrás para verificar_archivos_scalers."""
        return self.verificar_archivos_scalers(missing_files)
    
    def log_hybrid_artifacts_summary(self) -> None:
        """Alias de compatibilidad hacia atrás para registrar_resumen_artefactos_hibridos."""
        return self.registrar_resumen_artefactos_hibridos()
    
    def log_individual_artifacts_summary(self) -> None:
        """Alias de compatibilidad hacia atrás para registrar_resumen_artefactos_individuales."""
        return self.registrar_resumen_artefactos_individuales()
    
    def verify_artifacts_saved(
        self,
        is_hybrid: bool = False,
        is_multi_head: bool = False
    ) -> bool:
        """Alias de compatibilidad hacia atrás para verificar_artefactos_guardados."""
        return self.verificar_artefactos_guardados(is_hybrid, is_multi_head)
    
    def save_model_checkpoint(
        self,
        model: torch.nn.Module,
        model_name: str,
        model_info: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Alias de compatibilidad hacia atrás para guardar_checkpoint_modelo."""
        return self.guardar_checkpoint_modelo(model, model_name, model_info)
    
    def get_artifacts_dir(self) -> Path:
        """Alias de compatibilidad hacia atrás para obtener_directorio_artefactos."""
        return self.obtener_directorio_artefactos()

