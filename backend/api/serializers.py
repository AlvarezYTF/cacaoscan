"""
Serializers para la API de CacaoScan.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
# Importar modelos desde apps modulares
try:
    from auth_app.models import UserProfile
except ImportError:
    UserProfile = None

try:
    from images_app.models import CacaoImage, CacaoPrediction
except ImportError:
    CacaoImage = None
    CacaoPrediction = None

try:
    from training.models import TrainingJob
except ImportError:
    TrainingJob = None

try:
    from fincas_app.models import Finca, Lote
except ImportError:
    Finca = None
    Lote = None

try:
    from notifications.models import Notification
except ImportError:
    Notification = None

# Modelos Ãºnicos de API
from .models import ModelMetrics, SystemSettings


class ConfidenceSerializer(serializers.Serializer):
    """Serializer para confianzas de los modelos."""
    alto = serializers.FloatField()
    ancho = serializers.FloatField()
    grosor = serializers.FloatField()
    peso = serializers.FloatField()


class DebugInfoSerializer(serializers.Serializer):
    """Serializer para informaciÃ³n de debug."""
    segmented = serializers.BooleanField()
    yolo_conf = serializers.FloatField()
    latency_ms = serializers.IntegerField()
    models_version = serializers.CharField()
    device = serializers.CharField(required=False)
    total_time_s = serializers.FloatField(required=False)


class ScanMeasureResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de mediciÃ³n."""
    alto_mm = serializers.FloatField(help_text="Altura del grano en milÃ­metros")
    ancho_mm = serializers.FloatField(help_text="Ancho del grano en milÃ­metros")
    grosor_mm = serializers.FloatField(help_text="Grosor del grano en milÃ­metros")
    peso_g = serializers.FloatField(help_text="Peso del grano en gramos")
    confidences = ConfidenceSerializer(help_text="Niveles de confianza por target")
    crop_url = serializers.URLField(help_text="URL del recorte procesado")
    debug = DebugInfoSerializer(help_text="InformaciÃ³n de debug del procesamiento")
    image_id = serializers.IntegerField(help_text="ID de la imagen guardada en BD", required=False, allow_null=True)
    prediction_id = serializers.IntegerField(help_text="ID de la predicciÃ³n guardada en BD", required=False, allow_null=True)
    saved_to_database = serializers.BooleanField(help_text="Indica si los datos se guardaron correctamente en BD")


class ErrorResponseSerializer(serializers.Serializer):
    """Serializer para respuestas de error."""
    error = serializers.CharField()
    status = serializers.CharField()


class DatasetStatsSerializer(serializers.Serializer):
    """Serializer para estadÃ­sticas del dataset."""
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


