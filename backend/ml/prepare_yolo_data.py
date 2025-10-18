"""
Script de preparación de datos para entrenamiento YOLOv8.

Este script:
1. Lee el dataset.csv con las dimensiones reales
2. Genera anotaciones YOLOv8 para las imágenes
3. Crea la estructura de directorios necesaria
4. Prepara los datos para entrenamiento
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
import json
import shutil
from typing import List, Dict, Tuple
import cv2
from PIL import Image
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YOLODataPreparator:
    """
    Preparador de datos para entrenamiento YOLOv8.
    
    Convierte el dataset de cacao en formato YOLOv8.
    """
    
    def __init__(self, 
                 dataset_csv_path: str,
                 images_dir: str,
                 output_dir: str = "yolo_dataset"):
        """
        Inicializa el preparador de datos.
        
        Args:
            dataset_csv_path: Ruta al archivo dataset.csv
            images_dir: Directorio con las imágenes
            output_dir: Directorio de salida para datos YOLOv8
        """
        self.dataset_csv_path = Path(dataset_csv_path)
        self.images_dir = Path(images_dir)
        self.output_dir = Path(output_dir)
        
        # Crear directorios de salida
        self.train_dir = self.output_dir / 'train'
        self.val_dir = self.output_dir / 'val'
        self.test_dir = self.output_dir / 'test'
        
        for dir_path in [self.train_dir, self.val_dir, self.test_dir]:
            (dir_path / 'images').mkdir(parents=True, exist_ok=True)
            (dir_path / 'labels').mkdir(parents=True, exist_ok=True)
        
        # Cargar dataset
        self.dataset_df = None
        self.load_dataset()
        
        # Configuración de clases YOLOv8
        self.classes = ['cacao_grain']
        self.class_to_id = {cls: i for i, cls in enumerate(self.classes)}
        
        logger.info(f"YOLODataPreparator inicializado")
        logger.info(f"Dataset: {self.dataset_csv_path}")
        logger.info(f"Imágenes: {self.images_dir}")
        logger.info(f"Salida: {self.output_dir}")
    
    def load_dataset(self):
        """Carga el dataset CSV."""
        try:
            self.dataset_df = pd.read_csv(self.dataset_csv_path)
            logger.info(f"Dataset cargado: {len(self.dataset_df)} registros")
            logger.info(f"Columnas: {list(self.dataset_df.columns)}")
        except Exception as e:
            logger.error(f"Error cargando dataset: {e}")
            raise
    
    def generate_annotations(self, 
                           split_ratios: Tuple[float, float, float] = (0.7, 0.2, 0.1),
                           auto_detect_bbox: bool = True) -> Dict[str, int]:
        """
        Genera anotaciones YOLOv8 para todas las imágenes.
        
        Args:
            split_ratios: Proporciones para train/val/test
            auto_detect_bbox: Si detectar automáticamente el bbox del grano
            
        Returns:
            Dict con conteos de cada split
        """
        logger.info("Iniciando generación de anotaciones YOLOv8")
        
        # Validar proporciones
        if abs(sum(split_ratios) - 1.0) > 0.001:
            raise ValueError("Las proporciones de split deben sumar 1.0")
        
        # Obtener lista de imágenes disponibles
        available_images = self._get_available_images()
        logger.info(f"Imágenes disponibles: {len(available_images)}")
        
        # Dividir en train/val/test
        train_count = int(len(available_images) * split_ratios[0])
        val_count = int(len(available_images) * split_ratios[1])
        
        train_images = available_images[:train_count]
        val_images = available_images[train_count:train_count + val_count]
        test_images = available_images[train_count + val_count:]
        
        logger.info(f"Split: Train={len(train_images)}, Val={len(val_images)}, Test={len(test_images)}")
        
        # Procesar cada split
        splits = {
            'train': train_images,
            'val': val_images,
            'test': test_images
        }
        
        counts = {}
        
        for split_name, image_list in splits.items():
            count = self._process_split(split_name, image_list, auto_detect_bbox)
            counts[split_name] = count
        
        # Crear archivo de configuración
        self._create_dataset_config()
        
        logger.info("Generación de anotaciones completada")
        return counts
    
    def _get_available_images(self) -> List[str]:
        """Obtiene lista de imágenes disponibles."""
        available_images = []
        
        for _, row in self.dataset_df.iterrows():
            image_id = str(row['ID'])
            image_path = self.images_dir / f"{image_id}.bmp"
            
            if image_path.exists():
                available_images.append(image_id)
            else:
                logger.warning(f"Imagen no encontrada: {image_path}")
        
        return sorted(available_images)
    
    def _process_split(self, split_name: str, image_list: List[str], auto_detect_bbox: bool) -> int:
        """
        Procesa un split específico.
        
        Args:
            split_name: Nombre del split (train/val/test)
            image_list: Lista de IDs de imágenes
            auto_detect_bbox: Si detectar automáticamente el bbox
            
        Returns:
            int: Número de imágenes procesadas
        """
        split_dir = getattr(self, f"{split_name}_dir")
        processed_count = 0
        
        logger.info(f"Procesando split {split_name}: {len(image_list)} imágenes")
        
        for image_id in image_list:
            try:
                # Copiar imagen
                source_image = self.images_dir / f"{image_id}.bmp"
                target_image = split_dir / 'images' / f"{image_id}.jpg"
                
                # Convertir BMP a JPG
                self._convert_image(source_image, target_image)
                
                # Generar anotación
                annotation_file = split_dir / 'labels' / f"{image_id}.txt"
                self._generate_annotation(image_id, annotation_file, auto_detect_bbox)
                
                processed_count += 1
                
                if processed_count % 50 == 0:
                    logger.info(f"Procesadas {processed_count}/{len(image_list)} imágenes en {split_name}")
                
            except Exception as e:
                logger.error(f"Error procesando imagen {image_id}: {e}")
                continue
        
        logger.info(f"Split {split_name} completado: {processed_count} imágenes")
        return processed_count
    
    def _convert_image(self, source_path: Path, target_path: Path):
        """Convierte imagen BMP a JPG."""
        try:
            # Cargar imagen BMP
            image = cv2.imread(str(source_path))
            if image is None:
                raise ValueError(f"No se pudo cargar la imagen: {source_path}")
            
            # Convertir a RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Guardar como JPG
            pil_image = Image.fromarray(image_rgb)
            pil_image.save(target_path, 'JPEG', quality=95)
            
        except Exception as e:
            logger.error(f"Error convirtiendo imagen {source_path}: {e}")
            raise
    
    def _generate_annotation(self, image_id: str, annotation_file: Path, auto_detect_bbox: bool):
        """
        Genera archivo de anotación YOLOv8.
        
        Args:
            image_id: ID de la imagen
            annotation_file: Archivo de anotación de salida
            auto_detect_bbox: Si detectar automáticamente el bbox
        """
        try:
            # Obtener datos del grano
            grain_data = self.dataset_df[self.dataset_df['ID'] == int(image_id)].iloc[0]
            
            # Obtener dimensiones de la imagen
            image_path = self.images_dir / f"{image_id}.bmp"
            image = cv2.imread(str(image_path))
            img_height, img_width = image.shape[:2]
            
            if auto_detect_bbox:
                # Detectar automáticamente el grano en la imagen
                bbox = self._detect_grain_bbox(image)
            else:
                # Usar bbox centrado basado en las dimensiones reales
                bbox = self._estimate_bbox_from_dimensions(
                    grain_data['ANCHO'], grain_data['ALTO'], 
                    img_width, img_height
                )
            
            # Convertir a formato YOLOv8 (normalizado)
            yolo_bbox = self._convert_to_yolo_format(bbox, img_width, img_height)
            
            # Escribir archivo de anotación
            with open(annotation_file, 'w') as f:
                # Formato: class_id center_x center_y width height
                f.write(f"0 {yolo_bbox[0]:.6f} {yolo_bbox[1]:.6f} {yolo_bbox[2]:.6f} {yolo_bbox[3]:.6f}\n")
            
        except Exception as e:
            logger.error(f"Error generando anotación para {image_id}: {e}")
            raise
    
    def _detect_grain_bbox(self, image: np.ndarray) -> Tuple[int, int, int, int]:
        """
        Detecta automáticamente el bbox del grano usando procesamiento de imagen.
        
        Args:
            image: Imagen de entrada
            
        Returns:
            Tuple: (x1, y1, x2, y2) en píxeles
        """
        try:
            # Convertir a escala de grises
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Aplicar filtro gaussiano
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Detectar bordes
            edges = cv2.Canny(blurred, 50, 150)
            
            # Encontrar contornos
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if len(contours) == 0:
                # Fallback: usar bbox centrado
                h, w = image.shape[:2]
                margin = min(w, h) // 4
                return (margin, margin, w - margin, h - margin)
            
            # Encontrar el contorno más grande
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Obtener bbox del contorno
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Agregar margen
            margin = 10
            x1 = max(0, x - margin)
            y1 = max(0, y - margin)
            x2 = min(image.shape[1], x + w + margin)
            y2 = min(image.shape[0], y + h + margin)
            
            return (x1, y1, x2, y2)
            
        except Exception as e:
            logger.error(f"Error en detección automática: {e}")
            # Fallback: bbox centrado
            h, w = image.shape[:2]
            margin = min(w, h) // 4
            return (margin, margin, w - margin, h - margin)
    
    def _estimate_bbox_from_dimensions(self, 
                                     real_width_mm: float, 
                                     real_height_mm: float,
                                     img_width: int, 
                                     img_height: int) -> Tuple[int, int, int, int]:
        """
        Estima el bbox basado en las dimensiones reales del grano.
        
        Args:
            real_width_mm: Ancho real en mm
            real_height_mm: Alto real en mm
            img_width: Ancho de imagen en píxeles
            img_height: Alto de imagen en píxeles
            
        Returns:
            Tuple: (x1, y1, x2, y2) en píxeles
        """
        # Asumir que el grano ocupa aproximadamente el 60% del área de la imagen
        # y está centrado
        
        # Calcular tamaño estimado en píxeles
        # Usar la dimensión más grande para escalar
        max_real_dimension = max(real_width_mm, real_height_mm)
        max_img_dimension = max(img_width, img_height)
        
        # Factor de escala aproximado (ajustar según calibración real)
        scale_factor = max_img_dimension / (max_real_dimension * 10)  # Asumiendo ~10 píxeles/mm
        
        estimated_width = int(real_width_mm * scale_factor)
        estimated_height = int(real_height_mm * scale_factor)
        
        # Centrar en la imagen
        center_x = img_width // 2
        center_y = img_height // 2
        
        x1 = max(0, center_x - estimated_width // 2)
        y1 = max(0, center_y - estimated_height // 2)
        x2 = min(img_width, center_x + estimated_width // 2)
        y2 = min(img_height, center_y + estimated_height // 2)
        
        return (x1, y1, x2, y2)
    
    def _convert_to_yolo_format(self, 
                               bbox: Tuple[int, int, int, int], 
                               img_width: int, 
                               img_height: int) -> Tuple[float, float, float, float]:
        """
        Convierte bbox a formato YOLOv8 normalizado.
        
        Args:
            bbox: (x1, y1, x2, y2) en píxeles
            img_width: Ancho de imagen
            img_height: Alto de imagen
            
        Returns:
            Tuple: (center_x, center_y, width, height) normalizado
        """
        x1, y1, x2, y2 = bbox
        
        # Calcular centro y dimensiones
        center_x = (x1 + x2) / 2.0
        center_y = (y1 + y2) / 2.0
        width = x2 - x1
        height = y2 - y1
        
        # Normalizar
        center_x_norm = center_x / img_width
        center_y_norm = center_y / img_height
        width_norm = width / img_width
        height_norm = height / img_height
        
        return (center_x_norm, center_y_norm, width_norm, height_norm)
    
    def _create_dataset_config(self):
        """Crea archivo de configuración del dataset."""
        config = {
            'path': str(self.output_dir.absolute()),
            'train': 'train/images',
            'val': 'val/images',
            'test': 'test/images',
            'nc': len(self.classes),
            'names': self.classes
        }
        
        config_file = self.output_dir / 'dataset.yaml'
        with open(config_file, 'w') as f:
            import yaml
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"Configuración del dataset guardada: {config_file}")
    
    def create_sample_annotations(self, num_samples: int = 10) -> List[str]:
        """
        Crea anotaciones de muestra para verificación.
        
        Args:
            num_samples: Número de muestras a crear
            
        Returns:
            List: Rutas de archivos de muestra creados
        """
        logger.info(f"Creando {num_samples} anotaciones de muestra")
        
        sample_dir = self.output_dir / 'samples'
        sample_dir.mkdir(exist_ok=True)
        
        available_images = self._get_available_images()
        sample_images = available_images[:num_samples]
        
        sample_files = []
        
        for image_id in sample_images:
            try:
                # Copiar imagen
                source_image = self.images_dir / f"{image_id}.bmp"
                target_image = sample_dir / f"{image_id}.jpg"
                
                self._convert_image(source_image, target_image)
                
                # Crear anotación
                annotation_file = sample_dir / f"{image_id}.txt"
                self._generate_annotation(image_id, annotation_file, auto_detect_bbox=True)
                
                sample_files.append(str(target_image))
                
            except Exception as e:
                logger.error(f"Error creando muestra {image_id}: {e}")
                continue
        
        logger.info(f"Anotaciones de muestra creadas: {len(sample_files)}")
        return sample_files
    
    def validate_dataset(self) -> Dict[str, Any]:
        """
        Valida el dataset generado.
        
        Returns:
            Dict: Resultados de validación
        """
        logger.info("Validando dataset YOLOv8")
        
        validation_results = {
            'total_images': 0,
            'total_annotations': 0,
            'missing_annotations': 0,
            'invalid_annotations': 0,
            'splits': {}
        }
        
        for split_name in ['train', 'val', 'test']:
            split_dir = getattr(self, f"{split_name}_dir")
            
            images_dir = split_dir / 'images'
            labels_dir = split_dir / 'labels'
            
            image_files = list(images_dir.glob('*.jpg'))
            label_files = list(labels_dir.glob('*.txt'))
            
            split_results = {
                'images': len(image_files),
                'labels': len(label_files),
                'missing_labels': 0,
                'invalid_labels': 0
            }
            
            # Verificar que cada imagen tenga su anotación
            for image_file in image_files:
                image_id = image_file.stem
                label_file = labels_dir / f"{image_id}.txt"
                
                if not label_file.exists():
                    split_results['missing_labels'] += 1
                    continue
                
                # Validar formato de anotación
                try:
                    with open(label_file, 'r') as f:
                        lines = f.readlines()
                        if len(lines) == 0:
                            split_results['invalid_labels'] += 1
                            continue
                        
                        # Verificar formato YOLOv8
                        for line in lines:
                            parts = line.strip().split()
                            if len(parts) != 5:
                                split_results['invalid_labels'] += 1
                                break
                            
                            # Verificar que los valores estén en rango [0,1]
                            for i in range(1, 5):
                                if not (0 <= float(parts[i]) <= 1):
                                    split_results['invalid_labels'] += 1
                                    break
                
                except Exception as e:
                    split_results['invalid_labels'] += 1
            
            validation_results['splits'][split_name] = split_results
            validation_results['total_images'] += split_results['images']
            validation_results['total_annotations'] += split_results['labels']
            validation_results['missing_annotations'] += split_results['missing_labels']
            validation_results['invalid_annotations'] += split_results['invalid_labels']
        
        logger.info("Validación completada")
        logger.info(f"Total imágenes: {validation_results['total_images']}")
        logger.info(f"Total anotaciones: {validation_results['total_annotations']}")
        logger.info(f"Anotaciones faltantes: {validation_results['missing_annotations']}")
        logger.info(f"Anotaciones inválidas: {validation_results['invalid_annotations']}")
        
        return validation_results


    def prepare_incremental_data(self, dataset_path: Path, new_sample_id: int) -> Dict[str, Any]:
        """
        Prepara datos para entrenamiento incremental con nueva muestra.
        
        Args:
            dataset_path: Ruta al dataset actualizado
            new_sample_id: ID de la nueva muestra
            
        Returns:
            Dict con resultado de la preparación
        """
        try:
            logger.info(f"Preparando datos incrementales para muestra {new_sample_id}")
            
            # Leer dataset actualizado
            df = pd.read_csv(dataset_path)
            
            # Filtrar solo la nueva muestra
            new_sample = df[df['ID'] == new_sample_id]
            
            if len(new_sample) == 0:
                return {
                    'success': False,
                    'error': f'Muestra {new_sample_id} no encontrada en dataset'
                }
            
            # Configurar rutas para datos incrementales
            incremental_dir = self.output_dir / 'incremental'
            incremental_dir.mkdir(exist_ok=True)
            
            images_dir = incremental_dir / 'images'
            labels_dir = incremental_dir / 'labels'
            images_dir.mkdir(exist_ok=True)
            labels_dir.mkdir(exist_ok=True)
            
            # Procesar nueva muestra
            sample_data = new_sample.iloc[0]
            
            # Buscar imagen correspondiente
            image_path = self._find_image_for_id(new_sample_id)
            
            if not image_path or not image_path.exists():
                return {
                    'success': False,
                    'error': f'Imagen no encontrada para ID {new_sample_id}'
                }
            
            # Copiar imagen
            new_image_path = images_dir / f"{new_sample_id}.bmp"
            shutil.copy2(image_path, new_image_path)
            
            # Generar anotación YOLO
            annotation = self._generate_yolo_annotation_incremental(sample_data, new_image_path)
            
            # Guardar anotación
            label_path = labels_dir / f"{new_sample_id}.txt"
            with open(label_path, 'w') as f:
                f.write(annotation)
            
            # Crear archivo de configuración incremental
            config_path = incremental_dir / 'incremental_config.yaml'
            config = {
                'path': str(incremental_dir),
                'train': 'images',
                'val': 'images',  # Usar las mismas imágenes para validación en incremental
                'nc': 1,
                'names': ['cacao_grain'],
                'sample_id': new_sample_id,
                'created_at': datetime.now().isoformat()
            }
            
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            logger.info(f"Datos incrementales preparados: {new_image_path}")
            
            return {
                'success': True,
                'new_data_path': str(incremental_dir),
                'config_path': str(config_path),
                'total_samples': len(df),
                'new_sample_id': new_sample_id
            }
            
        except Exception as e:
            logger.error(f"Error preparando datos incrementales: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _find_image_for_id(self, sample_id: int) -> Optional[Path]:
        """
        Busca la imagen correspondiente a un ID de muestra.
        
        Args:
            sample_id: ID de la muestra
            
        Returns:
            Path a la imagen o None si no se encuentra
        """
        try:
            # Buscar en directorio de nuevas imágenes primero
            new_images_dir = Path(__file__).parent.parent / 'media' / 'cacao_images' / 'new'
            new_image_path = new_images_dir / f"{sample_id}.bmp"
            
            if new_image_path.exists():
                return new_image_path
            
            # Buscar en directorio original
            original_images_dir = Path(__file__).parent / 'media' / 'imgs'
            original_image_path = original_images_dir / f"{sample_id}.bmp"
            
            if original_image_path.exists():
                return original_image_path
            
            return None
            
        except Exception as e:
            logger.error(f"Error buscando imagen para ID {sample_id}: {e}")
            return None
    
    def _generate_yolo_annotation_incremental(self, sample_data: pd.Series, image_path: Path) -> str:
        """
        Genera anotación YOLO para muestra incremental.
        
        Args:
            sample_data: Datos de la muestra
            image_path: Ruta a la imagen
            
        Returns:
            String con anotación YOLO
        """
        try:
            # Obtener dimensiones de la imagen
            image = cv2.imread(str(image_path))
            img_height, img_width = image.shape[:2]
            
            # Detectar automáticamente el grano en la imagen
            bbox = self._detect_grain_bbox(image)
            
            # Convertir a formato YOLOv8 (normalizado)
            yolo_bbox = self._convert_to_yolo_format(bbox, img_width, img_height)
            
            # Formato: class_id center_x center_y width height
            return f"0 {yolo_bbox[0]:.6f} {yolo_bbox[1]:.6f} {yolo_bbox[2]:.6f} {yolo_bbox[3]:.6f}\n"
            
        except Exception as e:
            logger.error(f"Error generando anotación incremental: {e}")
            # Fallback: usar bbox centrado
            return "0 0.5 0.5 0.8 0.8\n"


def main():
    """Función principal para ejecutar la preparación de datos."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Preparar datos para entrenamiento YOLOv8')
    parser.add_argument('--dataset-csv', required=True, help='Ruta al archivo dataset.csv')
    parser.add_argument('--images-dir', required=True, help='Directorio con las imágenes')
    parser.add_argument('--output-dir', default='yolo_dataset', help='Directorio de salida')
    parser.add_argument('--split-ratios', nargs=3, type=float, default=[0.7, 0.2, 0.1],
                       help='Proporciones para train/val/test')
    parser.add_argument('--samples', type=int, default=10, help='Número de muestras para crear')
    parser.add_argument('--validate', action='store_true', help='Validar dataset generado')
    
    args = parser.parse_args()
    
    try:
        # Crear preparador
        preparator = YOLODataPreparator(
            dataset_csv_path=args.dataset_csv,
            images_dir=args.images_dir,
            output_dir=args.output_dir
        )
        
        # Generar anotaciones
        counts = preparator.generate_annotations(
            split_ratios=tuple(args.split_ratios),
            auto_detect_bbox=True
        )
        
        print(f"\n✅ Anotaciones generadas:")
        for split, count in counts.items():
            print(f"  {split}: {count} imágenes")
        
        # Crear muestras
        sample_files = preparator.create_sample_annotations(args.samples)
        print(f"\n✅ Muestras creadas: {len(sample_files)}")
        
        # Validar si se solicita
        if args.validate:
            validation_results = preparator.validate_dataset()
            print(f"\n✅ Validación completada:")
            print(f"  Total imágenes: {validation_results['total_images']}")
            print(f"  Total anotaciones: {validation_results['total_annotations']}")
            print(f"  Anotaciones faltantes: {validation_results['missing_annotations']}")
            print(f"  Anotaciones inválidas: {validation_results['invalid_annotations']}")
        
        print(f"\n🎯 Dataset YOLOv8 listo para entrenamiento!")
        print(f"📁 Directorio: {args.output_dir}")
        print(f"📄 Configuración: {args.output_dir}/dataset.yaml")
        
    except Exception as e:
        logger.error(f"Error en preparación de datos: {e}")
        raise


if __name__ == "__main__":
    main()
