"""
Serializers para autenticación y gestión de usuarios en CacaoScan.

Incluye serializers para login, registro, perfil de usuario
y operaciones de autenticación JWT.
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import User, UserProfile


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado para obtener tokens JWT.
    
    Extiende el serializer base para incluir información
    adicional del usuario en la respuesta.
    """
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Agregar claims personalizados
        token['email'] = user.email
        token['role'] = user.role
        token['full_name'] = user.get_full_name()
        token['is_verified'] = user.is_verified
        
        return token
    
    def validate(self, attrs):
        # Obtener datos base
        data = super().validate(attrs)
        
        # Agregar información del usuario
        data.update({
            'user': {
                'id': str(self.user.id),
                'email': self.user.email,
                'username': self.user.username,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'role': self.user.role,
                'is_verified': self.user.is_verified,
                'is_active': self.user.is_active,
                'date_joined': self.user.date_joined.isoformat(),
            }
        })
        
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de nuevos usuarios.
    
    Valida y crea usuarios con información básica y perfil.
    """
    
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Contraseña del usuario (mínimo 8 caracteres)"
    )
    
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirmación de contraseña"
    )
    
    # Campos del perfil (opcionales)
    region = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Región geográfica"
    )
    
    municipality = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Municipio"
    )
    
    farm_name = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Nombre de la finca (solo agricultores)"
    )
    
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            'phone_number',
            'role',
            # Campos del perfil
            'region',
            'municipality',
            'farm_name',
        ]
        
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }
    
    def validate_email(self, value):
        """Valida que el email no esté en uso."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Ya existe un usuario con este correo electrónico."
            )
        return value
    
    def validate_username(self, value):
        """Valida que el username no esté en uso."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Ya existe un usuario con este nombre de usuario."
            )
        return value
    
    def validate_password(self, value):
        """Valida la contraseña usando las reglas de Django."""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, attrs):
        """Validación global del serializer."""
        # Verificar que las contraseñas coincidan
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm', None)
        
        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': 'Las contraseñas no coinciden.'
            })
        
        # Validar que agricultores tengan información de finca
        role = attrs.get('role', 'farmer')
        farm_name = attrs.get('farm_name', '')
        
        if role == 'farmer' and not farm_name:
            attrs['farm_name'] = f"Finca de {attrs.get('first_name', 'Usuario')}"
        
        return attrs
    
    def create(self, validated_data):
        """Crea usuario y perfil asociado."""
        # Extraer campos del perfil
        profile_fields = {
            'region': validated_data.pop('region', ''),
            'municipality': validated_data.pop('municipality', ''),
            'farm_name': validated_data.pop('farm_name', ''),
        }
        
        # Crear usuario
        password = validated_data.pop('password')
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        # Actualizar perfil con información adicional
        if any(profile_fields.values()):
            for field, value in profile_fields.items():
                if value:
                    setattr(user.profile, field, value)
            user.profile.save()
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer para login de usuarios.
    
    Acepta email/username y contraseña, retorna información del usuario.
    """
    
    email_or_username = serializers.CharField(
        help_text="Email o nombre de usuario"
    )
    
    password = serializers.CharField(
        style={'input_type': 'password'},
        help_text="Contraseña del usuario"
    )
    
    def validate(self, attrs):
        email_or_username = attrs.get('email_or_username')
        password = attrs.get('password')
        
        if email_or_username and password:
            # Intentar autenticar por email primero
            user = None
            
            # Si contiene @, es email
            if '@' in email_or_username:
                try:
                    user_obj = User.objects.get(email=email_or_username)
                    user = authenticate(
                        request=self.context.get('request'),
                        username=user_obj.username,
                        password=password
                    )
                except User.DoesNotExist:
                    pass
            else:
                # Si no, es username
                user = authenticate(
                    request=self.context.get('request'),
                    username=email_or_username,
                    password=password
                )
            
            if not user:
                raise serializers.ValidationError(
                    'Credenciales inválidas. Verifique email/usuario y contraseña.',
                    code='authorization'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'Cuenta de usuario desactivada.',
                    code='authorization'
                )
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Debe incluir email/usuario y contraseña.',
                code='authorization'
            )


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para el perfil extendido del usuario.
    """
    
    location_display = serializers.ReadOnlyField()
    experience_level = serializers.ReadOnlyField(source='get_experience_level')
    
    class Meta:
        model = UserProfile
        fields = [
            'region',
            'municipality',
            'farm_name',
            'years_experience',
            'farm_size_hectares',
            'preferred_language',
            'email_notifications',
            'location_display',
            'experience_level',
            'created_at',
            'updated_at',
        ]
        
        read_only_fields = ['created_at', 'updated_at']


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer completo para información del usuario.
    
    Incluye perfil y información detallada.
    """
    
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.ReadOnlyField(source='get_full_name')
    role_display = serializers.ReadOnlyField(source='get_role_display')
    role_display_verbose = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'phone_number',
            'role',
            'role_display',
            'role_display_verbose',
            'is_verified',
            'is_active',
            'date_joined',
            'last_login',
            'profile',
        ]
        
        read_only_fields = [
            'id',
            'date_joined',
            'last_login',
            'is_verified',  # Solo admin puede cambiar
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar información del usuario.
    
    Permite actualizar datos básicos y perfil.
    """
    
    # Campos del perfil
    region = serializers.CharField(
        required=False,
        allow_blank=True,
        source='profile.region'
    )
    
    municipality = serializers.CharField(
        required=False,
        allow_blank=True,
        source='profile.municipality'
    )
    
    farm_name = serializers.CharField(
        required=False,
        allow_blank=True,
        source='profile.farm_name'
    )
    
    years_experience = serializers.IntegerField(
        required=False,
        allow_null=True,
        source='profile.years_experience'
    )
    
    farm_size_hectares = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True,
        source='profile.farm_size_hectares'
    )
    
    preferred_language = serializers.CharField(
        required=False,
        source='profile.preferred_language'
    )
    
    email_notifications = serializers.BooleanField(
        required=False,
        source='profile.email_notifications'
    )
    
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'phone_number',
            # Campos del perfil
            'region',
            'municipality',
            'farm_name',
            'years_experience',
            'farm_size_hectares',
            'preferred_language',
            'email_notifications',
        ]
    
    def update(self, instance, validated_data):
        """Actualiza usuario y perfil."""
        # Extraer datos del perfil
        profile_data = validated_data.pop('profile', {})
        
        # Actualizar usuario
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar perfil
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para cambio de contraseña.
    """
    
    old_password = serializers.CharField(
        style={'input_type': 'password'},
        help_text="Contraseña actual"
    )
    
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        help_text="Nueva contraseña"
    )
    
    confirm_password = serializers.CharField(
        style={'input_type': 'password'},
        help_text="Confirmación de nueva contraseña"
    )
    
    def validate_old_password(self, value):
        """Valida que la contraseña actual sea correcta."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Contraseña actual incorrecta.")
        return value
    
    def validate_new_password(self, value):
        """Valida la nueva contraseña."""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, attrs):
        """Valida que las contraseñas nuevas coincidan."""
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        
        if new_password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': 'Las contraseñas no coinciden.'
            })
        
        return attrs
    
    def save(self):
        """Cambia la contraseña del usuario."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserBulkActionSerializer(serializers.Serializer):
    """
    Serializer para acciones masivas de usuarios.
    """
    
    user_ids = serializers.ListField(
        child=serializers.CharField(),
        help_text="Lista de IDs de usuarios"
    )
    
    action = serializers.ChoiceField(
        choices=[
            ('activate', 'Activar'),
            ('deactivate', 'Desactivar'),
            ('verify', 'Verificar'),
            ('unverify', 'Desverificar'),
        ],
        help_text="Acción a realizar"
    )
    
    def validate_user_ids(self, value):
        """Valida que los IDs de usuario existan."""
        if not value:
            raise serializers.ValidationError("Debe proporcionar al menos un ID de usuario")
        
        # Verificar que no hay más de 100 usuarios (límite de seguridad)
        if len(value) > 100:
            raise serializers.ValidationError("No se pueden procesar más de 100 usuarios a la vez")
        
        # Verificar que los usuarios existen
        existing_count = User.objects.filter(id__in=value).count()
        if existing_count != len(value):
            raise serializers.ValidationError("Algunos IDs de usuario no existen")
        
        return value


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer para solicitud de restablecimiento de contraseña.
    """
    
    email = serializers.EmailField(
        help_text="Email del usuario para restablecimiento"
    )
    
    def validate_email(self, value):
        """Valida que el email tenga formato correcto."""
        return value.lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer para confirmación de restablecimiento de contraseña.
    """
    
    uid = serializers.CharField(help_text="UID del usuario")
    token = serializers.CharField(help_text="Token de restablecimiento")
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        help_text="Nueva contraseña"
    )
    confirm_password = serializers.CharField(
        style={'input_type': 'password'},
        help_text="Confirmación de nueva contraseña"
    )
    
    def validate_new_password(self, value):
        """Valida la nueva contraseña."""
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, attrs):
        """Valida que las contraseñas coincidan."""
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        
        if new_password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': 'Las contraseñas no coinciden.'
            })
        
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer para verificación de email.
    """
    
    uid = serializers.CharField(help_text="UID del usuario")
    token = serializers.CharField(help_text="Token de verificación")
