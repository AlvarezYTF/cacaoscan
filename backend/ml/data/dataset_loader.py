"""
Cargador y validador del dataset de cacao para CacaoScan.

Formato esperado del CSV:
ID,ALTO,ANCHO,GROSOR,PESO
1,22.8,10.2,16.3,1.72
2,22.0,10.9,13.3,1.45
...

- Separador: coma (,)
- Encabezados en mayúscula: ID, ALTO, ANCHO, GROSOR, PESO
- Cada fila representa un grano de cacao identificado por su ID
- Imagen correspondiente: backend/media/cacao_images/raw/{ID}.bmp
- Algunas imágenes pueden faltar; se detectan y excluyen con log en missing_ids.log
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union
import logging
import glob
import os

from ..utils.paths import (
    get_dataset_csv_path,
    get_raw_images_dir,
    get_missing_ids_log_path,
    ensure_dir_exists
)
from ..utils.io import write_log, get_file_timestamp


logger = logging.getLogger("cacaoscan.ml.data")


class CacaoDatasetLoader:
    """
    Cargador y validador del dataset de cacao para CacaoScan.
    
    Características:
    - Lee CSV con separador coma (,)
    - Convierte valores a float32
    - Normaliza nombres de columnas a minúscula
    - Genera columna image_path automáticamente
    - Verifica existencia de imágenes
    - Registra IDs faltantes en log
    - Detecta automáticamente archivos CSV en media/datasets/
    """
    
    def __init__(self, csv_path: Optional[str] = None):
        """
        Inicializa el cargador de dataset.
        
        Args:
            csv_path: Ruta específica al CSV (opcional). Si no se proporciona,
                     se detecta automáticamente en media/datasets/
        """
        self.raw_images_dir = get_raw_images_dir()
        self.missing_log_path = get_missing_ids_log_path()
        
        # Detectar archivo CSV automáticamente si no se proporciona
        if csv_path is None:
            self.csv_path = self._detect_csv_file()
        else:
            self.csv_path = Path(csv_path)
        
        if not self.csv_path or not self.csv_path.exists():
            raise FileNotFoundError(f"Dataset CSV no encontrado. Buscado en: {csv_path or 'media/datasets/'}")
        
        # Asegurar que los directorios existen
        ensure_dir_exists(self.raw_images_dir)
        ensure_dir_exists(self.missing_log_path.parent)
        
        logger.info(f"Dataset loader inicializado con CSV: {self.csv_path}")
    
    def _detect_csv_file(self) -> Optional[Path]:
        """
        Detecta automáticamente archivos CSV en media/datasets/.
        
        Returns:
            Path al archivo CSV encontrado o None si no hay ninguno
        """
        from ..utils.paths import get_datasets_dir
        datasets_dir = get_datasets_dir()
        
        if not datasets_dir.exists():
            logger.warning(f"Directorio de datasets no encontrado: {datasets_dir}")
            return None
        
        # Buscar archivos CSV
        csv_files = list(datasets_dir.glob("*.csv"))
        
        if not csv_files:
            logger.warning(f"No se encontraron archivos CSV en {datasets_dir}")
            return None
        
        if len(csv_files) == 1:
            csv_file = csv_files[0]
            logger.info(f"Archivo CSV detectado automáticamente: {csv_file}")
            return csv_file
        
        # Múltiples archivos CSV - priorizar dataset_sin_comillas.csv
        preferred_names = ["dataset_sin_comillas.csv", "dataset.csv"]
        
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
        
        Returns:
            DataFrame con el dataset cargado y validado con columnas normalizadas
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
        
        logger.info(f"✅ Columnas validadas: {list(df.columns)}")
        
        # Convertir tipos de datos y manejar valores nulos
        initial_count = len(df)
        
        # ID como entero
        df['ID'] = pd.to_numeric(df['ID'], errors='coerce').astype('Int64')
        
        # Dimensiones y peso como float32 (leer de cualquier orden de columna)
        df['ALTO'] = pd.to_numeric(df['ALTO'], errors='coerce').astype(np.float32)
        df['ANCHO'] = pd.to_numeric(df['ANCHO'], errors='coerce').astype(np.float32)
        df['GROSOR'] = pd.to_numeric(df['GROSOR'], errors='coerce').astype(np.float32)
        df['PESO'] = pd.to_numeric(df['PESO'], errors='coerce').astype(np.float32)
        
        # Eliminar filas con valores nulos
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
        
        # Generar columna image_path automáticamente
        df['image_path'] = df['id'].apply(
            lambda x: f"media/cacao_images/raw/{x}.bmp"
        )
        
        # Generar columna crop_image_path automáticamente
        df['crop_image_path'] = df['id'].apply(
            lambda x: f"media/cacao_images/crops/{x}.png"
        )
        
        # Verificar duplicados
        duplicates = df['id'].duplicated().sum()
        if duplicates > 0:
            logger.warning(f"Encontrados {duplicates} IDs duplicados. Eliminando duplicados...")
            df = df.drop_duplicates(subset=['id'], keep='first')
            logger.info(f"Dataset después de eliminar duplicados: {len(df)} registros")
        
        logger.info(f"✅ Dataset cargado exitosamente: {len(df)} registros válidos")
        logger.info(f"Columnas finales: {list(df.columns)}")
        
        return df
    
    def validate_images_exist(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[int]]:
        """
        Valida que las imágenes correspondientes a los IDs existan.
        
        Args:
            df: DataFrame con los datos del dataset (columnas normalizadas)
            
        Returns:
            Tuple con (DataFrame filtrado, Lista de IDs faltantes)
        """
        logger.info("Validando existencia de imágenes...")
        
        missing_ids = []
        valid_records = []
        
        for _, row in df.iterrows():
            image_id = row['id']  # Usar columna normalizada
            image_path = Path(row['image_path'])  # Usar path generado automáticamente
            
            if image_path.exists():
                valid_records.append(row)
            else:
                missing_ids.append(int(image_id))
                logger.debug(f"❌ Imagen faltante para ID {image_id}: {image_path}")
        
        # Guardar log de IDs faltantes
        if missing_ids:
            log_message = f"IDs con imágenes faltantes: {sorted(missing_ids)}"
            write_log(self.missing_log_path, log_message)
            logger.warning(f"📝 Guardado log de {len(missing_ids)} IDs faltantes en {self.missing_log_path}")
        
        valid_df = pd.DataFrame(valid_records) if valid_records else pd.DataFrame()
        
        logger.info(f"✅ Validación completada: {len(valid_df)} imágenes válidas / ❌ {len(missing_ids)} faltantes")
        
        return valid_df, missing_ids
    
    def get_valid_records(self) -> List[Dict]:
        """
        Obtiene la lista de registros válidos con rutas de imágenes.
        
        Returns:
            Lista de diccionarios con información de cada registro válido
        """
        # Cargar y validar dataset
        df = self.load_dataset()
        valid_df, missing_ids = self.validate_images_exist(df)
        
        # Crear lista de registros válidos
        valid_records = []
        
        for _, row in valid_df.iterrows():
            image_id = row['id']
            raw_path = Path(row['image_path'])
            
            # Generar ruta del crop
            crop_path = Path(row['crop_image_path'])
            
            record = {
                'id': int(image_id),
                'alto': float(row['alto']),
                'ancho': float(row['ancho']),
                'grosor': float(row['grosor']),
                'peso': float(row['peso']),
                'image_path': str(raw_path),
                'raw_image_path': str(raw_path),  # Alias para compatibilidad
                'crop_image_path': crop_path,  # Ruta del crop
                'mask_image_path': None,  # Se establecerá después del procesamiento
                'timestamp': get_file_timestamp(raw_path) if raw_path.exists() else None
            }
            valid_records.append(record)
        
        logger.info(f"✅ Generados {len(valid_records)} registros válidos")
        return valid_records
    
    def get_dataset_stats(self) -> Dict:
        """
        Obtiene estadísticas del dataset.
        
        Returns:
            Diccionario con estadísticas del dataset
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
            
            # Calcular estadísticas solo si hay datos válidos
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
        
        Args:
            df: DataFrame con datos del dataset
            target: Target a filtrar ('alto', 'ancho', 'grosor', 'peso')
            
        Returns:
            DataFrame filtrado
        """
        if target not in ['alto', 'ancho', 'grosor', 'peso']:
            raise ValueError(f"Target inválido: {target}. Debe ser uno de: alto, ancho, grosor, peso")
        
        # Filtrar filas donde el target no sea nulo
        filtered_df = df[df[target].notna()]
        
        logger.info(f"Dataset filtrado por {target}: {len(filtered_df)} registros")
        return filtered_df
    
    def get_target_data(self, target: str) -> Tuple[np.ndarray, List[Dict]]:
        """
        Obtiene datos para un target específico con registros válidos.
        
        Args:
            target: Target a obtener ('alto', 'ancho', 'grosor', 'peso')
            
        Returns:
            Tuple con (valores del target como array, registros válidos)
        """
        df = self.load_dataset()
        valid_df, missing_ids = self.validate_images_exist(df)
        filtered_df = self.filter_by_target(valid_df, target)
        
        # Obtener registros válidos
        records = []
        target_values = []
        
        for _, row in filtered_df.iterrows():
            records.append({
                'id': int(row['id']),
                'image_path': row['image_path'],
                target: float(row[target])
            })
            target_values.append(float(row[target]))
        
        return np.array(target_values, dtype=np.float32), records


def load_cacao_dataset(csv_path: Optional[str] = None) -> Tuple[pd.DataFrame, List[int]]:
    """
    Función de conveniencia para cargar el dataset y validar imágenes.
    
    Args:
        csv_path: Ruta específica al CSV (opcional)
    
    Returns:
        Tuple con (DataFrame válido, Lista de IDs faltantes)
    """
    loader = CacaoDatasetLoader(csv_path)
    df = loader.load_dataset()
    return loader.validate_images_exist(df)


def get_valid_cacao_records(csv_path: Optional[str] = None) -> List[Dict]:
    """
    Función de conveniencia para obtener registros válidos.
    
    Args:
        csv_path: Ruta específica al CSV (opcional)
    
    Returns:
        Lista de registros válidos con información completa
    """
    loader = CacaoDatasetLoader(csv_path)
    return loader.get_valid_records()


def get_target_data(target: str, csv_path: Optional[str] = None) -> Tuple[np.ndarray, List[Dict]]:
    """
    Función de conveniencia para obtener datos de un target específico.
    
    Args:
        target: Target a obtener ('alto', 'ancho', 'grosor', 'peso')
        csv_path: Ruta específica al CSV (opcional)
    
    Returns:
        Tuple con (valores del target como array, registros válidos)
    """
    loader = CacaoDatasetLoader(csv_path)
    return loader.get_target_data(target)
