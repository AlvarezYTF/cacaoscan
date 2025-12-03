"""
Utilidades para operaciones de entrada y salida.
"""
import json
import pickle
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
from PIL import Image


def save_json(data: Dict[str, Any], file_path: Path) -> None:
    """Guarda datos en formato JSON."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(file_path: Path) -> Dict[str, Any]:
    """Carga datos desde un archivo JSON."""
    with open(file_path, 'rb') as f:
        raw_content = f.read()
        # Try multiple encodings in order
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        text_content = None
        for encoding in encodings:
            try:
                text_content = raw_content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        if text_content is None:
            # Last resort: use utf-8 with errors='ignore'
            text_content = raw_content.decode('utf-8', errors='ignore')
        return json.loads(text_content)


def save_pickle(data: Any, file_path: Path) -> None:
    """Guarda datos en formato pickle."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)


def load_pickle(file_path: Path) -> Any:
    """Carga datos desde un archivo pickle."""
    with open(file_path, 'rb') as f:
        return pickle.load(f)


def save_csv(df: pd.DataFrame, file_path: Path, index: bool = False) -> None:
    """Guarda un DataFrame como CSV."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(file_path, index=index, encoding='utf-8')


def load_csv(file_path: Path) -> pd.DataFrame:
    """Carga datos desde un archivo CSV."""
    return pd.read_csv(file_path, encoding='utf-8')


def save_image(image: Image.Image, file_path: Path, format: str = None) -> None:
    """Guarda una imagen."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if format is None:
        # Map common extensions to PIL format names
        ext = file_path.suffix[1:].upper()
        format_map = {
            'JPG': 'JPEG',
            'JPEG': 'JPEG',
            'PNG': 'PNG',
            'GIF': 'GIF',
            'BMP': 'BMP',
            'TIFF': 'TIFF',
            'TIF': 'TIFF',
        }
        image_format = format_map.get(ext, ext)
    else:
        image_format = format
    image.save(file_path, format=image_format)


def load_image(file_path: Path) -> Image.Image:
    """Carga una imagen."""
    return Image.open(file_path)


def write_log(log_path: Path, message: str) -> None:
    """Escribe un mensaje en un archivo de log."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"{message}\n")


def get_file_timestamp(file_path: Path) -> Optional[float]:
    """Obtiene el timestamp de modificación de un archivo."""
    if file_path.exists():
        return file_path.stat().st_mtime
    return None


def file_exists_and_newer(source_path: Path, target_path: Path) -> bool:
    """Verifica si el archivo fuente es más nuevo que el objetivo."""
    if not target_path.exists():
        return False
    
    source_time = get_file_timestamp(source_path)
    target_time = get_file_timestamp(target_path)
    
    if source_time is None:
        return False
    
    return source_time > target_time


def ensure_dir_exists(dir_path: Path) -> None:
    """Asegura que un directorio existe, creándolo si es necesario."""
    dir_path.mkdir(parents=True, exist_ok=True)