# Serializers de autenticaciÃ³n
class LoginSerializer(serializers.Serializer):
    """Serializer para login de usuario."""
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')
        
        # Si viene email, usarlo como username
        if email and not username:
            username = email
            attrs['username'] = email
        
        # Validar que al menos uno estÃ© presente
        if not username and not email:
            raise serializers.ValidationError('Debe incluir username o email.')
        
        if username and password:
            # Intentar autenticar con username
            user = authenticate(username=username, password=password)
            
            # Si no funciona, intentar con email
            if not user and email:
                try:
                    # Usar .first() en lugar de .get() para evitar error si hay mÃºltiples usuarios
                    user_obj = User.objects.filter(email=email).first()
                    if user_obj:
                        user = authenticate(username=user_obj.username, password=password)
                    else:
                        user = None
                except Exception:
                    user = None
            
            if user:
                if not user.is_active:
                    # Verificar si tiene token de verificaciÃ³n pendiente
                    if hasattr(user, 'auth_email_token') and not user.auth_email_token.is_verified:
                        raise serializers.ValidationError(
                            'Tu cuenta no estÃ¡ verificada. Por favor verifica tu correo electrÃ³nico antes de iniciar sesiÃ³n. '
                            'Si no recibiste el correo, puedes solicitar uno nuevo desde la pÃ¡gina de registro.'
                        )
                    else:
                        raise serializers.ValidationError('Usuario inactivo.')
                attrs['user'] = user
                return attrs
            else:
                raise serializers.ValidationError('Credenciales invÃ¡lidas.')
        else:
            raise serializers.ValidationError('Debe incluir username/email y password.')


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer para registro de usuario."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password_confirm')
    
    def validate_username(self, value):
        """Validar username Ãºnico y formato."""
        # Si el username es un email, usar el email como username
        if '@' in value:
            return value
        
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya estÃ¡ en uso.")
        
        # Validar formato de username
        if len(value) < 3:
            raise serializers.ValidationError("El nombre de usuario debe tener al menos 3 caracteres.")
        
        if not value.replace('_', '').replace('-', '').isalnum():
            raise serializers.ValidationError("El nombre de usuario solo puede contener letras, nÃºmeros, guiones y guiones bajos.")
        
        return value
    
    def validate_email(self, value):
        """Validar email Ãºnico y formato."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya estÃ¡ registrado.")
        
        # ValidaciÃ³n bÃ¡sica de formato de email
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, value):
            raise serializers.ValidationError("Ingresa un email vÃ¡lido.")
        
        return value
    
    def validate_password(self, value):
        """Validar fortaleza de contraseÃ±a."""
        if len(value) < 8:
            raise serializers.ValidationError("La contraseÃ±a debe tener al menos 8 caracteres.")
        
        # Verificar que tenga al menos una letra mayÃºscula
        if not any(c.isupper() for c in value):
            raise serializers.ValidationError("La contraseÃ±a debe contener al menos una letra mayÃºscula.")
        
        # Verificar que tenga al menos una letra minÃºscula
        if not any(c.islower() for c in value):
            raise serializers.ValidationError("La contraseÃ±a debe contener al menos una letra minÃºscula.")
        
        # Verificar que tenga al menos un nÃºmero
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError("La contraseÃ±a debe contener al menos un nÃºmero.")
        
        return value
    
    def validate(self, attrs):
        """Validaciones generales."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Las contraseÃ±as no coinciden.")
        
        # Validar que first_name y last_name no estÃ©n vacÃ­os
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
        
        # Crear usuario usando create_user para hash automÃ¡tico de contraseÃ±a
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            is_active=False  # Usuario inactivo hasta verificar el email
        )
        
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para cambio de contraseÃ±a de usuario autenticado.
    """
    old_password = serializers.CharField(
        write_only=True,
        required=True,
        label="ContraseÃ±a actual"
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        label="Nueva contraseÃ±a"
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        label="Confirmar nueva contraseÃ±a"
    )
    
    def validate_old_password(self, value):
        """Validar que se proporcione la contraseÃ±a actual."""
        if not value:
            raise serializers.ValidationError("La contraseÃ±a actual es requerida.")
        return value
    
    def validate_new_password(self, value):
        """
        Validar que la nueva contraseÃ±a cumpla con los requisitos de seguridad:
        - MÃ­nimo 8 caracteres
        - Al menos una letra mayÃºscula
        - Al menos una letra minÃºscula
        - Al menos un nÃºmero
        """
        import re
        
        if len(value) < 8:
            raise serializers.ValidationError("La contraseÃ±a debe tener al menos 8 caracteres.")
        
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("La contraseÃ±a debe contener al menos una letra mayÃºscula.")
        
        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError("La contraseÃ±a debe contener al menos una letra minÃºscula.")
        
        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError("La contraseÃ±a debe contener al menos un nÃºmero.")
        
        return value
    
    def validate(self, attrs):
        """Validaciones generales."""
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        
        # Validar que las contraseÃ±as nuevas coincidan
        if new_password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': 'Las contraseÃ±as nuevas no coinciden.'
            })
        
        # Validar que la nueva contraseÃ±a sea diferente a la actual
        if old_password == new_password:
            raise serializers.ValidationError({
                'new_password': 'La nueva contraseÃ±a debe ser diferente a la contraseÃ±a actual.'
            })
        
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer para verificaciÃ³n de email."""
    token = serializers.UUIDField()
    
    def validate_token(self, value):
        """Validar que el token existe y no ha expirado."""
        from .models import EmailVerificationToken
        
        token_obj = EmailVerificationToken.get_valid_token(value)
        if not token_obj:
            raise serializers.ValidationError("Token invÃ¡lido o expirado.")
        
        if token_obj.is_verified:
            raise serializers.ValidationError("Este email ya ha sido verificado.")
        
        return value


