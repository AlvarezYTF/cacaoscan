"""
Utility functions for images_app.
"""
from typing import Optional
from api.utils.model_imports import get_model_safely

TipoArchivo = get_model_safely('catalogos.models.TipoArchivo')


def get_tipo_archivo_from_mime_type(mime_type: str) -> Optional[object]:
    """
    Get TipoArchivo from MIME type.
    
    Args:
        mime_type: MIME type string (e.g., 'image/jpeg')
    
    Returns:
        TipoArchivo instance or None if not found
    """
    if not TipoArchivo:
        return None
    
    if not mime_type:
        mime_type = 'image/jpeg'
    
    mime_type = mime_type.strip().lower()
    
    # Map of MIME types to TipoArchivo codigo
    mime_type_map = {
        'image/jpeg': 'IMAGE_JPEG',
        'image/jpg': 'IMAGE_JPG',
        'image/png': 'IMAGE_PNG',
        'image/webp': 'IMAGE_WEBP',
    }
    
    # Try to find by codigo
    codigo = mime_type_map.get(mime_type)
    if codigo:
        try:
            return TipoArchivo.objects.get(codigo=codigo, activo=True)
        except TipoArchivo.DoesNotExist:
            pass
    
    # Try to find by mime_type field
    try:
        return TipoArchivo.objects.filter(mime_type__iexact=mime_type, activo=True).first()
    except Exception:
        pass
    
    # Default to JPEG
    try:
        return TipoArchivo.objects.get(codigo='IMAGE_JPEG', activo=True)
    except TipoArchivo.DoesNotExist:
        return None

