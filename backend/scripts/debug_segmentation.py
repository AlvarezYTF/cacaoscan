"""
Script de debug para probar el segmentador YOLO-Seg de granos de cacao.

Este script permite:
- Probar la segmentación sobre una imagen
- Visualizar bounding box y máscara
- Generar PNG del grano recortado
- Mostrar métricas detalladas
- Ejecutar predicción completa (dimensiones y peso) si está disponible
"""
import sys
import argparse
from pathlib import Path
import numpy as np
import cv2
from PIL import Image

# Agregar el directorio backend al path para imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from ml.segmentation.cacao_segmentation_model import CacaoSegmentationModel
from ml.segmentation.processor import SegmentationError
from ml.utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.scripts.debug_segmentation")


def draw_bbox_and_mask(image_path: str, prediction: dict, output_path: Path) -> None:
    """
    Dibuja bounding box y máscara sobre la imagen original.
    
    Args:
        image_path: Ruta a la imagen original
        prediction: Diccionario con resultados de segmentación
        output_path: Ruta donde guardar la imagen con anotaciones
    """
    # Cargar imagen
    image = cv2.imread(image_path)
    if image is None:
        logger.error(f"No se pudo cargar la imagen: {image_path}")
        return
    
    # Dibujar bounding box
    bbox = prediction['bbox']
    x1, y1, x2, y2 = map(int, bbox)
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    # Dibujar máscara (semi-transparente)
    mask = prediction['mask']
    if mask.shape[:2] != image.shape[:2]:
        mask = cv2.resize(mask, (image.shape[1], image.shape[0]), interpolation=cv2.INTER_NEAREST)
    
    # Crear overlay de máscara
    mask_colored = np.zeros_like(image)
    mask_colored[mask > 0] = [0, 255, 0]  # Verde
    image = cv2.addWeighted(image, 0.7, mask_colored, 0.3, 0)
    
    # Añadir texto con información
    conf_text = f"Conf: {prediction['confidence']:.3f}"
    class_text = f"Class: {prediction['class_name']}"
    area_text = f"Area: {prediction['area_pixels']} px"
    
    cv2.putText(image, conf_text, (x1, y1 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(image, class_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(image, area_text, (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Guardar imagen
    cv2.imwrite(str(output_path), image)
    logger.info(f"Imagen con anotaciones guardada en: {output_path}")


def print_metrics(prediction: dict, metadata: dict = None) -> None:
    """
    Imprime métricas detalladas en consola.
    
    Args:
        prediction: Diccionario con resultados de segmentación
        metadata: Diccionario con metadata adicional (opcional)
    """
    print("\n" + "="*80)
    print("MÉTRICAS DE SEGMENTACIÓN YOLO-Seg")
    print("="*80)
    print(f"Confidence: {prediction['confidence']:.3f}")
    print(f"Class Name: {prediction['class_name']}")
    print(f"Area (pixels): {prediction['area_pixels']}")
    print(f"Aspect Ratio: {prediction['aspect_ratio']:.2f}")
    print(f"Image Size: {prediction['image_width']}x{prediction['image_height']}")
    print(f"BBox: [{int(prediction['bbox'][0])}, {int(prediction['bbox'][1])}, "
          f"{int(prediction['bbox'][2])}, {int(prediction['bbox'][3])}]")
    
    if metadata:
        print(f"\nCrop Size: {metadata.get('crop_width', 'N/A')}x{metadata.get('crop_height', 'N/A')}")
    
    print("="*80 + "\n")


def test_segmentation(image_path: str, output_dir: Path, run_prediction: bool = False) -> None:
    """
    Prueba la segmentación sobre una imagen.
    
    Args:
        image_path: Ruta a la imagen a segmentar
        output_dir: Directorio donde guardar resultados
        run_prediction: Si True, ejecuta también la predicción completa
    """
    image_path_obj = Path(image_path)
    if not image_path_obj.exists():
        logger.error(f"Imagen no encontrada: {image_path}")
        return
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Cargar modelo
        logger.info("Cargando modelo YOLO-Seg...")
        seg_model = CacaoSegmentationModel(confidence_threshold=0.75)
        
        # Cargar imagen PIL
        image = Image.open(image_path)
        
        # Realizar segmentación
        logger.info(f"Segmentando imagen: {image_path_obj.name}...")
        crop_image, metadata = seg_model.segment_and_crop(image)
        
        # Guardar crop
        crop_output_path = output_dir / f"{image_path_obj.stem}_crop.png"
        crop_image.save(crop_output_path, format='PNG')
        logger.info(f"Crop guardado en: {crop_output_path}")
        
        # Obtener predicción completa para visualización
        prediction = seg_model.segment(image)
        
        # Dibujar bbox y máscara
        debug_output_path = output_dir / f"{image_path_obj.stem}_debug.jpg"
        draw_bbox_and_mask(image_path, prediction, debug_output_path)
        
        # Imprimir métricas
        print_metrics(prediction, metadata)
        
        # Si se solicita, ejecutar predicción completa
        if run_prediction:
            try:
                from ml.prediction.predict import PredictorCacao
                
                logger.info("Cargando predictor completo...")
                predictor = PredictorCacao()
                if not predictor.load_artifacts():
                    logger.warning("No se pudieron cargar los artefactos del predictor. Saltando predicción.")
                    return
                
                logger.info("Ejecutando predicción completa...")
                result = predictor.predict(image)
                
                print("\n" + "="*80)
                print("PREDICCIÓN COMPLETA (Dimensiones y Peso)")
                print("="*80)
                print(f"Alto (mm): {result['alto_mm']:.2f}")
                print(f"Ancho (mm): {result['ancho_mm']:.2f}")
                print(f"Grosor (mm): {result['grosor_mm']:.2f}")
                print(f"Peso (g): {result['peso_g']:.2f}")
                print(f"Crop URL: {result.get('crop_url', 'N/A')}")
                print("="*80 + "\n")
                
            except Exception as e:
                logger.warning(f"No se pudo ejecutar predicción completa: {e}")
        
        logger.info("✅ Segmentación completada exitosamente")
        
    except SegmentationError as e:
        logger.error(f"❌ Error de segmentación: {e}")
        print(f"\n❌ ERROR: {e}\n")
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}", exc_info=True)
        print(f"\n❌ ERROR INESPERADO: {e}\n")


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Script de debug para probar segmentación YOLO-Seg de granos de cacao"
    )
    parser.add_argument(
        "image_path",
        type=str,
        help="Ruta a la imagen a segmentar"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="debug_output",
        help="Directorio donde guardar resultados (por defecto: debug_output)"
    )
    parser.add_argument(
        "--run-prediction",
        action="store_true",
        help="Ejecutar también la predicción completa (dimensiones y peso)"
    )
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    test_segmentation(args.image_path, output_dir, args.run_prediction)


if __name__ == "__main__":
    main()

