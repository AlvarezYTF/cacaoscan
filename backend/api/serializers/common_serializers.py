"""
Common serializers for CacaoScan API.
Serializers used across multiple domains.
"""
from rest_framework import serializers
from ..utils.model_imports import get_models_safely

# Import models safely
models = get_models_safely({
    'Notification': 'notifications.models.Notification',
    'SystemSettings': 'core.models.SystemSettings'
})
Notification = models['Notification']
SystemSettings = models.get('SystemSettings')


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer for error responses."""
    error = serializers.CharField()
    status = serializers.CharField()


class DatasetStatsSerializer(serializers.Serializer):
    """Serializer for dataset statistics."""
    total_records = serializers.IntegerField()
    valid_records = serializers.IntegerField()
    missing_images = serializers.IntegerField()
    missing_ids = serializers.ListField(child=serializers.IntegerField())
    dimensions_stats = serializers.DictField()


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications with date formatting."""
    tiempo_transcurrido = serializers.ReadOnlyField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = (
            'id', 'tipo', 'tipo_display', 'titulo', 'mensaje', 
            'leida', 'fecha_creacion', 'fecha_lectura', 
            'datos_extra', 'tiempo_transcurrido', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'fecha_creacion', 'fecha_lectura', 'created_at', 'updated_at',
            'tiempo_transcurrido', 'tipo_display'
        )
    
    def validate_titulo(self, value):
        """Validate notification title."""
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("El título debe tener al menos 3 caracteres.")
        return value.strip()
    
    def validate_mensaje(self, value):
        """Validate notification message."""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("El mensaje debe tener al menos 10 caracteres.")
        return value.strip()


class NotificationListSerializer(serializers.ModelSerializer):
    """Optimized serializer for notification listings."""
    tiempo_transcurrido = serializers.ReadOnlyField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = (
            'id', 'tipo', 'tipo_display', 'titulo', 'mensaje', 'leida', 
            'fecha_creacion', 'tiempo_transcurrido'
        )


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications."""
    
    class Meta:
        model = Notification
        fields = ('user', 'tipo', 'titulo', 'mensaje', 'datos_extra')
    
    def validate_tipo(self, value):
        """Validate notification type."""
        valid_types = [choice[0] for choice in Notification.TIPO_CHOICES]
        if value not in valid_types:
            raise serializers.ValidationError(f"Tipo inválido. Opciones válidas: {', '.join(valid_types)}")
        return value


class NotificationStatsSerializer(serializers.Serializer):
    """Serializer for notification statistics."""
    total_notifications = serializers.IntegerField()
    unread_count = serializers.IntegerField()
    notifications_by_type = serializers.DictField()
    recent_notifications = serializers.ListField()


class SystemSettingsSerializer(serializers.ModelSerializer):
    """Serializer for system configuration."""
    logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = SystemSettings
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_logo_url(self, obj):
        """Get logo URL if available."""
        if hasattr(obj, 'logo') and obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None

