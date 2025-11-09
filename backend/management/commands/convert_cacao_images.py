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
from typing import Optional

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

    def handle(self, *args, **options):
        limit = options["limit"]
        only = options["only"]

        raw_dir = ensure_dir_exists(get_raw_images_dir())
        jpg_dir = ensure_dir_exists(get_converted_jpg_dir())
        png_dir = ensure_dir_exists(get_processed_images_dir())

        processed = 0

        # 1) BMP -> JPG
        if only in ("bmp", "all"):
            bmp_files = list(raw_dir.glob("*.bmp"))
            self.stdout.write(self.style.NOTICE(f"BMP encontrados: {len(bmp_files)}"))
            for p in bmp_files[: (None if limit == 0 else limit)]:
                img, meta = convert_bmp_to_jpg(p)
                if not meta.get("success") or img is None:
                    logger.error(f"Fallo BMP->JPG {p.name}: {meta.get('error')}")
                    continue
                out_path = jpg_dir / f"{p.stem}.jpg"
                save_image(img, out_path, format="JPEG")
                processed += 1

        # 2) JPG -> PNG segmentado
        if only in ("png", "all"):
            # Aceptar como fuentes: JPG/JPEG en raw y converted_jpg, y también PNG en raw
            sources = (
                list(raw_dir.glob("*.jpg")) +
                list(raw_dir.glob("*.jpeg")) +
                list(raw_dir.glob("*.png")) +
                list(jpg_dir.glob("*.jpg")) +
                list(jpg_dir.glob("*.jpeg"))
            )
            self.stdout.write(self.style.NOTICE(f"Imágenes a segmentar (jpg/jpeg/png): {len(sources)}"))
            self.stdout.write(self.style.NOTICE(f"Guardando PNG en: {png_dir.absolute()}"))
            for p in sources[: (None if limit == 0 else limit)]:
                pil_png, meta = segment_and_crop_cacao_bean(p)
                if not meta.get("success") or pil_png is None:
                    logger.error(f"Fallo JPG->PNG {p.name}: {meta.get('error')}")
                    continue
                out_path = png_dir / f"{p.stem}.png"
                save_image(pil_png, out_path, format="PNG")
                self.stdout.write(f"  [OK] Guardado: {out_path.name}")
                processed += 1

        self.stdout.write(self.style.SUCCESS(f"Procesamiento completado. Archivos procesados: {processed}"))


