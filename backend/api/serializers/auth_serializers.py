"""
Authentication serializers for CacaoScan API.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from ..utils.model_imports import get_models_safely

# Import models safely
models = get_models_safely({
    'UserProfile': 'auth_app.models.UserProfile',
})
UserProfile = models['UserProfile']


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')
        
        # If email is provided, use it as username
        if email and not username:
            username = email
            attrs['username'] = email
        
        # Validate that at least one is present
        if not username and not email:
            raise serializers.ValidationError('Debe incluir username o email.')
        
        if username and password:
            # Try to authenticate with username
            user = authenticate(username=username, password=password)
            
            # If it doesn't work, try with email
            if not user and email:
                try:
                    # Use .first() instead of .get() to avoid error if there are multiple users
                    user_obj = User.objects.filter(email=email).first()
                    if user_obj:
                        user = authenticate(username=user_obj.username, password=password)
                    else:
                        user = None
                except Exception:
                    user = None
            
            if user:
                if not user.is_active:
                    # Check if there's a pending verification token
                    if hasattr(user, 'auth_email_token') and not user.auth_email_token.is_verified:
                        raise serializers.ValidationError(
                            'Tu cuenta no está verificada. Por favor verifica tu correo electrónico antes de iniciar sesión. '
                            'Si no recibiste el correo, puedes solicitar uno nuevo desde la página de registro.'
                        )
                    else:
                        raise serializers.ValidationError('Usuario inactivo.')
                attrs['user'] = user
                return attrs
            else:
                raise serializers.ValidationError('Credenciales inválidas.')
        else:
            raise serializers.ValidationError('Debe incluir username/email y password.')


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password_confirm')
    
    def validate_username(self, value):
        """Validate unique username and format."""
        if '@' in value:
            return value
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está en uso.")
        if len(value) < 3:
            raise serializers.ValidationError("El nombre de usuario debe tener al menos 3 caracteres.")
        if not value.replace('_', '').replace('-', '').isalnum():
            raise serializers.ValidationError("El nombre de usuario solo puede contener letras, números, guiones y guiones bajos.")
        return value
    
    def validate_email(self, value):
        """Validate unique email and format."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, value):
            raise serializers.ValidationError("Ingresa un email válido.")
        return value
    
    def validate_password(self, value):
        """Validate password strength."""
        from core.utils import validate_password_strength
        return validate_password_strength(value)
    
    def validate(self, attrs):
        """General validations."""
        from core.utils import validate_passwords_match
        validate_passwords_match(attrs['password'], attrs['password_confirm'])
        if not attrs.get('first_name', '').strip():
            raise serializers.ValidationError("El nombre es requerido.")
        if not attrs.get('last_name', '').strip():
            raise serializers.ValidationError("El apellido es requerido.")
        if attrs.get('username') != attrs.get('email'):
            attrs['username'] = attrs['email']
        return attrs
    
    def create(self, validated_data):
        """Create user with complete validations."""
        validated_data.pop('password_confirm')
        
        # Ensure username equals email
        validated_data['username'] = validated_data['email']
        
        # Create user using create_user for automatic password hashing
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            is_active=False  # User inactive until email verification
        )
        
        # Invalidar cache de estadísticas cuando se crean nuevos usuarios
        try:
            from core.utils import invalidate_system_stats_cache
            invalidate_system_stats_cache()
        except Exception:
            pass  # No fallar si hay error en invalidación de cache
        
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for authenticated user password change.
    """
    old_password = serializers.CharField(
        write_only=True,
        required=True,
        label="Contraseña actual"
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        label="Nueva contraseña"
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        label="Confirmar nueva contraseña"
    )
    
    def validate_old_password(self, value):
        """Validate that current password is provided."""
        if not value:
            raise serializers.ValidationError("La contraseña actual es requerida.")
        return value
    
    def validate_new_password(self, value):
        """
        Validate that new password meets security requirements.
        """
        from core.utils import validate_password_strength
        return validate_password_strength(value)
    
    def validate(self, attrs):
        """General validations."""
        from core.utils import validate_passwords_match, validate_password_different
        validate_passwords_match(attrs.get('new_password'), attrs.get('confirm_password'))
        validate_password_different(attrs.get('old_password'), attrs.get('new_password'))
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification."""
    token = serializers.UUIDField()
    
    def validate_token(self, value):
        """Validate that token exists and hasn't expired."""
        from ..models import EmailVerificationToken
        
        token_obj = EmailVerificationToken.get_valid_token(value)
        if not token_obj:
            raise serializers.ValidationError("Token inválido o expirado.")
        
        if token_obj.is_verified:
            raise serializers.ValidationError("Este email ya ha sido verificado.")
        
        return value


class ResendVerificationSerializer(serializers.Serializer):
    """Serializer for resending email verification."""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Validate that email exists and is not verified."""
        try:
            user = User.objects.get(email=value)
            if user.is_active and hasattr(user, 'auth_email_token'):
                if user.auth_email_token.is_verified:
                    raise serializers.ValidationError("Este email ya ha sido verificado.")
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("No existe una cuenta con este email.")


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user information."""
    role = serializers.SerializerMethodField()
    is_verified = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined', 'role', 'is_verified')
        read_only_fields = ('id', 'date_joined')
    
    def get_role(self, obj):
        """Determine user role based on permissions."""
        if obj.is_superuser or obj.is_staff:
            return 'admin'
        elif obj.groups.filter(name='analyst').exists():
            return 'analyst'
        else:
            return 'farmer'
    
    def get_is_verified(self, obj):
        """Get email verification status."""
        try:
            if hasattr(obj, 'email_verification_token'):
                return obj.email_verification_token.is_verified
        except Exception:
            pass
        return obj.is_active  # Fallback for users without verification token


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for extended user profile."""
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
        """Validate years of experience."""
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("Los años de experiencia deben estar entre 0 y 100.")
        return value
    
    def validate_farm_size_hectares(self, value):
        """Validate farm size."""
        if value is not None and (value < 0 or value > 10000):
            raise serializers.ValidationError("El tamaño de la finca debe estar entre 0 y 10,000 hectáreas.")
        return value


class SendOtpSerializer(serializers.Serializer):
    """Serializer for sending OTP code."""
    email = serializers.EmailField()


class VerifyOtpSerializer(serializers.Serializer):
    """Serializer for verifying OTP code."""
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6, min_length=6)

