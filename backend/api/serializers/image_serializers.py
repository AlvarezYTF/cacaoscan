"""
Image serializers for CacaoScan API.
"""
from rest_framework import serializers
from ..utils.model_imports import get_models_safely

# Import models safely
models = get_models_safely({
    'CacaoImage': 'images_app.models.CacaoImage',
    'CacaoPrediction': 'images_app.models.CacaoPrediction'
})
CacaoImage = models['CacaoImage']
CacaoPrediction = models['CacaoPrediction']


class ConfidenceSerializer(serializers.Serializer):
    """Serializer for model confidences."""
    alto = serializers.FloatField()
    ancho = serializers.FloatField()
    grosor = serializers.FloatField()
    peso = serializers.FloatField()


class DebugInfoSerializer(serializers.Serializer):
    """Serializer for debug information."""
    segmented = serializers.BooleanField()
    yolo_conf = serializers.FloatField()
    latency_ms = serializers.IntegerField()
    models_version = serializers.CharField()
    device = serializers.CharField(required=False)
    total_time_s = serializers.FloatField(required=False)


class ScanMeasureResponseSerializer(serializers.Serializer):
    """Serializer for measurement response."""
    alto_mm = serializers.FloatField(help_text="Altura del grano en milímetros")
    ancho_mm = serializers.FloatField(help_text="Ancho del grano en milímetros")
    grosor_mm = serializers.FloatField(help_text="Grosor del grano en milímetros")
    peso_g = serializers.FloatField(help_text="Peso del grano en gramos")
    confidences = ConfidenceSerializer(help_text="Niveles de confianza por target")
    crop_url = serializers.URLField(help_text="URL del recorte procesado")
    debug = DebugInfoSerializer(help_text="Información de debug del procesamiento")
    image_id = serializers.IntegerField(help_text="ID de la imagen guardada en BD", required=False, allow_null=True)
    prediction_id = serializers.IntegerField(help_text="ID de la predicción guardada en BD", required=False, allow_null=True)
    saved_to_database = serializers.BooleanField(help_text="Indica si los datos se guardaron correctamente en BD")


