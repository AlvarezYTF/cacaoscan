"""
Image processing service for CacaoScan.
Handles image validation, segmentation, and processing operations.
"""
import logging
import io
from typing import Dict, Any
from django.core.files.uploadedfile import UploadedFile
from PIL import Image

from api.services.base import BaseService, ServiceResult, ValidationServiceError

logger = logging.getLogger("cacaoscan.services.image.processing")


class ImageProcessingService(BaseService):
    """
    Service for handling image processing operations.
    
    Responsibilities:
    - Validating image files (type, size, dimensions)
    - Processing images (conversion, segmentation)
    - Image format validation
    """
    
    def __init__(self):
        super().__init__()
        self.allowed_image_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp']
        self.max_file_size = 20 * 1024 * 1024  # 20MB
        self.max_analysis_size = 8 * 1024 * 1024  # 8MB for analysis
    
    def validate_image_file(self, image_file: UploadedFile) -> ServiceResult:
        """
        Validates an image file (basic validation).
        
        Args:
            image_file: Uploaded image file
            
        Returns:
            ServiceResult with validation result
        """
        try:
            # Validate file type
            if image_file.content_type not in self.allowed_image_types:
                return ServiceResult.validation_error(
                    f"File type not allowed. Allowed types: {', '.join(self.allowed_image_types)}",
                    details={"field": "content_type", "allowed_types": self.allowed_image_types}
                )
            
            # Validate file size
            if image_file.size > self.max_file_size:
                return ServiceResult.validation_error(
                    f"File too large. Maximum {self.max_file_size // (1024*1024)}MB allowed",
                    details={"field": "file_size", "max_size": self.max_file_size, "actual_size": image_file.size}
                )
            
            # Validate that it's a valid image
            try:
                image_data = image_file.read()
                image_file.seek(0)  # Reset file position
                Image.open(io.BytesIO(image_data))
            except Exception as e:
                return ServiceResult.validation_error(
                    "Invalid or corrupted image file",
                    details={"field": "image_validity", "error": str(e)}
                )
            
            return ServiceResult.success(message="Image file is valid")
            
        except Exception as e:
            self.log_error(f"Error validating image: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Internal error validating image", details={"original_error": str(e)})
            )
    
    def validate_image_file_complete(self, image_file: UploadedFile) -> ServiceResult:
        """
        Validates an image file completely (type, size, dimensions).
        
        Args:
            image_file: Uploaded image file
            
        Returns:
            ServiceResult with validation result
        """
        try:
            # Validate file type
            if image_file.content_type not in self.allowed_image_types:
                return ServiceResult.validation_error(
                    f"File type not allowed. Allowed types: {', '.join(self.allowed_image_types)}",
                    details={"field": "content_type", "allowed_types": self.allowed_image_types}
                )
            
            # Validate file size (8MB maximum for analysis)
            if image_file.size > self.max_analysis_size:
                return ServiceResult.validation_error(
                    f"Image too large. Maximum allowed: 8MB",
                    details={"field": "file_size", "max_size": self.max_analysis_size, "actual_size": image_file.size}
                )
            
            # Validate filename
            filename = image_file.name
            if not filename or len(filename) > 255:
                return ServiceResult.validation_error(
                    "Invalid filename",
                    details={"field": "filename"}
                )
            
            # Validate that it's a valid image and get dimensions
            try:
                image_data = image_file.read()
                image_file.seek(0)  # Reset position
                image = Image.open(io.BytesIO(image_data))
                
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Validate minimum dimensions
                if image.width < 50 or image.height < 50:
                    return ServiceResult.validation_error(
                        "Image too small. Minimum: 50x50 pixels",
                        details={"field": "image_dimensions", "min_width": 50, "min_height": 50,
                                "actual_width": image.width, "actual_height": image.height}
                    )
                
            except Exception as e:
                return ServiceResult.validation_error(
                    f"Error processing image: {str(e)}",
                    details={"field": "image_validity", "error": str(e)}
                )
            
            return ServiceResult.success(message="Image file is valid")
            
        except Exception as e:
            self.log_error(f"Error validating image: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Internal error validating image", details={"original_error": str(e)})
            )
    
    def load_image(self, image_file: UploadedFile) -> ServiceResult:
        """
        Loads an image from an uploaded file.
        
        Args:
            image_file: Uploaded image file
            
        Returns:
            ServiceResult with PIL Image object
        """
        try:
            image_data = image_file.read()
            image_file.seek(0)  # Reset position
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            return ServiceResult.success(
                data=image,
                message="Image loaded successfully"
            )
            
        except Exception as e:
            self.log_error(f"Error loading image: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Internal error loading image", details={"original_error": str(e)})
            )
    
    def segment_image(self, image_path: str, method: str = "opencv") -> ServiceResult:
        """
        Segments a cacao bean from an image.
        
        Args:
            image_path: Path to the image file
            method: Segmentation method to use
            
        Returns:
            ServiceResult with path to segmented image
        """
        try:
            from pathlib import Path
            from ml.segmentation.processor import segment_and_crop_cacao_bean
            
            generated_path = segment_and_crop_cacao_bean(image_path, method=method)
            
            if generated_path:
                processed_path = Path(generated_path)
                self.log_info(f"Segmented PNG saved at: {processed_path.absolute()}")
                return ServiceResult.success(
                    data={'processed_png_path': processed_path},
                    message="Image segmented successfully"
                )
            else:
                self.log_warning(f"Could not segment image: empty return")
                return ServiceResult.error(
                    ValidationServiceError("Segmentation returned empty result")
                )
                
        except Exception as e:
            self.log_error(f"Error segmenting image: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Internal error segmenting image", details={"original_error": str(e)})
            )