class ResendVerificationSerializer(serializers.Serializer):
    """Serializer para reenvÃ­o de verificaciÃ³n de email."""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Validar que el email existe y no estÃ¡ verificado."""
        try:
            user = User.objects.get(email=value)
            if user.is_active and hasattr(user, 'auth_email_token'):
                if user.auth_email_token.is_verified:
                    raise serializers.ValidationError("Este email ya ha sido verificado.")
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("No existe una cuenta con este email.")


class UserSerializer(serializers.ModelSerializer):
    """Serializer para informaciÃ³n de usuario."""
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
        """Obtener estado de verificaciÃ³n del email."""
        try:
            if hasattr(obj, 'email_verification_token'):
                return obj.email_verification_token.is_verified
        except Exception:
            pass
        return obj.is_active  # Fallback para usuarios sin token de verificaciÃ³n


# Serializers para los nuevos modelos
class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para perfil extendido de usuario."""
    full_name = serializers.ReadOnlyField()
    role = serializers.ReadOnlyField()
    is_verified = serializers.ReadOnlyField()
    
    class Meta:
        model = UserProfile
        fields = (
            'phone_number', 'region', 'municipality', 'farm_name',
            'years_experience', 'farm_size_hectares', 'preferred_language',
            'email_notifications', 'created_at', 'updated_at',
            'full_name', 'role', 'is_verified'
        )
        read_only_fields = ('created_at', 'updated_at', 'full_name', 'role', 'is_verified')
    
    def validate_years_experience(self, value):
        """Validar aÃ±os de experiencia."""
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("Los aÃ±os de experiencia deben estar entre 0 y 100.")
        return value
    
    def validate_farm_size_hectares(self, value):
        """Validar tamaÃ±o de finca."""
        if value is not None and (value < 0 or value > 10000):
            raise serializers.ValidationError("El tamaÃ±o de la finca debe estar entre 0 y 10,000 hectÃ¡reas.")
        return value


class CacaoImageSerializer(serializers.ModelSerializer):
    """Serializer para imÃ¡genes de cacao."""
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
        """Validar fecha de cosecha."""
        if value and value.year < 1900:
            raise serializers.ValidationError("La fecha de cosecha debe ser posterior a 1900.")
        return value


class CacaoPredictionSerializer(serializers.ModelSerializer):
    """Serializer para predicciones de cacao."""
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
        """Obtener URL de la imagen."""
        if obj.image and obj.image.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.image.url)
            return obj.image.image.url
        return None
    
    def validate_alto_mm(self, value):
        """Validar altura."""
        if value <= 0 or value > 100:
            raise serializers.ValidationError("La altura debe estar entre 0 y 100 mm.")
        return value
    
    def validate_ancho_mm(self, value):
        """Validar ancho."""
        if value <= 0 or value > 100:
            raise serializers.ValidationError("El ancho debe estar entre 0 y 100 mm.")
        return value
    
    def validate_grosor_mm(self, value):
        """Validar grosor."""
        if value <= 0 or value > 50:
            raise serializers.ValidationError("El grosor debe estar entre 0 y 50 mm.")
        return value
    
    def validate_peso_g(self, value):
        """Validar peso."""
        if value <= 0 or value > 10:
            raise serializers.ValidationError("El peso debe estar entre 0 y 10 gramos.")
        return value


class CacaoImageDetailSerializer(CacaoImageSerializer):
    """Serializer detallado para imÃ¡genes con predicciÃ³n."""
    prediction = CacaoPredictionSerializer(read_only=True)
    
    class Meta(CacaoImageSerializer.Meta):
        fields = CacaoImageSerializer.Meta.fields + ('prediction',)


class ImagesListResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de lista de imÃ¡genes."""
    results = CacaoImageSerializer(many=True)
    count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)


class ImagesStatsResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de estadÃ­sticas de imÃ¡genes."""
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


class TrainingJobSerializer(serializers.ModelSerializer):
    """Serializer para trabajos de entrenamiento."""
    duration_formatted = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = TrainingJob
        fields = (
            'id', 'job_id', 'job_type', 'status', 'created_by', 'created_by_username',
            'model_name', 'dataset_size', 'epochs', 'batch_size', 'learning_rate',
            'config_params', 'metrics', 'model_path', 'logs', 'created_at',
            'started_at', 'completed_at', 'error_message', 'progress_percentage',
            'duration_formatted', 'is_active'
        )
        read_only_fields = (
            'id', 'job_id', 'created_by', 'created_at', 'started_at', 'completed_at',
            'duration_formatted', 'is_active'
        )
    
    def validate_epochs(self, value):
        if value <= 0 or value > 1000:
            raise serializers.ValidationError("Los epochs deben estar entre 1 y 1000.")
        return value
    
    def validate_batch_size(self, value):
        if value <= 0 or value > 128:
            raise serializers.ValidationError("El batch size debe estar entre 1 y 128.")
        return value
    
    def validate_learning_rate(self, value):
        if value <= 0 or value > 1.0:
            raise serializers.ValidationError("El learning rate debe estar entre 0 y 1.0.")
        return value
    
    def validate_dataset_size(self, value):
        if value <= 0:
            raise serializers.ValidationError("El tamaÃ±o del dataset debe ser mayor a 0.")
        return value


class TrainingJobCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear trabajos de entrenamiento."""
    
    class Meta:
        model = TrainingJob
        fields = (
            'job_type', 'model_name', 'dataset_size', 'epochs', 'batch_size',
            'learning_rate', 'config_params'
        )
    
    def validate_job_type(self, value):
        valid_types = ['regression', 'vision', 'incremental']
        if value not in valid_types:
            raise serializers.ValidationError(f"Tipo de trabajo invÃ¡lido. Use: {', '.join(valid_types)}")
        return value
    
    def validate_model_name(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("El nombre del modelo no puede estar vacÃ­o.")
        return value.strip()


class TrainingJobStatusSerializer(serializers.ModelSerializer):
    """Serializer simplificado para estado de trabajos."""
    duration_formatted = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = TrainingJob
        fields = (
            'id', 'job_id', 'job_type', 'status', 'created_by_username',
            'model_name', 'progress_percentage', 'created_at', 'started_at',
            'completed_at', 'duration_formatted', 'is_active'
        )


# Serializers para gestiÃ³n de fincas
class FincaSerializer(serializers.ModelSerializer):
    """Serializer para fincas con validaciones completas."""
    agricultor_name = serializers.CharField(source='agricultor.get_full_name', read_only=True)
    agricultor_email = serializers.CharField(source='agricultor.email', read_only=True)
    ubicacion_completa = serializers.ReadOnlyField()
    estadisticas = serializers.SerializerMethodField()
    
    class Meta:
        model = Finca
        fields = (
            'id', 'nombre', 'ubicacion', 'municipio', 'departamento', 
            'hectareas', 'agricultor', 'agricultor_name', 'agricultor_email',
            'descripcion', 'coordenadas_lat', 'coordenadas_lng', 
            'fecha_registro', 'activa', 'ubicacion_completa', 'estadisticas',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'fecha_registro', 'created_at', 'updated_at', 
            'ubicacion_completa', 'estadisticas', 'agricultor'
        )
    
    def get_estadisticas(self, obj):
        """Obtener estadÃ­sticas de la finca."""
        try:
            return obj.get_estadisticas()
        except Exception:
            # Retornar estadÃ­sticas vacÃ­as si hay error
            return {
                'total_lotes': 0,
                'lotes_activos': 0,
                'total_analisis': 0,
                'calidad_promedio': 0.0,
                'hectareas': float(obj.hectareas) if obj.hectareas else 0.0,
                'fecha_registro': obj.fecha_registro.strftime('%d/%m/%Y') if obj.fecha_registro else '',
                'activa': obj.activa if hasattr(obj, 'activa') else True
            }
    
    def validate_nombre(self, value):
        """Validar nombre de finca."""
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("El nombre de la finca debe tener al menos 3 caracteres.")
        
        # Verificar unicidad por agricultor
        agricultor = self.context.get('request').user if self.context.get('request') else None
        if agricultor and self.instance:
            # ActualizaciÃ³n: excluir la instancia actual
            if Finca.objects.filter(
                agricultor=agricultor, 
                nombre__iexact=value.strip()
            ).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Ya tienes una finca con este nombre.")
        elif agricultor:
            # CreaciÃ³n: verificar unicidad
            if Finca.objects.filter(
                agricultor=agricultor, 
                nombre__iexact=value.strip()
            ).exists():
                raise serializers.ValidationError("Ya tienes una finca con este nombre.")
        
        return value.strip()
    
    def validate_hectareas(self, value):
        """Validar hectÃ¡reas."""
        if value <= 0:
            raise serializers.ValidationError("Las hectÃ¡reas deben ser mayores a 0.")
        if value > 10000:
            raise serializers.ValidationError("Las hectÃ¡reas no pueden ser mayores a 10,000.")
        return value
    
    def validate_coordenadas_lat(self, value):
        """Validar latitud GPS."""
        if value is not None:
            if value < -90 or value > 90:
                raise serializers.ValidationError("La latitud debe estar entre -90 y 90 grados.")
        return value
    
    def validate_coordenadas_lng(self, value):
        """Validar longitud GPS."""
        if value is not None:
            if value < -180 or value > 180:
                raise serializers.ValidationError("La longitud debe estar entre -180 y 180 grados.")
        return value
    
    def validate(self, attrs):
        """Validaciones generales."""
        # Validar que municipio y departamento no estÃ©n vacÃ­os
        if not attrs.get('municipio', '').strip():
            raise serializers.ValidationError("El municipio es requerido.")
        
        if not attrs.get('departamento', '').strip():
            raise serializers.ValidationError("El departamento es requerido.")
        
        # Validar que si se proporcionan coordenadas, ambas estÃ©n presentes
        lat = attrs.get('coordenadas_lat')
        lng = attrs.get('coordenadas_lng')
        
        if (lat is not None and lng is None) or (lat is None and lng is not None):
            raise serializers.ValidationError("Debe proporcionar tanto latitud como longitud, o ninguna.")
        
        return attrs


class FincaListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listados de fincas (sin estadÃ­sticas pesadas)."""
    ubicacion_completa = serializers.SerializerMethodField()
    
    class Meta:
        model = Finca
        fields = (
            'id', 'nombre', 'municipio', 'departamento', 'ubicacion', 
            'ubicacion_completa', 'hectareas', 'activa', 'fecha_registro', 'agricultor_id',
            'coordenadas_lat', 'coordenadas_lng'
        )
    
    def get_ubicacion_completa(self, obj):
        """Obtener ubicaciÃ³n completa."""
        return f"{obj.municipio}, {obj.departamento}"


