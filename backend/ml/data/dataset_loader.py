"""
Cargador y validador del dataset de cacao para CacaoScan.

CORREGIDO:
- Se eliminó la función '_resolve_media_path' que causaba rutas duplicadas 'media/media'.
- Se usan 'settings.MEDIA_ROOT' y 'Path.joinpath' para construir rutas absolutas
  de forma robusta dentro de 'validate_images_exist' y 'get_valid_records'.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union
import logging
import glob
import os
import sys

# Configurar Django
project_root = Path(__file__).resolve().parents[2] # Sube 2 niveles (data/ml/backend)
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')
import django
try:
    django.setup()
    from django.conf import settings
    MEDIA_ROOT = Path(settings.MEDIA_ROOT)
except Exception as e:
    print(f"Warning: Django setup failed (normal if not in Django context). Error: {e}")
    MEDIA_ROOT = project_root / "media"

from ml.utils.paths import (
    get_raw_images_dir,
    get_missing_ids_log_path,
    ensure_dir_exists,
    get_datasets_dir,
    get_crops_dir
)
from ml.utils.io import write_log, get_file_timestamp

logger = logging.getLogger("cacaoscan.ml.data")


class CacaoDatasetLoader:
    """
    Cargador y validador del dataset de cacao para CacaoScan.
    """
    
    def __init__(self, csv_path: Optional[str] = None):
        """
        Inicializa el cargador de dataset.
        
        Args:
            csv_path: Ruta específica al CSV (opcional). Si no se proporciona,
                     se detecta automáticamente en media/datasets/
        """
        self.raw_images_dir = get_raw_images_dir()
        self.crops_dir = get_crops_dir()
        self.missing_log_path = get_missing_ids_log_path()
        
        # Detectar archivo CSV automáticamente si no se proporciona
        if csv_path is None:
            self.csv_path = self._detect_csv_file()
        else:
            self.csv_path = Path(csv_path)
        
        if not self.csv_path or not self.csv_path.exists():
            raise FileNotFoundError(f"Dataset CSV no encontrado. Buscado en: {csv_path or get_datasets_dir()}")
        
        # Asegurar que los directorios existen
        ensure_dir_exists(self.raw_images_dir)
        ensure_dir_exists(self.missing_log_path.parent)
        
        logger.info(f"Dataset loader inicializado con CSV: {self.csv_path}")
    
    def _detect_csv_file(self) -> Optional[Path]:
        """
        Detecta automáticamente archivos CSV en media/datasets/.
        """
        datasets_dir = get_datasets_dir()
        
        if not datasets_dir.exists():
            logger.warning(f"Directorio de datasets no encontrado: {datasets_dir}")
            return None
        
        # Buscar archivos CSV
        csv_files = list(datasets_dir.glob("*.csv"))
        
        if not csv_files:
            logger.warning(f"No se encontraron archivos CSV en {datasets_dir}")
            return None
        
        # Priorizar
        preferred_names = ["dataset_cacao.clean.csv", "dataset_cacao.csv", "dataset_sin_comillas.csv", "dataset.csv"]
        
        for preferred_name in preferred_names:
            for csv_file in csv_files:
                if csv_file.name == preferred_name:
                    logger.info(f"Archivo CSV preferido detectado: {csv_file}")
                    return csv_file
        
        # Si no hay preferido, usar el primero
        csv_file = csv_files[0]
        logger.warning(f"Múltiples archivos CSV encontrados. Usando: {csv_file}")
        return csv_file
    
    def load_dataset(self) -> pd.DataFrame:
        """
        Carga el dataset CSV y valida los tipos de datos.
        """
        logger.info(f"Cargando dataset desde {self.csv_path}")
        
        try:
            # Cargar CSV con separador coma
            df = pd.read_csv(self.csv_path, sep=',')
            
            logger.info(f"CSV cargado: {len(df)} filas, {len(df.columns)} columnas")
            logger.info(f"Columnas encontradas: {list(df.columns)}")
            
        except Exception as e:
            raise ValueError(f"Error leyendo CSV: {e}")
        
        # Validar que existen todas las columnas requeridas (sin importar el orden)
        required_columns = {'ID': 'id', 'ALTO': 'alto', 'ANCHO': 'ancho', 'GROSOR': 'grosor', 'PESO': 'peso'}
        missing_columns = [col for col in required_columns.keys() if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Columnas faltantes en el dataset: {missing_columns}")
        
        logger.info(f"[OK] Columnas validadas: {list(df.columns)}")
        
        # Convertir tipos de datos y manejar valores nulos
        initial_count = len(df)
        
        df['ID'] = pd.to_numeric(df['ID'], errors='coerce').astype('Int64')
        df['ALTO'] = pd.to_numeric(df['ALTO'], errors='coerce').astype(np.float32)
        df['ANCHO'] = pd.to_numeric(df['ANCHO'], errors='coerce').astype(np.float32)
        df['GROSOR'] = pd.to_numeric(df['GROSOR'], errors='coerce').astype(np.float32)
        df['PESO'] = pd.to_numeric(df['PESO'], errors='coerce').astype(np.float32)
        
        df = df.dropna()
        final_count = len(df)
        
        if initial_count != final_count:
            logger.warning(f"Eliminadas {initial_count - final_count} filas con valores nulos")
        
        # Normalizar nombres de columnas a minúscula para uso interno
        df = df.rename(columns={
            'ID': 'id',
            'ALTO': 'alto',
            'ANCHO': 'ancho', 
            'GROSOR': 'grosor',
            'PESO': 'peso'
        })
        
        # --- ESTA ES LA PARTE CORREGIDA ---
        # Generar rutas RELATIVAS a MEDIA_ROOT
        df['image_path'] = df['id'].apply(
            lambda x: f"cacao_images/raw/{x}.bmp"
        )
        df['crop_image_path'] = df['id'].apply(
            lambda x: f"cacao_images/crops/{x}.png"
        )
        
        # Verificar duplicados
        duplicates = df['id'].duplicated().sum()
        if duplicates > 0:
            logger.warning(f"Encontrados {duplicates} IDs duplicados. Eliminando duplicados...")
            df = df.drop_duplicates(subset=['id'], keep='first')
        
        logger.info(f"[OK] Dataset cargado exitosamente: {len(df)} registros válidos")
        logger.info(f"Columnas finales: {list(df.columns)}")
        
        return df
    
    def validate_images_exist(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[int]]:
        """
        Valida que las imágenes correspondientes a los IDs existan.
        """
        logger.info("Validando existencia de imágenes...")
        
        missing_ids = []
        valid_indices = []
        
        for index, row in df.iterrows():
            image_id = row['id']
            # --- CORRECCIÓN ---
            # Construir la ruta absoluta correctamente
            image_path = MEDIA_ROOT / row['image_path']
            
            if image_path.exists():
                valid_indices.append(index)
            else:
                missing_ids.append(int(image_id))
                logger.debug(f"[ERROR] Imagen faltante para ID {image_id}: {image_path}")
        
        if missing_ids:
            log_message = f"IDs con imágenes faltantes: {sorted(missing_ids)}"
            write_log(self.missing_log_path, log_message)
            logger.warning(f"[INFO] Guardado log de {len(missing_ids)} IDs faltantes en {self.missing_log_path}")
        
        valid_df = df.loc[valid_indices].copy()
        
        logger.info(f"[OK] Validación completada: {len(valid_df)} imágenes válidas / [ERROR] {len(missing_ids)} faltantes")
        
        return valid_df, missing_ids
    
    def get_valid_records(self) -> List[Dict]:
        """
        Obtiene la lista de registros válidos con rutas de imágenes.
        """
        df = self.load_dataset()
        valid_df, _ = self.validate_images_exist(df)
        
        valid_records = []
        
        for _, row in valid_df.iterrows():
            # --- CORRECCIÓN ---
            # Construir rutas absolutas correctamente
            raw_path = MEDIA_ROOT / row['image_path']
            crop_path = MEDIA_ROOT / row['crop_image_path']
            
            record = {
                'id': int(row['id']),
                'alto': float(row['alto']),
                'ancho': float(row['ancho']),
                'grosor': float(row['grosor']),
                'peso': float(row['peso']),
                'image_path': str(raw_path),       # Ruta absoluta
                'raw_image_path': str(raw_path),  # Ruta absoluta
                'crop_image_path': str(crop_path), # Ruta absoluta
                'mask_image_path': None,
                'timestamp': get_file_timestamp(raw_path) if raw_path.exists() else None
            }
            valid_records.append(record)
        
        logger.info(f"[OK] Generados {len(valid_records)} registros válidos")
        return valid_records
    
    def get_dataset_stats(self) -> Dict:
        """
        Obtiene estadísticas del dataset.
        """
        try:
            df = self.load_dataset()
            valid_df, missing_ids = self.validate_images_exist(df)
            
            stats = {
                'total_records': len(df),
                'valid_records': len(valid_df),
                'missing_images': len(missing_ids),
                'missing_ids': sorted(missing_ids),
                'dimensions_stats': {}
            }
            
            if len(valid_df) > 0:
                for target in ['alto', 'ancho', 'grosor', 'peso']:
                    stats['dimensions_stats'][target] = {
                        'min': float(valid_df[target].min()),
                        'max': float(valid_df[target].max()),
                        'mean': float(valid_df[target].mean()),
                        'std': float(valid_df[target].std()),
                        'median': float(valid_df[target].median()),
                        'count': int(valid_df[target].count())
                    }
            else:
                logger.warning("No hay datos válidos para calcular estadísticas")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error al obtener estadísticas del dataset: {e}")
            return {}


    def filter_by_target(self, df: pd.DataFrame, target: str) -> pd.DataFrame:
        """
        Filtra el dataset por un target específico.
        """
        if target not in ['alto', 'ancho', 'grosor', 'peso']:
            raise ValueError(f"Target inválido: {target}. Debe ser uno de: alto, ancho, grosor, peso")
        
        filtered_df = df[df[target].notna()]
        logger.info(f"Dataset filtrado por {target}: {len(filtered_df)} registros")
        return filtered_df
    
    def get_target_data(self, target: str) -> Tuple[np.ndarray, List[Dict]]:
        """
        Obtiene datos para un target específico con registros válidos.
        """
        df = self.load_dataset()
        valid_df, _ = self.validate_images_exist(df)
        filtered_df = self.filter_by_target(valid_df, target)
        
        records = []
        target_values = []
        
        for _, row in filtered_df.iterrows():
            # Construir ruta absoluta
            image_path = MEDIA_ROOT / row['image_path']
            records.append({
                'id': int(row['id']),
                'image_path': str(image_path),
                target: float(row[target])
            })
            target_values.append(float(row[target]))
        
        return np.array(target_values, dtype=np.float32), records


def load_cacao_dataset(csv_path: Optional[str] = None) -> Tuple[pd.DataFrame, List[int]]:
    """
    Función de conveniencia para cargar el dataset y validar imágenes.
    """
    loader = CacaoDatasetLoader(csv_path)
    df = loader.load_dataset()
    return loader.validate_images_exist(df)


def get_valid_cacao_records(csv_path: Optional[str] = None) -> List[Dict]:
    """
    Función de conveniencia para obtener registros válidos.
    """
    loader = CacaoDatasetLoader(csv_path)
    return loader.get_valid_records()


def get_target_data(target: str, csv_path: Optional[str] = None) -> Tuple[np.ndarray, List[Dict]]:
    """
    Función de conveniencia para obtener datos de un target específico.
    """
    loader = CacaoDatasetLoader(csv_path)
    return loader.get_target_data(target)