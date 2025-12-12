"""
Utility functions for images_app.
"""
from typing import Optional
from api.utils.model_imports import get_model_safely

Parametro = get_model_safely('catalogos.models.Parametro')
Tema = get_model_safely('catalogos.models.Tema')


def get_tipo_archivo_from_mime_type(mime_type: str) -> Optional[object]:
    """
    Get Parametro (TEMA_TIPO_ARCHIVO) from MIME type.
    
    Args:
        mime_type: MIME type string (e.g., 'image/jpeg')
    
    Returns:
        Parametro instance or None if not found
    """
    if not Parametro or not Tema:
        return None
    
    if not mime_type:
        mime_type = 'image/jpeg'
    
    mime_type = mime_type.strip().lower()
    
    # Map of MIME types to Parametro codigo
    mime_type_map = {
        'image/jpeg': 'IMAGE_JPEG',
        'image/jpg': 'IMAGE_JPG',
        'image/png': 'IMAGE_PNG',
        'image/webp': 'IMAGE_WEBP',
    }
    
    # Get TEMA_TIPO_ARCHIVO theme
    try:
        tema_tipo_archivo = Tema.objects.get(codigo='TEMA_TIPO_ARCHIVO')
    except Tema.DoesNotExist:
        return None
    
    # Try to find by codigo
    codigo = mime_type_map.get(mime_type)
    if codigo:
        try:
            return Parametro.objects.get(tema=tema_tipo_archivo, codigo=codigo, activo=True)
        except Parametro.DoesNotExist:
            pass
    
    # Try to find by metadata.mime_type field
    try:
        return Parametro.objects.filter(
            tema=tema_tipo_archivo,
            metadata__mime_type__iexact=mime_type,
            activo=True
        ).first()
    except Exception:
        pass
    
    # Default to JPEG
    try:
        return Parametro.objects.get(tema=tema_tipo_archivo, codigo='IMAGE_JPEG', activo=True)
    except Parametro.DoesNotExist:
        return None