class FincaDetailSerializer(FincaSerializer):
    """Serializer detallado para fincas con datos relacionados."""
    lotes = serializers.SerializerMethodField()
    
    class Meta(FincaSerializer.Meta):
        fields = FincaSerializer.Meta.fields + ('lotes',)
    
    def get_lotes(self, obj):
        """Obtener lotes de la finca."""
        # ImportaciÃ³n diferida para evitar circular imports
        try:
            # LoteSerializer se define después en el mismo archivo
            # Importamos directamente el nombre de la clase usando forward reference
            from fincas_app.models import Lote
            lotes = obj.lotes.all()[:10]  # Limitar a 10 lotes para evitar sobrecarga
            
            # Serializar manualmente para evitar dependencias circulares
            lotes_data = []
            for lote in lotes:
                lotes_data.append({
                    'id': lote.id,
                    'identificador': lote.identificador,
                    'variedad': lote.variedad,
                    'estado': lote.estado,
                    'activo': lote.activo,
                    'fecha_plantacion': lote.fecha_plantacion.isoformat() if lote.fecha_plantacion else None,
                    'area_hectareas': float(lote.area_hectareas) if lote.area_hectareas else None,
                })
            return lotes_data
        except Exception as e:
            # Si hay algún error, retornar lista vacía en lugar de fallar
            import logging
            logger = logging.getLogger("cacaoscan.api")
            logger.warning(f"Error serializando lotes de finca {obj.id}: {e}")
            return []


class FincaStatsSerializer(serializers.Serializer):
    """Serializer para estadÃ­sticas de fincas."""
    total_fincas = serializers.IntegerField()
    fincas_activas = serializers.IntegerField()
    total_hectareas = serializers.DecimalField(max_digits=12, decimal_places=2)
    promedio_hectareas = serializers.DecimalField(max_digits=10, decimal_places=2)
    fincas_por_departamento = serializers.ListField()
    fincas_por_municipio = serializers.ListField()
    calidad_promedio_general = serializers.FloatField()


