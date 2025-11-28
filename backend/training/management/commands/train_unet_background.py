"""
Comando Django para entrenar modelo U-Net para eliminación de fondo.
Adaptado para usar imágenes del dataset de cacao (BMP, JPG, PNG, TIFF).
"""
import os
import sys
import shutil
import tempfile
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from PIL import Image

# Asegurar que el path del proyecto esté configurado
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ml.data.transforms import train_background_ai, UNet
from ml.utils.paths import get_raw_images_dir, get_project_root, ensure_dir_exists
from ml.utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.commands.unet")


def _generate_single_mask(args):
    """Genera una máscara para una imagen (función auxiliar para multiprocessing)."""
    import cv2
    import numpy as np
    import time
    
    jpg_path, mask_path = args
    start_time = time.time()
    
    try:
        # Leer imagen con timeout implícito (cv2.imread es rápido)
        img = cv2.imread(str(jpg_path))
        if img is None:
            return False, f"Error leyendo imagen: {jpg_path.name}"
        
        # Validar dimensiones mínimas
        if img.shape[0] < 50 or img.shape[1] < 50:
            return False, f"Imagen muy pequeña: {jpg_path.name}"
        
        # Reducir tamaño si es muy grande (grabCut es lento en imágenes grandes)
        max_dimension = 800
        if max(img.shape[:2]) > max_dimension:
            scale = max_dimension / max(img.shape[:2])
            new_width = int(img.shape[1] * scale)
            new_height = int(img.shape[0] * scale)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        mask = np.zeros(img.shape[:2], np.uint8)
        # Rectángulo más conservador para evitar problemas
        margin = min(20, img.shape[0] // 10, img.shape[1] // 10)
        rect = (margin, margin, img.shape[1] - 2*margin, img.shape[0] - 2*margin)
        
        # Validar que el rectángulo sea válido
        if rect[2] <= 0 or rect[3] <= 0:
            return False, f"Rectángulo inválido: {jpg_path.name}"
        
        bgdModel = np.zeros((1, 65), np.float64)
        fgdModel = np.zeros((1, 65), np.float64)
        
        # Reducir iteraciones para ser más rápido (3 en lugar de 5)
        cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 3, cv2.GC_INIT_WITH_RECT)
        
        # Verificar timeout (más de 30 segundos es sospechoso)
        elapsed = time.time() - start_time
        if elapsed > 30:
            return False, f"Timeout (>30s): {jpg_path.name}"
        
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8') * 255
        cv2.imwrite(str(mask_path), mask2)
        return True, None
    except Exception as e:
        return False, f"Error: {str(e)}"