class CacaoImageSerializer(serializers.ModelSerializer):
    """Serializer for cacao images."""
    file_size_mb = serializers.ReadOnlyField()
    has_prediction = serializers.ReadOnlyField()
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    # Alias field for compatibility with tests
    filename = serializers.CharField(source='file_name', read_only=True)
    # Handle image.url for SimpleUploadedFile compatibility
    image_url = serializers.SerializerMethodField()
    # Return MIME type as string for compatibility
    file_type = serializers.SerializerMethodField()
    # Include prediction for history view using SerializerMethodField to avoid forward reference
    prediction = serializers.SerializerMethodField()
    # finca is a property, not a ForeignKey, so use SerializerMethodField
    finca = serializers.SerializerMethodField()
    
    class Meta:
        model = CacaoImage
        fields = (
            'id', 'user', 'user_name', 'image', 'image_url', 'uploaded_at', 'processed',
            'finca', 'lote', 'notas',
            'file_name', 'filename', 'file_size', 'file_size_mb', 'file_type',
            'created_at', 'updated_at', 'has_prediction', 'prediction'
        )
        read_only_fields = (
            'id', 'user', 'uploaded_at', 'processed', 'file_name', 'filename', 'file_size',
            'file_type', 'created_at', 'updated_at', 'file_size_mb', 'has_prediction', 'image_url', 'prediction', 'finca'
        )
    
    def get_finca(self, obj):
        """Get finca through lote property."""
        try:
            finca = obj.finca
            if finca:
                return finca.id
            return None
        except Exception:
            return None
    
    def get_prediction(self, obj):
        """Get prediction data if exists."""
        # Use try/except to safely access prediction
        # For OneToOne relationships, accessing the attribute directly raises
        # RelatedObjectDoesNotExist if the related object doesn't exist
        try:
            # Import here to avoid circular imports
            from django.core.exceptions import ObjectDoesNotExist
            
            try:
                pred = obj.prediction
            except ObjectDoesNotExist:
                # Related object doesn't exist, return None
                return None
            except AttributeError:
                # Attribute doesn't exist on the model
                return None
            except Exception as e:
                # Log unexpected exceptions but don't fail
                import logging
                logger = logging.getLogger("cacaoscan.api.serializers")
                logger.debug(f"Unexpected error accessing prediction for image {getattr(obj, 'id', 'unknown')}: {e}")
                return None
            
            if not pred:
                return None
            
            # Calculate average_confidence safely
            avg_conf = None
            try:
                # Try to get average_confidence property
                if hasattr(pred, 'average_confidence'):
                    try:
                        avg_conf_value = pred.average_confidence
                        if avg_conf_value is not None:
                            avg_conf = float(avg_conf_value)
                    except (AttributeError, TypeError, ValueError, Exception):
                        pass
                
                # If property didn't work, calculate manually
                if avg_conf is None:
                    confidences = []
                    try:
                        if hasattr(pred, 'confidence_alto') and pred.confidence_alto is not None:
                            confidences.append(float(pred.confidence_alto))
                    except (TypeError, ValueError):
                        pass
                    try:
                        if hasattr(pred, 'confidence_ancho') and pred.confidence_ancho is not None:
                            confidences.append(float(pred.confidence_ancho))
                    except (TypeError, ValueError):
                        pass
                    try:
                        if hasattr(pred, 'confidence_grosor') and pred.confidence_grosor is not None:
                            confidences.append(float(pred.confidence_grosor))
                    except (TypeError, ValueError):
                        pass
                    try:
                        if hasattr(pred, 'confidence_peso') and pred.confidence_peso is not None:
                            confidences.append(float(pred.confidence_peso))
                    except (TypeError, ValueError):
                        pass
                    
                    if confidences:
                        avg_conf = round(sum(confidences) / len(confidences), 3)
            except Exception:
                avg_conf = None
            
            # Safely extract all fields
            result = {}
            try:
                result['id'] = pred.id if hasattr(pred, 'id') else None
            except Exception:
                result['id'] = None
            
            for field in ['alto_mm', 'ancho_mm', 'grosor_mm', 'peso_g']:
                try:
                    value = getattr(pred, field, None)
                    result[field] = float(value) if value is not None else None
                except (TypeError, ValueError, AttributeError):
                    result[field] = None
            
            for field in ['confidence_alto', 'confidence_ancho', 'confidence_grosor', 'confidence_peso']:
                try:
                    value = getattr(pred, field, None)
                    result[field] = float(value) if value is not None else None
                except (TypeError, ValueError, AttributeError):
                    result[field] = None
            
            result['average_confidence'] = avg_conf
            
            try:
                result['processing_time_ms'] = getattr(pred, 'processing_time_ms', None)
            except Exception:
                result['processing_time_ms'] = None
            
            try:
                crop_url = getattr(pred, 'crop_url', None)
                result['crop_url'] = crop_url if crop_url else None
            except Exception:
                result['crop_url'] = None
            
            try:
                model_version = getattr(pred, 'model_version', None)
                if model_version:
                    try:
                        # If it's a ForeignKey, get the related object's value
                        if hasattr(model_version, 'codigo'):
                            result['model_version'] = str(model_version.codigo)
                        elif hasattr(model_version, 'valor'):
                            result['model_version'] = str(model_version.valor)
                        else:
                            result['model_version'] = str(model_version)
                    except Exception:
                        result['model_version'] = str(model_version) if model_version else None
                else:
                    result['model_version'] = None
            except Exception:
                result['model_version'] = None
            
            try:
                device_used = getattr(pred, 'device_used', None)
                if device_used:
                    try:
                        # If it's a ForeignKey, get the related object's value
                        if hasattr(device_used, 'codigo'):
                            result['device_used'] = str(device_used.codigo)
                        elif hasattr(device_used, 'valor'):
                            result['device_used'] = str(device_used.valor)
                        else:
                            result['device_used'] = str(device_used)
                    except Exception:
                        result['device_used'] = str(device_used) if device_used else None
                else:
                    result['device_used'] = None
            except Exception:
                result['device_used'] = None
            
            try:
                created_at = getattr(pred, 'created_at', None)
                result['created_at'] = created_at.isoformat() if created_at and hasattr(created_at, 'isoformat') else None
            except Exception:
                result['created_at'] = None
            
            return result
            
        except Exception as e:
            # Log error but don't fail the entire serialization
            import logging
            logger = logging.getLogger("cacaoscan.api.serializers")
            logger.warning(f"Error serializing prediction for image {getattr(obj, 'id', 'unknown')}: {e}", exc_info=True)
            return None
    
    def get_file_type(self, obj):
        """Return MIME type as string."""
        try:
            if obj.file_type:
                # file_type is a ForeignKey to Parametro
                # mime_type is stored in metadata JSONField
                if hasattr(obj.file_type, 'metadata') and obj.file_type.metadata:
                    mime_type = obj.file_type.metadata.get('mime_type')
                    if mime_type:
                        return mime_type
                # Fallback: try to get from codigo or nombre if metadata doesn't have mime_type
                # Some file types might have mime_type in codigo (e.g., 'image/jpeg')
                if hasattr(obj.file_type, 'codigo'):
                    codigo = obj.file_type.codigo
                    # If codigo looks like a mime type, return it
                    if '/' in str(codigo):
                        return str(codigo)
        except Exception:
            # If there's any error, return None
            pass
        return None
    
    def get_image_url(self, obj):
        """Get image URL, handling SimpleUploadedFile."""
        try:
            if obj.image:
                # Handle SimpleUploadedFile (used in tests)
                from django.core.files.uploadedfile import SimpleUploadedFile
                if isinstance(obj.image, SimpleUploadedFile):
                    # For SimpleUploadedFile, return the name
                    return obj.image.name if hasattr(obj.image, 'name') else None
                
                # Handle regular FileField
                if hasattr(obj.image, 'url'):
                    request = self.context.get('request')
                    if request:
                        return request.build_absolute_uri(obj.image.url)
                    return obj.image.url
        except Exception:
            # If there's any error getting the URL, return None
            pass
        return None
    
    # Removed validate_fecha_cosecha - fecha_cosecha is now obtained from lote.fecha_cosecha