# Serializers para gestiÃ³n de lotes
class LoteSerializer(serializers.ModelSerializer):
    """Serializer para lotes con validaciones completas."""
    finca_nombre = serializers.CharField(source='finca.nombre', read_only=True)
    finca_ubicacion = serializers.CharField(source='finca.ubicacion_completa', read_only=True)
    agricultor_nombre = serializers.CharField(source='finca.agricultor.get_full_name', read_only=True)
    ubicacion_completa = serializers.ReadOnlyField()
    estadisticas = serializers.SerializerMethodField()
    edad_meses = serializers.ReadOnlyField()
    
    class Meta:
        model = Lote
        fields = (
            'id', 'finca', 'finca_nombre', 'finca_ubicacion', 'agricultor_nombre',
            'identificador', 'variedad', 'fecha_plantacion', 'fecha_cosecha',
            'area_hectareas', 'estado', 'descripcion', 'coordenadas_lat', 
            'coordenadas_lng', 'fecha_registro', 'activo', 'ubicacion_completa',
            'estadisticas', 'edad_meses', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'fecha_registro', 'created_at', 'updated_at', 
            'ubicacion_completa', 'estadisticas', 'edad_meses'
        )
    
    def get_estadisticas(self, obj):
        """Obtener estadÃ­sticas del lote."""
        return obj.get_estadisticas()
    
    def validate_identificador(self, value):
        """Validar identificador de lote."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("El identificador del lote debe tener al menos 2 caracteres.")
        
        # Verificar unicidad por finca
        finca = self.context.get('finca')
        if finca and self.instance:
            # ActualizaciÃ³n: excluir la instancia actual
            if Lote.objects.filter(
                finca=finca, 
                identificador__iexact=value.strip()
            ).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Ya existe un lote con este identificador en la finca.")
        elif finca:
            # CreaciÃ³n: verificar unicidad
            if Lote.objects.filter(
                finca=finca, 
                identificador__iexact=value.strip()
            ).exists():
                raise serializers.ValidationError("Ya existe un lote con este identificador en la finca.")
        
        return value.strip()
    
    def validate_area_hectareas(self, value):
        """Validar Ã¡rea en hectÃ¡reas."""
        if value <= 0:
            raise serializers.ValidationError("El Ã¡rea debe ser mayor a 0.")
        if value > 1000:
            raise serializers.ValidationError("El Ã¡rea no puede ser mayor a 1,000 hectÃ¡reas.")
        return value
    
    def validate_fecha_cosecha(self, value):
        """Validar fecha de cosecha."""
        fecha_plantacion = self.initial_data.get('fecha_plantacion')
        if value and fecha_plantacion and value < fecha_plantacion:
            raise serializers.ValidationError("La fecha de cosecha no puede ser anterior a la fecha de plantaciÃ³n.")
        return value
    
    def validate_coordenadas_lat(self, value):
        """Validar latitud GPS."""
        if value is not None:
            if value < -90 or value > 90:
                raise serializers.ValidationError("La latitud debe estar entre -90 y 90 grados.")
        return value
    
    def validate_coordenadas_lng(self, value):
        """Validar longitud GPS."""
        if value is not None:
            if value < -180 or value > 180:
                raise serializers.ValidationError("La longitud debe estar entre -180 y 180 grados.")
        return value
    
    def validate(self, attrs):
        """Validaciones generales."""
        # Validar que variedad no estÃ© vacÃ­a
        if not attrs.get('variedad', '').strip():
            raise serializers.ValidationError("La variedad es requerida.")
        
        # Validar que si se proporcionan coordenadas, ambas estÃ©n presentes
        lat = attrs.get('coordenadas_lat')
        lng = attrs.get('coordenadas_lng')
        
        if (lat is not None and lng is None) or (lat is None and lng is not None):
            raise serializers.ValidationError("Debe proporcionar tanto latitud como longitud, o ninguna.")
        
        return attrs


class LoteListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listados de lotes."""
    finca_nombre = serializers.CharField(source='finca.nombre', read_only=True)
    agricultor_nombre = serializers.CharField(source='finca.agricultor.get_full_name', read_only=True)
    ubicacion_completa = serializers.ReadOnlyField()
    total_analisis = serializers.ReadOnlyField()
    analisis_procesados = serializers.ReadOnlyField()
    edad_meses = serializers.ReadOnlyField()
    
    class Meta:
        model = Lote
        fields = (
            'id', 'identificador', 'variedad', 'finca_nombre', 'agricultor_nombre',
            'area_hectareas', 'estado', 'total_analisis', 'analisis_procesados',
            'edad_meses', 'activo', 'fecha_plantacion', 'fecha_cosecha'
        )


