"""
Utility functions for images_app.
"""
import os
import tempfile
from pathlib import Path
from typing import Optional
from contextlib import contextmanager
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


@contextmanager
def get_local_image_path(image_field):
    """
    Get local file path for an image field, handling both local storage and S3.
    
    If the image is stored in S3, it will be downloaded to a temporary file.
    The temporary file will be automatically deleted when exiting the context.
    
    Args:
        image_field: Django ImageField instance
        
    Yields:
        str: Local file path to the image
        
    Example:
        with get_local_image_path(cacao_image.image) as image_path:
            # Use image_path for processing
            segment_and_crop_cacao_bean(image_path, method="yolo")
    """
    if not image_field:
        raise ValueError("Image field is required")
    
    # Check if using S3 storage
    use_s3 = os.environ.get('USE_S3', 'False').lower() == 'true'
    
    if use_s3:
        # Image is in S3, download to temporary file
        try:
            # Get the file from S3 storage
            with image_field.open('rb') as s3_file:
                # Create temporary file
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=Path(image_field.name).suffix
                )
                temp_path = temp_file.name
                
                # Copy content from S3 to temporary file
                temp_file.write(s3_file.read())
                temp_file.close()
                
                try:
                    yield temp_path
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
        except Exception:
            # If there's an error, try to clean up
            if 'temp_path' in locals() and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass
            raise
    else:
        # Image is local, use path directly
        try:
            image_path = image_field.path
            yield image_path
        except AttributeError:
            # If path doesn't exist, try to get from storage
            if hasattr(image_field, 'storage') and hasattr(image_field.storage, 'path'):
                image_path = image_field.storage.path(image_field.name)
                yield image_path
            else:
                raise ValueError(f"Cannot get local path for image: {image_field.name}")