class CacaoPredictionSerializer(serializers.ModelSerializer):
    """Serializer for cacao predictions."""
    average_confidence = serializers.ReadOnlyField()
    volume_cm3 = serializers.ReadOnlyField()
    density_g_cm3 = serializers.ReadOnlyField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CacaoPrediction
        fields = (
            'id', 'image', 'image_url', 'alto_mm', 'ancho_mm', 'grosor_mm', 'peso_g',
            'confidence_alto', 'confidence_ancho', 'confidence_grosor', 'confidence_peso',
            'average_confidence', 'processing_time_ms', 'crop_url',
            'model_version', 'device_used', 'volume_cm3', 'density_g_cm3',
            'created_at'
        )
        read_only_fields = (
            'id', 'image', 'processing_time_ms', 'model_version', 'device_used',
            'average_confidence', 'volume_cm3', 'density_g_cm3', 'created_at'
        )
    
    def get_image_url(self, obj):
        """Get image URL."""
        if obj.image and obj.image.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.image.url)
            return obj.image.image.url
        return None
    
    def validate_alto_mm(self, value):
        """Validate height."""
        if value <= 0 or value > 100:
            raise serializers.ValidationError("La altura debe estar entre 0 y 100 mm.")
        return value
    
    def validate_ancho_mm(self, value):
        """Validate width."""
        if value <= 0 or value > 100:
            raise serializers.ValidationError("El ancho debe estar entre 0 y 100 mm.")
        return value
    
    def validate_grosor_mm(self, value):
        """Validate thickness."""
        if value <= 0 or value > 50:
            raise serializers.ValidationError("El grosor debe estar entre 0 y 50 mm.")
        return value
    
    def validate_peso_g(self, value):
        """Validate weight."""
        if value <= 0 or value > 10:
            raise serializers.ValidationError("El peso debe estar entre 0 y 10 gramos.")
        return value


class CacaoImageDetailSerializer(CacaoImageSerializer):
    """Detailed serializer for images with prediction."""
    prediction = CacaoPredictionSerializer(read_only=True)
    
    class Meta(CacaoImageSerializer.Meta):
        fields = CacaoImageSerializer.Meta.fields + ('prediction',)


class ImagesListResponseSerializer(serializers.Serializer):
    """Serializer for image list response."""
    results = CacaoImageSerializer(many=True)
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)


class ImagesStatsResponseSerializer(serializers.Serializer):
    """Serializer for image statistics response."""
    total_images = serializers.IntegerField()
    processed_images = serializers.IntegerField()
    unprocessed_images = serializers.IntegerField()
    processed_today = serializers.IntegerField()
    processed_this_week = serializers.IntegerField()
    processed_this_month = serializers.IntegerField()
    average_confidence = serializers.FloatField()
    average_processing_time_ms = serializers.FloatField()
    region_stats = serializers.ListField()
    top_fincas = serializers.ListField()
    average_dimensions = serializers.DictField()