class LoteDetailSerializer(LoteSerializer):
    """Serializer detallado para lotes con datos relacionados."""
    cacao_images = serializers.SerializerMethodField()
    
    class Meta(LoteSerializer.Meta):
        fields = LoteSerializer.Meta.fields + ('cacao_images',)
    
    def get_cacao_images(self, obj):
        """Obtener imÃ¡genes de cacao del lote."""
        from .serializers import CacaoImageSerializer
        return CacaoImageSerializer(obj.cacao_images.all()[:10], many=True).data


class LoteStatsSerializer(serializers.Serializer):
    """Serializer para estadÃ­sticas de lotes."""
    total_lotes = serializers.IntegerField()
    lotes_activos = serializers.IntegerField()
    lotes_por_estado = serializers.DictField()
    total_area_hectareas = serializers.DecimalField(max_digits=12, decimal_places=2)
    promedio_area_hectareas = serializers.DecimalField(max_digits=10, decimal_places=2)
    variedades_mas_comunes = serializers.ListField()
    calidad_promedio_general = serializers.FloatField()


# Serializers para gestiÃ³n de notificaciones
class NotificationSerializer(serializers.ModelSerializer):
    """Serializer para notificaciones con formateo de fechas."""
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
        """Validar tÃ­tulo de notificaciÃ³n."""
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("El tÃ­tulo debe tener al menos 3 caracteres.")
        return value.strip()
    
    def validate_mensaje(self, value):
        """Validar mensaje de notificaciÃ³n."""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("El mensaje debe tener al menos 10 caracteres.")
        return value.strip()


class NotificationListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listados de notificaciones."""
    tiempo_transcurrido = serializers.ReadOnlyField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = (
            'id', 'tipo', 'tipo_display', 'titulo', 'mensaje', 'leida', 
            'fecha_creacion', 'tiempo_transcurrido'
        )


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear notificaciones."""
    
    class Meta:
        model = Notification
        fields = ('user', 'tipo', 'titulo', 'mensaje', 'datos_extra')
    
    def validate_tipo(self, value):
        """Validar tipo de notificaciÃ³n."""
        valid_types = [choice[0] for choice in Notification.TIPO_CHOICES]
        if value not in valid_types:
            raise serializers.ValidationError(f"Tipo invÃ¡lido. Opciones vÃ¡lidas: {', '.join(valid_types)}")
        return value


class NotificationStatsSerializer(serializers.Serializer):
    """Serializer para estadÃ­sticas de notificaciones."""
    total_notifications = serializers.IntegerField()
    unread_count = serializers.IntegerField()
    notifications_by_type = serializers.DictField()
    recent_notifications = serializers.ListField()