class Command(BaseCommand):
    help = 'Entrena modelo U-Net para eliminación de fondo de granos de cacao'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--epochs',
            type=int,
            default=20,
            help='Número de épocas de entrenamiento (default: 20)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=4,
            help='Tamaño de batch (default: 4, recomendado 16-32 con GPU)'
        )
        parser.add_argument(
            '--max-images',
            type=int,
            default=None,
            help='Máximo número de imágenes a usar (para pruebas, default: todas)'
        )
        parser.add_argument(
            '--learning-rate',
            type=float,
            default=1e-4,
            help='Learning rate (default: 1e-4)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar reentrenamiento incluso si el modelo ya existe'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧠 Iniciando entrenamiento del modelo U-Net para eliminación de fondo...'))
        
        epochs = options['epochs']
        batch_size = options['batch_size']
        max_images = options['max_images']
        learning_rate = options['learning_rate']
        
        # Verificar si el modelo ya existe
        project_root = get_project_root()
        segmentation_dir = project_root / "ml" / "segmentation"
        model_path = segmentation_dir / "cacao_unet.pth"
        
        if model_path.exists() and not options.get('force', False):
            file_size_mb = model_path.stat().st_size / (1024 * 1024)
            self.stdout.write(self.style.SUCCESS(
                f"✅ El modelo ya existe en: {model_path} ({file_size_mb:.2f} MB)"
            ))
            self.stdout.write("   Para reentrenar, usa: --force")
            return
        
        # Obtener directorio de imágenes raw
        raw_images_dir = get_raw_images_dir()
        
        if not raw_images_dir.exists():
            raise CommandError(f"Directorio de imágenes raw no encontrado: {raw_images_dir}")
        
        # Listar imágenes (BMP, JPG, PNG, TIFF)
        image_extensions = ['*.bmp', '*.jpg', '*.jpeg', '*.png', '*.tiff', '*.tif']
        image_files = []
        for ext in image_extensions:
            image_files.extend(raw_images_dir.glob(ext))
            image_files.extend(raw_images_dir.glob(ext.upper()))  # También busca mayúsculas
        
        # Eliminar duplicados (por si hay .jpg y .JPG)
        image_files = list(set(image_files))
        
        if not image_files:
            raise CommandError(f"No se encontraron imágenes en {raw_images_dir}. Formatos soportados: BMP, JPG, PNG, TIFF")

        if max_images:
            image_files = image_files[:max_images]

        self.stdout.write(f"📸 Encontradas {len(image_files)} imágenes")
        
        # Crear directorios temporales para entrenamiento
        # El modelo espera JPG, así que convertiremos BMP -> JPG temporalmente
        temp_dir = Path(tempfile.mkdtemp(prefix="unet_training_"))
        images_temp_dir = temp_dir / "images"
        masks_temp_dir = temp_dir / "masks"
        
        ensure_dir_exists(images_temp_dir)
        ensure_dir_exists(masks_temp_dir)
        
        try:
            self.stdout.write("🔄 Convirtiendo imágenes a JPG temporalmente...")
            
            # Convertir imágenes a JPG en directorio temporal (solo si no existe)
            converted_count = 0
            skipped_count = 0
            for image_file in image_files:
                jpg_name = image_file.stem + ".jpg"
                jpg_path = images_temp_dir / jpg_name
                
                # Verificar si ya existe
                if jpg_path.exists():
                    skipped_count += 1
                    continue
                
                try:
                    # Leer imagen (soporta BMP, JPG, PNG, TIFF, etc.)
                    img = Image.open(image_file)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Guardar como JPG temporal
                    img.save(jpg_path, "JPEG", quality=95)
                    converted_count += 1
                    
                    if converted_count % 50 == 0:
                        self.stdout.write(f"   Convertidas {converted_count}/{len(image_files)} imágenes...")
                        
                except Exception as e:
                    logger.warning(f"Error convirtiendo {image_file.name}: {e}")
                    continue
            
            if skipped_count > 0:
                self.stdout.write(f"   ⏭️  Omitidas {skipped_count} imágenes ya convertidas")
            
            self.stdout.write(self.style.SUCCESS(f"✅ Convertidas {converted_count} imágenes"))
            
            if converted_count == 0:
                raise CommandError("No se pudieron convertir imágenes. Verifica que las imágenes sean válidas.")
            
            # Modificar la función train_background_ai para usar nuestros parámetros
            self.stdout.write("🎯 Iniciando entrenamiento del modelo U-Net...")
            self.stdout.write(f"   Épocas: {epochs}")
            self.stdout.write(f"   Batch size: {batch_size}")
            self.stdout.write(f"   Learning rate: {learning_rate}")
            
            # Importar y modificar la función de entrenamiento
            import torch
            import torch.nn as nn
            import torch.optim as optim
            from torchvision import transforms as T
            from torch.utils.data import DataLoader
            from ml.data.transforms import CacaoDataset, UNet
            
            # Configurar transformaciones
            transform = T.Compose([
                T.Resize((256, 256)),
                T.ToTensor(),
            ])
            
            # Generar máscaras en paralelo ANTES de crear el dataset
            self.stdout.write("🎭 Generando máscaras automáticamente (paralelizado)...")
            self._generate_masks_parallel(images_temp_dir, masks_temp_dir, image_files)
            
            # Filtrar imágenes que tienen máscaras correspondientes
            self.stdout.write("🔍 Filtrando imágenes con máscaras válidas...")
            valid_image_files = []
            for image_file in image_files:
                jpg_name = image_file.stem + ".jpg"
                mask_name = image_file.stem + ".png"
                jpg_path = images_temp_dir / jpg_name
                mask_path = masks_temp_dir / mask_name
                
                if jpg_path.exists() and mask_path.exists():
                    valid_image_files.append(jpg_name)
                else:
                    if not mask_path.exists():
                        logger.warning(f"Omitiendo {jpg_name}: máscara no encontrada")
            
            if not valid_image_files:
                raise CommandError("No hay imágenes válidas con máscaras. Verifica la generación de máscaras.")
            
            self.stdout.write(f"✅ {len(valid_image_files)}/{len(image_files)} imágenes tienen máscaras válidas")
            
            # Crear directorios temporales solo con imágenes válidas
            valid_images_dir = temp_dir / "valid_images"
            valid_masks_dir = temp_dir / "valid_masks"
            ensure_dir_exists(valid_images_dir)
            ensure_dir_exists(valid_masks_dir)
            
            # Copiar solo imágenes y máscaras válidas
            for jpg_name in valid_image_files:
                mask_name = jpg_name.replace(".jpg", ".png")
                jpg_src = images_temp_dir / jpg_name
                mask_src = masks_temp_dir / mask_name
                jpg_dst = valid_images_dir / jpg_name
                mask_dst = valid_masks_dir / mask_name
                
                if jpg_src.exists():
                    shutil.copy2(jpg_src, jpg_dst)
                if mask_src.exists():
                    shutil.copy2(mask_src, mask_dst)
            
            # Crear dataset solo con imágenes válidas
            dataset = CacaoDataset(
                str(valid_images_dir),
                str(valid_masks_dir),
                transform,
                auto_generate=False  # Ya generamos las máscaras arriba
            )
            
            loader = DataLoader(
                dataset, 
                batch_size=batch_size, 
                shuffle=True,
                num_workers=4,  # Paralelizar carga de datos
                pin_memory=True if torch.cuda.is_available() else False  # Acelerar transferencia a GPU
            )
            
            # Configurar dispositivo
            device = "cuda" if torch.cuda.is_available() else "cpu"
            if torch.cuda.is_available():
                self.stdout.write(f"🚀 Usando GPU: {torch.cuda.get_device_name(0)}")
                self.stdout.write(f"   Memoria GPU: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
                # Aumentar batch size automáticamente si hay GPU
                if batch_size < 16:
                    self.stdout.write("   ⚠️  Considera usar --batch-size 16 o mayor para mejor uso de GPU")
            else:
                self.stdout.write("🖥️  Usando CPU (GPU no disponible)")
            
            # Crear modelo
            model = UNet().to(device)
            criterion = nn.BCELoss()
            optimizer = optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-4)
            
            # Entrenar
            self.stdout.write("\n📊 Progreso del entrenamiento:")
            for epoch in range(epochs):
                epoch_loss = 0.0
                batch_count = 0
                
                for imgs, masks in loader:
                    imgs = imgs.to(device)
                    masks = masks.to(device)
                    
                    optimizer.zero_grad()
                    preds = model(imgs)
                    loss = criterion(preds, masks)
                    loss.backward()
                    optimizer.step()
                    
                    epoch_loss += loss.item()
                    batch_count += 1
                
                avg_loss = epoch_loss / batch_count if batch_count > 0 else 0.0
                self.stdout.write(f"   Epoch {epoch+1}/{epochs} | Loss: {avg_loss:.4f}")
            
            # Guardar modelo (usar ruta relativa como en transforms.py)
            project_root = get_project_root()
            segmentation_dir = project_root / "ml" / "segmentation"
            ensure_dir_exists(segmentation_dir)
            model_path = segmentation_dir / "cacao_unet.pth"
            
            torch.save(model.state_dict(), model_path)
            
            # Verificar que se guardó
            if not model_path.exists():
                raise CommandError(f"Error: El modelo no se guardó en {model_path}")
            
            file_size_mb = model_path.stat().st_size / (1024 * 1024)
            self.stdout.write(self.style.SUCCESS(
                "\n✅ Modelo entrenado y guardado exitosamente!"
            ))
            self.stdout.write(f"   📁 Ubicación: {model_path}")
            self.stdout.write(f"   📦 Tamaño: {file_size_mb:.2f} MB")
            self.stdout.write("\n💡 Ahora puedes usar '--segmentation-backend ai' para usar este modelo")
            
        except Exception as e:
            logger.error(f"Error durante el entrenamiento: {e}", exc_info=True)
            raise CommandError(f"Error entrenando modelo U-Net: {e}")
        
        finally:
            # Limpiar directorios temporales
            if temp_dir.exists():
                self.stdout.write("🧹 Limpiando archivos temporales...")
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _generate_masks_parallel(self, images_dir: Path, masks_dir: Path, image_files: list):
        """Genera máscaras en paralelo usando ThreadPoolExecutor (más estable en Docker)."""
        # Preparar argumentos: (jpg_path, mask_path)
        tasks = []
        for image_file in image_files:
            jpg_name = image_file.stem + ".jpg"
            jpg_path = images_dir / jpg_name
            mask_path = masks_dir / (image_file.stem + ".png")
            if not mask_path.exists():  # Solo generar si no existe
                tasks.append((jpg_path, mask_path))
        
        if not tasks:
            self.stdout.write("✅ Todas las máscaras ya existen")
            return
        
        # Reducir workers para evitar bloqueos (2 es más seguro)
        num_workers = min(2, len(tasks))
        completed = 0
        failed = 0
        last_progress_time = time.time()
        
        self.stdout.write(f"   Usando {num_workers} threads en paralelo...")
        self.stdout.write(f"   Procesando {len(tasks)} máscaras...")
        
        try:
            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                futures = {executor.submit(_generate_single_mask, task): task for task in tasks}
                
                for future in as_completed(futures):
                    task = futures[future]
                    jpg_name = task[0].name
                    
                    try:
                        # Timeout de 60 segundos por tarea
                        success, error_msg = future.result(timeout=60)
                        
                        if success:
                            completed += 1
                        else:
                            failed += 1
                            if error_msg:
                                logger.warning(f"Error en {jpg_name}: {error_msg}")
                        
                        # Mostrar progreso cada 25 imágenes o cada 30 segundos
                        current_time = time.time()
                        if (completed + failed) % 25 == 0 or (current_time - last_progress_time) > 30:
                            self.stdout.write(f"   Máscaras generadas: {completed}/{len(tasks)} (fallidas: {failed})...")
                            last_progress_time = current_time
                            
                    except TimeoutError:
                        # TimeoutError de concurrent.futures
                        failed += 1
                        logger.error(f"Timeout generando máscara: {jpg_name}")
                        self.stdout.write(self.style.WARNING(f"   ⚠️  Timeout en {jpg_name}, continuando..."))
                    except Exception as e:
                        failed += 1
                        logger.error(f"Error generando máscara {jpg_name}: {e}")
                        continue
            
            self.stdout.write(self.style.SUCCESS(f"✅ Generadas {completed}/{len(tasks)} máscaras (fallidas: {failed})"))
            
            if failed > len(tasks) * 0.1:  # Si más del 10% fallaron
                self.stdout.write(self.style.WARNING(f"⚠️  Muchas máscaras fallaron ({failed}). Considera revisar las imágenes."))
                
        except Exception as e:
            logger.error(f"Error en generación paralela: {e}", exc_info=True)
            # Fallback: generar secuencialmente
            self.stdout.write(self.style.WARNING("⚠️  Fallback a generación secuencial..."))
            completed = 0
            failed = 0
            for i, task in enumerate(tasks):
                try:
                    jpg_name = task[0].name
                    success, error_msg = _generate_single_mask(task)
                    if success:
                        completed += 1
                    else:
                        failed += 1
                        if error_msg:
                            logger.warning(f"Error en {jpg_name}: {error_msg}")
                    
                    if (completed + failed) % 25 == 0:
                        self.stdout.write(f"   Máscaras generadas: {completed}/{len(tasks)} (fallidas: {failed})...")
                except Exception as e:
                    failed += 1
                    logger.warning(f"Error generando máscara {task[0].name}: {e}")
                    continue
            self.stdout.write(self.style.SUCCESS(f"✅ Generadas {completed}/{len(tasks)} máscaras (secuencial, fallidas: {failed})"))

