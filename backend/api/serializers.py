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
    
    def validate_username(self, value):
        """Validar username único y formato."""
        # Si el username es un email, usar el email como username
        if '@' in value:
            return value
        
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está en uso.")
        
        # Validar formato de username
        if len(value) < 3:
            raise serializers.ValidationError("El nombre de usuario debe tener al menos 3 caracteres.")
        
        if not value.replace('_', '').replace('-', '').isalnum():
            raise serializers.ValidationError("El nombre de usuario solo puede contener letras, números, guiones y guiones bajos.")
        
        return value
    
    def validate_email(self, value):
        """Validar email único y formato."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        
        # Validación básica de formato de email
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, value):
            raise serializers.ValidationError("Ingresa un email válido.")
        
        return value
    
    def validate_password(self, value):
        """Validar fortaleza de contraseña."""
        if len(value) < 8:
            raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        
        # Verificar que tenga al menos una letra mayúscula
        if not any(c.isupper() for c in value):
            raise serializers.ValidationError("La contraseña debe contener al menos una letra mayúscula.")
        
        # Verificar que tenga al menos una letra minúscula
        if not any(c.islower() for c in value):
            raise serializers.ValidationError("La contraseña debe contener al menos una letra minúscula.")
        
        # Verificar que tenga al menos un número
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError("La contraseña debe contener al menos un número.")
        
        return value
    
    def validate(self, attrs):
        """Validaciones generales."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        
        # Validar que first_name y last_name no estén vacíos
        if not attrs.get('first_name', '').strip():
            raise serializers.ValidationError("El nombre es requerido.")
        
        if not attrs.get('last_name', '').strip():
            raise serializers.ValidationError("El apellido es requerido.")
        
        # Si el username es diferente al email, usar el email como username
        if attrs.get('username') != attrs.get('email'):
            attrs['username'] = attrs['email']
        
        return attrs
    
    def create(self, validated_data):
        """Crear usuario con validaciones completas."""
        validated_data.pop('password_confirm')
        
        # Asegurar que el username sea igual al email
        validated_data['username'] = validated_data['email']
        
        # Crear usuario usando create_user para hash automático de contraseña
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            is_active=True  # Usuarios activos por defecto
        )
        
        return user


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer para verificación de email."""
    token = serializers.UUIDField()
    
    def validate_token(self, value):
        """Validar que el token existe y no ha expirado."""
        from .models import EmailVerificationToken
        
        token_obj = EmailVerificationToken.get_valid_token(value)
        if not token_obj:
            raise serializers.ValidationError("Token inválido o expirado.")
        
        if token_obj.is_verified:
            raise serializers.ValidationError("Este email ya ha sido verificado.")
        
        return value


class ResendVerificationSerializer(serializers.Serializer):
    """Serializer para reenvío de verificación de email."""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Validar que el email existe y no está verificado."""
        try:
            user = User.objects.get(email=value)
            if user.is_active and hasattr(user, 'email_verification_token'):
                if user.email_verification_token.is_verified:
                    raise serializers.ValidationError("Este email ya ha sido verificado.")
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("No existe una cuenta con este email.")


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
        """Obtener estado de verificación del email."""
        if hasattr(obj, 'email_verification_token'):
            return obj.email_verification_token.is_verified
        return obj.is_active  # Fallback para usuarios sin token de verificación
