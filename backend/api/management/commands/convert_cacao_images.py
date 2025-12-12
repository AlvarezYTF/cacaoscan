from __future__ import annotations

"""
Comando Django:
  Convierte imágenes para entrenamiento:
   - BMP -> JPG (en media/cacao_images/converted_jpg)
   - JPG -> PNG segmentado (en media/cacao_images/processed)

Uso:
  python manage.py convert_cacao_images --limit 0
  python manage.py convert_cacao_images --only bmp   # solo BMP->JPG
  python manage.py convert_cacao_images --only png   # solo JPG->PNG (segmentado)
"""

import io
from pathlib import Path
from typing import Optional, Callable, Tuple, Any

from django.core.management.base import BaseCommand

from ml.utils.logs import get_ml_logger
from ml.utils.io import ensure_dir_exists, save_image
from ml.utils.paths import (
    get_raw_images_dir,
    get_converted_jpg_dir,
    get_processed_images_dir,
)
from ml.segmentation.processor import convert_bmp_to_jpg, segment_and_crop_cacao_bean


logger = get_ml_logger("cacaoscan.management.convert_cacao_images")


class Command(BaseCommand):
    help = "Convierte imágenes BMP->JPG y JPG->PNG (segmentado) para entrenamiento"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=0, help="Límite de imágenes a procesar (0=sin límite)")
        parser.add_argument("--only", type=str, choices=["bmp", "png", "all"], default="all",
                            help="Etapa a ejecutar: bmp (BMP->JPG), png (JPG->PNG), all")

    def _process_files(
        self,
        files: list[Path],
        process_func: Callable[[Path], Tuple[Any, dict[str, Any]]],
        output_dir: Path,
        output_format: str,
        file_type_label: str,
        limit: int,
        show_progress: bool = False,
    ) -> int:
        """Procesa archivos usando una función de procesamiento genérica."""
        self.stdout.write(self.style.NOTICE(f"{file_type_label} encontrados: {len(files)}"))
        if show_progress:
            self.stdout.write(self.style.NOTICE(f"Guardando {output_format} en: {output_dir.absolute()}"))
        
        processed = 0
        files_to_process = files[: (None if limit == 0 else limit)]
        
        for file_path in files_to_process:
            result_image, meta = process_func(file_path)
            if not meta.get("success") or result_image is None:
                logger.error(f"Fallo procesamiento {file_path.name}: {meta.get('error')}")
                continue
            out_path = output_dir / f"{file_path.stem}.{output_format.lower()}"
            save_image(result_image, out_path, format=output_format)
            if show_progress:
                self.stdout.write(f"  [OK] Guardado: {out_path.name}")
            processed += 1
        
        return processed
    
    def _process_bmp_to_jpg(self, raw_dir: Path, jpg_dir: Path, limit: int) -> int:
        """Procesa archivos BMP a JPG."""
        bmp_files = list(raw_dir.glob("*.bmp"))
        return self._process_files(
            files=bmp_files,
            process_func=convert_bmp_to_jpg,
            output_dir=jpg_dir,
            output_format="JPEG",
            file_type_label="BMP",
            limit=limit,
            show_progress=False,
        )
    
    def _get_image_sources(self, raw_dir: Path, jpg_dir: Path) -> list[Path]:
        """Obtiene las fuentes de imágenes para segmentar."""
        return (
            list(raw_dir.glob("*.jpg")) +
            list(raw_dir.glob("*.jpeg")) +
            list(raw_dir.glob("*.png")) +
            list(jpg_dir.glob("*.jpg")) +
            list(jpg_dir.glob("*.jpeg"))
        )
    
    def _process_jpg_to_png(self, raw_dir: Path, jpg_dir: Path, png_dir: Path, limit: int) -> int:
        """Procesa archivos JPG/PNG a PNG segmentado."""
        sources = self._get_image_sources(raw_dir, jpg_dir)
        return self._process_files(
            files=sources,
            process_func=segment_and_crop_cacao_bean,
            output_dir=png_dir,
            output_format="PNG",
            file_type_label="Imágenes a segmentar (jpg/jpeg/png)",
            limit=limit,
            show_progress=True,
        )
    
    def handle(self, *args, **options):
        limit = options["limit"]
        only = options["only"]

        raw_dir = ensure_dir_exists(get_raw_images_dir())
        jpg_dir = ensure_dir_exists(get_converted_jpg_dir())
        png_dir = ensure_dir_exists(get_processed_images_dir())

        processed = 0

        if only in ("bmp", "all"):
            processed += self._process_bmp_to_jpg(raw_dir, jpg_dir, limit)

        if only in ("png", "all"):
            processed += self._process_jpg_to_png(raw_dir, jpg_dir, png_dir, limit)

        self.stdout.write(self.style.SUCCESS(f"Procesamiento completado. Archivos procesados: {processed}"))