class ModelMetricsSerializer(serializers.ModelSerializer):
    """Serializer para mÃ©tricas de modelos."""
    accuracy_percentage = serializers.ReadOnlyField()
    training_time_formatted = serializers.ReadOnlyField()
    performance_summary = serializers.ReadOnlyField()
    dataset_summary = serializers.ReadOnlyField()
    model_summary = serializers.ReadOnlyField()
    comparison_with_previous = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = ModelMetrics
        fields = [
            'id', 'model_name', 'model_type', 'target', 'version',
            'training_job', 'created_by', 'created_by_username',
            'metric_type', 'mae', 'mse', 'rmse', 'r2_score', 'mape',
            'additional_metrics', 'dataset_size', 'train_size',
            'validation_size', 'test_size', 'epochs', 'batch_size',
            'learning_rate', 'model_params', 'training_time_seconds',
            'inference_time_ms', 'stability_score', 'knowledge_retention',
            'notes', 'is_best_model', 'is_production_model',
            'created_at', 'updated_at',
            # Campos calculados
            'accuracy_percentage', 'training_time_formatted',
            'performance_summary', 'dataset_summary', 'model_summary',
            'comparison_with_previous'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_comparison_with_previous(self, obj):
        """Obtener comparaciÃ³n con versiÃ³n anterior."""
        return obj.get_comparison_with_previous()


class ModelMetricsListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de mÃ©tricas de modelos."""
    accuracy_percentage = serializers.ReadOnlyField()
    training_time_formatted = serializers.ReadOnlyField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = ModelMetrics
        fields = [
            'id', 'model_name', 'model_type', 'target', 'version',
            'metric_type', 'mae', 'rmse', 'r2_score', 'accuracy_percentage',
            'training_time_formatted', 'is_best_model', 'is_production_model',
            'created_by_username', 'created_at'
        ]


class ModelMetricsCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear mÃ©tricas de modelos."""
    
    class Meta:
        model = ModelMetrics
        fields = [
            'model_name', 'model_type', 'target', 'version',
            'training_job', 'metric_type', 'mae', 'mse', 'rmse',
            'r2_score', 'mape', 'additional_metrics', 'dataset_size',
            'train_size', 'validation_size', 'test_size', 'epochs',
            'batch_size', 'learning_rate', 'model_params',
            'training_time_seconds', 'inference_time_ms',
            'stability_score', 'knowledge_retention', 'notes',
            'is_best_model', 'is_production_model'
        ]
    
    def validate(self, data):
        """Validar datos del serializer."""
        # Validar que el dataset_size sea igual a la suma de train, validation y test
        dataset_size = data.get('dataset_size', 0)
        train_size = data.get('train_size', 0)
        validation_size = data.get('validation_size', 0)
        test_size = data.get('test_size', 0)
        
        if dataset_size != (train_size + validation_size + test_size):
            raise serializers.ValidationError(
                "El tamaÃ±o del dataset debe ser igual a la suma de train_size + validation_size + test_size"
            )
        
        # Validar mÃ©tricas principales
        if data.get('r2_score', 0) < 0 or data.get('r2_score', 0) > 1:
            raise serializers.ValidationError("RÂ² score debe estar entre 0 y 1")
        
        if data.get('mae', 0) < 0:
            raise serializers.ValidationError("MAE debe ser mayor o igual a 0")
        
        if data.get('rmse', 0) < 0:
            raise serializers.ValidationError("RMSE debe ser mayor o igual a 0")
        
        return data


class ModelMetricsUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar mÃ©tricas de modelos."""
    
    class Meta:
        model = ModelMetrics
        fields = [
            'mae', 'mse', 'rmse', 'r2_score', 'mape', 'additional_metrics',
            'training_time_seconds', 'inference_time_ms', 'stability_score',
            'knowledge_retention', 'notes', 'is_best_model', 'is_production_model'
        ]
    
    def validate(self, data):
        """Validar datos del serializer."""
        # Validar mÃ©tricas principales
        if 'r2_score' in data and (data['r2_score'] < 0 or data['r2_score'] > 1):
            raise serializers.ValidationError("RÂ² score debe estar entre 0 y 1")
        
        if 'mae' in data and data['mae'] < 0:
            raise serializers.ValidationError("MAE debe ser mayor o igual a 0")
        
        if 'rmse' in data and data['rmse'] < 0:
            raise serializers.ValidationError("RMSE debe ser mayor o igual a 0")
        
        return data


class ModelMetricsStatsSerializer(serializers.Serializer):
    """Serializer para estadÃ­sticas de mÃ©tricas de modelos."""
    total_models = serializers.IntegerField()
    models_by_type = serializers.DictField()
    models_by_target = serializers.DictField()
    best_models_count = serializers.IntegerField()
    production_models_count = serializers.IntegerField()
    average_r2_score = serializers.FloatField()
    best_r2_score = serializers.FloatField()
    worst_r2_score = serializers.FloatField()
    recent_models = serializers.ListField()


class ModelPerformanceTrendSerializer(serializers.Serializer):
    """Serializer para tendencia de rendimiento de modelos."""
    model_name = serializers.CharField()
    target = serializers.CharField()
    metric_type = serializers.CharField()
    trend_data = serializers.ListField()
    current_performance = serializers.DictField()
    improvement_trend = serializers.CharField()


class ModelComparisonSerializer(serializers.Serializer):
    """Serializer para comparaciÃ³n entre modelos."""
    model_a = ModelMetricsSerializer()
    model_b = ModelMetricsSerializer()
    comparison_metrics = serializers.DictField()
    winner = serializers.CharField()
    improvement_percentage = serializers.FloatField()


class SystemSettingsSerializer(serializers.ModelSerializer):
    """Serializer para configuraciÃ³n del sistema."""
    logo_url = serializers.SerializerMethodField()


class SendOtpSerializer(serializers.Serializer):
    """Serializer para envÃ­o de cÃ³digo OTP."""
    email = serializers.EmailField()


class VerifyOtpSerializer(serializers.Serializer):
    """Serializer para verificaciÃ³n de cÃ³digo OTP."""
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6, min_length=6)

