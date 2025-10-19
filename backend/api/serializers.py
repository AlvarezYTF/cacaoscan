"""
Serializers para la API de CacaoScan.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User


class ConfidenceSerializer(serializers.Serializer):
    """Serializer para confianzas de los modelos."""
    alto = serializers.FloatField()
    ancho = serializers.FloatField()
    grosor = serializers.FloatField()
    peso = serializers.FloatField()


class DebugInfoSerializer(serializers.Serializer):
    """Serializer para información de debug."""
    segmented = serializers.BooleanField()
    yolo_conf = serializers.FloatField()
    latency_ms = serializers.IntegerField()
    models_version = serializers.CharField()
    device = serializers.CharField(required=False)
    total_time_s = serializers.FloatField(required=False)


class ScanMeasureResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de medición."""
    alto_mm = serializers.FloatField(help_text="Altura del grano en milímetros")
    ancho_mm = serializers.FloatField(help_text="Ancho del grano en milímetros")
    grosor_mm = serializers.FloatField(help_text="Grosor del grano en milímetros")
    peso_g = serializers.FloatField(help_text="Peso del grano en gramos")
    confidences = ConfidenceSerializer(help_text="Niveles de confianza por target")
    crop_url = serializers.URLField(help_text="URL del recorte procesado")
    debug = DebugInfoSerializer(help_text="Información de debug del procesamiento")


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer para respuestas de error."""
    error = serializers.CharField()
    status = serializers.CharField()


class DatasetStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas del dataset."""
    total_records = serializers.IntegerField()
    valid_records = serializers.IntegerField()
    missing_images = serializers.IntegerField()
    missing_ids = serializers.ListField(child=serializers.IntegerField())
    dimensions_stats = serializers.DictField()


class ModelsStatusSerializer(serializers.Serializer):
    """Serializer para estado de modelos."""
    yolo_segmentation = serializers.CharField()
    regression_models = serializers.DictField()
    device = serializers.CharField(required=False)
    models_info = serializers.DictField(required=False)
    status = serializers.CharField()


class LoadModelsResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de carga de modelos."""
    message = serializers.CharField(required=False)
    error = serializers.CharField(required=False)
    status = serializers.CharField()


# Serializers de autenticación
class LoginSerializer(serializers.Serializer):
    """Serializer para login de usuario."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    attrs['user'] = user
                    return attrs
                else:
                    raise serializers.ValidationError('Usuario inactivo.')
            else:
                raise serializers.ValidationError('Credenciales inválidas.')
        else:
            raise serializers.ValidationError('Debe incluir username y password.')


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer para registro de usuario."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password_confirm')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer para información de usuario."""
    role = serializers.SerializerMethodField()
    is_verified = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'role', 'is_verified')
        read_only_fields = ('id', 'date_joined')
    
    def get_role(self, obj):
        """Determina el rol del usuario basado en permisos."""
        if obj.is_superuser or obj.is_staff:
            return 'admin'
        elif obj.groups.filter(name='analyst').exists():
            return 'analyst'
        else:
            return 'farmer'
    
    def get_is_verified(self, obj):
        """Determina si el usuario está verificado."""
        return obj.is_active
