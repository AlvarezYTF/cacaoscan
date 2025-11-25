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
    
    class Meta:
        model = CacaoImage
        fields = (
            'id', 'user', 'user_name', 'image', 'uploaded_at', 'processed',
            'finca', 'region', 'lote_id', 'variedad', 'fecha_cosecha', 'notas',
            'file_name', 'file_size', 'file_size_mb', 'file_type',
            'created_at', 'updated_at', 'has_prediction'
        )
        read_only_fields = (
            'id', 'user', 'uploaded_at', 'processed', 'file_name', 'file_size',
            'file_type', 'created_at', 'updated_at', 'file_size_mb', 'has_prediction'
        )
    
    def validate_fecha_cosecha(self, value):
        """Validate harvest date."""
        if value and value.year < 1900:
            raise serializers.ValidationError("La fecha de cosecha debe ser posterior a 1900.")
        return value


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

